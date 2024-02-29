import numpy as np



class readTrigger():
    def __init__(self,trigger_array):
        self.trigger_array = trigger_array

    def compute_trigger_delay(self,V_thresohold):
        return np.where(self.trigger_array > V_thresohold)[0][-1]







