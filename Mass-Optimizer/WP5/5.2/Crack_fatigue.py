import numpy as np

#### Paris Law ####
c = 0.01 * 10 ** -3 #[m]
k_1c = 26 * 10 ** 6
Y = 1.1
sigma = 24 * 10 ** 6 #Placeholder

#### c_crit ####
def c_crit(sigma, k_1c, Y):
    return k_1c ** 2 / (np.pi * Y ** 2 * sigma ** 2) * 10 ** 3 # [mm]

#### Graphing Paris Law ####
A = 1.85 * 10 ** -11
d_sig = 100 * 10 ** 6 # PLaceholder

m = 4.05

def dc(A, Y, d_sig, c, m):
    return A * (Y * d_sig * np.sqrt(np.pi * c) ) ** m

dc_f = 0

while c <= c_crit(sigma, k_1c, Y):

    dc_f += dc(A, Y, d_sig, c, m)

    c += dc_f







