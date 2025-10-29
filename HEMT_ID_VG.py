import numpy as np
import matplotlib.pyplot as plt
import serial
import time
import math
from Functions import ser, send_query, send, Set_DC_Voltage_PSupply, Measure_DC_I, R_out, Control_IV_Voltage

############################################################################################################
V_G_inc = 0.03#set the increment in V_G
V_G_initial = 1.25#set the initial value of V_G
V_G_final = 3#set the final value of V_G
V_G = V_G_initial

V_D_inc = 0.1#set the increment in V_D
V_D_initial = 0.2#set the initial value of V_D
V_D_final = 0.4#set the final value of V_D
V_D = V_D_initial

plot_every_sweep = True
###########################################################################################################
#check data limits
V_D_limit = 2.2
if V_D_final > V_D_limit:
    print(f"V_D_final = {V_D_final}V > {V_D_limit}V; Keep the V_D under {V_D_limit}V")
    print("Edit the Voltage Values Properly.")
    print("Exiting Code...")
    exit()

V_G_limit = 4.2
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
N_G = int(np.ceil(abs(V_G_final - V_G_initial)/V_G_inc) + 1)
N_D = int(np.ceil(abs(V_D_final - V_D_initial)/V_D_inc) + 1)

V_G_V_D_array = np.zeros((N_D, N_G))
I_D_V_D_array = np.zeros((N_D, N_G))

#R_D = 30.15   #2.5

###########################################################################################################
#Identify instrument
print("IDN:", send_query('*IDN?'))

# Enable remote mode
send('SYST:REM')

Set_DC_Voltage_PSupply(Source_ID=1, Vapp=0)
Set_DC_Voltage_PSupply(Source_ID=2, Vapp=0)
Set_DC_Voltage_PSupply(Source_ID=2, Vapp=0)
time.sleep(0.5)

#reset the power supply
send('*RST')

#set max current levels to 2A, 2A, 100ma
send("APP:CURR 3, 3, 3")

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

        #control Drain current because acutal V_DS may drop from applied due to supply resistance R_out
        V_D_measured = Control_IV_Voltage(Source_ID=1, Vcont=V_D)

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

