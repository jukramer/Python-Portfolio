import numpy as np
from parameters import *

class Calc():
    def __init__(self, INT_INTRVLS):
        self.INT_INTRVLS = INT_INTRVLS
    
    def lambda_c4_to_le(self):
        return np.rad2deg(np.arctan(np.tan(np.deg2rad(LAMBDA_C4))-C_ROOT/(2*b)*(TAPER_RATIO-1))) 
    
    def calc_c(self):
        C_ROOT = 2*S/(b*1+b*TAPER_RATIO)
        print(C_ROOT, TAPER_RATIO*C_ROOT)
    
    def c(self, y):
        return C_ROOT - (C_ROOT - C_TIP)*(2*y/(b))
    
    def mac(self):
        y_VALS = np.arange(0, b/2, self.INT_INTRVLS)
        return 2/S*np.trapz(self.c(y_VALS), y_VALS) #type:ignore
    
    def pos_mac(self):
        y = (b/6)*((1+2*TAPER_RATIO)/(1+TAPER_RATIO))
        x = y*np.tan(LAMBDA_LE)

        return x, y
    
    def check_aspect_ratio(self):
        A_check = 4 / ((Cl_airfoil + 1)*cos(LAMBDA_LE))
        if A_check < A:
            return True
        else:
            return False
    
    def estimayte_MDD(self):
        MDD = k_a / cos(LAMBDA) - tc_streamwise / cos(LAMBDA)**2 - CL / (10 * cos(LAMBDA)**3)
        return MDD
    
    def wing_component_form_factor(self):
        FF_w = (1 + 0.6 / x_c_m * tc + 100 * tc**4) * (1.34 * M**0.18 * cos(LAMBDA_LE)**0.28)
        return FF_w
     
    def wave_drag(self):
        if M < M_critical:
            CD_wave = 0 
        elif M >= M_critical and M <= MDD:
            CD_wave = 0.002 * (1 + 2.5 * (MDD - M)/0.05)**(-1)
        else:
            CD_wave = 0.002 * (1 + 2.5 * (MDD - M)/0.05)**(2.5)
        return CD_wave
    
    def getLD(self, polar_file):
        
        polar = np.loadtxt(polar_file, skiprows=11)
        
        cl = polar[:,1]/np.sqrt(1-0.68**2)
        cd = polar[:,2]
        cl_CR = 0.2643

        LD = cl/cd
        LD_CR = np.max(np.where(np.abs(cl-cl_CR)==np.min(np.abs(cl-cl_CR)), LD, -100)).item()
        cd_min = np.min(cd)
        print(cd_min)
        print(cd)
        cl_cdmin = np.max(np.where(cd==cd_min, cl, -100)).item()
        delta_cl = np.abs(cl_CR-cl_cdmin)
        slope = (cl[12]-cl[8])/(polar[12,0]-polar[8,0]) *180/np.pi
        cl_0 = np.max(np.where(polar[:,0]==0, cl, -100)).item()
        cm_CR = np.max(np.where(np.abs(cl-cl_CR)==np.min(np.abs(cl-cl_CR)), polar[:,4], -100)).item()
        alpha_cr = (cl_CR-cl_0)/slope
        alpha_0cl = (0-cl_0)/slope

        c_p = polar[:,7]/np.sqrt(1-0.68**2)
        v = np.sqrt(1-c_p)*V_CRUISE
        v *= np.cos(14.822*np.pi/180)
        M_local = np.max(np.where(np.abs(cl-cl_CR)==np.min(np.abs(cl-cl_CR)), v/a_CRUISE, -100)).item()

        print()
        print(abs(cm_CR))
        print(np.max(cl)*np.sqrt(1-0.68**2))
        print(np.max(np.where(cl == np.max(cl), polar[:,0], -100)))
        print(abs(alpha_cr/np.pi*180))
        print()
        print(M_local)
        print(cd_min)
        print(delta_cl)
        print(LD_CR)
        print()
        print(alpha_0cl)
        return alpha_cr
