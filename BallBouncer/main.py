import numpy as np
import sys
from entities import *

import PyQt6.QtCore as qtc
import PyQt6.QtWidgets as qtw
from PyQt6.QtGui import QPainter, QPen, QColor
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget

# Define parameters
g = -200 # downwards acceleration
t = 0 # time
dt = 0.01 # time steps for simulation

################### CLASSES ######################

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Define window
        self.setWindowTitle('Ball Bouncer')
        self.resize(1000, 700) # Set initial size
        self.setMinimumSize(900, 700)

        # Timer for updating canvas
        self.timer = qtc.QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(int(dt*1000))

        # define central widget
        centralWidget = qtw.QWidget()
        centralWidgetLayout = qtw.QHBoxLayout()

        # Define ring and ball
        self.ring = Ring(0, 200, 3)

        # Canvas
        self.canvas = DrawingWidget(self.ring)

        # Sidebar for controlling simulation
        sidebar = qtw.QWidget()
        sidebarLayout = qtw.QVBoxLayout()
        coordWidget = qtw.QWidget()

        self.ballLabel = qtw.QLabel(f'Amount of balls: {len(self.canvas.ballList)}')
        sidebarLayout.addWidget(self.ballLabel)

        self.xLabel = qtw.QLabel('x:')
        self.xBox = qtw.QLineEdit()
        self.xBox.setText('0')
        self.yLabel = qtw.QLabel('y:')
        self.yBox = qtw.QLineEdit()
        self.yBox.setText('0')
        self.vxLabel = qtw.QLabel('vx0:')
        self.vxBox = qtw.QLineEdit()
        self.vxBox.setText('0')
        self.vyLabel = qtw.QLabel('vy0:')
        self.vyBox = qtw.QLineEdit()
        self.vyBox.setText('0')
        self.rLabel = qtw.QLabel('r:')
        self.rBox = qtw.QLineEdit()
        self.rBox.setText('5')

        coordWidgetLayout = qtw.QGridLayout()
        coordWidgetLayout.addWidget(self.xLabel, 0, 0)
        coordWidgetLayout.addWidget(self.xBox, 0, 1)
        coordWidgetLayout.addWidget(self.yLabel, 1, 0)
        coordWidgetLayout.addWidget(self.yBox, 1, 1)
        coordWidgetLayout.addWidget(self.vxLabel, 2, 0)
        coordWidgetLayout.addWidget(self.vxBox, 2, 1)
        coordWidgetLayout.addWidget(self.vyLabel, 3, 0)
        coordWidgetLayout.addWidget(self.vyBox, 3, 1)
        coordWidgetLayout.addWidget(self.rLabel, 4, 0)
        coordWidgetLayout.addWidget(self.rBox, 4, 1)
        coordWidget.setLayout(coordWidgetLayout)
        sidebarLayout.addWidget(coordWidget)

        addButton = qtw.QPushButton('Add Ball')
        addButton.clicked.connect(self.addButton)
        resetButton = qtw.QPushButton('Reset')
        resetButton.clicked.connect(self.resetButton)
        sidebarLayout.addWidget(addButton)
        sidebarLayout.addWidget(resetButton)

        sidebar.setLayout(sidebarLayout)
        sidebar.setMaximumWidth(200)
        sidebarLayout.setAlignment(qtc.Qt.AlignmentFlag.AlignTop)

        centralWidgetLayout.addWidget(sidebar)
        centralWidgetLayout.addWidget(self.canvas)

        centralWidget.setLayout(centralWidgetLayout)
        self.setCentralWidget(centralWidget)

    def simLoop(self):
        loop(self.ring, self.ball)

    def addButton(self):
        ball = Ball(float(self.xBox.text()), float(self.yBox.text()), float(self.vxBox.text()), float(self.vyBox.text()), r=float(self.rBox.text()))
        self.canvas.addButton(ball)
        self.ballLabel.setText(f'Amount of balls: {len(self.canvas.ballList)}')

    def resetButton(self):
        self.canvas.resetButton()
        self.ballLabel.setText(f'Amount of balls: {len(self.canvas.ballList)}')
        

