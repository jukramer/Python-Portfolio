import colorsys as cls
import itertools as it
from numba import jit
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
    def __init__(self, vertices: np.ndarray, faces: np.ndarray, lines: np.ndarray, normals: np.ndarray, color: tuple):
        if not type(vertices) in {np.ndarray, list, tuple}:
            raise TypeError('Vertices must be of type np.ndarray, list, or tuple.')
        
        vertices = np.array(vertices)
        
        if not vertices.shape[1] == 3:
            raise ValueError('Dimension mismatch: vertices must have 3 coordinates (x,y,z)')
        
        self.vertices = vertices
        self.faces = faces
        self.lines = lines
        self.normals = normals
        self.color = color
    
    def addVertices(self, vertices: np.ndarray):
        vertices = np.array(vertices)
        vertices = np.reshape(vertices, (-1,3))
        self.vertices = np.vstack([self.vertices, vertices])
        

class Cube(Object):
    def __init__(self, pos: tuple, rotation: tuple, len: float, color: tuple):
        self.translation = list(pos)
        self.vertices = np.array(list(it.product([1, -1], repeat=3)))
        self.scaling = [len]*3
        self.rotation = list(map(np.deg2rad, rotation))
        self.color = np.array(color)
        
        self.faces = None
        self.lines = None
        self.normals = None
        self.findFaces()
        super().__init__(self.vertices, self.faces, self.lines, self.normals, self.color)
        
    def findFaces(self):
        N = self.vertices.shape[0]
        idx = (np.arange(N)[None, :] - np.arange(N)[:, None]) % N
        cycleVerticesArr = np.transpose(self.vertices[idx], (1, 2, 0))
        
        distArr = np.linalg.norm(cycleVerticesArr[:,:,1:] - np.repeat(self.vertices[:,:,None], N-1, axis=2), axis=1)
       
        # Drop one of each opposite corner pair (logically, 3 adjacent and opposite vertex give complete opposite corner vertex set)
        maxIdx = np.argsort(distArr)[0,6] + 1 # farthest (opposite) vertex to vertex 0
        minIdx = np.argsort(distArr)[0,:3] + 1 # 3 closest vertices to vertex 0
        maskIdx = np.ones(8, dtype=bool)
        maskIdx[np.union1d(maxIdx, minIdx)] = False
        verticesKept = cycleVerticesArr[0][:, maskIdx].T
        
        # Find indices of adjacent vertices to each vertex
        minIdx = np.argsort(distArr)[:,:3] # 3 closest vertices to vertex 0
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
        
        # Find lines
        lineIdx = np.array([[0,1],[0,2],[1,2]])
        self.lines = self.faces[:,lineIdx]
        
        # Find outward normals
        lineVerts = self.vertices[self.lines]
        lineVecs = lineVerts[:,:2,1,:] - lineVerts[:,:2,0,:]
        self.normals = np.cross(lineVecs[:,0,:], lineVecs[:,1,:], axis=1)
        self.normals = self.normals/np.linalg.norm(self.normals, axis=1)[:,None]
        
        # Ensure normals point outward
        normalMask = (self.vertices[self.faces][:,0] * self.normals < 0) & ~(self.vertices[self.faces][:,0] * self.normals == 0)
        self.normals[normalMask] *= -1
        
    def findNormals(self):
        # Find outward normals
        lineVerts = self.vertices[self.lines]
        lineVecs = lineVerts[:,:2,1,:] - lineVerts[:,:2,0,:]
        self.normals = np.cross(lineVecs[:,0,:], lineVecs[:,1,:], axis=1)
        self.normals = self.normals/np.linalg.norm(self.normals, axis=1)[:,None]
        
        # Ensure normals point outward
        normalMask = (self.vertices[self.faces][:,0] * self.normals < 0) & ~(self.vertices[self.faces][:,0] * self.normals == 0)
        self.normals[normalMask] *= -1
        
    def setTranslation(self, x, y, z):
        self.translation = [x,y,z]
        
    def setRotation(self, rx, ry, rz):
        self.rotation = [np.deg2rad(rx), np.deg2rad(ry), np.deg2rad(rz)]
        
    def setLen(self, len):
        self.scaling = [len]*3
    
    
