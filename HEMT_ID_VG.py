import numpy as np
import matplotlib.pyplot as plt
import serial
import time
import math
############################################################################################################
V_G_inc = #set the increment in V_G
V_G_initial = #set the initial value of V_G
V_G_final = #set the final value of V_G
V_G = V_G_initial

V_D_inc = #set the increment in V_D
V_D_initial = #set the initial value of V_D
V_D_final = #set the final value of V_D
V_D = V_D_initial

plot_every_sweep = False
###########################################################################################################
#check data limits
V_D_limit = 0.4
if V_D_final > V_D_limit:
    print(f"V_D_final = {V_D_final}V > {V_D_limit}V; Keep the V_D under {V_D_limit}V")
    print("Edit the Voltage Values Properly.")
    print("Exiting Code...")
    exit()

V_G_limit = 2
if V_G_final > V_G_limit:
    print(f"V_G_final = {V_G_final}V > {V_G_limit}V; Keep the V_G under {V_G_limit}V")
    print("Edit the Voltage Values Properly.")
    print("Exiting Code...")
    exit()

##############################################################################################################
#python has some troble with precision
#it calculates 1.7 - 1.1 as 0.59999999999999
#floor(0.59999999999999/0.2) will give 2 instead of 3
#very inconvenient
N_G = int(np.floor(abs(V_G_final - V_G_initial)/V_G_inc) + 1)
if (V_G_final-V_G_initial)%V_G_inc > 0:
    N_G += 1
#N_G = 2
N_D = int(np.floor(abs(V_D_final - V_D_initial)/V_D_inc) + 1)
if (V_D_final-V_D_initial)%V_D_inc > 0:
    N_D += 1
#N_D = 5

V_G_V_D_array = np.zeros((N_D, N_G))
I_D_V_D_array = np.zeros((N_D, N_G))

#R_D = 30.15   #2.5
############################################################################################################
ser = serial.Serial(
    port='COM3',      # your COM port
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
#Identify instrument
print("IDN:", send_query('*IDN?'))

# Enable remote mode
send('SYST:REM')

# Turn output ON
#send('OUTP ON')
#time.sleep(0.5)

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
    send("INIT")
    send(f"INST:NSEL {Source_ID}")
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

############################################################################################################
Set_DC_Voltage_PSupply(Source_ID=1, Vapp=0)
Set_DC_Voltage_PSupply(Source_ID=2, Vapp=0)
Set_DC_Voltage_PSupply(Source_ID=2, Vapp=0)
time.sleep(0.5)

# Turn output ON
send('OUTP ON')
time.sleep(0.5)

############################################################################################################
#ID VD Characteristics for different VG
############################################################################################################
#Full Input Output Response Tester
#Sweep Voltage
#Take the input voltage reading
#take the output voltage reading

for j in range(N_D):
    #print(f"j = {j} before I_D V_D sweep")
    #V_G = i*V_D_inc
    V_D_measured = Set_DC_Voltage_PSupply(Source_ID=1, Vapp=V_D)
    print(f"V_D = {V_D}")

    V_G = V_G_initial
    V_G_array = np.zeros(N_G)
    I_D_array = np.zeros(N_G)
    i = 0
    
    #time.sleep(1)
    #initialising
    
    I_D_measured = 0
    for i in range(N_G):
        #Apply gATE Voltage
        V_G_measured = Set_DC_Voltage_PSupply(Source_ID=3, Vapp=V_G)

        #Measure Drain voltage and currrent
        I_D_measured = Measure_DC_I(Source_ID=1)
        #if (I_D_measured > 0.49):
        #    break

        V_G_array[i] = V_G_measured
        I_D_array[i] = I_D_measured
        print(f"V_G = {V_G_array[i]}V;\t I_D = {I_D_array[i]}A")
        #print(f"i = {i}; j = {j}\n")
        V_G += V_G_inc

    #print(f"j = {j} after I_D V_D sweep\n")
    V_G_V_D_array[j] = V_G_array
    I_D_V_D_array[j] = I_D_array

    #temporary plot
    if plot_every_sweep:
        plt.figure(j)
        Imax = 0; Imin = 0;
        plt.scatter(V_G_V_D_array[j], I_D_V_D_array[j], label = f"V_D = {V_D}V")
        Imax = max(Imax, max(I_D_array)); Imin = min(Imin, min(I_D_array));
        Ipp = abs(Imax - Imin)
        plt.ylim(Imin - 0.1*Ipp, Imax + 0.1*Ipp)
        plt.xlabel("Gate Voltage, V_G(V)")
        plt.ylabel("Drain Current, I_D(A)")
        plt.title(f"HEMT NMOS I_D vs V_G for V_D = {V_D}")
        plt.grid(True); plt.legend(); 
        plt.show()

    V_D += V_D_inc
    
###########################################################################################################
#reset voltages to 0 after plot
Set_DC_Voltage_PSupply(Source_ID=1, Vapp=0)
Set_DC_Voltage_PSupply(Source_ID=3, Vapp=0)

###########################################################################################################
#print("Voltages = ", V_D_array, "\n")
#print("Currents = ", I_D_array, "\n")

#Save the data
np.savez("HEMT_IV_Data_ID_VG.npz", V_G_V_D_array=V_G_V_D_array, I_D_V_D_array=I_D_V_D_array, V_D_initial=V_D_initial, V_D_inc=V_D_inc)

# Plot All waveform
plt.figure(1)
Imax = 0; Imin = 0;
for j in range(N_D):
    V_D = V_D_initial + V_D_inc*j
    plt.scatter(V_G_V_D_array[j], I_D_V_D_array[j], label = f"V_D = {V_D}V")
    Imax = max(Imax, max(I_D_array)); Imin = min(Imin, min(I_D_array));
Ipp = abs(Imax - Imin)
plt.ylim(Imin - 0.1*Ipp, Imax + 0.1*Ipp)
plt.xlabel("Gate Voltage, V_G(V)")
plt.ylabel("Drain Current, I_D(A)")
plt.title(f"HEMT NMOS I_D vs V_G")
plt.grid(True); plt.legend(); 
plt.show()
###########################################################################################################
ser.close()


