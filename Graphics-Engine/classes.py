import matplotlib.pyplot as plt
import numpy as np
import pygame as pg


class Object:
    def __init__(self, vertices: np.ndarray):
        if not type(vertices) in {np.ndarray, list, tuple}:
            raise TypeError('Vertices must be of type np.ndarray, list, or tuple.')
        
        vertices = np.array(vertices)
        
        if not vertices.shape[1] == 3:
            raise ValueError('Dimension mismatch: vertices must have 3 coordinates (x,y,z)')
        
        self.vertices = vertices
        
    def addVertices(self, vertices: np.ndarray):
        vertices = np.array(vertices)
        vertices = np.reshape(vertices, (-1,3))
        self.vertices = np.vstack([self.vertices, vertices])

    
class Cam:
    def __init__(self, pos: np.ndarray, target: np.ndarray, fov: float | int, near: float, up=np.array([0,1,0])):
        self.pos = pos
        self.target = target
        self.fov = fov
        self.near = near
        self.up = up
            

class Render:
    def __init__(self, res: list | tuple, cam: Cam):
        if not (type(res) in {list, tuple} or len(res) == 2):
            raise ValueError('Resolution must be tuple of two values.')
        
        self.scr = pg.display.set_mode(res)
        self.cam = cam
              
    def renderWireframe(self, obj: Object):
        X = self.findProjection(obj)[:,:2] 
        plt.scatter(X[:,0], X[:,1])
        plt.show()
        
    def findProjection(self, obj: Object):
        X = np.hstack([obj.vertices, np.ones((obj.vertices.shape[0], 1))])
        P = np.array([[self.cam.near, 0, 0, 0],
                      [0, self.cam.near, 0, 0],
                      [0, 0, 1, 0],
                      [0, 0, 1, 0]])
        XProj = X @ P.T
        
        return XProj[:,:3]/np.tile(XProj[:,3], (3,1)).T


if __name__ == '__main__':
    cam = Cam(np.array([0, 0, 0]), [0, 0, 1], 30, 1)
    obj1 = Object(np.array([[2, 2, 2],
                            [2, -2, 2],
                            [-2, 2, 2],
                            [-2, -2, 2],
                            [2, 2, 3],
                            [2, -2, 3],
                            [-2, 2, 3],
                            [-2, -2, 3],]))
    render = Render((1000, 800), cam)
    
    render.renderWireframe(obj1)