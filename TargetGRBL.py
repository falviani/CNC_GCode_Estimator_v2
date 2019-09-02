from Estimators import *

'''
    Since none of these need to extend the __init__ processing of the base class,
    none of them call the super().__init__ processing
'''

''' This gcode not defined in this target '''
class gNotInTarget(EstimatorBase):

    def estimate(self):
        # output message to logger
        pass


''' Defined in this target but not implemented yet in this app '''
class gNotImplemented(EstimatorBase):

    def estimate(self):
        # output message to loggers
        self.context.updateDuration_noMove()

class gG0(EstimatorBase):

    def estimate(self):
        pass

class gG1(EstimatorBase):

    def estimate(self):
        pass


''' various estimators '''

class gG17(EstimatorBase):

    def estimate(self):
        self.context.updateDuration_noMove()


class gG18(EstimatorBase):

    def estimate(self):
        self.context.updateDuration_noMove()


class gG19(EstimatorBase):

    def estimate(self):
        self.context.updateDuration_noMove()


''' units = inches '''
class gG20(EstimatorBase):

    def estimate(self):
        self.context.setUnits(1)
        self.context.updateDuration_noMove()


''' units = mm '''
class gG21(EstimatorBase):

    def estimate(self):
        self.context.setUnits(0)
        self.context.updateDuration_noMove()


class gG54(EstimatorBase):

    def estimate(self):
        pass

''' Set positioning to absolute '''
class gG90(EstimatorBase):

    def estimate(self):
        self.context.modeDistance = 'A'     # absolute positioning
        self.context.updateDuration_noMove()


''' Set positioning to relative '''
class gG91(EstimatorBase):

    def estimate(self):
        self.context.modeDistance = 'R'     # relative positioning
        self.context.updateDuration_noMove()
