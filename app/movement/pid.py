class PID:
    def __init__(self, kp=0.02, ki=0.001, kd=0.005, max_integral=100.0):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.max_integral = max_integral
        self.prev_error = 0
        self.integral = 0

    def compute(self, error):
        # Only accumulate integral when close to the target (e.g., within 15 degrees)
        # This prevents massive windup during large turns.
        if abs(error) < 15.0:
            self.integral += error
            # Anti-windup: clamp the integral so it doesn't overpower the output
            self.integral = max(-self.max_integral, min(self.max_integral, self.integral))
        else:
            self.integral = 0
            
        self.derivative = error - self.prev_error
        angular_velocity = (self.kp * error) + (self.ki * self.integral) + (self.kd * self.derivative)

        angular_velocity = max(-0.5, min(0.5, angular_velocity))
        
        self.prev_error = error

        return angular_velocity