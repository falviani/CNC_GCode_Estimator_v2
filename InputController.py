from EstimatorFactory import *
from Estimators import  *

class InputController():
    rawCmds = []
    estimators = []     # generated estimators

    def __init__(self, context, cmdList):
        self.con = context
        self.rawCmds = cmdList
        self.factory = EstimatorFactory(context)

    def buildEstimators(self):
        lNo = 0
        try:
            for aCmd in self.rawCmds:
                lNo += 1
                if len(aCmd) > 0:
                    if aCmd[0] == '(':
                        pass
                    else:
                        while len(aCmd) > 0:
                            est, cmdRemaining, log = self.factory.build(aCmd)
                            if est is not None:
                                self.estimators.append(est)
                                if self.con.isLogging() and len(log) > 0:      # record build time message
                                    self.con.logfile.writeLn(log)
                            aCmd = cmdRemaining.strip()
                else:  # blank line
                    pass
        except Exception as e:
            msg = str(e)


    def runEstimators(self):
        for aCmd in self.estimators:
            if aCmd is not None:        # eventually this should be unnecessary
                aCmd.estimate()

