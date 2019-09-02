from PySide2 import QtCore, QtWidgets
from Estimators import *
from EstimatorFactory import *
from InputController import *
from MainWindow import *

import sys

app = QtWidgets.QApplication(sys.argv)
con = Context()
factory = EstimatorFactory(con)
#ic = InputController(con)

window = CNCMainWindow(con, factory)
window.show() # IMPORTANT!!!!! Windows are hidden by default.

# Start the event loop.
app.exec_()
