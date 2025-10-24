import numpy as np
import matplotlib.pyplot as plt

IV_Data = np.load("HEMT_IV_Data_ID_VG.npz")
V_G_V_D_array = IV_Data["V_G_V_D_array"]
I_D_V_D_array = IV_Data["I_D_V_D_array"]
V_D_initial = IV_Data["V_D_initial"]
V_D_inc = IV_Data["V_D_inc"]
N_D, N_G = np.shape(V_G_V_D_array)
print(f"N_G = {N_G}, N_D = {N_D}")

# Plot waveform
plt.figure(1)
Imax = 0; Imin = 0;
for j in range(N_D):
    #plt.plot(V_G_V_D_array[j], I_D_V_D_array[j], label = f"V_D = {V_D_initial + j*V_D_inc}")
    #plt.scatter(V_app_array, V_CH2_array, label = "V_CH2")
    plt.semilogy(V_G_V_D_array[j], I_D_V_D_array[j], label = f"V_D = {V_D_initial + j*V_D_inc}")
    Imax = max(Imax, max(I_D_V_D_array[j])); Imin = min(Imin, min(I_D_V_D_array[j]));

Ipp = abs(Imax - Imin)
plt.ylim(Imin - 0.1*Ipp, Imax + 0.1*Ipp)
plt.xlabel("Gate Voltage, V_G(V)")
plt.ylabel("Drain Current, I_D(A)")
plt.title("HEMT I_D vs V_G Characteristics")
plt.grid(True); plt.legend(); plt.show()