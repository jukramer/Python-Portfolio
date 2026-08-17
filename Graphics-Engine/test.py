import numpy as np

print(np.arange(1,10).reshape((3,3)))
print(np.arange(1,10).reshape((3,3))[np.triu_indices(3)])

print(np.triu_indices(3))
