import numpy as np
import matplotlib.figure as fgr

import PyQt6.QtCore as qtc
import PyQt6.QtWidgets as qtw
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.ticker import MultipleLocator, AutoMinorLocator

panelList = []

########### CLASSES ##################

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('MOI Calculator')
        self.resize(1000, 700) # Set initial size

        self.Ixx = 0
        self.Iyy = 0
        self.Ixy = 0
        self.Cx = 0
        self.Cy = 0

        # Create UI next to canvas
        # self.uiElement = memberWidgets()
        self.memberList = []
        memberWidget1 = memberWidgets(1)
        self.memberList.append(memberWidget1)

        # Create instance of matplotlib canvas
        self.canvas = mplCanvas(600, 400, 100)
        self.drawPanels()

        # Central widget
        central_widget = QWidget()
        sideBar = QWidget()
        self.layout = qtw.QHBoxLayout()
        self.sidebarLayout = qtw.QVBoxLayout()
        sideBar.setLayout(self.sidebarLayout)
        sideBar.setMinimumWidth(300)
        self.sidebarLayout.setAlignment(qtc.Qt.AlignmentFlag.AlignTop)

        # Scrollable area for sidebar
        self.scrollWidget = qtw.QScrollArea()
        self.scrollWidget.setWidget(sideBar)
        self.scrollWidget.setWidgetResizable(True)  # Ensure content resizes properly
        self.scrollWidget.setHorizontalScrollBarPolicy(qtc.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scrollWidget.setVerticalScrollBarPolicy(qtc.Qt.ScrollBarPolicy.ScrollBarAsNeeded) # horizontal scrollbar
        self.scrollWidget.setMinimumWidth(300)

        # Widget to display I and C position
        self.moiWidget = QWidget()
        self.moiWidgetLayout = qtw.QGridLayout()
        self.ixxLabel = qtw.QLabel(f'Ixx: {self.Ixx}')
        self.iyyLabel = qtw.QLabel(f'Iyy: {self.Iyy}')
        self.ixyLabel = qtw.QLabel(f'Ixy: {self.Ixy}')
        self.cxLabel = qtw.QLabel(f'Cx: {self.Cx}')
        self.cyLabel = qtw.QLabel(f'Cy: {self.Cy}')
        self.updateButton = qtw.QPushButton('Update')
        self.updateButton.clicked.connect(self.recalc)

        # Make labels highlightable and change cursor when hovering
        self.ixxLabel.setTextInteractionFlags(qtc.Qt.TextInteractionFlag.TextSelectableByMouse)
        self.iyyLabel.setTextInteractionFlags(qtc.Qt.TextInteractionFlag.TextSelectableByMouse)
        self.ixyLabel.setTextInteractionFlags(qtc.Qt.TextInteractionFlag.TextSelectableByMouse)
        self.cxLabel.setTextInteractionFlags(qtc.Qt.TextInteractionFlag.TextSelectableByMouse)
        self.cyLabel.setTextInteractionFlags(qtc.Qt.TextInteractionFlag.TextSelectableByMouse)
        self.ixxLabel.setCursor(qtc.Qt.CursorShape.IBeamCursor)
        self.iyyLabel.setCursor(qtc.Qt.CursorShape.IBeamCursor)
        self.ixyLabel.setCursor(qtc.Qt.CursorShape.IBeamCursor)
        self.cxLabel.setCursor(qtc.Qt.CursorShape.IBeamCursor)
        self.cyLabel.setCursor(qtc.Qt.CursorShape.IBeamCursor)

        # Same for the updateButton
        self.updateButton.setCursor(qtc.Qt.CursorShape.PointingHandCursor)

        # Add widgets to layout
        self.moiWidgetLayout.addWidget(self.ixxLabel, 0, 0)
        self.moiWidgetLayout.addWidget(self.iyyLabel, 0, 1)
        self.moiWidgetLayout.addWidget(self.ixyLabel, 0, 2)
        self.moiWidgetLayout.addWidget(self.cxLabel, 1, 0)
        self.moiWidgetLayout.addWidget(self.cyLabel, 1, 1)
        self.moiWidgetLayout.addWidget(self.updateButton, 1, 2)

        # Add widget to sidebar
        self.moiWidget.setLayout(self.moiWidgetLayout)
        self.sidebarLayout.addWidget(self.moiWidget)

        # Add member button
        self.addButton = QPushButton('New Member')
        self.addButton.clicked.connect(self.addMember)
        self.addButton.setCursor(qtc.Qt.CursorShape.PointingHandCursor) # pointing hand when hovering over button
        self.memberList.append(self.addButton)

        # Add memberwidgets
        for memberWidget in self.memberList:
            self.sidebarLayout.addWidget(memberWidget)

        self.layout.addWidget(self.scrollWidget)
        self.layout.addWidget(self.canvas)

        self.layout.setSpacing(15)
        central_widget.setLayout(self.layout)

        self.setCentralWidget(central_widget)

    def drawPanels(self):
        xVals, yVals = [], []
        self.canvas.ax.clear()
        for panel in panelList:
            try:
                # Generate points on panel
                x = np.linspace(panel.x1, panel.x2, 2)
                y = np.linspace(panel.y1, panel.y2, 2)

                xVals.append(panel.x1)
                xVals.append(panel.x2)
                yVals.append(panel.y1)
                yVals.append(panel.y2)

                # Plot panels
                self.canvas.ax.plot(x, y, color='black', linewidth=panel.t)

            except:
                # This try except statement prevents funky panels from breaking the program
                pass

        if len(xVals) == 0:
            xVals.append(0)
        if len(yVals) == 0:
            yVals.append(0)

        # Calculate limits to ensure square plot AR
        xLims = np.array([min(xVals)-5, max(xVals)+5])
        yLims = np.array([min(yVals)-5, max(yVals)+5])

        if abs(xLims[0] - xLims[1]) > abs(yLims[0] - yLims[1]):
            d = abs(abs(xLims[0] - xLims[1]) - abs(yLims[0] - yLims[1]))
            yLims = yLims + np.array([-d/2, d/2])

        elif abs(yLims[0] - yLims[1]) > abs(xLims[0] - xLims[1]):
            d = abs(abs(xLims[0] - xLims[1]) - abs(yLims[0] - yLims[1]))
            xLims = xLims + np.array([-d/2, d/2])

        # Stylize canvas
        self.canvas.ax.grid() # Generate grid
        self.canvas.ax.xaxis.set_major_locator(MultipleLocator(10)) # Major units of 10
        self.canvas.ax.xaxis.set_minor_locator(AutoMinorLocator(2)) # Minor units of 2
        self.canvas.ax.yaxis.set_major_locator(MultipleLocator(10))
        self.canvas.ax.xaxis.set_minor_locator(AutoMinorLocator(2))
        self.canvas.ax.set_aspect('equal') # Force equal aspect ratio between units
        self.canvas.ax.set_xlim(xLims)
        self.canvas.ax.set_ylim(yLims)

        # Plot centroid
        cx, cy = calcCentroid()
        print(cx, cy)
        self.canvas.ax.scatter(cx, cy, color='red', linewidth=5, zorder=1000)

        # Show Inertias

        self.canvas.draw()

    def addMember(self):
        global panelList
        member = memberWidgets(len(self.memberList))

        self.memberList.insert(-1, member)
        for memberWidget in self.memberList:
            self.sidebarLayout.addWidget(memberWidget)
            self.layout.setAlignment(qtc.Qt.AlignmentFlag.AlignTop)

        print('ello')

    def update(self):
        for memberWidget in self.memberList:
            self.sidebarLayout.addWidget(memberWidget)
            self.layout.setAlignment(qtc.Qt.AlignmentFlag.AlignTop)

    def recalc(self):
        try:
            print(self.memberList)
            panelList.clear()
            for member in self.memberList:
                print('sup')
                x1, x2 = float(member.x1Box.text()), float(member.x2Box.text())
                y1, y2 = float(member.y1Box.text()), float(member.y2Box.text())
                t = float(member.tBox.text())
                panel = PanelObject(t, x1, y1, x2, y2)
                panelList.append(panel)
                self.drawPanels()
                print(member)

            print('hello')

        except:
            print(panelList)
            self.Cx, self.Cy = calcCentroid()
            self.Ixx, self.Iyy, self.Ixy = calcFinalInertia()
            print(self.Ixx, self.Iyy, self.Ixy, self.Cx, self.Cy)

            #Update labels
            self.ixxLabel.setText(f'Ixx: {round(self.Ixx, 2)}')
            self.iyyLabel.setText(f'Iyy: {round(self.Iyy, 2)}')
            self.ixyLabel.setText(f'Ixy: {round(self.Ixy, 2)}')
            self.cxLabel.setText(f'Cx: {round(self.Cx, 2)}')
            self.cyLabel.setText(f'Cy: {round(self.Cy, 2)}')

            print('ow')


class mplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=600, height=400, dpi=100):
        self.fig = fgr.Figure(figsize=(width, height), dpi=dpi)
        self.ax = self.fig.add_subplot(111)
        super().__init__(self.fig)


