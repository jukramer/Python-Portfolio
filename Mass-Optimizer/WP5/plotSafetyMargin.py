"""
Plotter for margin of safety.\n
\n
This plotter takes an array of y values and corresponding applied stress values (alongside other parameters) to generate the plots.\n
Multiple plots can be generated in subplots by passing 2D arrays.\n
\n
The parameters work as follows:\n
-yVals: numpy array, each row contains the y values for one subplot. Inhomogeneous arrays are allowed. Example:\n
        np.array([[y11, y12, y13], [y21, y22]])\n
-sigmaAppliedVals: numpy array, each row contains the aoplied stress values for one subplot. Inhomogeneous arrays are allowed. Example:\n
        np.array([[s11, s12, s13], [s21, s22]])\n
-sigma Fail: Failure stress, single number\n
-n: safety factor, single number\n
-dimSubplots: tuple, containing dimensions of how you want your subplots. This should match the input value arrays. Example:\n
        (2, 3) -> creates 2 rows and 3 columns of subplots\n
-titles: tuple, containing the title for each of your plots, in order (left-right then down).\n
-colors: tuple, containing the graph color for each of your plots, in order (left-right then down).
"""
import matplotlib.pyplot as plt
import numpy as np
from numpy.typing import NDArray


class DimensionError(Exception):
    pass


# y values, raw applied stress values, failure stress, safety factor for applied stress
def plotFailureMargin(yVals: NDArray, sigmaAppliedVals: NDArray, sigmaFail: NDArray, n: float) -> None:
    # Check for correct parameter dimensions/types
    if yVals.shape != sigmaAppliedVals.shape:
        raise DimensionError('yVals and sigmaAppliedVals must have same length!')
                

    # Array of failure stress values to allow for array division
    safetyMarginArray = sigmaFail/sigmaAppliedVals
    
    ax, fig = plt.subplots(1, 1)        
            
    ax.set_xlabel('y [m]')
    ax.set_ylabel('Margin of Safety [-]')
    ax.grid()
                
    fig.tight_layout()
    fig.suptitle('Margins of Safety *failure mode*')
    plt.show()
    

if __name__ == '__main__':
    pass