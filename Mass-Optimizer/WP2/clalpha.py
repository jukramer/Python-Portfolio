from math import pi, sqrt, tan
from parameters import *

a = sqrt(1.4*287.05287*288.15)
M = 52.1/a
Beta = sqrt(1-M**2)
A = b**2/S

LAMBDA_Chalf = (LAMBDA_C4-LAMBDA_LE)*2+LAMBDA_LE

print(2*pi*A/(2+sqrt(4+(A*Beta/0.95)**2*(1+(tan(LAMBDA_Chalf*pi/180))**2/Beta**2))))