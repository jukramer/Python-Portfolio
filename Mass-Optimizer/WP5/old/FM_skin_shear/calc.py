import numpy as np
import math
import os, sys
from parameters import *

current_folder = sys.path[0]
sys_design_folder = os.path.dirname(os.path.dirname(current_folder))
sys.path.append(sys_design_folder)
from WP5 import Beam

def skin_shear_buckling(k_s, t, b):
   return np.pi**2 * k_s * E / (12*(1-poisson_ratio**2)) * (t/b)**2