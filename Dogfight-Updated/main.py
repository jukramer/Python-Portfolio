import pygame as pg
import pathlib
import math
import colorsys
import random
import numpy as np

# Global constants and variables
# Game logic
dt = 0.001 # time step
t = 0 # time
gameOver = False
running = True
winner = None
portalProb = 5 # percentage chance of portal generating per second
meteorProb = 20 # percentage chance of meteor generating per second
maxPortals = 2 
nStars = 100

# Lists to store objects
shipList = []
missileImgList = []
portalList = []
starList = []
meteorList = []

# Pygame
pg.display.set_caption("Dogfight")
pg.display.set_icon(pg.image.load(pathlib.Path(__file__).parent/'game_data_files'/'blueship.png'))
screenSize = (1200, 800)
screen = pg.display.set_mode(screenSize)
bgcolor = "black"
fps = 120

############################ CLASSES ###################################

class Missile:
    def __init__(self,x,y,theta):
        self.v = 1000
        self.x, self.y = x,y
        self.vx, self.vy = self.v * math.cos(math.radians(theta)), self.v * math.sin(math.radians(-theta))
        self.theta = theta
        self.img = missileImgList[int(theta)]
        self.surf = pg.Surface(self.img.get_size())
        self.surf.set_colorkey("black")
        self.gameOver = False
        self.surf.blit(self.img, (0, 0))
        self.alive = True
        self.timer = fps/3 # frames until explosion (one second)
        self.explosionTimer = 0
        self.exploding = False
        self.explosionSound = pg.mixer.Sound(pathlib.Path(__file__).parent/'game_data_files'/'explosion.wav')
        self.explosionImgList = []
        for i in range(4):
            img = pg.transform.scale_by(pg.image.load(pathlib.Path(__file__).parent/'game_data_files'/f'ex{i+1}.gif'), 5)
            self.explosionImgList.append(img)

    def draw(self):
        self.clock()
        self.calcPos()
        self.surf.blit(self.img, (0,0))
        screen.blit(self.surf, (self.x, self.y))

    def calcPos(self):
        # Calculate velocities
        self.vx, self.vy = self.v * math.cos(math.radians(self.theta)), self.v * math.sin(-math.radians(self.theta))
        self.x = self.x + self.vx / fps
        self.y = self.y + self.vy / fps

        # Check if out of bounds
        if self.x + self.surf.get_width() < 0 or self.x > screen.get_width() or self.y + self.surf.get_height() < 0 or self.y > screen.get_height():
            self.alive = False

    def explosion(self):
        self.exploding = True
        if self.exploding:
            if self.explosionTimer == 0:
                self.explosionSound.play()
            self.img = self.explosionImgList[int(self.explosionTimer/10)]
            self.surf.blit(self.img, (0,0))
            self.explosionTimer += 1
        if self.explosionTimer >= 40:
            self.alive = False

    def clock(self):
        self.timer -= 1
        if self.timer <= 0:
            self.exploding = True


class Ship:
    def __init__(self,x,y,theta,imgPath,leftKey,rightKey,shootKey, boostKey):
        self.x, self.y = x,y
        self.v = 200
        self.theta = theta
        self.omega = 0
        self.vx, self.vy = self.v*math.cos(math.radians(theta)), self.v*math.sin(math.radians(theta))

        self.leftKey, self.rightKey, self.shootKey, self.boostKey = leftKey, rightKey, shootKey, boostKey

        self.surfList = []
        self.missileList = []
        self.img = pg.transform.scale_by(pg.image.load(imgPath), 0.12)
        self.surf = pg.Surface(self.img.get_size())
        self.surf.set_colorkey("black")
        self.surf.blit(self.img,(0,0))
        # Store 360 rotated images in list
        for i in range(360):
            self.surfList.append(pg.transform.rotate(self.surf, i))

        self.boosting = False
        self.boostCooldown = 0
        self.boostFuel = 100

        self.missileCooldown = 0
        self.lives = 5
        self.alive = True        

    def draw(self):
        self.calcPos()
        self.theta = self.theta % 360
        self.surf = self.surfList[int(self.theta)]
        rect = self.surf.get_rect()
        rect.center = (self.x, self.y)
        screen.blit(self.surf, rect)
        self.shootMissile()
        self.missileCooldown -= 1
        
        self.boost()

    def calcPos(self):
        # Calculate velocities
        self.vx, self.vy = self.v * math.cos(math.radians(self.theta)), self.v * math.sin(-math.radians(self.theta))
        self.x = self.x + self.vx/fps
        self.y = self.y + self.vy/fps

        # Make ship reappear if it leaves the map
        if self.x + self.surf.get_width() < 0:
            self.x = screen.get_width()
        elif self.x > screen.get_width():
            self.x = -self.surf.get_width()
        elif self.y + self.surf.get_height() < 0:
            self.y = screen.get_height()
        elif self.y > screen.get_height():
            self.y = -self.surf.get_height()

        # Rotation of the ship
        if pg.key.get_pressed()[pg.key.key_code(self.leftKey)]:
            self.omega = 180
        elif pg.key.get_pressed()[pg.key.key_code(self.rightKey)]:
            self.omega = -180
        else:
            self.omega = 0
        self.theta = self.theta + self.omega/fps
        self.v = 200

    def shootMissile(self):
        # Limit number of missiles to three
        if pg.key.get_pressed()[pg.key.key_code(self.shootKey)] and len(self.missileList) < 4 and self.missileCooldown <=0:
            missile = Missile(self.x,self.y,self.theta)
            self.missileList.append(missile)
            self.missileCooldown = fps/2

    def boost(self):
        if pg.key.get_pressed()[pg.key.key_code(self.boostKey)] and self.boostCooldown == 0:
            self.v = 500
            self.boosting = True
            self.boostFuel -= 30/fps

        if self.boostFuel < 0: 
            self.boostCooldown = 5 
            self.boostFuel = 100
        
        if self.boostCooldown > 0:
            self.boostCooldown -= 1/fps

        self.boostCooldown = max(self.boostCooldown, 0)


