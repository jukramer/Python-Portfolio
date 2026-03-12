import matplotlib.pyplot as plt
import numpy as np
import scipy as sp
from scipy import interpolate

class L_Stringer():
    def __init__(self, base, height, thickness):
        self.base = base # m
        self.height = height # m
        self.thickness = thickness # m

        # assumes literal L shape. 
        # z upwards, x to the right
        # Origin bottom left
        self.area = self.base*self.height - (self.base-self.thickness)*(self.height-self.thickness)
        self.z_c = (self.height*self.thickness*self.height/2 + (self.base-self.thickness)*self.thickness*self.thickness/2)/self.area
        self.x_c = (self.base*self.thickness*self.base/2 + (self.height-self.thickness)*self.thickness*self.thickness/2)/self.area
        self.centroid = np.array([self.x_c, self.z_c])
    
        self.Ixx = (
            1/12*self.thickness*self.height**3 + self.thickness*self.height * (self.height/2-self.z_c)**2
          + 1/12*(self.base-self.thickness)*self.thickness**3 + (self.base-self.thickness)*self.thickness * (self.thickness/2-self.z_c)**2
        )

        self.Izz = (
            1/12*self.thickness*self.base**3 + self.thickness*self.base * (self.base/2-self.x_c)**2
          + 1/12*(self.height-self.thickness)*self.thickness**3 + (self.height-self.thickness)*self.thickness * (self.thickness/2-self.x_c)**2
        )

        self.Ixz = (
            0 + self.thickness*self.height * (self.thickness/2-self.x_c)*(self.height/2-self.z_c)
          + 0 + (self.base-self.thickness)*self.thickness * ((self.thickness+self.base)/2-self.x_c)*(self.thickness/2-self.z_c)
        )

    def get_I_at_angle(self, alpha):
        # alpha is measured from the horizontal
        I = self.Ixx*np.cos(alpha)**2 + self.Izz*np.sin(alpha)**2 - 2*self.Ixz*np.cos(alpha)*np.sin(alpha)

if __name__ == '__main__':
    stringer = L_Stringer(5/100, 3/100, 1/1000)
 