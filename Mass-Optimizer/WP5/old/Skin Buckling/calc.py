from parameters import *
import matplotlib.pyplot as plt
import numpy as np
import scipy as sp

class Calc:
    def __init__(self):
        self.t

    def skinBucklingStress(t, b):
        return np.pi**2*kC*E / (12*(1-POISSION_RATIO**2)) * (t/b)**2
    
    def SkinBucklingInterpolation(a_b):
        x=[0.7,0.85,1.0,1.15,1.3,1.45,1.6,1.8,2.0,2.2,2.4,2.6,2.75,2.9,3.05,3.2,3.35,3.5,3.7,3.85,4.0,4.15,4.3,4.45,4.6,4.8,5.0]
        y=[10.7,7.5,6.8,6,5.8,5.5,5.5,5.1,4.9,4.7,4.5,4.5,4.6,4.5,4.4,4.4,4.4,4.3,4.3,4.3,4.2,4.2,4.2,4.1,4.1,4.1,4.1]
        f=sp.interpolate.interp1d(x,y,kind='cubic')
        xnew=np.arange(np.min(x),np.max(x),0.001)
        ynew=f(xnew)
        plt.plot(x,y,'o',xnew,ynew,'-')
        plt.show()


if __name__ == '__main__':
    calc1 = Calc()
    calc2 = Calc()
