from math import pi

# Drag coefficient
# FUSELAGE DIMENSIONS
D_fus = 2.72 #fuselage diameter
L1 = 5.445 #length first
L2 = 3.956  
L3 = 8.712
S_wexp = 38 # exposed wing surface area [m^2]
S_hexp = 0 # exposed horizontal tail surface area [m^2]
S_vexp = 0 # exposed vertical tail surface area [m^2]
Sref = 33.60949107 #wing area

# AMBIENT PROPERTIES
rho = 0.287 # density [kg/m^3]
V = 200.63 # velocity [m/s]
l = 2.084764832 # length average root tip chord[m]
mu = 1.8e-5 # viscosity [Pa*s]
k = 0.634e-5 # Surface: smooth molded composite [m]

xc = 0.413 #(x/c)m
tc = 0.12 #thicknes chord airfoil
M = 0.68 #machnumber
sweep = 10.56*(pi/180) #wingsweep
ffus = (L1+L2+L3)/D_fus
lnac = 2.502 #length nacele
dnac = 1.35 #diameter nacele
fnac = lnac/dnac
xct = 0.3 #(x/c)m for the horizontal tail , location of maximum thickness
sweeptail = 25*(pi/180) #sweep horizontal tail
tct = 0.12 #thicknes chord airfoil horizontal tail
sweepvtail = 35*(pi/180) #sweep vertical tail
xcv = 0.3 #(x/c)m vertical tail location of maximum thickness
tcv = 0.12 #(t/c) vertical tail

u = 5*(pi/180) # upsweep angle [rad]
Amax = 2.722 # maximum fuselage cross-sectional area [m^2]
#Abase = 0 # fuselage base area [m^2]

# LANDING GEAR
d_mLG = 0.777 # height main landing gear [m]
w_mLG = 0.513 # width main landing gear [m]
d_nLG = 0.665 # height nose landing gear [m]
w_nLG = 0.456 # width nose landing gear
SS_N = 0.302
SA_N = 0.188
SS_M = 0.399
SA_M = 0.276
# SA_MLG = 0.8 # frontal area main landing gear [m^2]
# SA_NLG = 0.303  # frontal area main landing gear [m^2]

# nose lg total area = 0.303
# main lg total area = 0.8 
# main lg height = 0.777
# main lg width = 0.513
# nose lg height = 0.665
# nose lg width 0.456