class Meteor():
    def __init__(self):
        self.w = 50
        self.x = min(random.randint(-100, -self.w), random.randint(screenSize[0]+self.w, screenSize[0]+100))
        self.y = min(random.randint(-100, -self.w), random.randint(screenSize[1]+self.w, screenSize[1]+100))
        self.v = 250
        self.theta = np.arctan2(-self.y+screenSize[1]/2, -self.x+screenSize[0]/2) + random.randint(-30, 30)*np.pi/180 # adds +- 30 deg to angle;
        self.surfList = []
        self.img = pg.transform.scale_by(pg.image.load(pathlib.Path(__file__).parent/'game_data_files'/'meteor.png'), 0.12)
        self.surf = pg.Surface(self.img.get_size())
        self.surf.set_colorkey("black")
        self.surf.blit(self.img,(0,0))
        self.alive = True
        self.frames = 0
        # Store 360 rotated images in list
        for i in range(360):
            self.surfList.append(pg.transform.rotate(self.surf, i))

    def draw(self):
        self.surf = self.surfList[int(120*self.frames/fps)%360]
        rect = self.surf.get_rect()
        rect.center = (self.x, self.y)
        screen.blit(self.surf, rect)
        self.calcPos()
        self.frames += 1

        if abs(self.x) > 1.5*screenSize[0] and abs(self.y) > 1.5*screenSize[1]:
            meteorList.remove(self)

    def calcPos(self):
        self.vx, self.vy = self.v * math.cos(self.theta), self.v * math.sin(self.theta)
        self.x = self.x + self.vx/fps
        self.y = self.y + self.vy/fps


class Portal():
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.frames = 0
        
        # random coordinates
        self.x1, self.y1 = random.randint(0+self.w, screenSize[0]-self.w), random.randint(0+self.h, screenSize[1]-self.h)
        self.x2, self.y2 = screenSize[0]-self.x1, screenSize[1]-self.y1

        # random color hue (for hsl color)
        self.hue = random.randint(0, 360)

    def draw1(self):
        # Portal 1
        pg.draw.ellipse(screen, hslToRgb(self.hue, 0.8, 0.5), (self.x1-self.w/2, self.y1-self.h/2, self.w, self.h))
        pg.draw.ellipse(screen, hslToRgb(self.hue, 0.8, 0.6), (self.x1-0.8*self.w/2, self.y1-0.8*self.h/2, 0.8*self.w, 0.8*self.h))

        self.frames += 1
        if self.frames > fps*10:
            portalList.remove(self)

    def draw2(self):
        # Portal 2
        pg.draw.ellipse(screen, hslToRgb(self.hue, 0.6, 0.8), (self.x2-self.w/2, self.y2-self.h/2, self.w, self.h))
        pg.draw.ellipse(screen, hslToRgb(self.hue, 0.6, 0.9), (self.x2-0.8*self.w/2, self.y2-0.8*self.h/2, 0.8*self.w, 0.8*self.h))

    def teleport(self, object):
        if abs(object.x - self.x1) < 0.3*self.w and abs(object.y-self.y1) < 0.3*self.h:
            object.x = self.x2
            object.y = self.y2


############################## FUNCTIONS #####################################

def hslToRgb(h, s, l):
    r, g, b = colorsys.hls_to_rgb(h/360, l, s)
    return int(r*255), int(g*255), int(b*255)


