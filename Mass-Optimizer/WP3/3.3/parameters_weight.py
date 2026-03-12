from math import pi
from wettedarea import *

# CONSTANTS
m_to_ft = 3.280839895           # meter to feet conversion
g = 9.80665 * m_to_ft           # gravitational acceleration [ft/s^2]
lbs_to_N = 4.448                # pound to newton conversion
kg_to_lbs = 2.20462262          # kg to lbs
deg_to_rad = pi/180             # degrees to radians conversion
m_to_nm = 0.000539956803        # meters to nautical miles
ms_to_KEAS = 1.94384

# MASSES
W_TO = 7142.314593*kg_to_lbs         # maximum take off weight [lbs]
W_F = 1252.158247*kg_to_lbs            # fuel weight [lbs]
W_E = 4880.156346*kg_to_lbs            # empty weight in [lbs]
W_MZF = W_TO - W_F              # maximum zero fuel weight [lbs]
M_PROP = 2*551                  # mass of two engines [kg]

# PLANFORM
b = 17.29521525*m_to_ft              # span [ft]
Lambda_12 = 7.627843029*(pi/180)  # wing semi-chord sweep angle [rad]
S = 33.60949107*m_to_ft**2           # wing area [ft^2]
T_TO = 31673.07352/lbs_to_N            # total required take-off thrust

n_ult = 4.275                   # ultimate load factor [-]
t_r = 3.368779881*0.179*m_to_ft # maximum root thickness [ft] root chord x max thickness %
V_CR = 200.629*ms_to_KEAS

k_h = 1.0                       # for fixed incidence stabilizers [-]
S_h = 13.71342911*m_to_ft**2    # horizontal tail area [ft^2]
V_D = 0                         # design dive speed [KEAS]
Lambda_12_h = 23.67888685*deg_to_rad # semi-chord sweep angle horizontal tail [rad]

# EMPENNAGE
S_v = 11.37711*m_to_ft**2                         # vertical tail area [ft^2]
z_h = 3.694933*m_to_ft                        # distance from vert.tail root to where ht is mounted on the v.t. [ft]
b_v = 3.69493308*m_to_ft  # vertical tail span [ft]
k_v = 1 + 0.15*(S_h*z_h/(S_v*b_v))         # for fuselage mounted vertical tails
Lambda_12_v = 22.10157387*deg_to_rad # semi-chord sweep angle vertical tail [rad]

# FUSELAGE
k_f = 1.08          # for a pressurized fuselage
V_D = 1.5 * V_CR             # design dive speed [KEAS]
l_h = 7.8*m_to_ft             # distance from wing root c/4 to hor. tail root c/4 [ft]
w_f = 2.722625*m_to_ft             # maximum fuselage width [ft]
h_f = 2.722625*m_to_ft             # maximum fuselage height [ft]
S_fgs = Swet_fus*m_to_ft           # fuselage gross shell area [ft]
l_pax = 3.51*m_to_ft           # length of the passenger cabin [ft]
V_pax = l_pax * (h_f/2)**2 * pi         # passenger cabin volume in [ft^3]


# LG CONSTANTS
K_gr = 1.0          # for low wing airplanes [-]
A_g_main = 33.0     # constant for land gear main [-]
B_g_main = 0.04     # constant for land gear main [-]
C_g_main = 0.021    # constant for land gear main [-]
D_g_main = 0.0      # constant for land gear main [-]
A_g_nose = 12.0     # constant for land gear nose [-]
B_g_nose = 0.06     # constant for land gear nose [-]
C_g_nose = 0.0      # constant for land gear nose [-]
D_g_nose = 0.0      # constant for land gear nose [-]
K_fc = 0.64         # constant for airplanes with powerd flight controls [-]

R = 6100000*m_to_nm   # range in nautical miles
N_pax = 6           # number of passengers


# V-n diagram ??
c = 2.463102156*m_to_ft              #wing mean geometric chord [ft] is mean aerodynamic chord
CL_alpha = 6.03     # CL alpha [1/rad]
h_cr = 41000        # cruise altitude [ft]
Gw =  5000*kg_to_lbs              # flight design gross weight [lbs] still needst to be reassesed 
CL_max = 1.663      #