import colorsys as cls
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
xVals = np.zeros((8,2,1))

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
    def __init__(self, pos: np.ndarray, target: np.ndarray, up, fov: float | int, near: float, far: float):
        self.pos = pos
        self.target = np.array(target)/np.linalg.norm(target)
        self.fov = fov
        self.near = near
        self.far = far
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
           
    # ============= Rendering   
    def render(self, objs: list):
        pg.init()
        self.renderWireframe(*objs, rotation=(0, 0, np.pi/6))
        running = True
        theta = 0
        while running:
            self.clock.tick(FRAMERATE)
            theta += np.pi/600
            
            # Inputs/Events
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
            # Draw Scene   
            self.scr.fill("#FFFFFF")
            for obj in objs:
                self.renderWireframe(obj, rotation=(0, 0, theta))
            
            pg.display.flip()
        
        xVals = xVals.transpose((0,2,1))
        tVals = np.linspace(0, 1, xVals.shape[1])
        plt.plot(tVals, xVals[:,])
        plt.show()
            
    def renderWireframe(self, obj: Object, scaling=np.ones(3), rotation=np.zeros(3), translation=np.zeros(3)):
        X = self.findProjection(obj, scaling, rotation, translation)[:,:2] 
        global xVals
    
        # Scale X to screen 
        XScaled = min(self.res)*0.4*X
        XScaled[:,0] += self.res[0]/2
        XScaled[:,1] += self.res[1]/2
        # obj.vertices = obj.vertices @ RX(theta).T
        # obj.vertices = obj.vertices @ RX(theta).T
        
        # Draw lines
        for face in list(obj.faces):
            for line in list(it.combinations(face, 2)):
                pg.draw.line(self.scr, '#000000', XScaled[line[0],:], XScaled[line[1],:])
                
        # Draw vertices
        for i, vert in enumerate(list(XScaled)):
            if i < 4:
                color = '#FF0000'
            else: 
                color = '#00AAFF'
            xVals = np.dstack([xVals, XScaled])
            pg.draw.circle(self.scr, color, vert, 5)

    def findProjection(self, obj: Object, scaling: np.ndarray, rotation: np.ndarray, translation: np.ndarray):
        if len(scaling) not in {3, (3,), (3,1)}:
            raise ValueError('Scaling array must have 3 entries.')
        if len(rotation) not in {3, (3,), (3,1)}:
            raise ValueError('Rotation array must have 3 entries.')
        if len(translation) not in {3, (3,), (3,1)}:
            raise ValueError('Translation array must have 3 entries.')
        
        # Model Matrix
        S = np.array([[scaling[0], 0, 0, 0],
                      [0, scaling[1], 0, 0],
                      [0, 0, scaling[2], 0],
                      [0, 0, 0, 1]])
        
        RX = lambda x: np.array([[1, 0, 0, 0],
                                 [0, np.cos(x), -np.sin(x), 0],
                                 [0, np.sin(x), np.cos(x), 0],
                                 [0, 0, 0, 1]])
        
        RY = lambda x: np.array([[np.cos(x), 0, np.sin(x), 0],
                                 [0, 1, 0, 0],
                                 [-np.sin(x), 0, np.cos(x), 0],
                                 [0, 0, 0, 1]])
        
        RZ = lambda x: np.array([[np.cos(x), -np.sin(x), 0, 0],
                                 [np.sin(x), np.cos(x), 0, 0],
                                 [0, 0, 1, 0],
                                 [0, 0, 0, 1]])
        
        R = RZ(rotation[2]) @ RY(rotation[1]) @ RX(rotation[0])
        
        T = np.array([[1, 0, 0, translation[0]],
                      [0, 1, 0, translation[1]],
                      [0, 0, 1, translation[2]],
                      [0, 0, 0, 1]])
        
        M = T @ R @ S
        
        # View Matrix
        V = np.array([[*self.cam.right, -self.cam.right@self.cam.pos],
                      [*self.cam.up, -self.cam.up@self.cam.pos],
                      [*(-self.cam.target), self.cam.target@self.cam.pos],
                      [0, 0, 0, 1]])
        
        # Projection Matrix
        X = np.hstack([obj.vertices, np.ones((obj.vertices.shape[0], 1))])
        a = 1 # aspect ratio
        P = np.array([[1/(a*np.tan(self.cam.fov/2)), 0, 0, 0],
                      [0, 1/np.tan(self.cam.fov/2), 0, 0], 
                      [0, 0, -(self.cam.far+self.cam.near)/(self.cam.far-self.cam.near), -2*self.cam.far*self.cam.near/(self.cam.far-self.cam.near)],
                      [0, 0, -1, 0]])
        
        XHom = np.hstack([obj.vertices, np.ones_like(obj.vertices[:,0])[:,None]])
        XWorld = XHom @ M.T
        XCam = XWorld @ V.T
        XClip = XCam @ P.T
        
        return XClip[:,:3]/np.tile(XClip[:,3], (3,1)).T

# ========================= FUNCTIONS ==========================
def main():
    cam = Cam(np.array([2, 0, 4]), [0, 0, -1], [0, 1, 0], 90, 1, 50)
    # obj1 = Object(0.5*np.array([[2, 2, 2],
    #                         [2, -2, 2],
    #                         [-2, 2, 2],
    #                         [-2, -2, 2],
    #                         [2, 2, 4],
    #                         [2, -2, 4],
    #                         [-2, 2, 4],
    #                         [-2, -2, 4]]),
    #               np.array([]))
    render = Render((1000, 800), cam)
    cube1 = Cube(np.array([[1,1,1],
                        [1, -1, 1],
                        [-1,1, 3],
                        [-1,-1,1],
                        [-1,1,1],
                        [1,1, 3],
                        [1,-1, 3],
                        [-1,-1,3]]))
    
    cube2 = Cube(np.array([[2, 2, 6],
                            [2, -2, 6],
                            [-2, 2, 6],
                            [-2, -2, 6],
                            [2, 2, 2],
                            [2, -2, 2],
                            [-2, 2, 2],
                            [-2, -2, 2]]))
    
    render.render([cube2])
    

if __name__ == '__main__':
    main()