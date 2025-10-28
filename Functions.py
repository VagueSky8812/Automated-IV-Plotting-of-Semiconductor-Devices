import numpy as np
import matplotlib.pyplot as plt
import serial
import time
import math

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
    send("INIT")
    # Select channel 1
    send(f"INST:NSEL {Source_ID}")

    # Set voltage and current
    send(f"VOLT {Vapp}")
    voltage_str = send_query('MEAS:VOLT?')
    while (voltage_str is None):
        voltage_str = send_query('MEAS:VOLT?')
    voltage = float(voltage_str)
    voltage_target = Vapp
    voltage_rel_err = 1
    while(voltage_rel_err > 0.05):  #keep measuring voltage till voltage stabilises within 1% error
        voltage_str = send_query('MEAS:VOLT?')  #measure 1st
        while(voltage_str is None):             #repeat till we get a non-none value
            voltage_str = send_query('MEAS:VOLT?')
        voltage = float(voltage_str)
        if (voltage < 0.01):     #don't do it for 10mV or lower measures
            break
        voltage_rel_err = abs(1 - voltage_target/voltage)
        #print(f"Target Voltage = {Vapp}V; Measured Voltage = {voltage}V; Rel Error = {voltage_rel_err}")
    return voltage
    #time.sleep(0.5)

############################################################################################################
# Measure Voltage and Current
def Measure_DC_I(Source_ID = 1):
    # Select channel 1
    #send("INIT")
    send(f"INST:NSEL {Source_ID}")
    #time.sleep(1)
    send("INIT")
    current_str = send_query('MEAS:CURR?')
    while(current_str is None):
        current_str = send_query('MEAS:CURR?')
    current = float(current_str)
    current_prev = current
    current_rel_err = 1
    while(current_rel_err > 0.01):  #keep measuring current till voltage stabilises within 1% error
        current_str = send_query('MEAS:CURR?')  #measure 1st
        while(current_str is None):             #repeat till we get a non-none value
            current_str = send_query('MEAS:CURR?')
        current = float(current_str)
        if (current < 0.001):     #don't do it for 1mA or lower measures
            break
        current_rel_err = abs(1 - current_prev/current)
        current_prev = current
        #print(f"Current Relative Error = {current_rel_err}")

    #time.sleep(1)
    #return voltage, current
    return current

###########################################################################################################
