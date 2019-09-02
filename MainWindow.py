import os, sys

from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *

from EstimatorFactory import *
from Estimators import *
from InputController import *

class CNCMainWindow(QMainWindow):

    def __init__(self, context, factory):
        super(CNCMainWindow, self).__init__()
        self.gText = ''     # holds input gcode file text
        self.cmds = []      # holds individual lines
        self.context = context
        self.gcodeFactory = factory
        self.procController = None      # set when button pressed

        self.setWindowTitle("FreeCAD GCode Estimator")

        # Set the central widget of the Window. Widget will expand
        # to take up all the space in the window by default.
        host = QWidget()        #hosts the layouts
        layoutGrid = QGridLayout()

        #targets
        tLabel = QLabel('GCode Target System')
        tLabel.show()
        layoutGrid.addWidget(tLabel, 0, 0)
        bGrbl = QRadioButton("Grbl")
        bGrbl.setChecked(True)
        bGrbl.show()
        layoutGrid.addWidget(bGrbl, 1, 0)
        bLinuxCNC = QRadioButton("LinuxCNC")
        bLinuxCNC.show()
        layoutGrid.addWidget(bLinuxCNC, 2, 0)
        self.targetGroup = QButtonGroup()
        self.targetGroup.addButton(bGrbl, 1)
        self.targetGroup.addButton(bLinuxCNC, 2)
        self.targetGroup.buttonClicked.connect(self.targetChosen)
        spc = QLabel(' ')
        layoutGrid.addWidget(spc, 3, 0) # layoutInputs.addSpacerItem(spc)

        #button to locate file
        btnFindFile = QPushButton('Locate GCode File')
        btnFindFile.show()
        btnFindFile.clicked.connect(self.getFile)
        layoutGrid.addWidget(btnFindFile, 4, 0)
        layoutGrid.addWidget(spc, 5, 0) # layoutInputs.addSpacerItem(spc)

        #button to run estimator
        self.btnEstimate = QPushButton('Estimate')
        self.btnEstimate.show()
        self.btnEstimate.setEnabled(False)   # must have read file to enable this
        self.btnEstimate.clicked.connect(self.estimate)
        layoutGrid.addWidget(self.btnEstimate, 6, 0)
        layoutGrid.addWidget(spc, 7, 0)  # layoutInputs.addSpacerItem(spc)

        # option to create log file
        self.chkLog = QCheckBox('Create log file')
        self.chkLog.show()
        layoutGrid.addWidget(self.chkLog, 8, 0)
        self.chkLog.setEnabled(False)

        # outputs
        self.outFileName = QLabel('GCode input file: ',parent=host)
        self.outFileName.show()
        layoutGrid.addWidget(self.outFileName, 0, 1)
        self.outFileLines = QLabel('Line count: 99999',parent=host)
        self.outFileLines.show()
        layoutGrid.addWidget(self.outFileLines, 1, 1)
        self.outOpCount = QLabel('Opcodes processed: 0', parent=host)
        self.outOpCount.show()
        layoutGrid.addWidget(self.outOpCount, 2, 1)
        self.outTime = QLabel('Estimated time (secs): ', parent=host)
        self.outTime.show()
        layoutGrid.addWidget(self.outTime, 3, 1)

        # menu bar and file menu (for 'exit' item)
        # menubar processing
        mbar = QMenuBar()
        self.setMenuBar(mbar)
        fMenu = QMenu("File")

        exit_action = QAction("Exit",self)
        exit_action.setShortcut(QKeySequence("Ctl-Q"))
        exit_action.triggered.connect(self.exitCB)
        fMenu.addAction(exit_action)

        host.show()
        self.setCentralWidget(host)        #label

        mbar.addMenu(fMenu)
        #layoutTop.addChildLayout(layoutInputs)
        #layoutTop.addChildLayout(layoutOutputs)
        host.setLayout(layoutGrid)

    def getFile(self):
        fDlog = QFileDialog(self, 'Load GCode File', '', 'GCode(*.txt *.nc *.ngc *.gcode)')
        fDlog.setViewMode(QFileDialog.Detail)
        #fDlog.setFileMode(QFileDialog.ExistingFile)
        if fDlog.exec_():
            self.inFileName = fDlog.selectedFiles()
            try:
                f = QFile(self.inFileName[0])
                if f.open(QIODevice.ReadOnly):
                    self.gcodepath = QFileInfo(f).dir()         # directory of file
                    self.gcodefile = QFileInfo(f).fileName()    # just filename
                    ins = QTextStream(f)
                    while ins.atEnd() is not True:
                        aline = ins.readLine()
                        self.cmds.append(aline)
                        self.gText += aline         # cumulative total text file
                    f.close()
                self.outFileName.setText('GCode input file: ' + self.inFileName[0])
                self.outFileName.show()
                self.btnEstimate.setEnabled(True)
            except Exception as e:
                msg = str(e)
                tMsg = msg + ' '    # place for breakpoint
        # open & read input file

    def targetChosen(self, btnID):
        self.aa = 1     #dummy

    # Core of the entire application :)
    def estimate(self):
        dologging = self.chkLog.isChecked()
        if dologging:
            fn = self.gcodefile.split('.')[0]       # name w/o extension
            logpath = os.path.join(self.gcodepath, fn + '_log.txt')
            self.context.setLogFile(logpath)

        b = self.targetGroup.checkedId()
        if b == 1:
            self.context.setTarget(GcodeTarget.Grbl)
        elif b == 2:
            self.context.setTarget(GcodeTarget.LinuxCNC)
        else:
            self.context.setTarget(GcodeTarget.NoTarget)

        self.procController = InputController(self.context, self.cmds)
        self.outFileLines.setText('Line count: ' + str(len(self.cmds)))   # update user a little
        self.outFileLines.show()
        try:
            if dologging:
                with (logpath, 'u') as lFile:
                    self.context.setOpenLogFile(lFile)
                    self.procController.buildEstimators()
                    self.procController.runEstimators()
                    self.context.setOpenLogFile(None)
            else:
                self.procController.buildEstimators()
                self.procController.runEstimators()
            opCount = len(self.procController.estimators)
            self.outOpCount.setText('Opcodes processed: ' + str(opCount))
            self.outOpCount.show()
            t = self.context.getDuration()
            self.outTime.setText('Estimated time (secs): {5.4f}'.format(t))
        except Exception as e:
            s = str(e)

    def exitCB(self):
        QCoreApplication.quit()

