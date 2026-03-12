from parameters_drag import *
import math as m


#Sw calulation
Swet_wing = 1.07 * 2 * S_wexp
Swet_fus = ((m.pi * D_fus)/4)*(1/(3*L1**2)*((4*L1**2+D_fus**2/4)**1.5-(D_fus**3/8))-D_fus+4*L2+2*m.sqrt(L3**2+D_fus**2/4))
Swet_hor = 1.05 * 2 * S_hexp
Swet_vert = 1.05 * 2 * S_vexp
Swet_nac = 0 #wetted area nacelle is dependent on team engine


# print(Swet_wing)
# print(Swet_hor)
# print(Swet_vert)
# print(Swet_fus)


S_wet = Swet_wing + Swet_fus + Swet_hor + Swet_vert
# print(S_wet)

#FF calculation


FFwing =(1+(0.6/xc)*(tc)+100*(tc)**4) *(1.34*M**0.18*(m.cos(sweep)**0.28))
FFhort = (1+(0.6/xct)*(tct)+100*(tct)**4)* (1.34*M**0.18*(m.cos(sweeptail)**0.28))
FFvertc = (1+(0.6/xcv)*(tcv)+100*(tcv)**4)* (1.34*M**0.18*(m.cos(sweepvtail)**0.28))
FFfus = (1+(60/ffus**3)+(ffus/400))
FFnac = (1+(0.35/fnac))



