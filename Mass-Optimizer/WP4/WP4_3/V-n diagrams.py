import math
import numpy as np
import matplotlib.pyplot as plt

#W_payload = 1010 #kg
#W_oem  = 4876.78 #kg
#W_mtom = 7142.310 #kg
#W_mtom_lbs = 0.454 * W_mtom #lbs

#M_cr = 0.68
#Altitude = 41000 #ft
#Altitude_metric = Altitude / 3.281 #m
#rho_cr = 

#V_c = M_cr * rho_cr  #at cruise conditions
#V_s0 = 1
#V_s1 = 2
#V_a = V_s1 * math.sqrt(n)

# M_d - M_c >= 0.5
#V_f_takeoff = 1.6 * V_s1
#V_f_approach = 1.8 * V_s1
#V_f_landing =  1.8 * V_s0
#n_max = 2.1 + 24000 / (W_mtom_lbs + 10000)
# 2.5 <= n_max <= 3.8
#n_max_flaps = 2
#n_flaps = (V / V_s0)**2
#n_min = -1
#n_neg = -(V / V_s1)**2

def case1():
    # Weights
    W_payload = 1010 # kg
    W_oem = 4876.78 # kg
    W_mtom = 7142.310 # kg
    W_mtom_lbs = 0.454 * W_mtom # lbs
    
    # Flight conditions
    M_cr = 0.68
    Altitude = 41000 # ft
    Altitude_metric = Altitude / 3.281 # m
    rho_cr = 216.65 # kg/m3 or m/s conversion factor
    
    # Stall speeds
    V_s0 = 1   # flaps down
    V_s1 = 2   # flaps up
    
    # Limit load factors
    n_max_flaps = 2
    n_max = 2.1 + 24000 / (W_mtom_lbs + 10000)
    n_max = max(2.5, min(n_max, 3.8))
    n_min = -1
    
    # V-speeds
    V_c = M_cr * rho_cr
    V_d = V_c / 0.8
    V_a = V_s1 * math.sqrt(n_max)
    
    # Flap speeds
    V_f_takeoff = 1.6 * V_s1
    V_f_approach = 1.8 * V_s1
    V_f_landing = 1.8 * V_s0
    
    return {
        'V_s0': V_s0, 'V_s1': V_s1, 'V_a': V_a, 'V_c': V_c, 'V_d': V_d,
        'V_f_takeoff': V_f_takeoff, 'V_f_approach': V_f_approach, 'V_f_landing': V_f_landing,
        'n_max': n_max, 'n_min': n_min, 'n_max_flaps': n_max_flaps
    }
#hello
def case2():
    # Weights
    W_payload = 1010 # kg
    W_oem = 4876.78 # kg
    W_mtom = 7142.310 # kg
    W_mtom_lbs = 0.454 * W_mtom # lbs
    
    # Flight conditions
    M_cr = 0.68
    Altitude = 41000 # ft
    Altitude_metric = Altitude / 3.281 # m
    rho_cr = 216.65 # kg/m3 or m/s conversion factor
    
    # Stall speeds
    V_s0 = 1   # flaps down
    V_s1 = 2   # flaps up
    V_s = 100
    
    # Limit load factors
    n_max_flaps = 2
    n_max = 2.1 + 24000 / (W_mtom_lbs + 10000)
    n_max = max(2.5, min(n_max, 3.8))
    n_min = -1
    
    # V-speeds
    V_c = M_cr * rho_cr
    V_d = V_c / 0.8
    V_a = V_s1 * math.sqrt(n_max)
    
    # Flap speeds
    V_f_takeoff = 1.6 * V_s1
    V_f_approach = 1.8 * V_s1
    V_f_landing = 1.8 * V_s0
    
    return {
        'V_s0': V_s0, 'V_s1': V_s1, 'V_a': V_a, 'V_c': V_c, 'V_d': V_d,
        'V_f_takeoff': V_f_takeoff, 'V_f_approach': V_f_approach, 'V_f_landing': V_f_landing,
        'n_max': n_max, 'n_min': n_min, 'n_max_flaps': n_max_flaps
    }







########## GRAPHING #############

V_values_pos = [V for V in range(0, int(V_D) + 1, 5)]
def line_n_pos(V):
    if n_flaps <= n_max_flaps:
        n_pos = (V / V_s1)**2
        n_flaps = (V / V_s0)**2
    elif V <= V_a:
        n_pos = (V / V_s1)**2
        if n_pos <= n_max_flaps:
            n_flaps = n_max_flaps
    else:
        n_pos = n_max
    return n_pos, n_flaps

""" V_values_flaps = [V for V in range(0, int(V_D) + 1, 5)]
def line_n_pos(V):
    if n_flaps <= n_max_flaps:
        n_flaps = (V / V_s0)**2
    elif :
        n_flaps = n_max_flaps
    else:
        break
    return n_pos """

V_values_neg = [V for V in range(0, int(V_D) + 1, 5)]
def line_n_neg(V):
    if n_neg <= -1:
        n_neg = -(V / V_s1)**2
    elif V <= V_c:
        n_neg = -1
    else:
        n_neg = -1 + 1 / (V_D - V_c)
    return n_neg



########## PLOTTING #############

