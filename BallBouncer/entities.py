import math
import numpy as np

from PyQt6.QtGui import QColor


class Ball:
    def __init__(self, x, y, vx, vy, e=1, r=5, m=10, ballCollision = False):
        self.x, self.y = x, y # position
        self.vx, self.vy = vx, vy # velocity
        self.color = 'red' 
        self.t = r # radius
        self.m = m # mass
        self.hasCollided = False
        self.theta = np.arctan2(self.vy, self.vx) # velocity angle
        self.ballCollision = ballCollision
        self.e = e # coefficient of restitution
        self.escaped = False

    def getCollisionPoint(self):
        return self.x, self.y


class Ring:
    def __init__(self, w, r, t, a=0, thetaGap=0, lenGap=0, h=200):
        self.x, self.y = 0, 0 # position (usually always at 0,0)
        self.r = r
        self.t = t # thickness
        
        self.thetaGap = thetaGap # [deg] angular position of gap from positive y axis
        self.lenGap = lenGap # [deg] arc length of gap, CCW, from 
        self.w = w # [rad/s] angular velocity
        self.a = a # [rad/s^2] angular acceleration
        
        self.color = QColor()
        self.color.setHsl(int(h), 200, 160)

    def getCollisionPoint(self, x, y):
        # finds closest point on the ring to a certain point (x,y)
        if x-self.x == 0:
            if abs(y-self.r) <= abs(y+self.r):     
                return x, self.y + self.r, math.inf
            else: 
                return x, self.y - self.r, -math.inf

        # define line through circle and point
        m = (y-self.y)/(x-self.x) # slope
        b = y - m*x # y intercept

        # find intersection of line and ring
        D = ((m*b)/(1+m**2))**2 - (b**2-self.r**2)/(1+m**2) # discriminant
        xPos = [-m*b/(1+m**2) + np.sqrt(D), -m*b/(1+m**2) - np.sqrt(D)] # quadratic equation solutions in np array
        
        # choose correct x coord and find corresponding y coord. also returns line equation 
        if abs(xPos[0] - x) <= abs(xPos[1] - x):
            return xPos[0], m*xPos[0] + b, m, b
        elif abs(xPos[0] - x) > abs(xPos[1] - x): 
            return xPos[1], m*xPos[1] + b, m, b
        else: 
            return 'oops'


# Custom exception class
class collisionException(Exception):
    pass 