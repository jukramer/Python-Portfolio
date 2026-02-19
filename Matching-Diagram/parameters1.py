# REQUIREMENTS
M_MAX_PL= 1010 # [kg]
MACH_CRUISE = 0.68 # @ 41000ft

TAKEOFF_DIST = 1250 # [m]
LANDING_DIST = 620 # [m]

RANGE_DESIGN = 4482e3 # [m] @ 1010kg
RANGE_HARMONIC = 6.1e6 # [m] @ 1010kg
RANGE_FERRY = 7e6 # [m] 

# AIRCRAFT PROPERTIES - FAR/25
M_OEW = 6012 # [kg] DUMMY
M_MTOW = 9970.6 # [kg] DUMMY

CL_MAX_CR = 1.663 # Cruise
CL_MAX_TO = 1.9 # Takeoff
CL_MAX_L = 2.1 # Landing
AR = 8.9 # Aspect ratio 

CD_0_CR = 0.020627153 # CD0
CD_0_TO_GRUP = 0.040127153 # CD0
CD_0_TO_GRDWN = 0.093160785 # CD0
CD_0_L_GRUP = 0.066127153 # CD0
CD_0_L_GRDWN = 0.119160785 # CD0
e_CR = 0.858 
e_TO = 0.927
e_L = 0.971

C_LFL = 0.45 # FAR 25: 0.45, FAR 23: 0.6
V_APP = 60.41 # [m/s] estimate

B = 5 # Bypass ratio, assumed
THETA_BREAK = 1.07 # assumed, from reader
N_E = 2 # number of engines
KT = 0.85 # from adsee reader

H2 = 11 # [m] from adsee reader, for normal cs25 ac

BETA_TO = 1 # Takeoff mass fraction
BETA_CR = 1 # Cruise mass fraction 
BETA_L = 0.85 # Landing mass fraction

# ENVIRONMENTAL CONDITIONS
GAMMA = 1.4 # specific heat ratio in air
R = 287 # gas constant in air

T_SL = 288.15 # [K]
P_SL = 101325 # [Pa]
RHO_SL = 1.225 # [kg/m^3]

ALT_CR = 41000 #ft = 12496.8m
T_CR = 216.65 # [K]
P_CR = 17868.132 # [Pa]
RHO_CR = 0.287368 # [kg/m^3]

#CLIMB GRADIENTS
T_CG = 288.15 # [K]
P_CG = 101325 # [Pa]
RHO_SL = 1.225 # [kg/m^3]

#CLIMB RATE
c = 18 # [m/s]
T_CR = 216.65 # [K]
P_CR = 17868.132 # [Pa]
RHO_CR = 0.287368 # [kg/m**3]

# REFERENCE AIRCRAFT - Name, W/S, T/W, plot color
TWWS_AC_REF = (('Cessna Citation Latitude', 2719.36, 0.383, "#ff8400"),
               ('Cessna Citation Sovereign', 2717.02, 0.37, "#ffee00"),
               ('Embraer Praetor 500', 2272.81, 0.57, "#3cff00"),
               ('Bombardier Challenger 300', 3564.37, 0.35, "#12600b"),
               ('Gulfstream G200', 4598.97, 0.29, "#00ffff"),
               ('Bombardier Challenger 350', 3759.78, 0.39, "#1100ff"),
               ('Cessna Citation Longitude', 3521.65, 0.39, "#bb00ff"),
               ('Embraer Praetor 600', 4256.84, 0.35, "#ff00dd"))