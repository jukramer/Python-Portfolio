from Beam import *
from calc import *
from globalParameters import *
from Stringer import *
from plotSafetyMargin import plotFailureMargin
import matplotlib.pyplot as plt
import numpy as np
import warnings

STRINGER_FACTOR = 1e5
iterList = []
stressList = []
stressList2 = []
iters = 1

order_of_mag = np.array([[1e-2, 1e-2, 1e-2, 1e-2, 1e-2, 1e-1, 1e-1]])

np.set_printoptions(suppress=True)

def x_from_print():
    # from optimisation run:
    x = np.array(
        [[0.001604, 0.004027, 0.002671, 0.03842, 0.03804, 19.86, 19.73],
        [0.0116, 0.00341, 0.002097, 0.04197, 0.04137, 19.35, 18.8],
        [0.05499, 0.003279, 0.001675, 0.04031, 0.04099, 19.38, 17.46],
        [0.107, 0.004129, 0.00118, 0.03246, 0.03049, 20, 18.34],
        [0.1476, 0.003667, 0.000745, 0.03095, 0.02923, 18.74, 16.65],
        [0.3293, 0.003324, 0.0005258, 0.0291, 0.02715, 18.34, 17.73],
        [0.4559, 0.003633, 0.0004261, 0.02776, 0.02615, 17.88, 17.48],
        [0.6238, 0.003086, 0.0003407, 0.02764, 0.02703, 17.91, 18.06],
        [0.8198, 0.003612, 0.000461, 0.02909, 0.02893, 18.71, 17.73]]
        )/order_of_mag

    # tweaked:
    x = np.array(
        [[0.000, 0.0042, 0.0011, 0.0105, 0.0105, 12., 12.],
        [0.0239, 0.0042, 0.0011, 0.0105, 0.0105, 12, 12.],
        [0.0616, 0.0042, 0.0011, 0.0105, 0.0105, 12., 12],
        [0.1122, 0.0042, 0.0011, 0.0105, 0.0105, 10., 10.],
        [0.1598, 0.0042, 0.0011, 0.0105, 0.0105, 10., 10.],
        [0.3235, 0.0042, 0.0011, 0.0105, 0.0105, 8.0, 8.0],
        [0.4562, 0.0042, 0.0011, 0.0105, 0.0105, 6.0, 6.0],
        [0.6231, 0.0042, 0.0011, 0.0105, 0.0105, 4., 4.],
        [0.8206, 0.0042, 0.0011, 0.0105, 0.0105, 3., 3.]]
        )/order_of_mag
    
    return x.T.flatten()

def calc_mass(x):
    global bay_count
    bay_count = x.size//7
    x = x.reshape(7, bay_count) * order_of_mag.T
    posRibs, tSkinBay, tStringersBay, bStringersBay, hStringersBay, nStringersBayTop, nStringersBayBottom = x
    
    posRibs = np.array(posRibs)
    tStringersBay = np.array(tStringersBay)
    tSkinBay = np.array(tSkinBay)
    bStringersBay = np.array(bStringersBay)
    hStringersBay = np.array(hStringersBay)
    nStringersBayTop = np.array(nStringersBayTop)
    nStringersBayBottom = np.array(nStringersBayBottom)
    
    wing_box_points = [(0.2, 0.071507), (0.65, 0.071822), (0.65, -0.021653), (0.2, -0.034334)] # [(x/c,z/c), ...] 

    stringer_instance = L_Stringer(bStringersBay, hStringersBay, tStringersBay)
    wb = Beam(stringers=stringer_instance, intg_points=865)
    wb.define_spanwise_arrays(y_data, posRibs, tStringersBay, bStringersBay, hStringersBay, nStringersBayTop, nStringersBayBottom)
    wb.load_wing_box(points=wing_box_points, thickness=tSkinBay, root_chord=2.85, tip_chord=1.03, span=17.29)
    v = wb.get_displacement(np.vstack((y_data, M_data)).T, E, False)
    theta = wb.get_twist(np.vstack((y_data, T_data)).T, G, False)
    wb.get_mass(y_data)
    
    # Applied Stresses
    normalStressAppliedTens = np.tile(np.maximum(0, np.max(wb.konstantinos_konstantinopoulos(y_data, M_data), axis=1, keepdims=True)), (1,2))
    normalStressAppliedComp = np.tile(np.minimum(0, np.min(wb.konstantinos_konstantinopoulos(y_data, M_data), axis=1, keepdims=True)), (1,6))

    shearStressApplied = wb.getShearStress(y_data, V_data, T_data)
    
    # Critical Stresses
    stressStack = wb.getFailureStresses(y_data)[1]
    critStressArrayShear = stressStack[:, :2] # width 2
    critStressArrayComp = stressStack[:, 2:8] # width 6
    critStressArrayTens = stressStack[:, 8:] # width 2 

    modes = ['shearBuckStress', 'shearBuckStress', *['skinBuckStress' for _ in range(4)], 'colBuckStress', 'compYield', 'tensYield', 'crackPropStress']
    
    # Stress Margins
    marginArrayShear = critStressArrayShear/(shearStressApplied+1e-8)
    marginArrayComp = critStressArrayComp/(-normalStressAppliedComp+1e-8)
    marginArrayTens = critStressArrayTens/(normalStressAppliedTens+1e-8)

    minMarginShear = np.min(marginArrayShear)
    minMarginComp = np.min(marginArrayComp)
    argmin_comp = np.argmin(marginArrayComp, axis=1)[0]
    minMarginTens = np.min(marginArrayTens)
    
    # deltaArrayShear = critStressArrayShear - shearStressApplied
    # deltaArrayComp = critStressArrayComp - normalStressAppliedComp
    # deltaArrayTens = critStressArrayTens - normalStressAppliedTens

    rolled_ribs = np.roll(posRibs, -1)
    diff = rolled_ribs-posRibs
    diff[-1] = np.inf
    min_dist = np.min(diff)

    if iters % 100 == 0:
        print(f'Optimising ({iters})| {wb.mass:.1f}kg/{wb.volume:.3g}m³, Shear Margin: {minMarginShear:.3g}, Comp Margin: {minMarginComp:.3g}, Tens Margin: {minMarginTens:.3g}', end='\r')

    if iters % 500 == 0:
        arr = x.reshape(7, bay_count).T
        print('\n', np.array2string(arr, formatter={'float_kind':lambda v: f"{v:.4g}"}, separator=', '))
        wb.report_stats()
    
    return wb.mass, np.array([minMarginShear, minMarginComp, minMarginTens, np.min([minMarginShear,minMarginComp,minMarginTens]), v[-1], theta[-1]*180/np.pi, min_dist])