def init():
    global screen

    # Initialize pygame
    pg.init()

    # Add images for missile rotations
    missileImg = pg.transform.scale_by(pg.image.load(pathlib.Path(__file__).parent/'game_data_files'/'missile.png'), 0.12)
    missileSurf = pg.Surface((missileImg.get_size()), pg.SRCALPHA)
    missileSurf.blit(missileImg, (0,0))
    for i in range(360):
        missileImgList.append(pg.transform.rotate(missileSurf, i))

    # Initialize ships
    redShip = Ship(screen.get_width()/2-100, screen.get_height()/2, 180, pathlib.Path(__file__).parent/'game_data_files'/'redship.png', "a", "d", "s", 'w')
    blueShip = Ship(screen.get_width() / 2 + 100, screen.get_height() / 2, 0, pathlib.Path(__file__).parent/'game_data_files'/'blueship.png', "k", ";", "l", 'o')
    shipList.append(redShip)
    shipList.append(blueShip) 
    print(shipList)

    for i in range(nStars):
        starList.append((random.randint(0, screenSize[0]), random.randint(0, screenSize[1]), random.randint(2, 5)))


def checkColliding(object1, object2):
    if object1.x < object2.x < object1.x + object1.surf.get_width() and object1.y < object2.y < object1.y + object1.surf.get_height():
        return True
    elif object2.x < object1.x < object2.x + object2.surf.get_width() and object2.y < object1.y < object2.y + object2.surf.get_height():
        return True
    else:
        return False


def endGame():
    global winner, gameOver
    font = pg.font.SysFont("Arial", 50)
    missile = Missile(0,0,0)
    # missile.explosionSound.play()
    if winner == "red":
        text = font.render("Red wins!!!!!", True, "red")
        screen.blit(text, (screen.get_width()/2 - text.get_width()/2, screen.get_height()/2.7))
    elif winner == "blue":
        text = font.render("Blue wins!!!!!", True, "blue")
        screen.blit(text, (screen.get_width()/2 - text.get_width()/2, screen.get_height()/2.7))

    text = font.render("Play again? Press SPACE", True, "white")
    screen.blit(text, (screen.get_width()/2 - text.get_width()/2, screen.get_height()*2/3))

    if pg.key.get_pressed()[pg.key.key_code("space")]:
        gameOver = False
        shipList.clear()
        meteorList.clear()
        portalList.clear()
        init()


def main():
    global gameOver, running, screen, bgcolor, fps, winner
    init()

    while running:
        # Checks for events of type QUIT
        for event in pg.event.get():
            pg.event.pump()
            if event.type == pg.QUIT:
                running = False
            if pg.key.get_pressed()[pg.K_ESCAPE]:
                running = False

        # Wipe the screen after each frame
        screen.fill(bgcolor)

        if not gameOver:
            # Draw and update entities
            for star in starList:
                pg.draw.circle(screen, 'white', star[0:2], star[2])

            for missile in shipList[0].missileList:
                missile.draw()
                if checkColliding(missile, shipList[1]):
                    missile.exploding = True
                    shipList[1].alive = False
                    winner = "red"
                    gameOver = True

                if not missile.alive:
                    shipList[0].missileList.pop(shipList[0].missileList.index(missile))

            for missile in shipList[1].missileList:
                missile.draw()
                if checkColliding(missile, shipList[0]):
                    missile.exploding = True
                    shipList[0].alive = False
                    winner = "blue"
                    gameOver = True

                if not missile.alive:
                    shipList[1].missileList.pop(shipList[1].missileList.index(missile))
                
            # splitting the portal draw functions allows for nicer effect when ship enters portal
            for portal in portalList:
                portal.draw2()
            
            for ship in shipList:
                ship.draw()

            # Random chance of generating portal every frame
            i = random.randint(0, 500)

            if i*fps < portalProb/fps and len(portalList) < maxPortals:
                portal = Portal(60, 100)
                portalList.append(portal)

            for portal in portalList:
                for ship in shipList:
                    portal.teleport(ship)
                portal.draw1()

            # Random chance of generating meteor every frame
            i = random.randint(0, 500)

            if i*fps < meteorProb/fps and len(meteorList) < 5:
                meteor = Meteor()
                meteorList.append(meteor)
            
            for meteor in meteorList:
                meteor.draw()
                if checkColliding(meteor, shipList[0]):
                    shipList[0].alive = False
                    winner = "blue"
                    gameOver = True

                if checkColliding(meteor, shipList[1]):
                    shipList[0].alive = False
                    winner = "red"
                    gameOver = True

        elif gameOver:
            endGame()

        pg.time.Clock().tick(fps)
        pg.display.flip()


if __name__ == '__main__':
    main()