
MIN_NUM = float('-inf')
MAX_NUM = float('inf')

class PID(object):
    def __init__(self, kp, ki, kd, mn=MIN_NUM, mx=MAX_NUM):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.min = mn
        self.max = mx

        self.int_val = self.last_error = 0.

        #conditional integral
        self.integral_on = True

    def reset(self):
        self.int_val = 0.0

    def step(self, error, sample_time):
        # integral on? or off?
        #set False 
        #if error is the same sign with PID output and it's saturated.

        integral = self.int_val + error * sample_time;
        derivative = (error - self.last_error) / sample_time;

        if self.integral_on == True:
            val = self.kp * error + self.ki * integral + self.kd * derivative;
        else:
            val = self.kp * error + self.kd * derivative;
            
        saturated = True
        if val > self.max:
            val = self.max
        elif val < self.min:
            val = self.min
        else:
            self.int_val = integral
            saturated = False
        self.last_error = error

        same_sign = (error > 0 and val > 0 ) or (error < 0 and val < 0 )

        if saturated and same_sign: 
                self.integral_on = False
        else:
                self.integral_on = True  #turn on again!

        return val
