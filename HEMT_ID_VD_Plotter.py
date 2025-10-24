import numpy as np
import matplotlib.pyplot as plt

IV_Data = np.load("HEMT_IV_Data_ID_VD.npz")
#IV_Data = np.load("HEMT_IV_Data_Kethley.npz")
V_D_V_G_array = IV_Data["V_D_V_G_array"]
I_D_V_G_array = IV_Data["I_D_V_G_array"]
V_G_initial = IV_Data["V_G_initial"]
V_G_inc = IV_Data["V_G_inc"]
N_G, N_D = np.shape(V_D_V_G_array)
print(f"N_G = {N_G}, N_D = {N_D}")

# Plot waveform
plt.figure(1)
Imax = 0; Imin = 0;
for j in range(N_G):
    plt.plot(V_D_V_G_array[j], I_D_V_G_array[j], label = f"V_G = {V_G_initial + j*V_G_inc}")
    #plt.scatter(V_app_array, V_CH2_array, label = "V_CH2")
    Imax = 1#max(Imax, max(I_D_V_G_array[j])); 
    Imin = min(Imin, min(I_D_V_G_array[j]));

Ipp = abs(Imax - Imin)
plt.ylim(Imin - 0.1*Ipp, Imax + 0.1*Ipp)
plt.xlabel("Drain Voltage, V_D(V)")
plt.ylabel("Drain Current, I_D(A)")
plt.title("HEMT I_D V_D Characteristics")
plt.grid(True); plt.legend(); plt.show()