class DrawingWidget(QWidget):
    def __init__(self, ring):
        super().__init__()
        self.setWindowTitle("PyQt6 Drawing Example")
        self.setGeometry(100, 100, 800, 600)
        self.ring = ring
        self.ballList = []

        self.timer = qtc.QTimer(self)
        self.timer.timeout.connect(self.simLoop)
        self.timer.start(int(dt*1000))

    def paintEvent(self, event):
        # initialize painter
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor('#262626')) #bg color
        painter.translate(int(self.width()/2), int(self.height()/2)) # move origin to center
        painter.scale(1.5, -1.5) # flip image about x axis (so y axis is upwards +)

        # draw ring
        ringColor = QColor()
        ringColor.setHsl(200, 200, 160)
        pen = QPen(ringColor, self.ring.t)
        painter.setPen(pen)
        painter.drawArc(qtc.QRect(int((self.ring.x)-(self.ring.r)), int(self.ring.y-(self.ring.r)), int(2*self.ring.r), int(2*self.ring.r)), 0, 360*16)

        # draw balls
        for i, ball in enumerate(self.ballList):
            color = QColor('#262626')
            color.setHsl(int(i*18), 200, 160)
            pen = QPen(color, ball.t)
            painter.setPen(pen)
            painter.drawEllipse(int(ball.x)-int(1/2*ball.t), int(ball.y)-int(1/2*ball.t), int(ball.t), int(ball.t))

    def simLoop(self):
        for ball in self.ballList:
            try:
                loop(self.ring, ball)
            except:
                pass
        self.update()

    def addButton(self, ball):
        self.ballList.append(ball)

    def resetButton(self):
        self.ballList.clear()
            

################### Functions #######################

def checkCollision(a, b):
    ax, ay = a.getCollisionPoint(b.x, b.y)[0:2]
    bx, by = b.getCollisionPoint()[0:2]
    d = np.sqrt((ax-bx)**2 + (ay-by)**2)

    if d <= abs(a.t + 0.95*b.t):
        return True
    else:
        return False
        

def collision(a,b):
    if (isinstance(a, Ball) and isinstance(b, Ball)) and (a.ballCollision and b.ballCollision):
        # ball ball collision:
        pass

    elif (isinstance(a, Ring) and isinstance(b, Ball)):
        # convert xy to nt coordinates (n+ radially in, t+ counterclockwise w.r.t ring)
        phi = np.arctan2(b.y-a.y, b.x-a.x)
        vn0 = b.vx*np.cos(phi) + b.vy*np.sin(phi)
        vt0 = b.vx*np.sin(phi) - b.vy*np.cos(phi) 

        vn = -vn0*b.e
        vt = vt0-a.w*a.r  
        
        # convert back to xy coords
        vx = vn*np.cos(phi) + vt*np.sin(phi)
        vy = vn*np.sin(phi) - vt*np.cos(phi)

        return vx, vy

    else:
        # in case weird objects are passed
        raise collisionException('Invalid objects (must be ring + ball or ball + ball). ball + ring is not valid.')   


def loop(ring, ball):
    global t
    vx, vy = ball.vx, ball.vy

    # Collision
    if checkCollision(ring, ball):
        vx, vy = collision(ring, ball)

    # Gravity 
    vy = vy + g*dt

    ball.vx = vx
    ball.vy = vy
   
    # update position
    ball.x = ball.x + ball.vx*dt
    ball.y = ball.y + ball.vy*dt

    # Ensure balls cannot escape ring
    phi = np.arctan2(ball.y-ring.y, ball.x-ring.x) # angle between ray from center of ring to ball and positive x axis
    if np.sqrt((ball.x-ring.x)**2 + (ball.y-ring.y)**2) > ring.r:
        ball.x = (ring.r - ring.t - ball.t)*np.cos(phi)
        ball.y = (ring.r - ring.t - ball.t)*np.sin(phi)

    t += dt


if __name__ == '__main__':
    ring = Ring(5, 200, 3)
    ball = Ball(0, 0, 0, 0)

    app = QApplication(sys.argv) # Define app
    window = MainWindow() # Initialize window class
    window.show() # Show window
    app.exec() # Execute app