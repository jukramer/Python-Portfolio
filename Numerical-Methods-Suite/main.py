import numpy as np
import scipy as sp
import matplotlib.pyplot as plt

class rootFinder():
    def __init__(self, e):
        self.e = e # max acceptable error

    def recursiveBisection(self, f, a, b):
        n = 0 # n iterations
        nMax = 1000 # n of iterations until stopping
        nList = []
        xList = []

        if f(a)*f(b) >= 0:
            print('f(a) and f(b) must have different signs and not be 0!')
            return 

        while n < nMax:
            n += 1
            c = 0.5*(a+b)

            nList.append(n)
            xList.append(c)
            
            if f(c)*f(a) < 0:
                b = c
            else:
                a = c

            try:
                if abs(f(c)) < self.e:
                    print(f'Found root {c} after {n} iterations!')
                    plt.plot(nList, xList)
                    plt.show()
                    break
            except:
                pass

        plt.plot(nList, xList)
        plt.show()

    def FPI(self, phi, x0):
        n = 0 # n iterations
        nMax = 1000 # n of iterations until stopping
        nList = []
        xList = []

        while n < nMax:
            n+=1
            print(f'hello{n}')

            if n == nMax or sp.misc.derivative(phi, x0, 1e-3)>1:
                print('Method diverges.')
                break

            try:
                x0 = phi(x0)
                print(x0)
            except:
                print('Method failed - invalid phi(x)')
                break

            nList.append(n)
            xList.append(x0)

            if abs(x0-phi(x0)) < self.e:
                print(f'Found root {x0} after {n} iterations!')
                plt.plot(nList, xList)
                plt.show()
                break

        plt.plot(nList, xList)
        plt.show()

        
    def newton(self, f, x0):
        n = 0 # n iterations
        nMax = 1000 # n of iterations until stopping
        nList = []
        xList = []

        while n < nMax:
            n+=1
            x1 = x0 - f(x0)/sp.misc.derivative(f, x0, 1e-3)
            x0 = x1

            nList.append(n)
            xList.append(x0)

            if abs(f(x0)) < self.e:
                print(f'Found root {x0} after {n} iterations!')
                plt.plot(nList, xList)
                plt.show()
                break

        if n == nMax:
            print('Method diverges.')

        
class Interpolator():
    def __init__(self, e):
        self.e = e # max acceptable error

    def findInterpolation(self, xi, fi):
        # Convert basic lists to np arrays
        xi, fi = np.array(xi), np.array(fi)

        # Check that all datapoints are complete
        if len(xi) != len(fi):
            print('xi and fi must have the same amount of points!')
            return
        
        n = len(xi)
        
        A = np.zeros((n,n)) # matrix for values

        # Populate matrix with correct values of phi(xi)
        for i in range(n):
            for j in range(n):
                A[i][j] = xi[i]**j

        # Find coefficient vector
        a = np.linalg.inv(A) @ fi

        return a
    
    def polynomial(self, a, x):
        n = len(a)
        xList = []

        # Populate xList with x^0, x^1, x^2 ... x^n
        for i in range(n):
            xList.append(x**i)

        xList = np.array(xList) # convert xList to np array

        return np.dot(a, xList)
    
    def plotInterpolation(self, xi, fi):
        xp = np.linspace(min(xi), max(xi), len(xi)*100)
        fp = self.polynomial(self.findInterpolation(xi, fi), xp)

        plt.scatter(xi, fi, color='black')
        plt.plot(xi, fi, color = '#6451f0')
        plt.plot(xp, fp, color = 'red')
        plt.show()
        
        
if __name__ == '__main__':
    # r = rootFinder(1e-25)
    # r.FPI(lambda x: np.log(5*x**2), 2)
    i = Interpolator(1e-25)
    i.plotInterpolation(np.linspace(-5, 5, 11), abs(np.linspace(-5, 5, 11)))