def mass_wrap(x):
    global iters
    iters += 1
    # print(calcVol(x)[0])
    return calc_mass(x)[0]

def constr_wrap(x):
    # print(calcVol(x)[1].shape)
    return calc_mass(x)[1]

def optimise_main():
    global y_data, M_data, T_data, V_data, T_data
    global initial_x
    
    if not False:
        warnings.simplefilter('ignore', category=UserWarning)

    # EXTERNAL LOADING
    calc = Calc(r'WP4\WP4_1\dataa0.txt', r'WP4\WP4_1\dataa10.txt')
    calc.set_load_case_from_flight(LOAD_FACTOR, W_MTOW)

    aeroLoading, inertialLoading, torsionLoading = lambda x: calc.totalLoading(x, LOAD_FACTOR, M_WING)[0], lambda x: calc.totalLoading(x, LOAD_FACTOR, M_WING)[1], lambda x: calc.totalLoading(x, LOAD_FACTOR, M_WING)[3]
    loadingDist = lambda x: calc.findLoadingDist(x)
    pointLoads, pointTorques = (lambda x: calc.totalLoading(x, LOAD_FACTOR, M_WING)[2])(0), (lambda x: calc.totalLoading(x, LOAD_FACTOR, M_WING)[4])(0)
    
    # INTERNAL LOADING
    y_data, M_data, T_data, V_data = calc.plot(aeroLoading,
                                       inertialLoading, 
                                       torsionLoading, 
                                       loadingDist, 
                                       pointLoads, 
                                       NULL_ARRAY_2, 
                                       pointTorques, 
                                       (0, HALF_SPAN),
                                       subplots=True,
                                       plot=False)
    
    # OPTIMIZATION
    # posRibs, tSkinBay, tStringersBay, bStringersBay, hStringersBay, nStringersBayTop, nStringersBayBottom = x
    posRibs = (np.linspace(0, 1, 10)[:-1])**2
    ones = np.ones_like(posRibs)
    # initial_x = (np.array([posRibs, 4e-3*ones, 3e-3*ones, 5e-2*ones, 5e-2*ones, 20*ones, 20*ones])/order_of_mag.T).flatten()
    initial_x = x_from_print()
    # print(initial_x.reshape(7, 9).T * order_of_mag)
    # initial_x = (np.array([posRibs, 4e-3*ones, 2.7e-3*ones, 3e-2*ones, 3e-2*ones, np.linspace(20, 5, 9), np.linspace(20, 5, 9)])/order_of_mag.T).flatten()

    
    constraints_sigma = sp.optimize.NonlinearConstraint(constr_wrap, lb=[1, 1, 1, 1, -0.15*HALF_SPAN*2, -10.0, 0.01], ub=[np.inf, np.inf, np.inf, 1.1, 0.15*HALF_SPAN*2, 10.0, np.inf], keep_feasible=False)
    bounds_x = sp.optimize.Bounds((np.array([0*ones, 1e-3*ones,     1e-3*ones,     1e-2*ones,     1e-2*ones,     2*ones,   2*ones])/order_of_mag.T).flatten(), 
                                  (np.array([ones,   10e-3*ones, 10e-3*ones, 10e-2*ones, 10e-2*ones, 100*ones, 100*ones])/order_of_mag.T).flatten(),
                                  keep_feasible=False)
    
    optim = sp.optimize.minimize(mass_wrap, initial_x, method='trust-constr', bounds=bounds_x, constraints=constraints_sigma, ) # type:ignore | options = {"gtol": 1e-8}
    # optim = sp.optimize.shgo(volWrap, bounds=bounds_x, constraints=constraints_sigma) # type:ignore

    raw_result = optim.x
    print('')
    print("Success:", optim.success)
    print("Status:", optim.status)
    print("Message:", optim.message)
    print("Constraint violation:", optim.constr_violation)
    print("Optimality:", optim.optimality)
    print('\nResults:')
    arr = raw_result.reshape(7, bay_count).T * order_of_mag
    print(np.array2string(arr, formatter={'float_kind':lambda v: f"{v:.4g}"}, separator=', '))
    print(constr_wrap(raw_result))

    
    # print(stressList[0].shape)
    # print(stressList2[0].shape)
    # # plt.plot(iterList, stressList)
    # # plt.plot(iterList, stressList2)
    # # plt.yscale('log')
    # # plt.plot(np.linspace(0, 1, maxMarginArray.shape[0]), maxMarginArray)
    # plt.show()

if __name__ == '__main__':
    optimise_main() 
