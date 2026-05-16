class PID:
    def __init__(self, kp=0.01, ki=0.001, kd=0.005):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.prev_error = 0
        self.integral = 0

    def compute(self, error):
        self.integral += error
        self.derivative = error - self.prev_error
        angular_velocity = (self.kp * error) + (self.ki * self.integral) + (self.kd * self.derivative)

        angular_velocity = max(-0.5, min(0.5, angular_velocity))
        
        self.prev_error = error

        return angular_velocity