class Light:
    def __init__(self, intensity, target: tuple | np.ndarray):
        self.intensity = intensity
        self.target = np.array(target)/np.linalg.norm(np.array(target))


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
        self.bgcolor = (255, 150, 150)
        
        # Initialize buffers
        self.colorBuffer = np.full((*res, 3), self.bgcolor, dtype=np.uint8)
        self.zBuffer = np.full((12, *res), np.inf, dtype=np.float32)
        
    # ============= Rasterizer
    def rasterize(self, obj: Object, light: Light, XProj,  wireframes=False):
        verticesProj, vertNDC, _= self.findProjection(obj, obj.vertices)
        facesVert = obj.vertices[obj.faces]
        facesVertProj = np.round(verticesProj[obj.faces]).astype(int) # round to ints
        facesVertNDC = vertNDC[obj.faces]
        
        normalsRot = self.rotateNormals(obj)
        colors = self.findColorLambert(obj, light, normalsRot)

        self.resetBuffers()
        
        xMins = np.amin(facesVertProj[:,:,0], axis=1)
        xMaxs = np.minimum(np.amax(facesVertProj[:,:,0], axis=1), self.res[0])
        yMins = np.amin(facesVertProj[:,:,1], axis=1)
        yMaxs = np.minimum(np.amax(facesVertProj[:,:,1], axis=1), self.res[1])
        
        dxs = xMaxs - xMins + 1
        dys = yMaxs - yMins + 1
        
        xs = np.arange(np.amax(dxs))[None,:]
        xs = xs + xMins[:,None]
        ys = np.arange(np.amax(dys))[None,:]
        ys = ys + yMins[:,None]
        
        xs = np.minimum(xs, self.res[0]-1)
        ys = np.minimum(ys, self.res[1]-1)
        
        # xs, ys = np.ogrid[xMin:xMax+1, yMin:yMax+1]
        
        V1Ps = facesVertProj[:,0,:]
        V2Ps = facesVertProj[:,1,:]
        V3Ps = facesVertProj[:,2,:]
        Z1NDCs = facesVertNDC[:,0,2][:,None,None]
        Z2NDCs = facesVertNDC[:,1,2][:,None,None]
        Z3NDCs = facesVertNDC[:,2,2][:,None,None]
        
        Ds = (V2Ps[:,1] - V3Ps[:,1]) * (V1Ps[:,0] - V3Ps[:,0]) + (V3Ps[:,0] - V2Ps[:,0]) * (V1Ps[:,1] - V3Ps[:,1])
        
        lambda1s = (((V2Ps[:,1] - V3Ps[:,1])[:,None] * (xs - V3Ps[:,0,None]))[:,:,None] + ((V3Ps[:,0,None] - V2Ps[:,0,None]) * (ys - V3Ps[:,1,None]))[:,None,:]) / Ds[:,None,None]
        lambda2s = (((V3Ps[:,1] - V1Ps[:,1])[:,None] * (xs - V3Ps[:,0,None]))[:,:,None] + ((V1Ps[:,0,None] - V3Ps[:,0,None]) * (ys - V3Ps[:,1,None]))[:,None,:]) / Ds[:,None,None]
        lambda3s = 1 - lambda1s - lambda2s
        
        Dmask = np.isclose(Ds, 0)
        
        if np.dot(Dmask, Dmask):
            lambda1s[Dmask,:,:] = -np.inf
            lambda2s[Dmask,:,:] = -np.inf
            lambda3s[Dmask,:,:] = -np.inf
            
        inTriangle = (lambda1s >= 0) & (lambda2s >= 0) & (lambda3s >= 0)
        ZNDCs = -(lambda1s*Z1NDCs + lambda2s*Z2NDCs + lambda3s*Z3NDCs)
        ZNDCs[~inTriangle] = -np.inf # set z values not inside triangle to -inf
        
        self.zBuffer[np.arange(12)[:,None,None], xs[:,:,None], ys[:,None,:]] = ZNDCs
        maxZ = self.zBuffer.max(axis=0)
        faceAtPixel = self.zBuffer.argmax(axis=0)
        covered = maxZ > -np.inf
        self.colorBuffer[covered] = colors[faceAtPixel[covered]]
        
        # self.colorBuffer[] = colors[np.argmin(ZNDCs, axis=0)]
        #TODO: find way to flatten x/y coords into color buffer
        
        
        # # self.zBuffer[xMin:xMax+1, yMin:yMax+1][zGreater & inTriangle] = ZNDCs[zGreater & inTriangle]
        # self.colorBuffer[xMin:xMax+1, yMin:yMax+1, :][zGreater & inTriangle] = colors[i,:]
        
        return 
        for i in range(obj.faces.shape[0]):
            # if i > 0:
            #     break
            # Bounding box
            xMin = np.amin(facesVertProj[i,:,0])
            xMax = np.amax(facesVertProj[i,:,0])
            yMin = np.amin(facesVertProj[i,:,1])
            yMax = np.amax(facesVertProj[i,:,1])
            dx = xMax - xMin + 1
            dy = yMax - yMin + 1
            
            # xs = np.arange(xMin, xMax+1)
            # ys = np.arange(yMin, yMax+1)
            xs, ys = np.ogrid[xMin:xMax+1,yMin:yMax+1]
            # box = np.mgrid[xMin:xMax+1, yMin:yMax+1].transpose(1,2,0) # grid containing (x,y) coords of each pixel in box
            
            # Interpolate z vals
            V1P = facesVertProj[i,0,:]
            V2P = facesVertProj[i,1,:]
            V3P = facesVertProj[i,2,:]
            Z1NDC = facesVertNDC[i,0,2]
            Z2NDC = facesVertNDC[i,1,2]
            Z3NDC = facesVertNDC[i,2,2]
            
            D = (V2P[1] - V3P[1]) * (V1P[0] - V3P[0]) + (V3P[0] - V2P[0]) * (V1P[1] - V3P[1])
                
            lambda1s = ((V2P[1] - V3P[1]) * (xs - V3P[0]) + (V3P[0] - V2P[0]) * (ys - V3P[1])) / D
            lambda2s = ((V3P[1] - V1P[1]) * (xs - V3P[0]) + (V1P[0] - V3P[0]) * (ys - V3P[1])) / D
            lambda3s = 1 - lambda1s - lambda2s
            
            if np.isclose(D, 0):
                lambda1s = np.full((dx, dy), -np.inf)
                lambda2s = np.full((dx, dy), -np.inf)
                lambda3s = np.full((dx, dy), -np.inf)
            
            ZNDCs = -(lambda1s*Z1NDC + lambda2s*Z2NDC + lambda3s*Z3NDC)
            
            # Check if points in triangle
            inTriangle = (lambda1s >= 0) & (lambda2s >= 0) & (lambda3s >= 0)
            
            # Check and update z-buffer & color buffer 
            zGreater = ZNDCs > self.zBuffer[xMin:xMax+1, yMin:yMax+1]
            self.zBuffer[xMin:xMax+1, yMin:yMax+1][zGreater & inTriangle] = ZNDCs[zGreater & inTriangle]
            self.colorBuffer[xMin:xMax+1, yMin:yMax+1, :][zGreater & inTriangle] = colors[i,:]
      
    def resetBuffers(self):
        self.colorBuffer[:,:] = self.bgcolor
        self.zBuffer.fill(-np.inf)
        
    # ============= Rendering   
    def render(self, obj: Object, light: Light):
        pg.init()
        running = True
        t=0
        
        surf = pg.surfarray.make_surface(self.colorBuffer)
        self.scr.blit(surf, (0,0))
        
        while running:
            t += 0.01
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
                
            obj.setRotation(0, t*90, t*90)
            self.rasterize(obj, light, None)
            pg.surfarray.blit_array(surf, self.colorBuffer)
            self.scr.blit(surf, (0,0))
            pg.display.update()
    
    def renderPG(self, obj: list, lights: list):
        pg.init()
        self.renderWireframe(obj, lights)
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
            
            # obj.setTranslation(-3, np.sin(t*3), -5 + 4*np.cos(t*3))
            rx, ry, rz = obj.rotation
            obj.setRotation(0, t*90, t*90)
            # obj.setTranslation(0, 0, )
            # obj.setRotation(rx, ry+0.1, rz+0.08)
            self.renderWireframe(obj, lights)
            
            pg.display.flip()
        
        xVals = xVals.transpose((0,2,1))
        tVals = np.linspace(0, 1, xVals.shape[1])
        plt.plot(tVals, xVals[:,])
        plt.show()
        
    def renderWireframe(self, obj: Object, light: Light):
        # Project vertices/lines
        XVertsProjScaled, XLinesProjScaled, clipMask, XCrossMask = self.projectWireframe(obj)
        # Project normals
        normalsRot = self.rotateNormals(obj)
        colors = self.findColorLambert(obj, light, normalsRot)
    
        # # Scale X to screen 
        # XScaled = min(self.res)*0.4*XVerts[:,:2]
        # XScaled[:,0] += self.res[0]/2
        # XScaled[:,1] += self.res[1]/2
        
        # XLinesProjScaled = min(self.res)*0.4*XLinesProj[:,:,:,:2]
        # XLinesProjScaled[:,:,:,0] += self.res[0]/2
        # XLinesProjScaled[:,:,:,1] += self.res[1]/2
        
        XFacesScaled = XVertsProjScaled[obj.faces]

        # Draw lines
        for i, row in enumerate(list(XLinesProjScaled)):
            for j, line in enumerate(list(row)):
                if XCrossMask[i,j]:
                    pg.draw.line(self.scr, 'black', *list(line))
                
        # Draw vertices
        for i, vert in enumerate(list(XVertsProjScaled)):
            if i < 4:
                color = '#FF0000'
            else: 
                color = '#00AAFF'
            # xVals = np.dstack([xVals, XScaled])
            if clipMask[i]:
                pg.draw.circle(self.scr, color, vert, 5)
                
        # Draw faces
        for i, face in enumerate(list(XFacesScaled)):
            if np.dot(normalsRot[i,:], self.cam.target) < 0: 
                pg.draw.polygon(self.scr, colors[i,:], face)

    def projectWireframe(self, obj: Object):
        XProj, _, XClip = self.findProjection(obj, obj.vertices)
        clipMask = XClip[:,-2] > -XClip[:,-1]

        # Find Projected lines
        XLines = XClip[obj.lines,:]
        XLinesZ = XLines[:,:,:,-2]
        XLinesW = XLines[:,:,:,-1]

        XLinesMask = XLinesZ + XLinesW >= 0
        XCrossMask = XLinesMask[:,:,0] ^ XLinesMask[:,:,1]

        f0 = XLinesZ[:,:,0] + XLinesW[:,:,0]
        f1 = XLinesZ[:,:,1] + XLinesW[:,:,1]
        XLinesParams = np.where(XCrossMask, f0/(f0-f1), np.nan)[:,:,None,None]
        XLinesInter0 = XLines[:,:,0:1,:] + XLinesParams*(XLines[:,:,1:2,:]-XLines[:,:,0:1,:])
        XLinesClip = np.where(~XLinesMask[:,:,0:1,None] & XCrossMask[:,:,None,None], np.dstack([XLinesInter0[:,:,0:1,:], XLines[:,:,1:2,:]]), XLines)
        XLinesClip = np.where(~XLinesMask[:,:,1:2,None] & XCrossMask[:,:,None,None], np.dstack([XLines[:,:,0:1,:], XLinesInter0[:,:,0:1,:],]), XLinesClip)
        XLinesProj = XLinesClip[:,:,:,:3]/XLinesClip[:,:,:,3:]
        
        # Scale to screen
        XLinesProjScaled = min(self.res)*0.4*XLinesProj[:,:,:,:2]
        XLinesProjScaled[:,:,:,0] += self.res[0]/2
        XLinesProjScaled[:,:,:,1] += self.res[1]/2

        return XProj, XLinesProjScaled, clipMask, XLinesMask[:,:,0] | XLinesMask[:,:,1] 

    def findProjection(self, obj: Object, X: np.ndarray):
        scaling = obj.scaling
        rotation = obj.rotation
        translation = obj.translation
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
        a = 1 # aspect ratio
        P = np.array([[1/(a*np.tan(self.cam.fov/2)), 0, 0, 0],
                        [0, 1/np.tan(self.cam.fov/2), 0, 0], 
                        [0, 0, -(self.cam.far+self.cam.near)/(self.cam.far-self.cam.near), -2*self.cam.far*self.cam.near/(self.cam.far-self.cam.near)],
                        [0, 0, -1, 0]])
        
        # Apply Projection
        XHom = np.hstack([X, np.ones_like(X[:,0])[:,None]])
        XWorld = XHom @ M.T
        XCam = XWorld @ V.T
        XClip = XCam @ P.T
        XProj = XClip[:,:3]/XClip[:,3:]
        
        # Scale XProj to screen
        XScaled = min(self.res)*0.4*XProj[:,:2]
        XScaled[:,0] += self.res[0]/2
        XScaled[:,1] += self.res[1]/2
        
        return XScaled, XProj, XClip
    
    def rotateNormals(self, obj: Object):
        rotation = obj.rotation
        
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
        
        normalsWorld = obj.normals @ R[:3, :3].T
        
        return normalsWorld

    def findColorLambert(self, obj: Object, light: Light, normals: np.ndarray):
        return obj.color[None,:] * light.intensity * np.maximum(0, -normals @ light.target.T)[:,None]

# ========================= FUNCTIONS ==========================
def main():
    light = Light(1, (0, 0, -1))
    cam = Cam((0,0,0), (0,0,-1), (0,1,0), 90, 0.1, 50)
    render = Render((1000, 800), cam)
    cube3 = Cube((0,0,-5), (45,30,90), 2, (255,0,0))
    
    render.render(cube3, light)
    

if __name__ == '__main__':
    main()