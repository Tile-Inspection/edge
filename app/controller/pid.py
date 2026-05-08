class PID:
    def __init__(self):
        self.kp = 0.01
        self.ki = 0.001
        self.kd = 0.005
        self.prev_error = 0
        self.integral = 0

    def compute(self, error):
        self.integral += error
        self.derivative = error - self.prev_error
        angular_velocity = (self.kp * error) + (self.ki * self.integral) + (self.kd * self.derivative)

        # Clamp angular velocity to [-1.0, 1.0] bounds
        angular_velocity = max(-1.0, min(1.0, angular_velocity))
        
        self.prev_error = error

        return angular_velocity