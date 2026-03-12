from calc import *
import numpy as np
import os

np.set_printoptions(suppress=True)

if __name__ == '__main__':
    INT_INTRVLS = 100 # integration intervals
    calc = Calc(INT_INTRVLS)
    
    # C_ROOT = 2*S/(b*1+b*TAPER_RATIO)
    # print(C_ROOT, TAPER_RATIO*C_ROOT)
    # print(b/2*np.tan(np.deg2rad(LAMBDA_LE)))
    
    dir = 'WP2/xflr_data'

    for entry in os.scandir(dir):
        if entry.is_file():
            # try:
            print(entry.path)
            Calc.getLD(Calc, entry.path)
            # # except:
            #     print(entry.path, 'Failed')
