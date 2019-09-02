from enum import Enum
from vector3d import *
from PySide2.QtCore import *

'''
This is the basis for the classes that do the actual estimation calculation.
There is a class for each operator in the GCode definition. Where the implementation differs,
that is reflected in the code for the different target's class.
There is a set of subclasses for each target interpreter (grbl, linuxcnc, etc.),
with one source file per target for source code manageability.
Instances of the appropriate class are created by the EstimatorFactory.

The base set of classes is for the grbl target. This should minimize class propagation.
Other targets derive from it, overriding the actual calculation as needed.

Regardless of the units specified in the gcode file (if specified), this calculates in mm/sec.
Conversion is done as needed within estimators
'''

'''
The Context class holds common info needed by all estimators.
It is intended to be a singleton, created during app initialization.
Each estimator instance has a reference to the single context instance.
Usage differs slightly between 'build' andd 'run' processing.
'''

class Context():

    def __init__(self):
        self.target = GcodeTarget.NoTarget
        self.names = ['NoTarget', 'GRBL', 'LinuxCNC']
        self.lineNo = 0
        self.duration = 0.0     # in 'run' mode is cumulative time in seconds
        self.feedrate = 0.0     # in specified units; can be set by modal code
        self.units = 0          # if specified in the gcode file 0=mm/sec 1=inches/sec
        self.speed = 0.0        # spindle rotation in rpm
        self.log = False        # do we log each gcode as estimated
        self.logPath = ''       # if used, must be set by controller before running estimator list
        self.logFile = None
        # modes - there are many
        self.modeMotion = ''
        self.modeDistance = 'A'     # A=absolute R=relative
        #normal coordinates
        # this is the point *moved from*, updated by an estimator after calculating distance
        self.loc = point.Point(0,0,0)
        # alternate coordinates - not used right now
        self.altLoc = point.Point(0,0,0)

    # setters
    def setTarget(self, targ):
        self.target = targ

    ''' 0=mm/sec 1=inches/sec '''
    def setUnits(self, unit):
        self.units = unit

    def setLoc(self, newLoc):
        self.loc = newLoc

    def updateDuration(self, timeAmt):
        self.duration += timeAmt

    def updateDuration_noMove(self):
        self.duration += 0.001  # 1ms processing time

    ''' if logfile is set, logging is assumed true '''
    def setLogFilePath(self, path):
        self.logPath = path    # getters
        self.log = True

    '''
        file has ALREADY been opened in controlling process and will be closed there automatically
        reset to None when commplete for safety
    '''
    def setOpenLogFile(self, f):
        self.logFile = f

    # getters
    ''' in seconds '''
    def getDuration(self):
        return self.duration

    def getTarget(self):
        return self.target

    def getTargetName(self):
        if (self.target >= GcodeTarget.NoTarget and self.target <= GcodeTarget.LinuxCNC):
            return self.names[self.target]
        else:
            return 'Unknown Target!'

    # returns raw value
    def getLoc(self):
        return self.loc

    # guarantee value in mm, regardless of internal format
    def getLocMM(self):
        if self.units == 1:     # stored internally in inches
            return point.Point(self.loc.x*2.54, self.loc.y*2.54, self.loc.z*2.54)
        else:
            return self.loc

    def getUnits(self):
        return self.units

    def isLogging(self):
        return self.log

class EstimatorBase():

    def __init__(self, Context, cmd):
        self.context = Context
        self.cmdText = cmd
        self.dur = 0.0
        self.dist = 0.0

    '''
        straight-line distance calculation. Arcs, splines, etc. will need to reimplement this
    '''
    def distance_from_Context_Location(self, newLoc):
        self.dist = point.distance(self.context.getLoc(), newLoc)

    def getCmd(self):
        return self.cmdText

    def getDuration(self):
        # calculated distance & feed rate yield duration
        return self.dur

    def getDistance(self):
        return self.dist

    ''' Not universally used but extremely common '''
    def parseXYZ(self):
        # parse cmdText and create point this is to move to
        destPt = point.Point(0,0,0)     #temp

    # mostly for codes that don't move
    def logDur(self):
        ln = 'Cmd: {0}  Duration: {1:.4f}'.format(self.cmdText, self.dur)
        self.context.logFile.writeLine(ln)

    def logDestDur(self):
        ln = 'Cmd: {0} Distance: {1:.4f}  Duration: {2:.4f}'.format(self.cmdText, self.dist, self.dur)
        self.context.logFile.writeLine(ln)

    '''
        The core operation. In many cases this will update both context location and duration.
    '''
    ''' need to figure out where to save new location so this can use it '''
    def estimate(self):
        self.dur = 0.0
        self.dist = 0.0
        # self.dist = self.distance_from_Context_Location()
        # compute duration based on distance

class GcodeTarget(Enum):
    NoTarget = 0
    Grbl = 1
    LinuxCNC = 2
    #Centroids = 3
    #Comparams = 4
    #Dynapath = 5
    #JTech = 6
    #Opensbp = 7
    #Philips = 8
    #Rml = 9
    #Slic3r = 10
    #Smoothie = 11