plt.figure(figsize=(10, 6))
plt.plot(V, n_pos, 'b-', linewidth=2)
plt.plot(V, n_neg, 'b-', linewidth=2)
plt.plot(V, n_flaps, 'b-', linewidth=2)
plt.plot([V_d, V_d], [0, n_max], 'b-', linewidth=2)
plt.plot([V_a, V_a], [0, n_max], 'k-', linestyle='--', linewidth=1)
plt.plot([V_c, V_c], [n_min, n_max], 'k-', linestyle='--', linewidth=1)
plt.plot(V, 1, 'k-', linestyle='--', linewidth=1)
plt.plot(V, -1, 'k-', linestyle='--', linewidth=1)
plt.plot([V_s, V_s], [0, 1], 'k-', linestyle='--', linewidth=1)
plt.title('V_EAS vs n Diagram')
plt.xlabel('V_EAS')
plt.ylabel('n')
plt.legend()
plt.grid(True)
plt.show()


#plt.axvline(x=V_line, ymax=n_max/plt.ylim()[1], color='black', linestyle='--', linewidth=2, label=f'V = {V_line}')




########### Cruise, OEW ############# CASE 1: 














#############################################################

V_values = [v for v in range(0, int(V_D) + 1, 5)]
def linear_n(v):
    if v <= V_B:
        n_pos = 1 + delta_n_B * (v / V_B)
        n_neg = 1 - delta_n_B * (v / V_B)
    elif v <= V_C:
        n_pos = 1 + delta_n_B + (delta_n_C - delta_n_B) * (v - V_B) / (V_C - V_B)
        n_neg = 1 - delta_n_B - (delta_n_C - delta_n_B) * (v - V_B) / (V_C - V_B)
    elif v <= V_D:
        n_pos = 1 + delta_n_C + (delta_n_D - delta_n_C) * (v - V_C) / (V_D - V_C)
        n_neg = 1 - delta_n_C - (delta_n_D - delta_n_C) * (v - V_C) / (V_D - V_C)
    else:
        n_pos = 1 + delta_n_D
        n_neg = 1 - delta_n_D
    return n_pos, n_neg

n_pos = []
n_neg = []
for v in V_values:
    np, nn = linear_n(v)
    n_pos.append(np)
    n_neg.append(nn)
n_max = max(n_pos)
n_ult = 1.5 * n_max
n_new = 0.7 * n_max


print("----- Speeds -----")
print(f"V_B = {V_B:.2f} m/s")
print(f"V_C = {V_C:.2f} m/s")
print(f"V_D = {V_D:.2f} m/s\n")

print("----- Mu_g -----")
print(f"mu_gb = {mu_gb:.3f}")
print(f"mu_gc = {mu_gc:.3f}")
print(f"mu_gd = {mu_gd:.3f}\n")

print("----- Gust Alleviation Factors -----")
print(f"K_B = {K_B:.3f}")
print(f"K_C = {K_C:.3f}") 
print(f"K_D = {K_D:.3f}\n")

print("----- Reference Gust Velocities -----")
print(f"u_hat_B = {u_hat_B:.2f} m/s")
print(f"u_hat_C = {u_hat_C:.2f} m/s")
print(f"u_hat_D = {u_hat_D:.2f} m/s\n")

print("----- Gust Velocities -----")
print(f"u_B = {u_B:.2f} m/s")
print(f"u_C = {u_C:.2f} m/s")
print(f"u_D = {u_D:.2f} m/s\n")

print("----- Delta n -----")
print(f"Δn_B = {delta_n_B:.3f}")
print(f"Δn_C = {delta_n_C:.3f}")
print(f"Δn_D = {delta_n_D:.3f}\n")

print("----- Load factors -----")
print(f"n_max from gust diagram = {n_max:.3f}")
print(f"n_ult = {n_ult:.3f}")
print(f"n_new = {n_new:.3f}\n")

plt.plot([V_D,V_D], [1+delta_n_D,1-delta_n_D], 'black')
plt.plot([0,V_D], [1,1+delta_n_D],'gray', linestyle='--')
plt.plot([0,V_C], [1,1+delta_n_C],'gray', linestyle='--')
plt.plot([0,V_D], [1,1-delta_n_D],'gray', linestyle='--')
plt.plot([0,V_C], [1,1-delta_n_C],'gray', linestyle='--')
plt.axhline(1, color='gray', linestyle='--', linewidth=1)
plt.axvline(V_B, color='k', linestyle=':', label='$V_B$')
plt.axvline(V_C, color='k', linestyle=':', label='$V_C$')
plt.axvline(V_D, color='k', linestyle=':', label='$V_D$')
plt.plot(V_values, n_pos, 'black', label='Gust envelope')
plt.plot(V_values, n_neg, 'black')
plt.text(V_B - 5, 0.98, '$V_B$', ha='center', va='top')
plt.text(V_C - 5, 0.98, '$V_C$', ha='center', va='top')
plt.text(V_D - 5, 0.98, '$V_D$', ha='center', va='top')
# Highlight Δn points
plt.scatter([V_B, V_C, V_D],
            [1 + delta_n_B, 1 + delta_n_C, 1 + delta_n_D],
            color='black', marker='o', zorder=5)
plt.scatter([V_B, V_C, V_D],
            [1 - delta_n_B, 1 - delta_n_C, 1 - delta_n_D],
            color='black', marker='o', zorder=5)

plt.title('Gust Load Diagram (V–n)')
plt.xlabel('Airspeed (m/s)')
plt.ylabel('Load Factor n')
plt.grid(True)
plt.legend()
plt.show()

