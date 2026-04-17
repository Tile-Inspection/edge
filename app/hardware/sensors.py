class Sensors:
    def __init__(self):
        self.steps = 0

    def is_wall_ahead(self):
        self.steps += 1

        # simulate wall every 5 steps
        if self.steps % 5 == 0:
            print("Wall detected ahead!")
            return True

        return False