class memberWidgets(qtw.QWidget):
    def __init__(self, n):
        super().__init__()

        self.layout = qtw.QGridLayout()
        self.n = n
        self.type = 0 # rectangle

        # Title
        self.title = qtw.QLabel(f'Member #{n}')
        self.layout.addWidget(self.title, 0, 0)

        # Dropdown box for selecting type (currently only rectangular)
        self.typeWidget = QWidget()
        self.typeLabel = qtw.QLabel('Type:')
        self.typeSelector = qtw.QComboBox()
        self.typeSelector.addItem('Rectangular')
        self.typeSelector.setCursor(qtc.Qt.CursorShape.PointingHandCursor)  # pointing hand when hovering over button
        self.layout.addWidget(self.typeLabel, 1, 0)
        self.layout.addWidget(self.typeSelector, 1, 1)
        self.typeSelector.setStyleSheet(""" 
            QComboBox {
                padding: 4px; /* Adjust padding as needed */
            }
            QComboBox QAbstractItemView {
        padding: 2px; /* Padding inside the drop-down list */
        }
            """)

        # Boxes for positions
        if self.type == 0:
            self.x1Label = qtw.QLabel('x1:')
            self.x1Box = qtw.QLineEdit()
            self.layout.addWidget(self.x1Label, 2, 0)
            self.layout.addWidget(self.x1Box, 2, 1)

            self.x2Label = qtw.QLabel('x2:')
            self.x2Box = qtw.QLineEdit()
            self.layout.addWidget(self.x2Label, 3, 0)
            self.layout.addWidget(self.x2Box, 3, 1)

            self.y1Label = qtw.QLabel('y1:')
            self.y1Box = qtw.QLineEdit()
            self.layout.addWidget(self.y1Label, 2, 2)
            self.layout.addWidget(self.y1Box, 2, 3)

            self.y2Label = qtw.QLabel('y2:')
            self.y2Box = qtw.QLineEdit()
            self.layout.addWidget(self.y2Label, 3, 2)
            self.layout.addWidget(self.y2Box, 3, 3)

            self.tLabel = qtw.QLabel('t:')
            self.tBox = qtw.QLineEdit()
            self.layout.addWidget(self.tLabel, 4, 0)
            self.layout.addWidget(self.tBox, 4, 1)

        # Delete button
        self.delButton = qtw.QPushButton('Remove')
        self.delButton.clicked.connect(self.removeMember)
        self.delButton.setCursor(qtc.Qt.CursorShape.PointingHandCursor)  # pointing hand when hovering over button
        self.layout.addWidget(self.delButton, 5,0)

        self.layout.setAlignment(qtc.Qt.AlignmentFlag.AlignTop)
        self.setLayout(self.layout)

    def updateType(self):
        self.type = self.typeSelector.currentIndex()

    def removeMember(self):
        widget.memberList.pop(widget.memberList.index(self))
        widget.sidebarLayout.removeWidget(self)


