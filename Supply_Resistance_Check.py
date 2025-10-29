import numpy as np
import matplotlib.pyplot as plt
import serial
import time
import math
from Functions import ser, send_query, send, Set_DC_Voltage_PSupply, Measure_DC_I

############################################################################################################

V_D_inc = 0.01#set the increment in V_D
V_D_initial = 0.01#set the initial value of V_D
V_D_final = 0.17#set the final value of V_D
V_D = V_D_initial

plot_every_sweep = True
###########################################################################################################
#check data limits
V_D_limit = 5
if V_D_final > V_D_limit:
    print(f"V_D_final = {V_D_final}V > {V_D_limit}V; Keep the V_D under {V_D_limit}V")
    print("Edit the Voltage Values Properly.")
    print("Exiting Code...")
    exit()

##############################################################################################################
#python has some troble with precision
#it calculates 1.7 - 1.1 as 0.59999999999999
#floor(0.59999999999999/0.2) will give 2 instead of 3
#very inconvenient

N_D = int(np.ceil(abs(V_D_final - V_D_initial)/V_D_inc) + 1)

V_array = np.zeros(N_D)
I_array = np.zeros(N_D)

#R_D = 30.15   #2.5
###########################################################################################################
#Identify instrument
print("IDN:", send_query('*IDN?'))

# Enable remote mode
send('SYST:REM')

#reset the power supply
send('*RST')

# Turn output ON
send('OUTP ON')
time.sleep(0.5)

#set max current levels to 2A, 2A, 100ma
send("APP:CURR 3, 3, 3")

#ID VD Characteristics for different VG
############################################################################################################
#Full Input Output Response Tester
#Sweep Voltage
#Take the input voltage reading
#take the output voltage reading

#R_out = 11.846   #output resistance of power supply; 
#can cause trouble with high current cases; especially for ID_VG sweeps

for i in range(N_D):
    V_D_measured = Set_DC_Voltage_PSupply(Source_ID=1, Vapp=V_D)
    time.sleep(0.5)
    I_D_measured = Measure_DC_I(Source_ID=1)

    V_array[i] = V_D_measured
    I_array[i] = I_D_measured
    print(f"V = {V_D_measured}V;\t I = {I_D_measured}A")

    V_D += V_D_inc
    
###########################################################################################################
#reset voltages to 0 after plot
Set_DC_Voltage_PSupply(Source_ID=1, Vapp=0)
Set_DC_Voltage_PSupply(Source_ID=3, Vapp=0)

###########################################################################################################
#print("Voltages = ", V_D_array, "\n")
#print("Currents = ", I_D_array, "\n")

#Save the data
np.savez("Supply_Characteristics.npz", V_array=V_array, I_array=I_array, V_D_initial=V_D_initial, V_D_inc=V_D_inc)

plt.figure(1)
Imax = 0; Imin = 0;
plt.scatter(V_array, I_array)
Imax = max(Imax, max(I_array)); Imin = min(Imin, min(I_array));
Ipp = abs(Imax - Imin)
plt.ylim(Imin - 0.1*Ipp, Imax + 0.1*Ipp)
plt.xlabel("Supply Voltage, V(V)")
plt.ylabel("Supply Current, I_SC(A)")
plt.title(f"Supply Characteristics")
plt.grid(True);
plt.show()

###########################################################################################################
ser.close()

