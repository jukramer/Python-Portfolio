import numpy as np
import math
import sys
import matplotlib.backends as bke
import matplotlib.figure as fgr

import PyQt6.QtCore as qtc
import PyQt6.QtWidgets as qtw
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


################### CLASSES ######################

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Define window
        self.setWindowTitle('MDoF Vibrations Simulator')
        self.resize(1000, 700) # Set initial size

        self.solList = [] # List of all mdofcalc class instances

        # define central widget
        centralWidget = qtw.QWidget()
        centralWidgetLayout = qtw.QHBoxLayout()

        # Sidebar for controlling simulation
        sidebar = qtw.QWidget()
        self.sideBarLayout = qtw.QVBoxLayout()

        # Drop down menu for selecting #dof
        self.dofSelector = qtw.QComboBox()
        self.dofSelector.setCurrentText('2')
        self.dofSelector.addItems(['2'])

        # Initial conditions
        icContainer = QWidget()
        icLabel = qtw.QLabel('Initial conditions:')
        icContainerLayout = qtw.QVBoxLayout()
        icContainer.setLayout(icContainerLayout)
        icContainerLayout.addWidget(icLabel)
        
        self.icWidget1 = qtw.QWidget()
        self.icWidgetLayout1 = qtw.QHBoxLayout()
        self.icWidget1.setLayout(self.icWidgetLayout1)
        self.x1Label = qtw.QLabel(f'x1<sub>0</sub>:')
        self.x1Box = qtw.QLineEdit()
        self.v1Label = qtw.QLabel(f'v1<sub>0</sub>:')
        self.v1Box = qtw.QLineEdit()
        self.x1Box.setText('10')
        self.v1Box.setText('0')
        self.icWidgetLayout1.addWidget(self.x1Label)
        self.icWidgetLayout1.addWidget(self.x1Box)
        self.icWidgetLayout1.addWidget(self.v1Label)
        self.icWidgetLayout1.addWidget(self.v1Box)
        icContainerLayout.addWidget(self.icWidget1)

        self.icWidget2 = qtw.QWidget()
        self.icWidgetLayout2 = qtw.QHBoxLayout()
        self.icWidget2.setLayout(self.icWidgetLayout2)
        self.x2Label = qtw.QLabel(f'x2<sub>0</sub>:')
        self.x2Box = qtw.QLineEdit()
        self.v2Label = qtw.QLabel(f'v2<sub>0</sub>:')
        self.v2Box = qtw.QLineEdit()
        self.x2Box.setText('10')
        self.v2Box.setText('0')
        self.icWidgetLayout2.addWidget(self.x2Label)
        self.icWidgetLayout2.addWidget(self.x2Box)
        self.icWidgetLayout2.addWidget(self.v2Label)
        self.icWidgetLayout2.addWidget(self.v2Box)
        icContainerLayout.addWidget(self.icWidget2)

        # Text box for alpha and beta (rayleigh damping)
        self.rayWidget = qtw.QWidget()
        self.rayWidgetLayout = qtw.QHBoxLayout()
        self.rayLabel = qtw.QLabel('Coefficients for Rayleigh Damping:    ')
        self.aLabel = qtw.QLabel('\u03B1: ')    
        self.aBox = qtw.QLineEdit()
        self.aBox.setText('0')
        self.bLabel = qtw.QLabel('\u03B2: ')
        self.bBox = qtw.QLineEdit()
        self.bBox.setText('0')
        self.rayWidgetLayout.addWidget(self.aLabel)
        self.rayWidgetLayout.addWidget(self.aBox)
        self.rayWidgetLayout.addWidget(self.bLabel)
        self.rayWidgetLayout.addWidget(self.bBox)
        self.rayWidget.setLayout(self.rayWidgetLayout)

        # Calculate button
        calcButton = qtw.QPushButton('Calculate')
        calcButton.clicked.connect(self.calculate)

        # Configure sidebar and add elements
        self.sideBarLayout.addWidget(self.dofSelector)
        self.sideBarLayout.addWidget(icContainer)
        self.sideBarLayout.addWidget(self.rayLabel)
        self.sideBarLayout.addWidget(self.rayWidget)
        self.initMatrices()  # Initialize matrices
        self.sideBarLayout.addWidget(calcButton)
        sidebar.setLayout(self.sideBarLayout)
        self.sideBarLayout.setAlignment(qtc.Qt.AlignmentFlag.AlignTop)
        self.sideBarLayout.setAlignment(qtc.Qt.AlignmentFlag.AlignLeft)
        sidebar.setFixedWidth(240)

        # Configure matplotlib canvas
        self.canvasWidget = QWidget()
        self.canvas = mplCanvas(600, 400, 100)
        toolbar = bke.backend_qt5agg.NavigationToolbar2QT(self.canvas, self)
        self.canvasLayout = qtw.QVBoxLayout()
        self.canvasLayout.addWidget(toolbar)
        self.canvasLayout.addWidget(self.canvas)
        self.canvasWidget.setLayout(self.canvasLayout)

        # Reset button
        resetButton = QPushButton('Reset')
        resetButton.clicked.connect(self.resetButton)
        self.sideBarLayout.addWidget(resetButton)

        # Configure central widget
        centralWidgetLayout.addWidget(sidebar)
        centralWidgetLayout.addWidget(self.canvasWidget)
        centralWidget.setLayout(centralWidgetLayout)
        self.setCentralWidget(centralWidget)

        self.dofSelector.currentIndexChanged.connect(self.initMatrices) # reinitializes matrices every time new size is selected

    def initMatrices(self):
        # Table for mass matrix
        self.mWidget = qtw.QWidget()
        mWidgetLayout = qtw.QVBoxLayout()
        self.mWidget.setLayout(mWidgetLayout)
        mLabel = qtw.QLabel('Mass Matrix:') # Title label
        mWidgetLayout.addWidget(mLabel)
        self.mTable = qtw.QTableWidget()
        mWidgetLayout.addWidget(self.mTable)
        self.mTable.setRowCount(int(self.dofSelector.currentText()))
        self.mTable.setColumnCount(int(self.dofSelector.currentText()))
        # Make only diagonal cells selectable and set default values:
        for i in range(int(self.dofSelector.currentText())):
            for j in range(int(self.dofSelector.currentText())):
                if i != j:
                    self.mTable.setItem(i, j, qtw.QTableWidgetItem('0'))
                    self.mTable.item(i, j).setFlags(qtc.Qt.ItemFlag.ItemIsEnabled)
                else:
                    self.mTable.setItem(i, j, qtw.QTableWidgetItem('5'))
        # Configure table
        self.mTable.horizontalHeader().setVisible(False)
        self.mTable.verticalHeader().setVisible(False)

        # Table for stiffness matrix
        self.kWidget = qtw.QWidget()
        kWidgetLayout = qtw.QVBoxLayout()
        self.kWidget.setLayout(kWidgetLayout)
        kLabel = qtw.QLabel('Stiffness Matrix:') # Title label
        kWidgetLayout.addWidget(kLabel)
        self.kTable = qtw.QTableWidget()
        kWidgetLayout.addWidget(self.kTable)
        self.kTable.setRowCount(int(self.dofSelector.currentText()))
        self.kTable.setColumnCount(int(self.dofSelector.currentText()))
        # Configure table
        self.kTable.horizontalHeader().setVisible(False)
        self.kTable.verticalHeader().setVisible(False)
        for i in range(int(self.dofSelector.currentText())):
            for j in range(int(self.dofSelector.currentText())):
                self.kTable.setItem(i, j, qtw.QTableWidgetItem('0'))
                    
        # Table for damping matrix
        self.cWidget = qtw.QWidget()
        cWidgetLayout = qtw.QVBoxLayout()
        self.cWidget.setLayout(cWidgetLayout)
        cLabel = qtw.QLabel('Damping Matrix:') # Title label
        cWidgetLayout.addWidget(cLabel)
        self.cTable = qtw.QTableWidget()
        cWidgetLayout.addWidget(self.cTable)
        self.cTable.setRowCount(int(self.dofSelector.currentText()))
        self.cTable.setColumnCount(int(self.dofSelector.currentText()))
        # Configure table
        self.cTable.horizontalHeader().setVisible(False)
        self.cTable.verticalHeader().setVisible(False)
        self.updateCTable()
        for i in range(int(self.dofSelector.currentText())):
                for j in range(int(self.dofSelector.currentText())):
                    self.cTable.item(i, j).setFlags(qtc.Qt.ItemFlag.ItemIsEnabled)

        # Update damping matrix based on a, b, M, and K
        self.aBox.textChanged.connect(self.updateCTable)
        self.bBox.textChanged.connect(self.updateCTable)
        self.mTable.itemChanged.connect(self.updateCTable)
        self.kTable.itemChanged.connect(self.updateCTable)

        self.sideBarLayout.addWidget(self.mWidget)
        self.sideBarLayout.addWidget(self.kWidget)
        self.sideBarLayout.addWidget(self.cWidget)

    def updateCTable(self):
        try:
            for i in range(int(self.dofSelector.currentText())):
                for j in range(int(self.dofSelector.currentText())):
                    self.cTable.setItem(i, j, qtw.QTableWidgetItem(f'{float(self.aBox.text())*float(self.mTable.item(i,j).text())+float(self.bBox.text())*float(self.kTable.item(i,j).text())}'))        
        except:
            pass

    def resetButton(self):
        self.solList.clear()
        self.canvas.ax.clear()
        self.canvas.draw()

    def calculate(self):
        self.drawPlot()

    def drawPlot(self):
        self.canvas.ax.clear()
        system =  mdofCalculator(float(self.mTable.item(0,0).text()), float(self.mTable.item(1,1).text()),
                                float(self.kTable.item(0,0).text()), float(self.kTable.item(0,1).text()), float(self.kTable.item(1,0).text()), float(self.kTable.item(1,1).text()),
                                float(self.cTable.item(0,0).text()), float(self.cTable.item(0,1).text()), float(self.cTable.item(1,0).text()), float(self.cTable.item(1,1).text()),
                                float(self.x1Box.text()), float(self.x2Box.text()), float(self.v1Box.text()), float(self.v2Box.text()), float(self.aBox.text()), float(self.bBox.text()), 100, 50)
        
        self.solList.append(system)

        modalDE = system.findModalDE()

        r1 = system.solveDE(modalDE[0][0], modalDE[1][0], modalDE[2][0], modalDE[3][0], system.T)
        r2 = system.solveDE(modalDE[0][1], modalDE[1][1], modalDE[2][1], modalDE[3][1], system.T)
        print(len(r1[1]), len(r2[1]))

        t = r1[0]
        x1 = system.transformDE(r1[1], r2[1])[0]
        x2 = system.transformDE(r1[1], r2[1])[1] 
        x1Max = max(abs(x1))
        print(x1)
        print(x1Max)
        print(len(x1))
        x2Max = max(abs(x2))

        restIndices = [0]

        # Strip values when system at rest for long time
        for i, (x10, x20) in enumerate(zip(reversed(x1), reversed(x2))):
            if x10 < 0.005*x1Max and x20 < 0.005*x2Max:
                restIndices.append(i+1)
            else:
                break

        x1 = x1[:-restIndices[-1]]
        x2 = x2[:-restIndices[-1]]
        t = t[:-restIndices[-1]]
        
        self.canvas.ax.plot(t, x1, label='x1')    
        self.canvas.ax.plot(t, x2, label='x2')   
        self.canvas.ax.legend(loc='best')
               

        # Adjust axes
        try:
            self.canvas.ax.set_ylim([-max(abs(x1), abs(x2)), max(abs(x1), abs(x2))])
        except:
            pass

        self.canvas.draw()


class mplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=600, height=400, dpi=100):
        self.fig = fgr.Figure(figsize=(width, height), dpi=dpi)
        self.ax = self.fig.add_subplot(111)
        super().__init__(self.fig)
        

class mdofCalculator():
    def __init__(self, m1, m2, k11, k12, k21, k22, c11, c12, c21, c22, x1, x2, v1, v2, a, b, nSteps, T, nMatrix=2):
        self.n = nMatrix
        self.N = nSteps
        self.a = a
        self.b = b
        self.t = 0
        self.T = T
        self.dt = T/nSteps

        # Define matrices
        self.M = np.array([[m1, 0], 
                           [0, m2]]).astype(float)
        self.K = np.array([[k11, k12],
                           [k21, k22]]).astype(float)
        self.C = np.array([[c11, c12],
                           [c21, c22]]).astype(float)
        self.x0 = np.array([x1, x2]).astype(float)
        self.v0 = np.array([v1, v2]).astype(float)

    def findModalDE(self):
        # Find M^1/2 and M^-1/2 (here self.M2 and self.Mn2)
        self.M2 = np.sqrt(self.M)
        self.Mn2 = np.reciprocal(np.sqrt(self.M))
        self.Mn2[self.Mn2 == np.inf] = float(0) # replace 1/0 = inf with 0

        # Find K~ (here W)
        self.W = self.M2 @ self.K @ self.M2 

        # Find Eigenvalues and eigenvectors of W
        self.eigenval, self.eigenvec = np.linalg.eig(self.W)

        # Normalize eigenvectors, define P and L
        self.P = self.eigenvec/np.linalg.norm(self.eigenvec, axis=0)
        self.L = np.diag(self.eigenval)

        # Find S and S^-1 (here S and S1)
        self.S = self.Mn2 @ self.P 
        self.S1 = self.P.T @ self.M2

        # Find modal ICs
        self.r0 = self.S1 @ self.x0
        self.vr0 = self.S1 @ self.v0

        # Find damping coefficients
        self.c = self.a/2 * np.reciprocal(self.eigenval) + self.b*self.eigenval/2

        return self.r0, self.vr0, self.c, self.eigenval

    def solveDE(self, r0, rv0, c, w, T): # solves modal DE numerically with Symplectic Euler
        tList = [0]
        uList = [r0]
        vList = [rv0]

        t = 0
        dt = 0.0001

        def f(v, u):
            return -2*c*w*v - w**2 * u

        while t < T:
            v0, u0 = vList[-1], uList[-1]

            # Symplectic Euler: Update velocity first, then position
            v_new = v0 + f(v0, u0) * dt
            u_new = u0 + v_new * dt

            uList.append(u_new)
            vList.append(v_new)

            t += dt
            tList.append(t)

        # print(uList)

        return tList, uList

    def transformDE(self, list1, list2):
        modalSolution = np.array([list1, list2])
        print(len(modalSolution))
        print(self.P)
        print(self.Mn2)
        print(self.S)
        realSolution = self.S @ modalSolution
        
        return realSolution


if __name__ == '__main__':
    app = QApplication(sys.argv) # Define app
    window = MainWindow() # Initialize window class
    window.show() # Show window
    app.exec() # Execute app
    m = mdofCalculator(1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,100, 10000)
    de = m.solveDE(10, 0, 0.1, 3, 20)