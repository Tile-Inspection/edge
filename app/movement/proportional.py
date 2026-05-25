class Proportional:
    def __init__(self, kp=0.1, max_error=90.0):
        self.kp = kp
        self.max_error = max_error
        self.prev_error = 0
        self.integral = 0

    def compute(self, error):
        # Normalize the error to prevent astronomical values when cubing 
        normalized_error = error / self.max_error
        angular_velocity = self.kp * (normalized_error ** 3)

        angular_velocity = max(-1, min(1, angular_velocity))
        
        self.prev_error = error

        return angular_velocity