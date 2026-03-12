import numpy as np
import matplotlib.pyplot as plt
from parameters import *

class Calc():
    def __init__(self):
        pass
    
    # Returns SL Thrust and corresponding Thrust at CR (equal to drag)
    def thrust(self):
        CD = C_D0 + CL_DES**2/(np.pi*ASPECT_RATIO*e)
        D_CR = CD*0.5*RHO_CR*V_CR**2*S
        T_SL = RHO_SL/RHO_CR*D_CR
        
        return T_SL, D_CR
    
    # aerodynamic stall
    def v_stall(self, WS, rho, C_Lmax):
        return np.sqrt(WS*2/rho/C_Lmax)
    
    def v_min_thrust(self, T, rho):
        T_alt = T*(rho/RHO_SL)
        CD = C_D0 + CL_DES**2/(np.pi*ASPECT_RATIO*e)
        return np.sqrt(2*T_alt/(CD*rho*S))        
    
    def v_max(self, T, WS, rho, C_D0, A, e):
        T_alt = T*(rho/RHO_SL)
        W = WS*S
        
        TWmax = T_alt/W
        
        return np.sqrt((TWmax*WS+WS*np.sqrt(TWmax**2-4*C_D0/(np.pi*e*A)))/(rho*C_D0))
    
    def h_to_rho(self, h_vals):
        return self.ISA(h_vals)[2]
    
    def ISA(self, h):
        g = 9.80665
        R = 287
        T0 = 288.15
        p0 = 101325
        rho = 1.225
        h0 = 0

        layers = [
            (11000, -0.0065),
            (20000, 0),
            (32000, 0.001),
            (47000, 0.0028),
            (51000, 0),
            (71000, -0.0028),
            (86000, -0.002)]

        for hLimit, a in layers:
            if h <= h0:
                break

            h1 = min(h, hLimit)
            delta_h = h1-h0

            if a == 0:
                T1 = T0
                p1 = p0 * np.exp((-g*delta_h/(R*T0)))
            else:
                T1 = T0 + a * delta_h
                p1 = p0 * (T1/T0)**(-g/(a*R))

            T0 = T1
            p0 = p1
            h0 = h1
            
        density = p0/(R*T0)
        
        return T0, p0, density 
    
    def plotFE(self, h_min, h_max, h_step):
        h_vals = np.arange(h_min, h_max, h_step)
        
        T_vals = []
        rho_vals = []
    
        for h in h_vals:
            T_vals.append(self.ISA(h)[0])
            rho_vals.append(self.ISA(h)[2])
            
        T_vals = np.array(T_vals) # ambient temp vals with altitude
        rho_vals = np.array(rho_vals) # density vals with altitude
        
        v_stall_vals = self.v_stall(WS_CR, rho_vals, CL_MAX) # aerodynamic stall
        v_min_thrust_vals = self.v_min_thrust(TMAX_SL, rho_vals) # vmin due to thrust limit
        v_max_vals = self.v_max(TMAX_SL, WS_CR, rho_vals, C_D0, ASPECT_RATIO, e) # thrust limit
        
        # Convert to Mach numbers
        M_stall_vals = v_stall_vals/np.sqrt(GAMMA*R_AIR*T_vals)
        M_min_thrust_vals = v_min_thrust_vals/np.sqrt(GAMMA*R_AIR*T_vals)
        M_max_vals = v_max_vals/np.sqrt(GAMMA*R_AIR*T_vals)
        
        # Find extension of M_max
        
        h_max = np.max(np.where(M_max_vals == np.min(M_max_vals[~np.isnan(M_max_vals)]), h_vals, -100))
        print(h_max/0.3048)
        
        M_start = np.max(np.where(h_vals == h_max, M_stall_vals, -100))
        M_end = np.min(M_max_vals[~np.isnan(M_max_vals)])
        print(M_start, M_end)
        
        plt.rcParams.update({'font.size': 10})
        plt.rcParams.update({'lines.linewidth': 3})
        plt.plot(M_stall_vals, h_vals/0.3048, label='$\mathrm{M_{min}}$') # h conversion m -> ft
        plt.plot(M_min_thrust_vals, h_vals/0.3048, label='$\mathrm{M_{min}}$') # h conversion m -> ft
        plt.plot(M_max_vals, h_vals/0.3048, label='$\mathrm{M_{max}}$') 
        plt.hlines(h_max/0.3048, M_start, M_end, linestyles='dashed', colors='red', label='Extended $M_{max}$ Ceiling')  
        plt.legend(loc='upper right')
        plt.xlabel('Mach Number [-]')
        plt.ylabel('Altitude [ft]')
        plt.title('Aircraft Preliminary Flight Envelope')
        plt.show() 
        # plt.savefig('plotTransparent.png', transparent=True)