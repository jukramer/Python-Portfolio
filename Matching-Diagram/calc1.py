import matplotlib.pyplot as plt
import numpy as np
from parameters1 import *

plt.rcParams['font.size'] = 14.5

class Calc:
    def __init__(self):
        pass
    
    def alphaT(self, WS, T, P, rho, CL, MACH = None):
        V_alpha = np.sqrt(WS*2/rho*1/CL)
        
        if not MACH:
            MACH = V_alpha/np.sqrt(GAMMA*R*T)
        else:
            MACH = np.array(MACH)

        pt = P*(1+(GAMMA-1)/GAMMA*MACH**2)**(GAMMA/(GAMMA-1))
        Tt = T*(1+(GAMMA-1)/GAMMA*MACH**2)
        
        deltat = pt/P_SL
        thetat = Tt/T_SL
        alphat = None
    
        if B < 5:
            alphat = np.where(thetat<THETA_BREAK, deltat, deltat*(1-2.1*(thetat-THETA_BREAK)/THETA_BREAK))
            
        elif B >= 5:
            alphat = np.where(thetat < THETA_BREAK, deltat*(1-(0.43+0.014*B)*np.sqrt(MACH_CRUISE)), 
                            deltat*(1-(0.43+0.014*B)*np.sqrt(MACH_CRUISE) - 3*(thetat-THETA_BREAK)/(1.5+MACH_CRUISE)))

        return alphat
        
    def WSMaxApproach(self, beta): # /1.23 for FAR 25
        return 1/beta*RHO_SL/2*(V_APP/1.23)**2*CL_MAX_L
        
    def WSMaxLField(self, beta):
        return 1/beta*LANDING_DIST/C_LFL*RHO_SL*CL_MAX_L/2
    
    def TSCruiseSpeed(self, beta, WS):
        alphat = self.alphaT(WS, T_CR, P_CR, RHO_CR, CL_MAX_CR, MACH_CRUISE) # SL T/P Vals
        V_cr = MACH_CRUISE * np.sqrt(GAMMA*R*T_CR)
        print(V_cr)

        return beta/alphat*((CD_0_CR/2*RHO_CR*V_cr**2/(beta*WS))+(beta*WS/(np.pi*AR*e_CR/2*RHO_CR*V_cr**2)))

    # def TSRateofClimb(self, beta, WS): # rate of climb
    #     alphat = self.alphaT(WS, T_SL, P_SL, RHO_SL, CL_MAX_TO) # SL T/P Vals
    #     return beta/alphat*(np.sqrt(c**2*RHO_SL/(2*beta*WS)*np.sqrt(CD_0*np.pi*AR*e_TO))+2*np.sqrt(CD_0/(np.pi*AR*e)))

    def TSToF(self, beta, WS): # takeoff field length
        alphat = self.alphaT(WS, T_SL, P_SL, RHO_SL, CL_MAX_TO) # SL T/P Vals
        return 1.15/alphat*np.sqrt(WS/(TAKEOFF_DIST*KT*RHO_SL*9.80665*np.pi*AR*e_TO)) + 4*H2/TAKEOFF_DIST

    def TSClimbGradient(self, beta, WS, CL, CD_0, e, OEI, climbgrad):
        alphat = self.alphaT(WS, T_SL, P_SL, RHO_SL, CL) # SL T/P Vals
        
        V = np.sqrt(WS*2/RHO_SL/CL)
        
        if OEI:
            return N_E/(N_E-1)*beta/alphat*(climbgrad/V+2*np.sqrt(CD_0/(np.pi*AR*e)))
        else:
            return beta/alphat*(climbgrad/V+2*np.sqrt(CD_0/(np.pi*AR*e)))
    
    def drawMatchingDiagram(self, WS_MIN, WS_MAX, WS_INTRVL):
        WS_VALS = np.arange(WS_MIN, WS_MAX, WS_INTRVL)
        
        # Approach/Landing Constraints
        WS_MAX_APP = self.WSMaxApproach(0.85) # 0.85 assumed
        WS_MAX_LAND = self.WSMaxLField(0.85)
        print(WS_MAX_APP, WS_MAX_LAND)
        
        # TS Cruise/ROC/Takeoff
        TS_VALS_CR = self.TSCruiseSpeed(1, WS_VALS) # 1 assumed
        # TS_VALS_ROC = self.TSRateofClimb(1, WS_VALS) # 1 assumed
        TS_VALS_TAKEOFF = self.TSToF(1, WS_VALS) # 1 assumed
        
        # TS Climb gradient
        TS_VALS_CLIMBGRAD_5 = self.TSClimbGradient(1, WS_VALS, CL_MAX_TO, CD_0_TO_GRDWN, e_TO, True, 0)
        TS_VALS_CLIMBGRAD_6 = self.TSClimbGradient(1, WS_VALS, CL_MAX_TO, CD_0_TO_GRUP, e_TO, True, 0.024)
        TS_VALS_CLIMBGRAD_7 = self.TSClimbGradient(1, WS_VALS, CL_MAX_CR, CD_0_CR, e_CR, True, 0.012)
        TS_VALS_CLIMBGRAD_8 = self.TSClimbGradient(1, WS_VALS, CL_MAX_L, CD_0_TO_GRUP, e_L, True, 0.021)
        TS_VALS_CLIMBGRAD_9 = self.TSClimbGradient(1, WS_VALS, CL_MAX_L, CD_0_TO_GRDWN, e_L, False, 0.032)
        
        # Max values of all TS curves
        TS_VALS_MAX = np.maximum.reduce(np.array([TS_VALS_CR, TS_VALS_TAKEOFF, TS_VALS_CLIMBGRAD_6, TS_VALS_CLIMBGRAD_7, TS_VALS_CLIMBGRAD_8, TS_VALS_CLIMBGRAD_9]))
        WS_VALS_RED, TS_VALS_MAX_RED = self.designSpace(WS_MIN, WS_INTRVL, WS_MAX_APP, WS_MAX_LAND, TS_VALS_MAX)

        # Plotting
        fig, ax = plt.subplots()
        plt.subplots_adjust(right=0.7)
        plt.subplots_adjust(left=0.08)
        ax.set_xlim((WS_MIN, WS_MAX))
        ax.set_ylim((0, 0.5*max(TS_VALS_MAX_RED[np.isfinite(TS_VALS_MAX_RED)])//1))
        
        line1 = ax.axvline(WS_MAX_APP, color='#236ee8', label='Stall', zorder=2)
        line2 = ax.axvline(WS_MAX_LAND, color="#be18f0", label='Landing Field', zorder=2)
        
        line3, = ax.plot(WS_VALS, TS_VALS_CR, color="#0FCBFF", label='Cruise', zorder=2)
        
        # line4, = ax.plot(WS_VALS, TS_VALS_ROC, color="#1E6E10", label='Rate of Climb', zorder=2)
        line5, = ax.plot(WS_VALS, TS_VALS_TAKEOFF, color="#FF3C3C", label='Takeoff Field', zorder=2)
        line10, = ax.plot(WS_VALS, TS_VALS_CLIMBGRAD_5, color="#FF1DD6", label='Climb Gradient REQ_5', zorder=2)
        line6, = ax.plot(WS_VALS, TS_VALS_CLIMBGRAD_6, color="#FF8A1D", label='Climb Gradient REQ_6', zorder=2)
        line7, = ax.plot(WS_VALS, TS_VALS_CLIMBGRAD_7, color="#FFE100", label='Climb Gradient REQ_7', zorder=2)
        line8, = ax.plot(WS_VALS, TS_VALS_CLIMBGRAD_8, color="#B1FF14", label='Climb Gradient REQ_8', zorder=2)
        line9, = ax.plot(WS_VALS, TS_VALS_CLIMBGRAD_9, color="#1FCF62", label='Climb Gradient REQ_9', zorder=2)
                
        # WS and TW values spanning design space
        plt.fill_between(WS_VALS_RED, TS_VALS_MAX_RED, max(TS_VALS_MAX_RED[np.isfinite(TS_VALS_MAX_RED)])*np.ones_like(TS_VALS_MAX_RED), color="#f7d7d9")
        
        # Labeling
        legendConstraints = plt.legend(title='Constraints', bbox_to_anchor=(1.01,1), loc='upper left', handles=[line1, line2, line3, line5, line6, line7, line8, line9, line10])
        ax.add_artist(legendConstraints)
        
        plt.xlabel(xlabel='Wing Loading [N/m$^2$]')
        plt.ylabel(ylabel='Thrust-to-Weight Ratio [-]')
        plt.title('Aircraft T/W-W/S Diagram')
        
        designSpaceLabelPos = (1.15*np.mean((min(WS_VALS_RED), max(WS_VALS_RED))), # x
                               0.5*np.mean((min(TS_VALS_MAX_RED[np.isfinite(TS_VALS_MAX_RED)]), max(TS_VALS_MAX_RED[np.isfinite(TS_VALS_MAX_RED)])))) # y
        plt.text(*designSpaceLabelPos, 'Design Space', horizontalalignment='center', color="#000000")
        
        # Design Points (including reference aircraft)
        designPointHandles = []
        designPoint = plt.scatter(2084, 0.453, color='#ff0000', edgecolors='black', label='Design Point', zorder=3)
        designPointHandles.append(designPoint)
        
        for i, ac in enumerate(TWWS_AC_REF):
            designPointRef = plt.scatter(*ac[1:3], color=ac[3], label=ac[0], edgecolors='#000000', zorder=3)
            designPointHandles.append(designPointRef)
            
        legendDesignPoints = plt.legend(title='Design Points', bbox_to_anchor=(1.01,0), handles=designPointHandles, loc='lower left')
        ax.add_artist(legendDesignPoints)

        plt.show()
        
    def designSpace(self, WS_MIN, WS_INTRVL, WS_MAX_APP, WS_MAX_LAND, TS_VALS_MAX):        
        WS_MAX = min(WS_MAX_APP, WS_MAX_LAND)
        WS_VALS_RED = np.arange(WS_MIN, WS_MAX, WS_INTRVL)
        N_VALS = len(WS_VALS_RED)
        
        TS_VALS_MAX_RED = TS_VALS_MAX[:N_VALS]
        
        WS_MAX_POINT = np.array((WS_MAX, TS_VALS_MAX[N_VALS])).reshape(-1, 1)
        POINTS = np.vstack((WS_VALS_RED.T, TS_VALS_MAX_RED.T))
        POINTS = np.hstack((POINTS, WS_MAX_POINT))
        
        return POINTS[0,], POINTS[1,]
