import itertools as it
import matplotlib.pyplot as plt
import numpy as np
import pygame as pg

RX = lambda x: np.array([[1, 0, 0],
                         [0, np.cos(x), -np.sin(x)],
                         [0, np.sin(x), np.cos(x)]])

RY = lambda x: np.array([[np.cos(x), 0, np.sin(x)],
                         [0, 1, 0],
                         [-np.sin(x), 0, np.cos(x)]])

RZ = lambda x: np.array([[np.cos(x), -np.sin(x), 0],
                         [np.sin(x), np.cos(x), 0],
                         [0, 0, 1]])

FRAMERATE = 60

# =========================== CLASSES ============================
# ============== GEOMETRY
class Object:
    def __init__(self, vertices: np.ndarray, faces: np.ndarray):
        if not type(vertices) in {np.ndarray, list, tuple}:
            raise TypeError('Vertices must be of type np.ndarray, list, or tuple.')
        
        vertices = np.array(vertices)
        
        if not vertices.shape[1] == 3:
            raise ValueError('Dimension mismatch: vertices must have 3 coordinates (x,y,z)')
        
        self.vertices = vertices
        self.faces = faces
        
    def addVertices(self, vertices: np.ndarray):
        vertices = np.array(vertices)
        vertices = np.reshape(vertices, (-1,3))
        self.vertices = np.vstack([self.vertices, vertices])
        

class Cube(Object):
    def __init__(self, vertices: np.ndarray):
        if vertices.shape[0] != 8:
            raise ValueError('A cube must have 8 vertices.')
        
        self.vertices = vertices
        self.faces = None
        self.findFaces()
        super().__init__(self.vertices, self.faces)
        
    def findFaces(self):
        N = self.vertices.shape[0]
        idx = (np.arange(N)[None, :] - np.arange(N)[:, None]) % N
        cycleVerticesArr = np.transpose(self.vertices[idx], (1, 2, 0))
        
        distArr = np.linalg.norm(cycleVerticesArr[:,:,1:] - np.repeat(self.vertices[:,:,None], N-1, axis=2), axis=1)
        
        # Drop one of each opposite corner pair
        maxIdx = np.argsort(distArr)[0,6] + 1
        minIdx = np.argsort(distArr)[0,:3] + 1
        maskIdx = np.ones(8, dtype=bool)
        maskIdx[np.union1d(maxIdx, minIdx)] = False
        verticesKept = cycleVerticesArr[0][:, maskIdx].T
        
        minIdx = np.argsort(distArr)[:,:3]
        adjacentVertices = np.dstack([self.vertices[:,:,None],
                                      cycleVerticesArr[:,:,1:][np.arange(0, N)[:,None,None], np.arange(0, 3)[None,:,None], minIdx[:,None,:]]])
        
        matchesKept = np.all(self.vertices[:,None,:] == verticesKept[None,:,:], axis=-1)
        idxKept = np.argmax(matchesKept, axis=0)
        
        matchesAdjacent = np.all(adjacentVertices.transpose(0, 2, 1)[:, :, None, :] == self.vertices[None, None, :, :], axis=-1)
        adjacentIndices = np.argmax(matchesAdjacent, axis=2)
        
        adjacentVerticesKept = adjacentIndices[idxKept,:]
        idxFaces = np.array(list(it.combinations(range(adjacentVerticesKept.shape[1]), 3)))
        self.faces = adjacentVerticesKept[:,idxFaces[:-1]].reshape(-1,3)
        self.faces = self.faces[self.faces[:,0].argsort()]

# ============== RENDERING
class Cam:
    def __init__(self, pos: np.ndarray, target: np.ndarray, fov: float | int, near: float, up=np.array([0,1,0])):
        self.pos = pos
        self.target = np.array(target)/np.linalg.norm(target)
        self.fov = fov
        self.near = near
        self.up = np.array(up)
        self.right = np.cross(self.target, self.up)
            

class Render:
    def __init__(self, res: list | tuple, cam: Cam):
        if not (type(res) in {list, tuple} or len(res) == 2):
            raise ValueError('Resolution must be tuple of two values.')
        
        self.scr = pg.display.set_mode(res)
        self.clock = pg.time.Clock()
        self.res = res
        self.cam = cam
              
    def renderWireframe(self, obj: Object):
        X = self.findProjection(obj)[:,:2] 
        
        # Scale X to screen
        XScaled = min(self.res)*0.4*X
        XScaled[:,0] += self.res[0]/2
        XScaled[:,1] += self.res[1]/2
        print(XScaled)
        
        pg.init()
        running = True
        theta = np.pi/800
        while running:
            self.clock.tick(FRAMERATE)
            keys = pg.key.get_pressed()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                    pg.quit()
            if keys[pg.K_ESCAPE]:
                running = False
                pg.quit()
            if keys[pg.K_SPACE]:
                theta = 0
            if keys[pg.K_c]:
                theta = np.pi/800
            if keys[pg.K_x]:
                theta = -np.pi/800
            
            self.scr.fill('#FFFFFF')
            
            # Spin cube
            X = self.findProjection(obj)[:,:2] 
        
            # Scale X to screen 
            XScaled = min(self.res)*0.4*X
            XScaled[:,0] += self.res[0]/2
            XScaled[:,1] += self.res[1]/2
            obj.vertices = obj.vertices @ RX(theta).T
            # obj.vertices = obj.vertices @ RX(theta).T
            
            # Draw lines
                
            # Draw vertices
            for vert in list(XScaled):
                pg.draw.circle(self.scr, '#FF0000', vert, 5)
                
            pg.display.flip()

        
    def findProjection(self, obj: Object):
        X = np.hstack([obj.vertices, np.ones((obj.vertices.shape[0], 1))])
        P = np.array([[self.cam.near, 0, 0, 0],
                      [0, self.cam.near, 0, 0],
                      [0, 0, 1, 0],
                      [0, 0, 1, 0]])
        XProj = X @ P.T
        
        return XProj[:,:3]/np.tile(XProj[:,3], (3,1)).T

# ========================= FUNCTIONS ==========================
def main():
    # cam = Cam(np.array([0, 0, 0]), [0, 1, 0], 30, 1, up = [0, 0, 1])
    # obj1 = Object(np.array([[2, 2, 2],
    #                         [2, -2, 2],
    #                         [-2, 2, 2],
    #                         [-2, -2, 2],
    #                         [2, 2, 4],
    #                         [2, -2, 4],
    #                         [-2, 2, 4],
    #                         [-2, -2, 4],]))
    # render = Render((1000, 800), cam)
    # render.renderWireframe(obj1)
    cube = Cube(np.array(list(it.product([1,-1], repeat=3))))
    

if __name__ == '__main__':
    main()