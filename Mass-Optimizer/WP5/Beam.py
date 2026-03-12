from globalParameters import *
import matplotlib.pyplot as plt
import numpy as np
import scipy as sp
from Stringer import L_Stringer


class Beam():
    def __init__(self, stringers, intg_points: int = 100) -> None:
        self.intg_points = intg_points
        self.stringer_object: L_Stringer = stringers
        self.nBays = False
        
        # SPANWISE ARRAYS

    def vertical_average_square_distance(self):
        return 0.00231111397305, 0.00035866651005
        z_top1 = self.points[0][1]
        z_top2 = self.points[1][1]
        z_bot1 = self.points[3][1]
        z_bot2 = self.points[2][1]
        y_centroid_stacked = self.centroid[:, 1, None].repeat(2, axis=1)

        return np.mean((np.array([z_top1, z_top2]) - y_centroid_stacked)**2, axis=1, keepdims=False), np.mean((np.array([z_bot1, z_bot2]) - y_centroid_stacked)**2, axis=1, keepdims=False)

    def define_spanwise_arrays(self, y, posRibs, tStringersBay, bStringersBay, hStringersBay, nStringersBayTop, nStringersBayBottom):
        self.posRibs = np.array(posRibs)*HALF_SPAN # [% span] e.g. [0.1, 0.3, 0.5, ...] MUST Have 0 and for root!!!!
        prev_rib = np.roll(self.posRibs, 1)
        prev_rib[0] = 0
        if (prev_rib>self.posRibs).any():
            print(f'Found misordered ribs. Trying to fix it.', end='\r')
            self.posRibs = np.maximum(self.posRibs, prev_rib)
        assert int(posRibs[0]) == 0
        self.nBays = self.posRibs.shape[0]
        sectionIDX = np.digitize(y, self.posRibs[1:])
        self.posRibs = np.concatenate([self.posRibs, np.array([HALF_SPAN])])
        
        self.distRibs = np.array([self.posRibs[i+1] - self.posRibs[i] for i in range(self.nBays)])[sectionIDX]
        self.nStringersTop = nStringersBayTop[sectionIDX]
        self.nStringersBottom = nStringersBayBottom[sectionIDX]
        self.tStringersBay = tStringersBay[sectionIDX*0]
        self.bStringersBay = bStringersBay[sectionIDX*0]
        self.hStringersBay = hStringersBay[sectionIDX*0]
        self.single_stringer_area = self.stringer_object.area[sectionIDX*0]
        self.single_stringer_Ixx = self.stringer_object.Ixx[sectionIDX*0]

        self.sectionIDX = sectionIDX
        
        # self.posRibs = self.posRibs[:-1]
        
        return self.distRibs, self.tStringersBay, self.bStringersBay, self.hStringersBay, self.nStringersTop, self.nStringersBottom
        
    def load_wing_box(self, points, thickness, root_chord, tip_chord, span):
        self.points = points # [(x/c,z/c), ...] 
        self.thickness = thickness[self.sectionIDX*0]
        self.root_chord = root_chord
        self.tip_chord = tip_chord
        self.span = span

        self.get_I_of_cross_section()

    def get_I_of_cross_section(self):
        self.edge_centroids_list = []
        self.edge_lengths_list = []
        self.edge_angles_list = []

        for i in range(4): # for each edge
            x1, y1 = self.points[i % 4]
            x2, y2 = self.points[ (i+1) % 4]

            edge_centroid = np.array([(x2+x1)/2, (y2+y1)/2])
            edge_length = np.sqrt( (y2-y1)**2 + (x2-x1)**2 )
            edge_angle = np.arctan( (y2-y1)/(x2-x1) ) if abs(x2-x1)>1e-6 else np.pi/2

            self.edge_centroids_list.append(edge_centroid)
            self.edge_lengths_list.append(edge_length)
            self.edge_angles_list.append(edge_angle)

        self.centroid = np.zeros((self.sectionIDX.size, 2))
        skin_area = sum(self.edge_lengths_list)*self.thickness
        total_stringer_area = (self.nStringersTop + self.nStringersBottom) * self.single_stringer_area
        for i, c in enumerate(self.edge_centroids_list):
            self.centroid[:, 0] += c[0] * self.edge_lengths_list[i]*self.thickness / (skin_area+total_stringer_area)
            self.centroid[:, 1] += c[1] * self.edge_lengths_list[i]*self.thickness / (skin_area+total_stringer_area)
        self.centroid = self.centroid[self.sectionIDX]

        # [(0.2, 0.071507), (0.65, 0.071822), (0.65, -0.021653), (0.2, -0.034334)]
        z_top1 = self.points[0][1]
        z_top2 = self.points[1][1]
        z_bot1 = self.points[3][1]
        z_bot2 = self.points[2][1]
        self.centroid[:, 1] = self.nStringersTop * (z_top1+z_top2)/2 * self.single_stringer_area / (skin_area+total_stringer_area)
        self.centroid[:, 1] = self.nStringersBottom * (z_bot1+z_bot2)/2 * self.single_stringer_area / (skin_area+total_stringer_area)

        self.Ixx_base_wingbox = 0
        self.Izz_base_wingbox = 0
        for i, c in enumerate(self.edge_centroids_list):
            self.Ixx_base_wingbox += (
                self.thickness * self.edge_lengths_list[i]**3 * np.sin(self.edge_angles_list[i])**2 / 12 # main component
                + self.edge_lengths_list[i] * self.thickness * (c-self.centroid)[:, 1]**2                   # parallel axis component
                )

            self.Izz_base_wingbox += (
                self.thickness * self.edge_lengths_list[i]**3 * np.cos(self.edge_angles_list[i])**2 / 12 # main component
                + self.edge_lengths_list[i] * self.thickness * (c-self.centroid)[:, 0]**2                   # parallel axis component
                )
            
        self.Ixz = 0

    def get_chord(self, y):
        frac = 2*np.abs(y)/self.span
        return (1-frac)*self.root_chord + (frac)*self.tip_chord
    
    def get_displacement(self, data, E=E, disable=False):
        s = self.intg_points
        y, M = data[:, 0], data[:, 1]
        c = self.get_chord(y)
        # raise RuntimeError('Multiply by stringer count???')

        avg_squared_dist_top, avg_squared_dist_bot = self.vertical_average_square_distance()

        I = (self.Ixx_base_wingbox*c**3 # scaled wing box
            + self.single_stringer_Ixx*(self.nStringersTop + self.nStringersBottom)
            + self.nStringersTop*avg_squared_dist_top*self.single_stringer_area
            + self.nStringersBottom*avg_squared_dist_bot*self.single_stringer_area
            )
        self.Ixx_list = I
        
        d2v_dy2 = - M/(E * I)
        
        if disable:
            return np.zeros(s)
            
        # integrand_1 = sp.interpolate.interp1d(y, d2v_dy2, kind='cubic', fill_value="extrapolate")
        # dv_dy = np.empty(s)
        # y2 = np.empty(s)
        # for i in range(s):
        #     y2[i] = self.span/2*i/(s-1)
        #     dv_dy[i] = sp.integrate.quad(integrand_1, 0, self.span/2*i/(s-1))[0] # type: ignore
        

        # integrand_2 = sp.interpolate.interp1d(y2, dv_dy, kind='cubic', fill_value="extrapolate")
        # self.v = np.empty(s)
        # for i in range(s):
        #     self.v[i] = sp.integrate.quad(integrand_2, 0, self.span/2*i/(dv_dy.size-1))[0] # type: ignore

        self.dv_dy = sp.integrate.cumulative_trapezoid(y=d2v_dy2, x=y, initial=0) # type: ignore
        self.v = sp.integrate.cumulative_trapezoid(y=self.dv_dy, x=y, initial=0) # type: ignore
        # self.v = np.zeros_like(self.dv_dy)
        # self.v[-1] = sp.integrate.simpson(self.dv_dy, y)

        return self.v
    
    def get_twist(self, data, G, disable=False):
        s = self.intg_points
        a, b, c, d = self.points # Order matters
        chord = self.get_chord(data[:, 0])
        self.Areas = (a[1]-d[1]+b[1]-c[1])/2*(c[0]-d[0]) * chord**2
        integral = chord*sum(self.edge_lengths_list)/self.thickness
        self.J = 4*self.Areas**2 / (integral)

        y = data[:, 0]
        torque = data[:, 1]
        dtheta_dy = torque/(self.J*G)

        if disable:
            return np.zeros(s)

        # integrand = sp.interpolate.interp1d(y, dtheta_dy, kind='cubic', fill_value="extrapolate")
        # self.theta = np.empty(s)
        # for i in range(s):
        #     self.theta[i] = sp.integrate.quad(integrand, 0, self.span/2*i/(s-1))[0] # type: ignore

        self.theta = sp.integrate.cumulative_trapezoid(dtheta_dy, y, initial=0)

        return self.theta

    def get_mass(self, y):
        # y = np.linspace(0, self.span/2, self.intg_points)
        chord = self.get_chord(y)
        skin_area = sum(self.edge_lengths_list)*self.thickness*chord
        total_stringer_area = (self.nStringersTop + self.nStringersBottom) * self.single_stringer_area

        # integrand = sp.interpolate.interp1d(y, skin_area+total_stringer_area, kind='cubic', fill_value="extrapolate")
        # self.volume = sp.integrate.quad(integrand, 0, self.span/2)[0] # type: ignore
        self.volume = sp.integrate.simpson(skin_area+total_stringer_area, y) #type:ignore
        self.mass = self.volume*density

        # print(f'Volume: {self.volume:.4g} m³')
        return self.mass

    def report_stats(self):
        print(f'Deflected {self.v[-1]:.4g}m | Allowed {0.15*self.span:.4g}m')
        print(f'Twisted {self.theta[-1]*180/np.pi:.4g}° | Allowed {10.0:.4g}°')

    def konstantinos_konstantinopoulos(self, y, M, T=0, report=False):
        num_points = M.size
        self.normal_stress = np.empty((num_points, 4))
        chord = self.get_chord(y)

        for i, p in enumerate(self.points):
            x_c, z_c = p
            x = x_c * chord
            z = z_c * chord
            
            # self.normal_stress[:, i] = ((0*self.Ixx_list - M * self.Ixz)*x + (M*self.Izz - 0 * self.Ixz)*z) / (self.Ixx_list*self.Izz - self.Ixz**2)
            self.normal_stress[:, i] = M*z / self.Ixx_list
        if report:
            print(f'Max tensile: {np.max(self.normal_stress)/1e6:.0f}MPa, max compressive: {np.min(self.normal_stress)/1e6:.0f}MPa')

        return self.normal_stress

    def getShearStress(self, y, V, T):
        # Shear force contribution
        kV = 2 # shear factor, tau_max = kV*tau_avg (see reader app. F)
        # print(self.points)
        hFrontSpar = abs(self.points[0][1] - self.points[3][1])*self.get_chord(y)
        hRearSpar = abs(self.points[1][1] - self.points[2][1])*self.get_chord(y)
        forceShearStress = kV*V/(hFrontSpar*self.thickness+hRearSpar*self.thickness)
        
        # Torsion contribution
        a, b, c, d = self.points # Order matters
        self.Areas = (a[1]-d[1]+b[1]-c[1])/2*(c[0]-d[0]) * self.get_chord(y)**2
        torsionShearStress = T/(2*self.Areas*self.thickness)

        # This gives the maximum shear stress in the section, which should occur in the front spar.
        return np.array([forceShearStress+torsionShearStress, forceShearStress-torsionShearStress]).T
        
    # FAILURE STRESS CALCULATIONS
    def getFailureStresses(self, y):
        if not self.nBays:
            print('You must define the ribs first!')
            raise Exception
        
        # Failure stresses
        # Shear 
        shearBuckStressCrit = self.shearBuckStress(y, self.distRibs)
        
        # Compressive
        skinBuckStressCrit = self.skinBuckStress(y, self.distRibs)
        colBuckStressCrit = self.colBuckStress(self.distRibs)
        compYieldCrit = np.full_like(y, SIGMA_Y_COMP)
        
        # Tensile
        tensYieldCrit = np.full_like(y, SIGMA_Y_TENS)
        crackPropStressCrit = np.full_like(y, self.crackPropStress())  

        stressStack = np.hstack([shearBuckStressCrit, skinBuckStressCrit, colBuckStressCrit[:, None], compYieldCrit[:, None], tensYieldCrit[:, None], crackPropStressCrit[:, None]])
        return np.min(stressStack, axis=1), stressStack    

    # Shear Buckling - this is a shear stress!!
    def shearBuckStress(self, y, rib_spacing):
        hFrontSpar = abs(self.points[0][1] - self.points[3][1])*self.get_chord(y)
        hRearSpar = abs(self.points[1][1] - self.points[2][1])*self.get_chord(y)
        heights = np.array([hFrontSpar, hRearSpar]).T

        a_b = rib_spacing[:, None]/heights

        k_s = self.ShearBucklingInterpolation(a_b)

        t = self.thickness[:, None]
        
        tau = np.pi**2 * k_s * E / (12*(1-POISSON_RATIO**2)) * (t/heights)**2
            
        return tau # shape(y.size, 2) for both spars
    
    def ShearBucklingInterpolation(self, a_b, plot=False):
        x_data=[1.00, 1.17, 1.50, 1.750, 2.00, 2.50, 3.0, 4.0, 5.0]
        y_data=[15.0, 13.0, 11.6, 10.84, 10.4, 9.84, 9.7, 9.5, 9.53]
        f=sp.interpolate.interp1d(x_data, y_data, kind='cubic', bounds_error=False, fill_value=(15, 9.53))

        if plot:
            x_plt=np.arange(np.min(x_data)-1, np.max(x_data)+10, 0.001)
            y_plt=f(x_plt)
            img = plt.imread('WP5/old/Skin Buckling/web.png')  # replace with your image path
            fig, ax = plt.subplots()

            ax.imshow(img, extent=(-0.5, 5.55, 15.25, 3.85),
                origin='lower', aspect='auto', alpha=0.4, zorder=0)
            ax.plot(x_data, y_data, 'o', zorder=2, markersize=1, color='k')
            ax.plot(x_plt, y_plt, '-', zorder=3, linewidth=1)

            ax.set_xlim(-1, 6)
            ax.set_ylim(3, 17)
            plt.show()

        return f(a_b)
    
    # Skin buckling
    def skinBuckStress(self, y, rib_spacing):
        t = self.thickness[:, None]
        chord = self.get_chord(y)
        edges = np.array(self.edge_lengths_list)
        b = np.outer(chord, edges)
        b[:, 0] /= self.nStringersTop
        b[:, 2] /= self.nStringersBottom
        sigma = np.pi**2*self.SkinBucklingInterpolation(rib_spacing[:, None]/b)*E / (12*(1-POISSON_RATIO**2)) * (t/b)**2
        sigma[:, 1] = np.inf
        sigma[:, 3] = np.inf
        return sigma
    
    def SkinBucklingInterpolation(self, a_b, plot=False):
        x_data=[0.7,  0.85, 1.0, 1.15, 1.3, 1.67, 2.0, 2.2, 2.5, 2.75, 3.0, 3.2, 3.35, 3.70, 4.18, 4.66, 4.8, 5.0]
        y_data=[10.7, 8.16, 6.8, 6.17, 5.8, 5.6,  4.9, 4.7, 4.6, 4.70, 4.5, 4.4, 4.4,  4.45, 4.27, 4.35, 4.3, 4.3]
        f=sp.interpolate.interp1d(x_data, y_data, kind='cubic', bounds_error=False, fill_value=(10.7, 4.3))

        if plot:
            x_plt=np.arange(np.min(x_data)-1, np.max(x_data)+10, 0.001)
            y_plt=f(x_plt)
            img = plt.imread('WP5/old/Skin Buckling/skin.png')  # replace with your image path
            fig, ax = plt.subplots()

            ax.imshow(img, extent=(-0.70, 6.0, 16.45, -1.05),
                origin='lower', aspect='auto', alpha=0.4, zorder=0)
            ax.plot(x_data, y_data, 'o', zorder=2, markersize=1, color='k')
            ax.plot(x_plt, y_plt, '-', zorder=3, linewidth=1)

            ax.set_xlim(-1, 16)
            ax.set_ylim(-1, 17)
            plt.show()
        
        # if (a_b<0.7).any():
        #     raise RuntimeError(np.min(a_b))

        return f(a_b)
    
    # Column Buckling - normal stress
    def colBuckStress(self, L):
        K = K_CC
        A = self.single_stringer_area
        I = self.Ixx_list
        return (K * np.pi**2 * E * I)/(L**2 * A)
    
    def calcStringerLen(self, sigma, K, I, A):
        return np.sqrt((K * np.pi**2 * E * I)/(sigma * A))
    
    def calcStringerArea(self, sigma, K, I, L):
        return np.sqrt((K * np.pi**2 * E * I)/(sigma * L**2))
    
    def calcStringerLenAll(self, sigma):
        # Wing tip / free end
        # TODO: I_stringer, A_Stringer
        if 1==1:
            raise RuntimeError('Check this')
        L_ribs_from_tip = self.calcStringerLen(sigma, K_FC, self.single_stringer_Ixx, self.single_stringer_area)
        # Between ribs / both fixed
        L_ribs_between = self.calcStringerLen(sigma, K_CC, self.single_stringer_Ixx, self.single_stringer_area)

        nRibs = np.ceil((b/2 - L_ribs_from_tip) / L_ribs_between).astype(int)

        return L_ribs_from_tip, L_ribs_between, nRibs
    
    def calcStringerAreaAll(self, sigma):
        LRibsFromTip, LRibsBetween, _ = self.calcStringerLenAll(sigma)

        if 1==1:
            raise RuntimeError('Check this')
        
        # Wing tip / free end
        A_ribs_from_tip = self.calcStringerArea(sigma, K_FC, self.single_stringer_Ixx, LRibsFromTip)

        # Between ribs / both fixed
        A_ribs_between = self.calcStringerArea(sigma, K_CC, self.single_stringer_Ixx, LRibsBetween)

        return A_ribs_from_tip, A_ribs_between

    # Crack Propagation
    def calcCCrit(self, sigma):
        return K_1C ** 2 / (np.pi * SHAPE_FACTOR ** 2 * sigma ** 2) * 10 ** 3 # [mm]
    
    def crackPropStress(self):
        return K_1C/np.sqrt(np.pi*CRACK_LENGTH)
    
    # PLOTTING
    def plot(self):
        y = np.linspace(0, self.span/2, self.intg_points)

        plt.figure()
        plt.title('Stiffness Diagram')
        plt.plot(y, self.Ixx_list*1e4, label=f'I$_x$$_x$')
        plt.plot(y, self.J*1e4, label=f'J')
        plt.xlabel('y [$m$]')
        plt.ylabel('Stiffness × $10^4$ [$m^4$]')
        plt.xlim(0, self.span/2)
        plt.ylim(0, )
        plt.grid(which='both')
        plt.legend()
        plt.tight_layout()
        plt.show(block=False)
        
        plt.figure()
        plt.title('Deflection / Twisting Diagram')
        plt.plot(y, self.v/(np.max(np.abs(self.v))), label=f'v | max {self.v[-1]:.4g} m')
        plt.plot(y, self.theta/(np.max(np.abs(self.theta))), label=f'theta | max {np.max(np.abs(self.theta))*180/np.pi*np.sign(self.theta[-1]):.4g}°')
        plt.xlabel('y [$m$]')
        plt.ylabel('Normalised value')
        plt.xlim(0, self.span/2)
        plt.ylim(0, 1)
        plt.grid(which='both')
        plt.legend()
        plt.tight_layout()
        plt.show(block=True)


if __name__=='__main__':
    print(f'Wrong file dummy')
    