class PanelObject:
    def __init__(self, thickness, x1, y1, x2, y2):
        self.t = thickness
        self.b = np.sqrt((x2-x1)**2+(y2-y1)**2)
        self.A = self.b*self.t
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
        self.xc = self.x1+(self.x2-self.x1)/2
        self.yc = self.y1+(self.y2-self.y1)/2
        self.theta = self.calcTheta()
        self.Ixx = self.calcI()[0]
        self.Iyy = self.calcI()[1]
        self.Ixy = self.calcI()[2]
        self.pxx = 0
        self.pyy = 0
        self.pxy = 0

    def calcTheta(self):
        if abs(self.x1 - self.x2) < 0.001:
            return 0
        else:
            return np.arctan2((self.y2 - self.y1), (self.x2 - self.x1))

    def calcI(self):
        # Calculate moments of inertia
        Ixx = (self.t*self.b**3*np.sin(self.theta)**2)/12
        Iyy = (self.t * self.b ** 3 * np.cos(self.theta) ** 2) / 12
        Ixy = (self.t * self.b ** 3 * np.sin(self.theta) * np.cos(self.theta)) / 12

        return Ixx, Iyy, Ixy
    

################ FUNCTIONS ######################

def calcCentroid():
    global panelList

    Qx, Qy, A = 0, 0, 0

    for panel in panelList:
        Qx += panel.xc*panel.A
        Qy += panel.yc*panel.A
        A += panel.A

    try:
        xc = Qx/A
        yc = Qy/A

        return xc, yc

    except:
        return 0, 0


def calcFinalInertia():
    global panelList
    Ixx, Iyy, Ixy = 0, 0, 0
    xc, yc = calcCentroid()
    print(xc, yc)

    for panel in panelList:
        panel.pxx = panel.A*(panel.yc - yc)**2
        panel.pyy = panel.A*(panel.xc - xc)**2
        panel.pxy = panel.A*(panel.xc - xc)*(panel.yc - yc)
        Ixx += panel.Ixx + panel.pxx
        Iyy += panel.Iyy + panel.pyy
        Ixy += panel.Ixy + panel.pxy

    return Ixx, Iyy, Ixy


if __name__ == '__main__':
    app = QApplication([]) # Define app
    widget = MainWindow() # Initialize window class
    widget.show() # Show window
    app.exec() # Execute app

    while True:
        widget.update()