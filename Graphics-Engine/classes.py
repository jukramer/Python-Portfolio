import colorsys as cls
import itertools as it
import matplotlib.pyplot as plt
from numba import jit
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
        self.bgcolor = (255, 255, 255)
        
        # Initialize buffers
        self.colorBuffer = np.full((*res, 3), self.bgcolor, dtype=np.uint8)
        self.zBuffer = np.full((res), np.inf, dtype=np.float32)
        
    # ============= Rasterizer
    def rasterize(self, objs: Object, light: Light, XProj,  wireframes=False) -> None:
        if not type(objs) == list:
            objs = [objs]
        
        # First object
        verticesProj, vertNDC, _= self.findProjection(objs[0], objs[0].vertices)
        facesVert = objs[0].vertices[objs[0].faces]
        facesVertProj = np.round(verticesProj[objs[0].faces]).astype(int) # round to ints
        facesVertNDC = vertNDC[objs[0].faces]
        
        normalsRot = self.rotateNormals(objs[0])
        colors = self.findColorLambert(objs[0], light, normalsRot)

        for i, obj in enumerate(objs):
            if i > 0:
                verticesProj, vertNDC, _= self.findProjection(obj, obj.vertices)
                facesVert = np.vstack([obj.vertices[obj.faces], facesVert])
                facesVertProj = np.vstack([np.round(verticesProj[obj.faces]).astype(int), facesVertProj]) # round to ints
                facesVertNDC = np.vstack([vertNDC[obj.faces], facesVertNDC])
                
                normalsRot = self.rotateNormals(obj)
                colors = np.vstack([self.findColorLambert(obj, light, normalsRot), colors])

        np.seterr(all='ignore')
        self.resetColorBuffer()
        self.resetZBuffer()
        self.colorBuffer = rasterizeJit(facesVert.shape[0], facesVert, facesVertProj, facesVertNDC, self.zBuffer, self.colorBuffer, colors)

    def resetColorBuffer(self) -> None:
        self.colorBuffer = np.full((*self.res, 3), self.bgcolor, dtype=np.uint8)
        
    def resetZBuffer(self) -> None:
        self.zBuffer = np.full((self.res), -np.inf, dtype=np.float32)
        
    # ============= Rendering   
    def render(self, objs: list[Object], light: Light) -> None:
        pg.init()
        running = True
        t=0
        
        if not type(objs) == list:
            objs = [objs]
        
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
                
            for i, obj in enumerate(objs):
                obj.setRotation(0, 90*t, 0)
                obj.setTranslation(5*np.cos(t+np.pi*i),5*np.sin(t+np.pi*i),-10)
                
            self.rasterize(objs, light, None)
            surf = pg.surfarray.make_surface(self.colorBuffer)
            surf = pg.transform.scale(surf, self.res)
            self.scr.blit(surf, (0,0))
            pg.display.update()
    
    def renderOld(self, objs: list, lights: list) -> None:
        obj = objs[0]
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
            for obj in objs:
                # obj.setTranslation(-3, np.sin(t*3), -5 + 4*np.cos(t*3))
                rx, ry, rz = obj.rotation
                obj.setRotation(0, t, t)
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
@jit(nopython=True, cache=True)
def rasterizeJit(nFaces, facesVert, facesVertProj, facesVertNDC, zBuffer, colorBuffer, colors):
    for i in range(nFaces):
        # Bounding box
        # print('---------------')
        xMin = np.amin(facesVertProj[i,:,0])
        xMax = np.amax(facesVertProj[i,:,0])
        yMin = np.amin(facesVertProj[i,:,1])
        yMax = np.amax(facesVertProj[i,:,1])

        # Interpolate z vals
        V1P = facesVertProj[i,0,:]
        V2P = facesVertProj[i,1,:]
        V3P = facesVertProj[i,2,:]
        Z1NDC = facesVertNDC[i,0,2]
        Z2NDC = facesVertNDC[i,1,2]
        Z3NDC = facesVertNDC[i,2,2]
        
        D = (V2P[1] - V3P[1]) * (V1P[0] - V3P[0]) + (V3P[0] - V2P[0]) * (V1P[1] - V3P[1])
        
        for x in range(xMin, xMax + 1):
            for y in range(yMin, yMax + 1):
                if np.isclose(D, 0):
                    lambda1 = -np.inf
                    lambda2 = -np.inf
                    lambda3 = -np.inf
                else:
                    lambda1 = ((V2P[1] - V3P[1]) * (x - V3P[0]) + (V3P[0] - V2P[0]) * (y - V3P[1])) / D
                    lambda2 = ((V3P[1] - V1P[1]) * (x - V3P[0]) + (V1P[0] - V3P[0]) * (y - V3P[1])) / D
                    lambda3 = 1 - lambda1 - lambda2
                
                if lambda1 >= 0 and lambda2 >= 0 and lambda3 >= 0:
                    zNDC = -(lambda1*Z1NDC + lambda2*Z2NDC + lambda3*Z3NDC)
                    if zNDC > zBuffer[x, y]:
                        zBuffer[x, y] = zNDC
                        colorBuffer[x, y, 0] = colors[i, 0]
                        colorBuffer[x, y, 1] = colors[i, 1]
                        colorBuffer[x, y, 2] = colors[i, 2]
        
    return colorBuffer
    

def main():
    light = Light(1, (0, 1, -1))
    cam = Cam((0,0,0), (0,0,-1), (0,1,0), 90, 0.1, 50)
    render = Render((1000, 800), cam)
    cube3 = Cube((-4,-2,-10), (45,30,90), 2, (50,120,255))
    cube4 = Cube((2,3,-7), (45,30,90), 2, (255,120,150))
    
    render.render([cube3, cube4], light)
    

if __name__ == '__main__':
    main()