from parameters_weight import *
import matplotlib.pyplot as plt
import numpy as np

mu_g = 2*(Gw/S) / (rho*c*g*CL_alpha)
kg = 0.88* mu_g/(5.3 + mu_g)

UdeB = 84.67 - 0.000933* h_cr
UdeC = 66.67 - 0.000833*h_cr 
UdeD = 33.34 - 0.000417* h_cr


SlopeB = (kg*UdeB*CL_alpha)/(498* Gw/S)
SlopeC = (kg*UdeC*CL_alpha)/(498* Gw/S)
SlopeD = (kg*UdeD*CL_alpha)/(498* Gw/S)


n_plim = 2.1 + (24000/(W_cr+10000))
n_plim = max(n_plim, 2.5)

n_nlim = -1.0


#Va calculations
C_nmax = 1.1* C_Lmax
V_s1 = (2*(Gw/S)/(rho*C_nmax))**(1/2)
V_A = V_s1 * n_plim**(1/2)

def N_b(x):
    return 1 + SlopeB * x

def N_c(x):
    return 1 + SlopeC * x

def N_d(x):
    return 1 + SlopeD * x





x_vals = np.arange(0, 100, 0.1)
N_b_vals = N_b(x_vals)
N_c_vals = N_c(x_vals)
N_d_vals = N_d(x_vals)



plt.plot((x_vals), (N_b_vals), linestyle='dashed') # (x1, x2), (y1, y2)
plt.plot((x_vals), (N_c_vals), linestyle='dashed') 
plt.plot((x_vals), (N_d_vals), linestyle='dashed')
plt.hlines(n_plim,0,100)
plt.hlines(-1,0,100)


plt.show()




