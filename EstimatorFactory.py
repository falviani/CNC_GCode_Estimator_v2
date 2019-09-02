from Estimators import *
from TargetGRBL import *
from TargetLinuxCNC import *
import re

class EstimatorFactory():
    con = None      # singleton estimator contest

    def __init__(self, context):
        self.con = context

    '''
    builds estimator instance of the required class
    returns new estimator and any remaining text from the string passed in
    (there can be multiple commands on a single line)
    assumes input string has been stripped

    cases in if/else tree are in (approximately) order of popularity for
    what performance improvement can be had
    '''
    def build(self, cmdText):
        est = None  # new estimator
        self.text = cmdText
        logEntry = ''
        # stuff happens here
        try:
            op = cmdText[0]
            if op == '(':
                return (est, '', logEntry)
            else:
                op = op.upper()
                rem = ''
                if op == 'G':
                    (est, rem) = self.gDo()
                elif op == 'M':
                    (est, rem) = self.mDo()
                else:
                    pass    # temp
                return (est, rem, logEntry)
        except Exception as e:
            msg = str(e)
            return (None, '', msg)

    '''
        helper function:
            assumes characters 2-n in cmdText are 0-9 or . (at least 1)
            returns number and remaining text (another command can follow with no intervening white space!)
    '''
    def extractOpNum(self):
        num=0
        remains=''
        try:
            p = re.compile(r'.([0-9.]+)(.*)')    # number followed by everything else
            m = p.match(self.text)
            num = m.group(1)
            remains = m.group(2)
        except Exception as e:
            msg = str(e)
        #
        return (num, remains)

    def gDo(self):
        est = None
        opNo, rem = self.extractOpNum()
        if opNo == '0':
            if self.con.getTarget() == GcodeTarget.Grbl:
                est = gG0(self.con, rem)
            elif self.con.getTarget() == GcodeTarget.LinuxCNC:
                est = lG0(self.con, rem)
            else:
                est = gNotInTarget(self.con, rem)
            return (est, rem)
        elif opNo == '1':
            if self.con.getTarget() == GcodeTarget.Grbl:
                est = gG1(self.con, rem)
            elif self.con.getTarget() == GcodeTarget.LinuxCNC:
                est = lG1(self.con, rem)
            else:
                est = gNotInTarget(self.con, rem)
            return (est, rem)
        elif opNo == '17':
            if self.con.getTarget() == GcodeTarget.Grbl:
                est = gG17(self.con, rem)
            elif self.con.getTarget() == GcodeTarget.LinuxCNC:
                est = lG17(self.con, rem)
            else:
                est = gNotInTarget(self.con, rem)
            return (est, rem)
        elif opNo == '90':
            if self.con.getTarget() == GcodeTarget.Grbl:
                est = gG90(self.con, rem)
            elif self.con.getTarget() == GcodeTarget.LinuxCNC:
                est = lG90(self.con, rem)
            else:
                est = gNotInTarget(self.con, rem)
            return (est, rem)
        elif opNo == '91':
            if self.con.getTarget() == GcodeTarget.Grbl:
                est = gG91(self.con, rem)
            elif self.con.getTarget() == GcodeTarget.LinuxCNC:
                est = lG917(self.con, rem)
            else:
                est = gNotInTarget(self.con, rem)
            return (est, rem)
        else:
            est = gNotInTarget(self.con, rem)
            return (est, rem)

    def mDo(self):
        est = None
        opNo, rem = self.extractOpNum()
        if opNo == '0':
            pass #build M0
        elif opNo == '1':
            pass # build M1
        else:
            est = gNotInTarget(self.con)
            return (est, rem)
