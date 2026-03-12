############## WP5 ##############
# MATERIAL PROPERTIES
E = 72.4e9
G = 28.0e9
density = 2780 # kg/m³
POISSON_RATIO = 1/3
SHAPE_FACTOR = 1.1 # SHAPE FACTOR
CRACK_LENGTH = 1.5e-3 #[m]
K_1C = 26e6
SIGMA_Y_TENS = 450e6
SIGMA_Y_COMP = 450e6

# COLUMN BUCKLING
K_SS = 1
K_CC = 4
K_FC = 1/4
K_one_pinned_one_fixed = (1/0.7)**2


############## WP4 ##############

# PHYSICAL CONSTANTS
g = 9.80665

# PLANFORM
b = 17.29
HALF_SPAN = b/2
S = 33.609
ASPECT_RATIO = 8.9

C_ROOT = 2.85
C_TIP = 1.03
TAPER_RATIO = C_TIP/C_ROOT
CG_POS_CHORDWISE = 0.42246943

WING_TRIM = 0.8902570116290437 # [deg]

# PROPULSION
d_prop = 1.617
# T_TO = 31673.07352
T_TO = 4948.90970012397

# LIFT COEFFICIENTS
C_L0 = 0.264333
C_L10 = 1.123905

# LOAD FACTORS
n_lim = 3.8
n_ult = 1.5*n_lim

# MASSES/WEIGHTS
W_MTOW = 7142.31*9.80665
M_WING = (1275.260140713509 + 1251.441374)/2 # Fuel mass plus wing mass / 2 (mass of half wing)
W_minusfuel = 5886.78*g
W_OEM = 4876.784*g

# AMBIENT PROPERTIES

RHO = 0.287

# V_CR = 45.2 # Case 1
# LOAD_FACTOR = -1 # Case 1
# ARRAY_PATH = 'Case1'

# V_CR = 64.5 # Case 2
# LOAD_FACTOR = 2  # Case 2
# ARRAY_PATH = 'Case2'

# V_CR = 88.2 # Case 3
# LOAD_FACTOR = 3.8 # Case 3
# ARRAY_PATH = 'Case3'

# V_CR = 200.6 # Case 4 
# LOAD_FACTOR = -1*1.5 # Case 4
# ARRAY_PATH = 'Case 4'

V_CR = 291.8 # Case 5
LOAD_FACTOR = 3.8*1.5 # Case 5
ARRAY_PATH = 'Case 5'

# V_CR = 200.6 # Case 5
# LOAD_FACTOR = 1 # Case 5
# ARRAY_PATH = 'caseTest'

q = 0.5*RHO*V_CR**2

# SL
# RHO_SL = 1.225