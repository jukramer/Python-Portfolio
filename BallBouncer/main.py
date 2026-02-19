from entities import *
import numpy as np
import sys

import PyQt6.QtCore as qtc
from PyQt6.QtGui import QPainter, QPen, QColor
import PyQt6.QtWidgets as qtw
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

        # Define ring
        ringInitArr = ((80, 70, 60, 50, 40),
                       (200, 205, 210, 215, 220),
                       (200, 220, 240, 260, 280))
        
        self.ringList = [Ring(ringInitArr[0][i], ringInitArr[1][i], 2, 0, 20, 100, ringInitArr[2][i]) for i in range(len(ringInitArr[0]))]
        
        # Canvas
        self.canvas = DrawingWidget(self.ringList)

        # Sidebar for controlling simulation
        sidebar = qtw.QWidget()
        sidebarLayout = qtw.QVBoxLayout()
        coordWidget = qtw.QWidget()
        ringWidget = qtw.QWidget()

        self.ballLabel = qtw.QLabel(f'Amount of balls: {len(self.canvas.ballList)}')
        self.ringLabel = qtw.QLabel(f'Amount of rings: {len(self.canvas.ringList)}')
        sidebarLayout.addWidget(self.ballLabel)
        sidebarLayout.addWidget(self.ringLabel)

        # Ball initial condition input fields
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

        # Position input elements
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
        
        # Ring initial condition input fields
        # self.rLabelRing = qtw.QLabel('r:')
        # self.rBoxRing = qtw.QLineEdit()
        # self.rBoxRing.setText('150')
        # self.wLabelRing = qtw.QLabel('w:')
        # self.wBoxRing = qtw.QLineEdit()
        # self.wBoxRing.setText('0')
        # self.thetaGapLabelRing = qtw.QLabel('Gap Position: ')
        # self.thetaGapBoxRing = qtw.QLineEdit()
        # self.thetaGapBoxRing.setText('0')
        # self.lenGapLabelRing = qtw.QLabel('Gap Length: ')
        # self.lenGapBoxRing = qtw.QLineEdit()
        # self.lenGapBoxRing.setText('0')
        
        # addRingButton = qtw.QPushButton('Add Ring')
        # addRingButton.clicked.connect(self.addRingButton)
        # sidebarLayout.addWidget(addRingButton)
        
        sidebar.setLayout(sidebarLayout)
        sidebar.setMaximumWidth(200)
        sidebarLayout.setAlignment(qtc.Qt.AlignmentFlag.AlignTop)

        centralWidgetLayout.addWidget(sidebar)
        centralWidgetLayout.addWidget(self.canvas)

        centralWidget.setLayout(centralWidgetLayout)
        self.setCentralWidget(centralWidget)

    # def simLoop(self):
    #     for ring in self.ringList:
    #         ring.thetaGap += ring.w*dt
    #         loop(ring, self.ball)

    def addButton(self):
        ball = Ball(float(self.xBox.text()), float(self.yBox.text()), float(self.vxBox.text()), float(self.vyBox.text()), r=float(self.rBox.text()))
        self.canvas.addButton(ball)
        self.ballLabel.setText(f'Amount of balls: {len(self.canvas.ballList)}')
        
    def resetButton(self):
        self.canvas.resetButton()
        self.ballLabel.setText(f'Amount of balls: {len(self.canvas.ballList)}')
        

class DrawingWidget(QWidget):
    def __init__(self, ringList):
        super().__init__()
        self.setWindowTitle("PyQt6 Drawing Example")
        self.setGeometry(100, 100, 800, 600)
        self.ballList = []
        self.ringList = ringList # TODO: Figure out ring handling

        self.timer = qtc.QTimer(self)
        self.timer.timeout.connect(self.simLoop)
        self.timer.start(int(dt*1000))

    def paintEvent(self, event):
        # initialize painter
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor("#292929")) #bg color
        painter.translate(int(self.width()/2), int(self.height()/2)) # move origin to center
        painter.scale(1.5, -1.5) # flip image about x axis (so y axis is upwards +)

        # draw ring
        for ring in self.ringList:
            pen = QPen(ring.color, ring.t)
            painter.setPen(pen)
            painter.drawArc(qtc.QRect(int((ring.x)-(ring.r)), int(ring.y-(ring.r)), int(2*ring.r), int(2*ring.r)), int(ring.thetaGap*16), int((360-ring.lenGap)*16))
        
        # draw balls
        for i, ball in enumerate(self.ballList):
            color = QColor('#262626')
            color.setHsl(int(i*18), 200, 160)
            pen = QPen(color, ball.t)
            painter.setPen(pen)
            painter.drawEllipse(int(ball.x)-int(1/2*ball.t), int(ball.y)-int(1/2*ball.t), int(ball.t), int(ball.t))

    def simLoop(self):
        for ring in self.ringList:
            ring.thetaGap += ring.w*dt
            
        for ball in self.ballList:
            try:
                loop(self.ringList, ball)
            except:
                pass
                
        self.update()

    def addButton(self, ball):
        self.ballList.append(ball)

    def resetButton(self):
        self.ballList.clear()
            

################### FUNCTIONS #######################

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
        beta = np.pi/2 - phi
        
        # if ball goes through gap
        print(np.rad2deg(beta), a.thetaGap)
        if np.rad2deg(beta) > a.thetaGap%360 and np.rad2deg(beta) < (a.thetaGap + a.lenGap)%360:
            print('escape!')
            b.escaped = True
            a.color.setHsl(0, 255, 100)
            return b.vx, b.vy
        
        vn0 = b.vx*np.cos(phi) + b.vy*np.sin(phi)
        vt0 = b.vx*np.sin(phi) - b.vy*np.cos(phi) 

        vn = -vn0*b.e
        vt = vt0-a.w*a.r  
        vt = vt0
        
        # convert back to xy coords
        vx = vn*np.cos(phi) + vt*np.sin(phi)
        vy = vn*np.sin(phi) - vt*np.cos(phi)

        return vx, vy

    else:
        # in case weird objects are passed
        raise collisionException('Invalid objects (must be ring + ball or ball + ball). ball + ring is not valid.')   


def loop(ringList, ball):
    global t
    vx, vy = ball.vx, ball.vy      
    
    # Collision
    for ring in ringList:
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
    if np.sqrt((ball.x-ring.x)**2 + (ball.y-ring.y)**2) > ring.r and not ball.escaped:
        ball.x = (ring.r - ring.t - ball.t)*np.cos(phi)
        ball.y = (ring.r - ring.t - ball.t)*np.sin(phi)

    t += dt


if __name__ == '__main__':
    app = QApplication(sys.argv) # Define app
    window = MainWindow() # Initialize window class
    window.show() # Show window
    app.exec() # Execute app