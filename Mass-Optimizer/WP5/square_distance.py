import numpy as np
from parameters import *

centroid = np.array([x_centroid, y_centroid])
points = np.asarray(points)


def vertical_average_square_distance(points, centroid):
    y = points[:, 1]
    return np.mean((y - y_centroid)**2)