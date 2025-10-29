import numpy as np
import matplotlib.pyplot as plt
import serial
import time
import math

###########################################################################################################
R_out = 0.11   #output resistance of power supply; 
#can cause trouble with high current cases; especially for ID_VG sweeps

###########################################################################################################
ser = serial.Serial(
    port='COM5',      # your COM port
    baudrate=9600,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    timeout=1
)

# Send a command that expects a response
def send_query(cmd):
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    ser.write((cmd + "\r\n").encode())
    time.sleep(0.2)
    response = b""
    while ser.in_waiting:
        response += ser.read(ser.in_waiting)
        time.sleep(0.05)
    resp_str = response.decode().strip()
    return resp_str if resp_str else None


# Send a command that does NOT expect a response
def send(cmd):
    ser.write((cmd + "\r\n").encode())
    time.sleep(0.1)

###########################################################################################################
def Set_DC_Voltage_PSupply(Source_ID, Vapp):
    #print(f"selecting channel {Source_ID}")
    # Select channel 1
    send(f"INST:NSEL {Source_ID}")

    #print("Initialising")
    send("INIT")

    # Set voltage and current
    #print(f'Sending voltage {Vapp}V')
    send(f"VOLT {Vapp}")

    voltage_str = send_query('MEAS:VOLT?')
    #print("Read back Voltage string 1st time")
    while (voltage_str is None):
        voltage_str = send_query('MEAS:VOLT?')
        #print("Voltage string read back none")
    #print("Out of none loop 1")

    voltage = float(voltage_str.split("\n", 1)[0])
    #print(f"Voltage read = {voltage}")
    voltage_target = Vapp
    voltage_rel_err = 1
    max_iter = 10
    iter = 0
    while((voltage_rel_err > 0.05) and (iter <= max_iter)):  #keep measuring voltage till voltage stabilises within 1% error
        iter += 1
        voltage_str = send_query('MEAS:VOLT?')  #measure 1st
        while(voltage_str is None):             #repeat till we get a non-none value
            voltage_str = send_query('MEAS:VOLT?')
        voltage = float(voltage_str.split("\n", 1)[0])
        #print(f"Voltage read = {voltage}")
        if (abs(voltage) < 0.01):     #don't do it for 10mV or lower measures
            break
        
        if voltage_target != 0:
            voltage_rel_err = abs(1 - voltage/voltage_target)
        #print(f"Target Voltage = {Vapp}V; Measured Voltage = {voltage}V; Rel Error = {voltage_rel_err}")
    return voltage
    #time.sleep(0.5)

############################################################################################################
# Measure Voltage and Current
def Measure_DC_I(Source_ID = 1):
    # Select channel 1
    send("INIT")
    send(f"INST:NSEL {Source_ID}")
    
    current_str = send_query('MEAS:CURR?')
    while(current_str is None):
        current_str = send_query('MEAS:CURR?')
    current = float(current_str.split("\n", 1)[0])
    current_prev = current
    current_rel_err = 1
    while(current_rel_err > 0.01):  #keep measuring current till voltage stabilises within 1% error
        current_str = send_query('MEAS:CURR?')  #measure 1st
        while(current_str is None):             #repeat till we get a non-none value
            current_str = send_query('MEAS:CURR?')
        current = float(current_str.split("\n", 1)[0])
        if (current < 0.001):     #don't do it for 1mA or lower measures
            break
        current_rel_err = abs(1 - current_prev/current)
        current_prev = current
        #print(f"Current Relative Error = {current_rel_err}")

    #time.sleep(1)
    #return voltage, current
    return current

###########################################################################################################
def Control_IV_Voltage(Source_ID, Vcont):
    V_D_measured = Set_DC_Voltage_PSupply(Source_ID, Vapp=Vcont)
    V_D_Supply = Set_DC_Voltage_PSupply(Source_ID, Vapp=Vcont)
    #control Drain current because acutal V_DS may drop from applied due to supply resistance R_out
    #V_D_measured = Set_DC_Voltage_PSupply(Source_ID=1, Vapp=V_D)
    #V_D_measured_rel_error = 1
    V_D_measured_err = 1
    I_D_measured = Measure_DC_I(Source_ID)
    while(abs(V_D_measured_err) > 0.005):
        V_D_Supply = Set_DC_Voltage_PSupply(Source_ID, Vapp=(Vcont + R_out*I_D_measured))
        I_D_measured = Measure_DC_I(Source_ID)
        V_D_measured = V_D_Supply - I_D_measured*R_out
            
        if (V_D_measured < 0.01):
            break
        V_D_measured_err = Vcont - V_D_measured
        #V_D_measured_rel_error = (1 - V_D_measured/Vcont)
    return V_D_measured
