from WP4_1.calc import *
from WP4_2.Beam import *
import matplotlib.pyplot as plt
import numpy as np
import warnings


def main(debug=False):   
    if not debug:
        warnings.simplefilter('ignore', category=UserWarning)

    # EXTERNAL LOADING
    calc = Calc(r'WP4\WP4_1\dataa0.txt', r'WP4\WP4_1\dataa10.txt')
    calc.set_load_case_from_flight(LOAD_FACTOR, W_MTOW)

    xVals = np.arange(0, HALF_SPAN, 0.01)
    
    aeroLoading, inertialLoading, torsionLoading = lambda x: calc.totalLoading(x, LOAD_FACTOR, M_WING)[0], lambda x: calc.totalLoading(x, LOAD_FACTOR, M_WING)[1], lambda x: calc.totalLoading(x, LOAD_FACTOR, M_WING)[3]
    loadingDist = lambda x: calc.findLoadingDist(x)
    pointLoads, pointTorques = (lambda x: calc.totalLoading(x, LOAD_FACTOR, M_WING)[2])(0), (lambda x: calc.totalLoading(x, LOAD_FACTOR, M_WING)[4])(0)
    
    print(pointLoads)
    print(pointTorques)
    
    # aeroLoadingVals = aeroLoading(xVals)
    # inertialLoadingVals = inertialLoading(xVals)
    # torsionLoadingVals = torsionLoading(xVals)
    
    # figLoad, (axLoad1, axLoad2, axLoad3) = plt.subplots(1,3)
    # axLoad1.plot(xVals, aeroLoadingVals, color='blue')
    # axLoad1.set_title('Distributed Normal Force')
    # axLoad1.set_xlabel('y [m]')
    # axLoad1.set_ylabel('Distributed Normal Force [N]')
    
    # axLoad2.plot(xVals, torsionLoadingVals, color='green')
    # axLoad2.set_title('Distributed Pitching Moment')
    # axLoad2.set_xlabel('y [m]')
    # axLoad2.set_ylabel('Distributed Pitching Moment [Nm]')
    
    # axLoad3.plot(xVals, inertialLoadingVals, color='red')
    # axLoad3.set_title('Distributed Inertial Loading')
    # axLoad3.set_xlabel('y [m]')
    # axLoad3.set_ylabel('Distributed Inertial Loading [N]')
    
    # figLoad.set_size_inches(15,5)
    # figLoad.suptitle(fr'External Loading', size='16', weight='semibold')
    # figLoad.tight_layout()
    # figLoad.savefig(fr'diagrams\Loading')
    # plt.show()

    # INTERNAL LOADING
    y_data, M_data, T_data = calc.plot(aeroLoading,
                                       inertialLoading, 
                                       torsionLoading, 
                                       loadingDist, 
                                       pointLoads, 
                                       NULL_ARRAY_2, 
                                       pointTorques, 
                                       (0, HALF_SPAN),
                                       subplots=True,
                                       plot=True)
        
    # DEFLECTION CALCULATIONS
    wing_box_points = [(0.2, 0.071507), (0.65, 0.071822), (0.65, -0.021653), (0.2, -0.034334)] # [(x/c,z/c), ...] 

    aux_spar_endpoints = [(0.425, -1), (0.2, -1)] # [(x/c_start, y_start), (x/c_end, y_end)] | Mind the units

    # Thin stringers
    stringer_area = 0.05/1000 # m²
    stringer_count_top = 13
    stringer_count_bottom = 13
    skin_thickness = 1/1000

    # # Thick stringers
    # stringer_area = 0.312/1000 # m²
    # stringer_count_top = 2
    # stringer_count_bottom = 2
    # skin_thickness = 1/1000

    # # Thick skin
    # stringer_area = 0 # m²
    # stringer_count_top = 0
    # stringer_count_bottom = 0
    # skin_thickness = 1.6/1000

    zis_is_ze_beam = Beam(y_data.size)
    zis_is_ze_beam.load_wing_box(points=wing_box_points, stringer_area=stringer_area, stringer_count_top=stringer_count_top, stringer_count_bottom=stringer_count_bottom, aux_spar_endpoints=aux_spar_endpoints, thickness=skin_thickness, aux_spart_thickness=np.nan, root_chord=2.85, tip_chord=1.03, span=17.29)
    zis_is_ze_beam.get_displacement(np.column_stack((y_data, M_data)), E=72.4e9)
    zis_is_ze_beam.get_twist(np.column_stack((y_data, T_data)), G=28e9)
    print(f'Deflected {zis_is_ze_beam.v[-1]:.4g}m | Allowed {0.15*zis_is_ze_beam.span:.4g}m')
    print(f'Twisted {zis_is_ze_beam.theta[-1]*180/np.pi:.4g}° | Allowed {10.0:.4g}°')
    zis_is_ze_beam.get_volume()
    zis_is_ze_beam.plot()

if __name__ == '__main__':
    main()