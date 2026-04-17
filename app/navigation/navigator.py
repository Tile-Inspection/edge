class Navigator:
    def __init__(self, motion):
        self.motion = motion
        self.turn_right_next = True  # alternate turns

    def handle_wall(self):
        if self.turn_right_next:
            self.motion.turn_right()
            self.motion.move_forward_tile()
            self.motion.turn_right()
        else:
            self.motion.turn_left()
            self.motion.move_forward_tile()
            self.motion.turn_left()

        self.turn_right_next = not self.turn_right_next