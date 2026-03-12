from parameters_weight import *
import math

def calc_weight():
    # Wing weight estimation
    W_W = 0.0017*W_MZF*(b/math.cos(Lambda_12))**0.75*(1 + (6.3*math.cos(Lambda_12)/b)**(1/2))*n_ult**0.55*(b*S/(t_r*W_MZF*math.cos(Lambda_12)))**0.30
    print(f'Wing weight: {W_W}')
    
    # Empennage weight estimation
    W_h = k_h*S_h*(3.81*(S_h**0.2*V_D)/(1000*(math.cos(Lambda_12_h))**(1/2))-0.287)
    W_v = k_v*S_v*(3.81*(S_v**0.2*V_D)/(1000*(math.cos(Lambda_12_v))**(1/2))-0.287)
    
    W_emp = W_h + W_v
    # Fuselage weight
    W_f = 0.021*k_f*(V_D*l_h/(w_f + h_f))**(1/2)*S_fgs**1.2
    

    # Nacelle weight estimation (high bypass ratio turbofan)
    W_n = 0.065*T_TO

    # Landing gear weight estimation
    # main landing gear
    W_g_main = K_gr*(A_g_main + B_g_main*(W_TO)**(3/4) + C_g_main*W_TO + D_g_main*(W_TO)**(3/2))

    # nose landing gear
    W_g_nose = K_gr*(A_g_nose + B_g_nose*(W_TO)**(3/4) + C_g_nose*W_TO + D_g_nose*(W_TO)**(3/2))

    W_g = W_g_main + W_g_nose
    

    # Total structure weight
    W_struc = W_W + W_emp + W_f + W_n + W_g     # [lbs]

    #Flight control system
    W_fc = K_fc * (W_TO)**(2/3)

    #Hydraulic systems
    W_hy = 0.008 * W_TO

    #electrical systems
    W_ELS = 10.8*(V_pax)**0.7*(1-0.018*(V_pax)**0.35)

    #instrumentation, avionics and electronics
    W_IAE = 0.575*(W_E)**0.556 * R**0.25

    #airconditioning pressurization, ani- and- deicing systems
    W_api = 6.75*(l_pax)**1.28

    #oxygen system
    W_ox = 40 + 2.4* N_pax

    #auxilary power unit
    W_apu = 0.008 * W_TO

    #furnishing weight estimation
    W_fur = 0.211*(W_TO - W_F)**0.91
    
    W_sys = W_fc + W_hy + W_ELS + W_IAE + W_api + W_ox + W_apu
    
    W_ew = (W_struc + W_sys + W_fur)
    
    print(W_struc/kg_to_lbs, W_sys/kg_to_lbs)
    
    return W_ew/kg_to_lbs + M_PROP
    
    