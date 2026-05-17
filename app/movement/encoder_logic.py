import time

class EncoderAutoRun:
    def __init__(self, motion, left_encoder, right_encoder):
        self.motion = motion
        self.left_encoder = left_encoder
        self.right_encoder = right_encoder
        
        # Proportional gain to keep wheels synchronized
        self.kp = 0.00 

    def move_forward_pulses(self, target_pulses: int, base_speed: float = 0.5, timeout: float = 15.0):
        """
        Moves the robot forward until the average of both wheel encoders reaches the target_pulses.
        Uses a simple proportional controller to keep the wheel encoders synchronized (going straight).
        Returns the final tick counts (left, right).
        """
        self.left_encoder.reset()
        self.right_encoder.reset()
        
        start_time = time.time()
        
        while True:
            left_ticks = self.left_encoder.get_ticks()
            right_ticks = self.right_encoder.get_ticks()
            
            avg_ticks = (left_ticks + right_ticks) / 2.0
            
            if avg_ticks >= target_pulses:
                break
                
            if time.time() - start_time > timeout:
                print("EncoderAutoRun: Timeout reached before hitting target pulses.")
                break
                
            # If left wheel has more ticks than right, the robot is veering right.
            # We want to turn left (angular < 0 in motion.py).
            # error will be negative if left > right.
            error = right_ticks - left_ticks
            angular_velocity = error * self.kp
            
            # Clamp angular velocity to prevent wild swinging
            angular_velocity = max(-0.2, min(0.2, angular_velocity))
            
            self.motion.send_velocity(base_speed, angular_velocity)
            
            time.sleep(0.02)
            
        self.motion.stop()
        
        return self.left_encoder.get_ticks(), self.right_encoder.get_ticks()
