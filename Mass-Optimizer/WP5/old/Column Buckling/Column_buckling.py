import numpy as np
from parameters import *


###

# Need to use Micah's moment of inertia (I_zz for I_stringer)

###

def calculate_safety_factor(K, L_between_ribs):
    sigma_crit = (K * np.pi**2 * E * I_stringer)/(L_between_ribs**2 * A_stringer)
    print("Safety factor: ", sigma_crit/sigma_applied)


calculate_safety_factor(K_one_free_one_fixed, L_ribs_from_tip)
calculate_safety_factor(K_both_clamped, L_ribs_between)


 
###

# For iteration purposes

###


def calculate_stringer_length(K):
    L_between_ribs_new = np.sqrt((K * np.pi**2 * E * I_stringer)/(sigma * A_stringer))
    return L_between_ribs_new

def calculate_stringer_area(K, L_between_ribs):
    A_stringer_new = np.sqrt((K * np.pi**2 * E * I_stringer)/(sigma * L_between_ribs**2))
    return A_stringer_new


def calculate_all_stringer_length():

    # Wing tip / free end
    L_ribs_from_tip = calculate_stringer_length(K_one_free_one_fixed)

    # Between ribs / both fixed
    L_ribs_between = calculate_stringer_length(K_both_clamped)

    number_of_ribs = np.ceil((b/2 - L_ribs_from_tip) / L_ribs_between).astype(int)

    return L_ribs_from_tip, L_ribs_between, number_of_ribs

def calculate_all_stringer_area():

    # Wing tip / free end
    A_ribs_from_tip = calculate_stringer_area(K_one_free_one_fixed, L_ribs_from_tip)

    # Between ribs / both fixed
    A_ribs_between = calculate_stringer_area(K_both_clamped, L_ribs_between)

    return A_ribs_from_tip, A_ribs_between


L_ribs_from_tip, L_ribs_between, number_of_ribs = calculate_all_stringer_length()

print("Stringer length at wing tip (one free, one fixed): ", L_ribs_from_tip, " m")
print("Stringer length between ribs (both fixed): ", L_ribs_between, " m")
print("Number of ribs needed per half wing: ", number_of_ribs)


# L_between_ribs_new = np.sqrt((K * np.pi**2 * E * I_stringer)/(sigma * A_stringer))
# A_stringer_new = np.sqrt((K * np.pi**2 * E * I_stringer)/(sigma * L_between_ribs**2))