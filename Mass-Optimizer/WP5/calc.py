# from WP5.old.parameters import *
from globalParameters import *
from typing import Callable
import matplotlib.pyplot as plt
import numpy as np
import scipy as sp
import warnings

# CONSTANTS
NULL_ARRAY_2 = np.zeros((2,1)) # 0-load array (for 2-row point loads)
NULL_ARRAY_3 = np.zeros((3,1)) # 0-load araray (for 3-row point loads)

            
class DimensionError(Exception):
    pass


class Calc():
    def __init__(self, file0, file10):
        with open(file0) as data0:
            dat0 = np.genfromtxt(data0, skip_header=21, invalid_raise=False)

        with open(file10) as data10:
            dat10 = np.genfromtxt(data10, skip_header=21, invalid_raise=False)

        # Min and max x vals for plotting
        self.xMin, self.xMax = (0, 0)
        self.step = 1e-2
        
        self.ylst0 = dat0[:,0]
        self.Cllst0 = dat0[:,3]
        Cdlst0 = dat0[:,5]
        Cmlst0 = dat0[:,7]
        clst0 = dat0[:,1]

        ylst10 = dat10[:,0]
        Cllst10 = dat10[:,3]
        Cdlst10 = dat10[:,5]
        Cmlst10 = dat10[:,7]
        clst10 = dat10[:,1]

        # Interpolate datapoints from XFLR5 data to obtain python functions
        self.Cl0 = sp.interpolate.interp1d(self.ylst0, self.Cllst0, kind='cubic', fill_value='extrapolate')
        self.Cd0 = sp.interpolate.interp1d(self.ylst0, Cdlst0, kind='cubic', fill_value='extrapolate')
        self.Cm0 = sp.interpolate.interp1d(self.ylst0, Cmlst0, kind='cubic', fill_value='extrapolate')

        self.Cl10 = sp.interpolate.interp1d(ylst10, Cllst10, kind='cubic', fill_value='extrapolate')
        self.Cd10 = sp.interpolate.interp1d(ylst10, Cdlst10, kind='cubic', fill_value='extrapolate')
        self.Cm10 = sp.interpolate.interp1d(ylst10, Cmlst10, kind='cubic', fill_value='extrapolate')

        # Global wing CL values and alpha
        self.CL0 = C_L0
        self.CL10 = C_L10
        self.alpha0 = 0.0
        self.alpha10 = 10.0

        # Placeholders for current load cases
        self.Cl = None
        self.Cd = None
        self.Cm = None
        self.alpha = None

        self.D = 0

    def chord(self, y):
        return C_ROOT + (C_TIP-C_ROOT) * 2 * y/b
    
    def findSweep(self, n, m, mSweepAngle):
        result = np.tan(np.deg2rad(mSweepAngle)) - 4/ASPECT_RATIO*(n-m)*(1-TAPER_RATIO)/(1+TAPER_RATIO)
        return np.rad2deg(np.atan(result))
    
    def findLoadingDist(self, y, posAero=0.25, posInertial=CG_POS_CHORDWISE): 
        # By necessity, posInertial is 0, as weight acts through the centroid
        return self.chord(y)*(CG_POS_CHORDWISE-posAero)
             
    def alpha_load_case(self, V, w, rho):
        L = w*n_ult
        C_L_d = L / (0.5*rho*(V**2)*S)

        return C_L_d

    def set_load_case_from_flight(self, n, W, V=V_CR, rho=RHO, Sref=S):
        q_here = 0.5*rho*V**2
        CLd = n*W/(q_here*Sref)
        
        t = (CLd - self.CL0) / (self.CL10 - self.CL0)

        self.Cl = lambda y: self.Cl0(y) + t*(self.Cl10(y) - self.Cl0(y))
        self.Cd = lambda y: self.Cd0(y) + t*(self.Cd10(y) - self.Cd0(y))
        self.Cm = lambda y: self.Cm0(y) + t*(self.Cm10(y) - self.Cm0(y))

        self.alpha = self.alpha0 + t*(self.alpha10 - self.alpha0)
    

    ######### EXTERNAL LOADING ##############
    # AERODYNAMIC LOADING
    def calcNormal(self, y, alphaA):
        c = self.chord(y)
        alphaA = np.deg2rad(alphaA)
        L = self.Cl(y)*q*c
        D = self.Cd(y)*q*c
        
        return np.cos(alphaA)*L + np.sin(alphaA)*D
    
    def momentUnitSpan(self, y):
        return self.Cm(y)*q*self.chord(y)**2

    # INERTIAL LOADING
    def inertialLoading(self, y, massWing, n=1):
        weightDens = n*g*massWing/S
        return -weightDens*self.chord(y)*np.cos(np.deg2rad(self.alpha))
        
    # PROPULSIVE LOADING
    def propulsiveLoading(self, thetaT, T):
        return np.array(([0], [T/2*np.sin(thetaT)*np.cos(self.findSweep(CG_POS_CHORDWISE, 0.25, 10.56))], [0.25*C_ROOT]))
    
    def propulsiveMoment(self, thetaT, T, d):
        return np.array(([0], [T/2*np.sin(thetaT)*d*np.cos(self.findSweep(CG_POS_CHORDWISE, 0.25, 10.56))]))
    
    # TOTAL LOADING
    def totalLoading(self, x, n, mWing):
        # print(self.D)
        return self.calcNormal(x, self.alpha-WING_TRIM), self.inertialLoading(x, mWing, n), self.propulsiveLoading(WING_TRIM, T_TO), self.momentUnitSpan(x), self.propulsiveMoment(WING_TRIM, T_TO, d_prop)
        
    ############ INTERNAL LOADING ##############
    # Shear force as function of x. pointLoads must have cols (position, load) (shape 2xn)
    # loading must be a python function.
    def shear(self, x, loading: Callable, pointLoads):
        xValsInt = np.arange(x, self.xMax, self.step)
        yValsInt = loading(xValsInt)
        
        V = sp.integrate.simpson(x=xValsInt, y=yValsInt)

        for i in range(pointLoads.shape[1]):
            V += pointLoads[1,i] * (1-np.heaviside(x-pointLoads[0,i], 1))

        return V

    # Moment force as function of x. pointLoads must have cols (position, load) (shape 2xn)
    # loading must be a python function.
    def moment(self, x, shearVals, pointMoments):
        xValsInt = np.arange(x, self.xMax, self.step)
        i = shearVals.shape[0] - xValsInt.shape[0]
        M = sp.integrate.simpson(x=xValsInt, y=shearVals[i:])

        for i in range(pointMoments.shape[1]):
            M += pointMoments[1,i] * (1-np.heaviside(x-pointMoments[0,i], 1))

        
        return -M

    # Torsion as function of x. forcePointLoads must have cols (position, load, dist) (shape 3xn);
    # torquePointLoads must have cols (position, load) (shape 2xn)
    # forceloading, torsionLoading, and loadingDist must be a python function.
    def torsion(self, x, loadingVals, forcePointLoads, torquePointLoads):
        xValsInt = np.arange(x, self.xMax, self.step)
        i = loadingVals.shape[0] - xValsInt.shape[0]
        T = sp.integrate.simpson(x=xValsInt, y=loadingVals[i:])
        
        # for i in range(forcePointLoads.shape[1]):
        #     T += forcePointLoads[1,i] * forcePointLoads[2,i] * (1-np.heaviside(x-forcePointLoads[0,i], 1))

        for i in range(torquePointLoads.shape[1]):
            T += torquePointLoads[1,i] * (1-np.heaviside(x-torquePointLoads[0,i], 1))
            
        return T
    
    ############ PLOTTING ##############
    def plot(self, aeroLoading, inertialLoading, torsionLoading, loadingDist, pointLoads, pointMoments, pointTorques, lims, subplots = True, plot = True, step=0.01, debug=False):
        if not debug:
            warnings.simplefilter('ignore', category = UserWarning)
        
        # Ensure arrays of correct dimension
        if not (pointLoads.shape[0] == 3 and pointMoments.shape[0] == 2 and pointTorques.shape[0] == 2 and len(lims) == 2):
            raise DimensionError('Loading arrays must be of correct dimension.')

        self.xMin, self.xMax = lims
        self.step = step
        xVals = np.arange(self.xMin, self.xMax, step)
        loadingVals = aeroLoading(xVals)     

        self.shearVec = np.vectorize(self.shear, signature='(),(),(3,1)->()')
        shearVals = self.shearVec(xVals, lambda x: aeroLoading(x) + inertialLoading(x), pointLoads)
        
        self.momentVec = np.vectorize(self.moment, signature='(),(n),(m,l)->()')
        momentVals = self.momentVec(xVals, shearVals, pointMoments)
        
        self.torsionVec = np.vectorize(self.torsion, signature='(),(m),(3,1),(2,1)->()')
        torsionLoadVals = torsionLoading(xVals) + aeroLoading(xVals)*loadingDist(xVals)
        torsionVals = self.torsionVec(xVals, torsionLoadVals, pointLoads, pointTorques)
        
        np.savez(ARRAY_PATH, xVals, momentVals, torsionVals)
        # return
        print('Plotting!')
        # Plot with subplots
        if subplots and plot:
            fig, (ax1, ax2, ax3) = plt.subplots(1,3)

            ax1.plot(xVals, shearVals/1000, color='blue')
            ax1.set_title('Shear Force Diagram')
            ax1.set_xlabel('y [m]')
            ax1.set_ylabel('Shear Force [kN]')
            ax1.grid()
            
            ax2.plot(xVals, momentVals/1000, color='red')
            ax2.set_title('Bending Moment Diagram')
            ax2.set_xlabel('y [m]')
            ax2.set_ylabel('Bending Moment [kNm]')
            ax2.grid()
            
            ax3.plot(xVals, torsionVals/1000, color='purple')
            ax3.set_title('Torsion Diagram')
            ax3.set_xlabel('y [m]')
            ax3.set_ylabel('Torsion [kNm]')
            ax3.grid()
                
            # ax4.plot(xVals, loadingVals)
            # ax4.set_title('Aerodynamic Loading Diagram')
            # ax4.set_xlabel('y [m]')
            # ax4.set_ylabel('Lift [Nm]')
            
            fig.set_size_inches(15,5)
            fig.suptitle(fr'{ARRAY_PATH} Internal Loading Diagrams', size='16', weight='semibold')
            fig.tight_layout()
            fig.savefig(fr'diagrams\totalDiagram{ARRAY_PATH}')
            
        # Plot in sequential plots
        if plot and not subplots:
            plt.grid()
            
            plt.plot(xVals, shearVals/1000, color='blue')
            plt.title('Shear Force Diagram')
            plt.xlabel('y [m]')
            plt.ylabel('Shear Force [kN]')
            plt.tight_layout()
            
            plt.savefig(f'diagrams/shearForceDiagram{ARRAY_PATH}.png')
            plt.clf()
            plt.grid()

            plt.plot(xVals, momentVals/1000, color='red')
            plt.title('Bending Moment Diagram')
            plt.xlabel('y [m]')
            plt.ylabel('Bending Moment [kNm]')
            plt.tight_layout()

            plt.savefig(f'diagrams/bendingMomentDiagram{ARRAY_PATH}.png')
            plt.clf()
            plt.grid()
            plt.tight_layout()

            plt.plot(xVals, torsionVals/1000, color='purple')
            plt.title('Torsion Diagram')
            plt.xlabel('y [m]')
            plt.ylabel('Torsion [kNm]')
            plt.tight_layout()

            plt.savefig(f'diagrams/torsionDiagram{ARRAY_PATH}.png')
            plt.clf()
            
        return np.vstack((xVals, momentVals, torsionVals, shearVals))
    
    def plot_coeffs_half_span(self):

        # span van 0 tot halfspan
        y = np.arange(0, HALF_SPAN + self.step, self.step)

        # interpolaties evalueren
        Cl0_vals  = self.Cl0(y)
        Cd0_vals  = self.Cd0(y)
        Cm0_vals  = self.Cm0(y)

        Cl10_vals = self.Cl10(y)
        Cd10_vals = self.Cd10(y)
        Cm10_vals = self.Cm10(y)

        # twee subplots naast elkaar
        fig, axes = plt.subplots(1, 2, figsize=(12, 4), sharey=True)

        # ---------- 0° ----------
        ax = axes[0]
        ax.plot(y, Cl0_vals, label="Lift coefficient")
        ax.plot(y, Cd0_vals, label="Induced drag coefficient")
        ax.plot(y, Cm0_vals, label="Moment coefficient")
        ax.set_title("Interpolation of Cl, Cd, Cm against the span (0°)")
        ax.set_xlabel("Span location [m]")
        ax.set_ylabel("Coefficient [-]")
        ax.grid(True)
        ax.legend()

        # ---------- 10° ----------
        ax = axes[1]
        ax.plot(y, Cl10_vals, label="Lift coefficient")
        ax.plot(y, Cd10_vals, label="Induced drag coefficient")
        ax.plot(y, Cm10_vals, label="Moment coefficient")
        ax.set_title("Interpolation of Cl, Cd, Cm against the span (10°)")
        ax.set_xlabel("Span location [m]")
        ax.grid(True)
        ax.legend()

        fig.tight_layout()
        plt.show()

            

