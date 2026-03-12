L = 1/2 * rho * V ** 2 * C_l * S #lift equation
V_app = 1.23*V_so # relation between approach and stall speed in CS-25 plane
N_f = m_f/(m_f+m_t) # gravimetric efficiency
e_eff = η_f * rho_e/rho # effective specific energy for fuels
rho_e_eff = n_v * rho_e # effective energy density for fuels
m_MTO = m_pl + m_OE + m_ec # max take-off mass
R = η_eng * η_p * L/D * e_f/g * ln((m_OE+m_pl+m_f)/(m_OE+m_pl)) # Breguet Range equation
m_f/m_MTO = 1-exp( -R_eq * D * g/(n_eng * n_p * e_f *L)) # Breguet range equation rewritten for mass fraction
C_L = 2*L/ (rho * V ** 2 * S_w) #Cl
C_D = 2*D/ (rho * V ** 2 * S_w) #Cd

page 80
2 + 2
 Stall speed (Vs) or approach speed (Vapp)
2. Landing field length (LFL, LLF)
3. Cruise speed (VCR) or cruise Mach number (MCR)
4. Climb rate (c)
5. Climb gradient (G)
6. Take-off field length (TOFL, LTO)

beta = m/m_MTO

LANDING_DIST = 1/0.6 * (AIR_DIST * GROUNDROLL_DIST) #p149



