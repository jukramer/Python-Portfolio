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

# =========================== CLASSES ============================
# ============== GEOMETRY
class Object:
    def __init__(self, vertices: np.ndarray, faces: np.ndarray, lines: np.ndarray):
        if not type(vertices) in {np.ndarray, list, tuple}:
            raise TypeError('Vertices must be of type np.ndarray, list, or tuple.')
        
        vertices = np.array(vertices)
        
        if not vertices.shape[1] == 3:
            raise ValueError('Dimension mismatch: vertices must have 3 coordinates (x,y,z)')
        
        self.vertices = vertices
        self.faces = faces
        self.lines = lines
    
    def addVertices(self, vertices: np.ndarray):
        vertices = np.array(vertices)
        vertices = np.reshape(vertices, (-1,3))
        self.vertices = np.vstack([self.vertices, vertices])
        

class Cube(Object):
    def __init__(self, pos: tuple, rotation: tuple, len: float):
        self.translation = list(pos)
        self.vertices = np.array(list(it.product([1, -1], repeat=3)))
        self.scaling = [len]*3
        self.rotation = list(rotation)
        
        self.faces = None
        self.lines = None
        self.findFaces()
        super().__init__(self.vertices, self.faces, self.lines)
        
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
        
        lineIdx = np.array([[0,1],[0,2],[1,2]])
        self.lines = self.faces[:,lineIdx]
        
    def setTranslation(self, x, y, z):
        self.translation = [x,y,z]
        
    def setRotation(self, rx, ry, rz):
        self.rotation = [rx,ry,rz]
        
    def setLen(self, len):
        self.scaling = [len]*3

# ============== RENDERING
class Cam:
    def __init__(self, pos: tuple | np.ndarray, target: tuple | np.ndarray, up, fov: float | int, near: float, far: float):
        self.pos = np.array(pos)
        self.target = np.array(target)/np.linalg.norm(np.array(target))
        self.fov = np.deg2rad(fov)
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
        obj = objs[0]
        pg.init()
        self.renderWireframe(obj)
        running = True
        theta = 0
        t=0
        # return
        while running:
            t+= 0.01
            self.clock.tick(FRAMERATE)
            # theta += np.pi/600
            
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
                # obj.setTranslation(-3, np.sin(t*3), -5 + 4*np.cos(t*3))
                rx, ry, rz = obj.rotation
                obj.setRotation(0, t, t)
                obj.setTranslation(0, 0, -5+t)
                # obj.setRotation(rx, ry+0.1, rz+0.08)
                self.renderWireframe(obj)
            
            pg.display.flip()
        
        xVals = xVals.transpose((0,2,1))
        tVals = np.linspace(0, 1, xVals.shape[1])
        plt.plot(tVals, xVals[:,])
        plt.show()
            
    def renderWireframe(self, obj: Object):
        X, XLinesProj, clipMask, XCrossMask = self.findProjection(obj, obj.scaling, obj.rotation, obj.translation)
    
        # Scale X to screen 
        XScaled = min(self.res)*0.4*X[:,:2]
        XScaled[:,0] += self.res[0]/2
        XScaled[:,1] += self.res[1]/2
        
        XLinesProjScaled = min(self.res)*0.4*XLinesProj[:,:,:,:2]
        XLinesProjScaled[:,:,:,0] += self.res[0]/2
        XLinesProjScaled[:,:,:,1] += self.res[1]/2

        # Draw lines
        for i, row in enumerate(list(XLinesProjScaled)):
            for j, line in enumerate(list(row)):
                if XCrossMask[i,j]:
                    pg.draw.line(self.scr, 'black', *list(line))
                
        # Draw vertices
        for i, vert in enumerate(list(XScaled)):
            if i < 4:
                color = '#FF0000'
            else: 
                color = '#00AAFF'
            # xVals = np.dstack([xVals, XScaled])
            if clipMask[i]:
                pg.draw.circle(self.scr, color, vert, 5)

    def findProjection(self, obj: Object, scaling: np.ndarray, rotation: np.ndarray, translation: np.ndarray):
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
        # XProj = XClip[:,:3]/np.tile(XClip[:,3], (3,1)).T
        XProj = XClip[:,:3]/XClip[:,3:]
        
        clipMask = XClip[:,-2] > -XClip[:,-1]
        
        # Find Projected lines
        XLines = XClip[obj.lines,:]
        XLinesZ = XLines[:,:,:,-2]
        XLinesW = XLines[:,:,:,-1]
        
        XLinesMask = XLinesZ + XLinesW >= 0
        XStartInsideMask = XLinesMask[:,:,0]
        XCrossMask = XLinesMask[:,:,0] ^ XLinesMask[:,:,1]

        f0 = XLinesZ[:,:,0] + XLinesW[:,:,0]
        f1 = XLinesZ[:,:,1] + XLinesW[:,:,1]
        XLinesParams = np.where(XCrossMask, f0/(f0-f1), np.nan)[:,:,None,None]
        XLinesInter0 = XLines[:,:,0:1,:] + XLinesParams*(XLines[:,:,1:2,:]-XLines[:,:,0:1,:])
        XLinesInter1 = XLines[:,:,1:2,:] + XLinesParams*(XLines[:,:,0:1,:]-XLines[:,:,1:2,:])

        # XLinesClip = np.where(~XLinesMask[:,:,0:1,None] & XCrossMask[:,:,None,None],
        #                np.concatenate([XLinesInter0, XLines[:,:,1:2,:]], axis=2), XLines)
        # XLinesClip = np.where(~XLinesMask[:,:,1:2,None] & XCrossMask[:,:,None,None],
        #                np.concatenate([XLines[:,:,0:1,:], XLinesInter0], axis=2), XLinesClip)
        
        XLinesClip = np.where(~XLinesMask[:,:,0:1,None] & XCrossMask[:,:,None,None], np.dstack([XLinesInter0[:,:,0:1,:], XLines[:,:,1:2,:]]), XLines)
        XLinesClip = np.where(~XLinesMask[:,:,1:2,None] & XCrossMask[:,:,None,None], np.dstack([XLines[:,:,0:1,:], XLinesInter0[:,:,0:1,:],]), XLinesClip)
        XLinesProj = XLinesClip[:,:,:,:3]/XLinesClip[:,:,:,3:]
         
        return XProj, XLinesProj, clipMask, XLinesMask[:,:,0] | XLinesMask[:,:,1] 

# ========================= FUNCTIONS ==========================
def main():
    cam = Cam((0,0,0), (0,0,-1), (0,1,0), 90, 0.1, 50)
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
    # cube1 = Cube(np.array([[1,1,1],
    #                     [1, -1, 1],
    #                     [-1,1, 3],
    #                     [-1,-1,1],
    #                     [-1,1,1],
    #                     [1,1, 3],
    #                     [1,-1, 3],
    #                     [-1,-1,3]]))
    
    # cube2 = Cube(np.array([[2, 2, -6],
    #                         [2, -2, -6],
    #                         [-2, 2, -6],
    #                         [-2, -2, -6],
    #                         [2, 2, -2],
    #                         [2, -2, -2],
    #                         [-2, 2, -2],
    #                         [-2, -2, -2]]))
    
    cube3 = Cube((0,0,-5),(0,0,0),2)
                           
    
    render.render([cube3])
    

if __name__ == '__main__':
    main()