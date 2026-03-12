K_both_pinned = 1
K_both_clamped = 4
K_one_free_one_fixed = 1/4
K_one_pinned_one_fixed = (1/0.7)**2

###########################################################################

sigma = 10e6

sigma_applied = 1.5 * sigma

E = 72.40e9

###########################################################################

b = 17.29

L_between_ribs = b/4

###########################################################################

t = 0.0015

L_vert = 0.02

L_hor = 0.02

#5/100, 3/100, 1/1000

t = 1/1000

L_vert = 5/100

L_hor = 3/100

A_stringer = L_vert * t  + (L_hor - t) * t 

# Needs to be upadted to Micah's moment of inertia
I_stringer = (1/12 * t * L_vert**3 + t * L_vert * (L_vert/2)**2) + (1/12 * (L_hor - t) * t**3 + (L_hor - t) * t * (t/2)**2)

########################################################################### 

print("Stringer area (m^2): ", A_stringer)


