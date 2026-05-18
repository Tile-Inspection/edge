class Proportional:
    def __init__(self, kp=0.1):
        self.kp = kp
        self.prev_error = 0
        self.integral = 0

    def compute(self, error):
        angular_velocity = self.kp * error

        angular_velocity = max(-1, min(1, angular_velocity))
        
        self.prev_error = error

        return angular_velocity