import numpy as np
import matplotlib.pyplot as plt
from noise import snoise2 as sn

# Parameters
width = 100
height = 100

def generateTerrain():
    terrain = np.zeros((height, width))

    for y in range(height):
        for x in range(width):
            terrain[y,x]=sn(x, y, octaves=4, persistence=0.5, lacunarity=2.0)

    return terrain

if __name__ == '__main__':
    plt.imshow(generateTerrain(), cmap='terrain')
    plt.colorbar()
    plt.show() 