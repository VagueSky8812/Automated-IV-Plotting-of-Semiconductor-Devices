import numpy as np
import matplotlib.pyplot as plt
import serial
import time
import math
from Functions import ser, send_query, send, Set_DC_Voltage_PSupply, Measure_DC_I, R_out, Control_IV_Voltage

###########################################################################################################
V_G_inc = 0.1#set the increment in V_G
V_G_initial = 1.4#set the initial value of V_G
V_G_final = 1.7#set the final value of V_G
V_G = V_G_initial

V_D_inc = 0.04#set the increment id V_D
V_D_initial = 0#set the initial value of V_D
V_D_final = 1.5#set the final value of V_D
V_D = V_D_initial

R_D = 0 #30.15   #2.5

plot_every_sweep = False
###########################################################################################################
#check data limits
V_D_limit = 5
if V_D_final > V_D_limit:
    print(f"V_D_final = {V_D_final}V > {V_D_limit}V; Keep the V_D under {V_D_limit}V")
    print("Edit the Voltage Values Properly.")
    print("Exiting Code...")
    exit()

V_G_limit = 1.7
if V_G_final > V_G_limit:
    print(f"V_G_final = {V_G_final}V > {V_G_limit}V; Keep the V_G under {V_G_limit}V")
    print("Edit the Voltage Values Properly.")
    print("Exiting Code...")
    exit()

###########################################################################################################
#Identify instrument
print("IDN:", send_query('*IDN?'))

# Enable remote mode
send('SYST:REM')

#reset the power supply
send('*RST')

#set max current levels to 2A, 2A, 100ma
send("APP:CURR 3, 3, 3")

Set_DC_Voltage_PSupply(Source_ID=1, Vapp=0)
Set_DC_Voltage_PSupply(Source_ID=2, Vapp=0)
Set_DC_Voltage_PSupply(Source_ID=3, Vapp=0)
# Turn output ON
send('OUTP ON')
time.sleep(0.5)

#ID VD Characteristics for different VG
############################################################################################################
#Full Input Output Response Tester
#Sweep Voltage
#Take the input voltage reading
#take the output voltage reading
#python has some troble with precision
#it calculates 1.7 - 1.1 as 0.59999999999999
#floor(0.59999999999999/0.2) will give 2 instead of 3
#very inconvenient
N_G = int(np.ceil(abs(V_G_final - V_G_initial)/V_G_inc) + 1)
N_D = int(np.ceil(abs(V_D_final - V_D_initial)/V_D_inc) + 1)

V_D_V_G_array = np.zeros((N_G, N_D))
I_D_V_G_array = np.zeros((N_G, N_D))

for j in range(N_G):
    #print(f"j = {j} before I_D V_D sweep")
    #V_G = i*V_D_inc
    Set_DC_Voltage_PSupply(Source_ID=3, Vapp=V_G)
    print(f"V_G = {V_G}")

    V_D = V_D_initial
    V_D_array = np.zeros(N_D)
    I_D_array = np.zeros(N_D)
    i = 0
    
    #time.sleep(1)
    #initialising
    V_D_measured = V_D_initial
    I_D_measured = 0
    V_D_measured_prev = V_D_measured
    I_D_measured_prev = I_D_measured
    for i in range(N_D):
        #apply voltage
        #our purpose is to plot IV;
        #the function generator needs to give 100mA mx; so we must use 50Ohhm setting manually
        #So for V_applied commanded it will produce 2*V_applied;
        #So we must command it to produce 0.5*V_applied
        #Set_DC_Voltage_PSupply(Source_ID = "1", frequency=1e3, amplitude=0.5*Vapplied, duty_cycle = 99.6)

        #Apply Voltage
        V_D_measured = Control_IV_Voltage(Source_ID=1, Vcont=V_D)

        #Measure voltage
        I_D_measured = Measure_DC_I(Source_ID=1)
        #if (I_D_measured > 0.49):
        #    break

        V_D_array[i] = V_D_measured - I_D_measured*R_D
        I_D_array[i] = I_D_measured
        #print(f"V_D_measured = {V_D_measured}V;\t I_D_measured = {I_D_measured}A")
        print(f"V_D = {V_D_array[i]}V;\t I_D = {I_D_array[i]}A")
        #print(f"i = {i}; j = {j}\n")
        V_D += V_D_inc

    #print(f"j = {j} after I_D V_D sweep\n")
    V_D_V_G_array[j] = V_D_array
    I_D_V_G_array[j] = I_D_array

    #temporary plot
    if plot_every_sweep:
        plt.figure(j)
        Imax = 0; Imin = 0;
        plt.scatter(V_D_V_G_array[j], I_D_V_G_array[j], label = f"V_G = {V_G}V")
        Imax = max(Imax, max(I_D_array)); Imin = min(Imin, min(I_D_array));
        Ipp = abs(Imax - Imin)
        plt.ylim(Imin - 0.1*Ipp, Imax + 0.1*Ipp)
        plt.xlabel("Drain Voltage, V_D(V)")
        plt.ylabel("Drain Current, I_R(A)")
        plt.title(f"HEMT NMOS I_D vs V_D for V_G = {V_G}")
        plt.grid(True); plt.legend(); 
        plt.show()

    V_G += V_G_inc

###########################################################################################################
#reset voltages to 0 after plot
Set_DC_Voltage_PSupply(Source_ID=1, Vapp=0)
Set_DC_Voltage_PSupply(Source_ID=3, Vapp=0)

###########################################################################################################

#print("Voltages = ", V_D_array, "\n")
#print("Currents = ", I_D_array, "\n")

#Save the data

np.savez("HEMT_IV_Data_ID_VD.npz", V_D_V_G_array=V_D_V_G_array, I_D_V_G_array=I_D_V_G_array, V_G_initial=V_G_initial, V_G_inc=V_G_inc)

# Plot All waveform
plt.figure(1)
Imax = 0; Imin = 0;
for j in range(N_G):
    V_G = V_G_initial + V_G_inc*j
    plt.scatter(V_D_V_G_array[j], I_D_V_G_array[j], label = f"V_G = {V_G}V")
    Imax = max(Imax, max(I_D_array)); Imin = min(Imin, min(I_D_array));
Ipp = abs(Imax - Imin)
plt.ylim(Imin - 0.1*Ipp, Imax + 0.1*Ipp)
plt.xlabel("Drain Voltage, V_D(V)")
plt.ylabel("Drain Current, I_D(A)")
plt.title("HEMT NMOS IV Characteristics")
plt.grid(True); plt.legend(); 
plt.show()
###########################################################################################################
ser.close()

