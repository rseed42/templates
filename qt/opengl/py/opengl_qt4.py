#!/usr/bin/env python
import sys
from PyQt4 import QtCore, QtGui, QtOpenGL
try:
    from OpenGL import GL
except ImportError:
    app = QtGui.QApplication(sys.argv)
    QtGui.QMessageBox.critical(None, "OpenGL 2dpainting",
            "PyOpenGL must be installed to run this example.")
    sys.exit(1)

import numpy as np
#===============================================================================
# GUI Definitions
WND_TITLE = 'OpenGL PyQt4 Template'
GOLDEN_RATIO = 1.
# Dimensions
FIELD_WIDTH = 600
FIELD_HEIGHT = FIELD_WIDTH*GOLDEN_RATIO
FIELD_SIZE = np.array([FIELD_WIDTH, FIELD_HEIGHT])
#-------------------------------------------------------------------------------
# Colors
BLACK = np.zeros(3)
GREY = np.array([0.18,0.18,0.18])
WHITE = np.ones(3)
RED = np.array([1.0,0,0])
GREEN = np.array([0,1.0,0])
BLUE = np.array([0,0,1.0])
MAGENTA = np.array([1.0,0,1.0])
ORANGE = np.array([1.0,0.5,0])
PURPLE = np.array([0.63,0.12,0.94])
LBLUE = np.array([0.68,0.85,0.9])
CYAN = np.array([0,1.0,1.0])
YELLOW = np.array([1.0,1.0,0])
BGCOL = BLACK
#-------------------------------------------------------------------------------
# GL Widget
#-------------------------------------------------------------------------------
class GLWidget(QtOpenGL.QGLWidget):
    def __init__(self, parent=None):
        super(GLWidget, self).__init__(parent)
        self.setFixedSize(*FIELD_SIZE)

    def status_message(self, s):
        self.parent().status_bar.showMessage(s)

    def initializeGL(self):
        GL.glShadeModel(GL.GL_SMOOTH)
        GL.glClearColor(BGCOL[0], BGCOL[1], BGCOL[2], 0)
        GL.glClearDepth(1.0)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glDepthFunc(GL.GL_LEQUAL)
        GL.glHint(GL.GL_PERSPECTIVE_CORRECTION_HINT, GL.GL_NICEST)

    def paintGL(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        GL.glLoadIdentity()
        GL.glTranslatef(0.0, 0.0, -1)

    def resizeGL(self, width, height):
        side = min(width, height)
        hr = 0.5*height/width
        if side < 0:
            return
        GL.glViewport((width - side) / 2, (height - side) / 2, side, side)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(0, 1.0, 0, GOLDEN_RATIO, -1.0, 1.0)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glViewport(0,0,width,height)

    def keyPressEvent(self, event):
        key = event.key()
        if key == QtCore.Qt.Key_Q:
            QtGui.qApp.quit()

        if key == QtCore.Qt.Key_Left:
            pass

        elif key == QtCore.Qt.Key_Right:
            pass

        elif key == QtCore.Qt.Key_Down:
            pass

        elif key == QtCore.Qt.Key_Up:
            pass

        elif key == QtCore.Qt.Key_Space:
            pass

#-------------------------------------------------------------------------------
# Window
#-------------------------------------------------------------------------------
class Window(QtGui.QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.glWidget = GLWidget()
        self.setCentralWidget(self.glWidget)
        self.setWindowTitle("OpenGL PyQt4 Template")
        self.glWidget.setFocusPolicy(QtCore.Qt.StrongFocus)
        # Status bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage('OpenGL PyQt4')
        # Menu
        self.menu_bar = self.menuBar()
        self.create_menus()

    def create_menus(self):
        fileMenu = self.menu_bar.addMenu('&Something')

        quitAction = QtGui.QAction('&Quit', self)
        quitAction.setShortcut('Ctrl+Q')
        quitAction.setStatusTip('Quit')
        quitAction.triggered.connect(QtGui.qApp.quit)
        fileMenu.addAction(quitAction)

#-------------------------------------------------------------------------------
# Main
#-------------------------------------------------------------------------------
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
