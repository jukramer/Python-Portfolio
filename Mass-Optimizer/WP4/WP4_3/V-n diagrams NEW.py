import math
import numpy as np
import matplotlib.pyplot as plt


# Weights / parameters
W_payload = 1010 # kg
W_oem = 4876.78 # kg
W_mtom = 7142.310 # kg
W_mtom_lbs = 0.454 * W_mtom # lbs
S = 33.609 # m^2
C_L_max_cr = 1.663
C_L_max_to = 2
C_L_max_a = 2.1
C_L_max_l = 2.1

print(2.1+24000/(W_mtom_lbs + 10000))

# Flight conditions
M_cr = 0.68
Altitude = 41000 # ft
Altitude_metric = Altitude / 3.281 # m
rho_cr = 0.287407 # kg/m3 or m/s conversion factor
rho = 1.225 # kg/m^3
g = 9.80665 # m/s^2

a_cr = 295.07
a_SL = 343.29
    
def plot(k, i, W, rho_0, a, name):

    pressure_scaling = math.sqrt(rho/rho_0)

    # Stall speeds
    V_s0_takeoff = np.sqrt(2*g*W_mtom/(rho*S*C_L_max_to)) / pressure_scaling  # flaps down takeoff
    V_s0_approach = np.sqrt(2*g*W_mtom/(rho*S*C_L_max_a)) / pressure_scaling  # flaps down approach
    V_s0_landing = np.sqrt(2*g*W/(rho_0*S*C_L_max_l)) / pressure_scaling  # flaps down landing
    V_s1 = np.sqrt(2*g*W/(rho_0*S*C_L_max_cr)) / pressure_scaling   # flaps up
        
    # Limit load factors
    n_max_flaps = 2
    n_max = 2.1 + 24000/(W_mtom_lbs + 10000) #3.192
    n_max = max(2.5, min(n_max, 3.8))
    n_min = -1

    # V-speeds
    V_c = M_cr * a / pressure_scaling
    V_d = (V_c / 0.8)
    V_a = (V_s1 * math.sqrt(n_max))

    print("pressure scaling: ", pressure_scaling)
        
    # Flap speeds
    V_f_takeoff = 1.6 * V_s1
    V_f_approach = 1.8 * V_s1
    V_f_landing = 1.8 * V_s0_landing
        

    ########## GRAPHING #############

    n_max_flaps = 2

    def line_n_pos(V):
        if V <= V_a:
            n_pos = (V / V_s1)**2
        else:
            n_pos = n_max
        return n_pos
    
    def line_n_flaps(V):
        if V <= V_a:
            n_pos = (V / V_s1)**2
        else:
            n_pos = n_max
            
        if V <= V_f_takeoff:
            n_flaps_calc = (V / V_s0_takeoff)**2
            if n_flaps_calc <= n_max_flaps:
                n_flaps = n_flaps_calc
                V_flaps_max1 = 0
            else:
                n_flaps = n_max_flaps
                V_flaps_max1 = 0
        else:
            n_flaps = float('nan')
            V_flaps_max1 = 0
            
        if n_flaps <= n_pos:
            n_flaps = float('nan')
            V_flaps_max1 = V
        
        return n_flaps, V_flaps_max1

    def line_n_neg(V):
        n_neg_calc = -(V / V_s1)**2
        if n_neg_calc >= -1:
            n_neg = n_neg_calc
        elif V <= V_c:
            n_neg = -1

        else:
            n_neg = -1 + (V - V_c) / (V_d - V_c)
        return n_neg

    V_values = np.linspace(0, V_d, 200)

    n_pos_values = []
    n_neg_values = [] 
    n_flaps_values = []

    Y = 0

    for V_val in V_values:
        n_pos = line_n_pos(V_val)
        n_neg_val = line_n_neg(V_val)
        n_flaps_val, V_flaps_max1 = line_n_flaps(V_val)
        if Y == 0 and V_flaps_max1 > 0:
            V_f_max = V_flaps_max1
            Y = 1
        n_pos_values.append(n_pos)
        n_neg_values.append(n_neg_val)
        n_flaps_values.append(n_flaps_val)

    ########## PLOTTING #############
    '''
    print(V_a)
    print(V_c)
    print(V_d)
    print(V_s0_landing)
    print(V_f_landing)
    '''

    # Plot
    axes[k, i].set_xlim(0, V_d + 10)
    axes[k, i].set_ylim(n_min - 0.5, n_max + 0.5)
    axes[k, i].plot([0, V_d + 10], [0, 0], 'k-', linewidth=1.5)
    axes[k, i].plot(V_values, n_pos_values, 'b-', linewidth=2)
    axes[k, i].plot(V_values, n_neg_values, 'b-', linewidth=2)
    if W == W_mtom:
        axes[k, i].plot(V_values, n_flaps_values, 'b-', linewidth=2)
    axes[k, i].plot([V_d, V_d], [0, n_max], 'b-', linewidth=2)
    axes[k, i].plot([V_a, V_a], [0, n_max], 'k--', linewidth=1)
    axes[k, i].plot([V_c, V_c], [n_min, n_max], 'k--', linewidth=1)
    axes[k, i].plot([0, V_d], [1, 1], 'k--', linewidth=1)
    axes[k, i].plot([0, V_d], [-1, -1], 'k--', linewidth=1)
    axes[k, i].plot([V_s1, V_s1], [0, 1], 'k--', linewidth=1)

    axes[k, i].text(V_s1 + 5, 0.1, '$V_S$', ha='center', va='bottom', fontsize=8)
    axes[k, i].text(V_a + 7, 0.1, '$V_S\\sqrt{n_{max}}$', ha='center', va='bottom', fontsize=8)
    axes[k, i].text(V_c + 5, 0.1, '$V_C$', ha='center', va='bottom', fontsize=8)
    axes[k, i].text(V_d + 5, 0.1, '$V_D$', ha='center', va='bottom', fontsize=8)
    axes[k, i].text(V_c - 20, -1.3, '$n_{min}$', ha='center', va='bottom', fontsize=8)
    axes[k, i].text(V_d - 20, n_max + 0.1, '$n_{max}$', ha='center', va='bottom', fontsize=8)
    if W == W_mtom:
        axes[k, i].text(V_f_takeoff - 22, n_max_flaps + 0.1, '$n_{max_{flaps}}$', ha='center', va='bottom', fontsize=8)


    axes[k, i].set_title(name)
    axes[k, i].set_xlabel('V_EAS (m/s)')
    axes[k, i].set_ylabel('n (-)')
    #axes[k, i].legend()
    axes[k, i].grid(True)
    print(axes)
    # Common elements
    for row in axes:
        for ax in row:
            ax.plot([0, V_d + 10], [0, 0], 'k-', linewidth=1.5)
            ax.set_xlabel('V_EAS (m/s)')
            ax.set_ylabel('n (-)')
    
    # if W == W_mtom and a == a_cr:
    #     print("Cruise: V_C = ", V_c, "n = -1" )
    #     print("Cruise: V_D = ", V_d, "n = " , n_max)

    # if W == W_mtom and a == a_SL:
    #     print("Sea Level: V_C = ", V_c, "n = -1" )
    #     print("Sea Level: V_D = ", V_d, "n = " , n_max)
    print(k, "  ", i)
    print("Cruise: V_S = ", V_s1, "n = -1")
    if W == W_mtom:
        print("Cruise: V_flaps = ", V_f_max, "n = ", n_max_flaps)
    print("Cruise: V_S_n = ", V_a, "n = ", n_max)
    print("Cruise: V_C = ", V_c, "n = -1" )
    print("Cruise: V_D = ", V_d, "n = " , n_max)


fig, axes = plt.subplots(2, 3, figsize=(18, 8))
plot(0, 0, W_oem, rho_cr, a_cr, 'V_EAS vs n Diagram, Cruise, EOM')
plot(0, 1, W_mtom, rho_cr, a_cr, 'V_EAS vs n Diagram, Cruise, MTOM')
plot(0, 2, W_oem + W_payload, rho_cr, a_cr,'V_EAS vs n Diagram, Cruise, EOM + Payload')
plot(1, 0, W_oem, rho_cr, a_SL, 'V_EAS vs n Diagram, Sea Level, EOM')
plot(1, 1, W_mtom, rho_cr, a_SL, 'V_EAS vs n Diagram, Sea Level, MTOM')
plot(1, 2, W_oem + W_payload, rho_cr, a_SL, 'V_EAS vs n Diagram, Sea Level, EOM + Payload')

plt.tight_layout()
plt.show()

fig, axes = plt.subplots(2, 2, figsize=(18, 8))
plot(0, 0, W_mtom, rho_cr, a_cr, 'V_EAS vs n Diagram, Cruise, MTOM')
plot(0, 1, W_mtom, rho_cr, a_SL, 'V_EAS vs n Diagram, Sea Level, MTOM')

plt.tight_layout()
plt.show()