if __name__ == '__main__':
    calc = Calc(r'WP4\WP4_1\dataa0.txt', r'WP4\WP4_1\dataa10.txt')
        
    # wlst = [W_MTOW, W_minusfuel, W_OEM]
    # # Vlst = [1.5*V_CR, V_CR, V_stallwflaps]
    # RHOlst = [RHO, RHO_SL]
    # for V in Vlst:
    #     for w in wlst:
    #         for rho in RHOlst:
    #             CLd = calc.alpha_load_case(V, w, rho)
    #             print(
    #             f"V = {V:6.2f} m/s | "
    #             f"W = {w:8.0f} N ({w/g:6.1f} kg) | "
    #             f"rho = {rho:5.3f} kg/m³ | "
    #             f"CLd = {CLd:8.3f}"
    #             )
                
    # External Loading    
    calc.set_load_case_from_flight(n_ult, W_MTOW)

    aeroLoading, inertialLoading, torsionLoading = lambda x: calc.totalLoading(x, LOAD_FACTOR, M_WING)[0], lambda x: calc.totalLoading(x, LOAD_FACTOR, M_WING)[1], lambda x: calc.totalLoading(x, LOAD_FACTOR, M_WING)[3]
    loadingDist = lambda x: calc.findLoadingDist(x)
    pointLoads, pointTorques = (lambda x: calc.totalLoading(x, LOAD_FACTOR, M_WING)[2])(0), (lambda x: calc.totalLoading(x, LOAD_FACTOR, M_WING)[4])(0)
    
    print(pointLoads)
    
    calc.plot(aeroLoading,
              inertialLoading, 
              torsionLoading, 
              loadingDist, 
              pointLoads, 
              NULL_ARRAY_2, 
              pointTorques, 
              (0, HALF_SPAN))
    
    calc.plot_coeffs_half_span()