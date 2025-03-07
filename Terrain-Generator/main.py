import numpy as np
import matplotlib.pyplot as plt
from noise import snoise2 as sn
import random

# Parameters
mapSize = (1000, 1000)
scale = 200

def generateTerrain(mapSize):
    terrain = np.zeros(mapSize)
    seed = random.randint(0, 1000)

    for y in range(mapSize[1]):
        for x in range(mapSize[0]):
            terrain[y,x]=sn(x/scale, y/scale, octaves=3, persistence=0.5, lacunarity=2.0, base=seed)

    return terrain

def normalize(matrix):
    a = np.min(matrix)
    b = np.max(matrix)

    if a == b:
        print('Matrix may not have the same values everywhere.')
        raise ZeroDivisionError

    return matrix*a/(b-a) + a/(a-b)

if __name__ == '__main__':
    plt.imshow(normalize(generateTerrain(mapSize)), cmap='terrain')
    plt.colorbar()
    plt.show() 


