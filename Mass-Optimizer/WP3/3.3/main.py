from formulas_drag_coefficient import *
from formulas_weight import *

if __name__ == '__main__':
    print(calc_CD0(calc_s_wet(), calc_cf(), calc_FF(), False))
    print(calc_weight())
