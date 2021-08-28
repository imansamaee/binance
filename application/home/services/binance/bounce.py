from application.home.services.binance.trajectory import Trajectory


class Bounce:
    def __init__(self, rounds=10, occurrence=3, required_lines=4):
        self.rounds = rounds
        self.occurrence = occurrence
        self.required_lines = required_lines
        self.trajectory = Trajectory(occurrence, rounds)
        self.ready_to_buy = False

    def update_trajectory(self, _trajectory):
        self.trajectory.rounds += 1
        # print(_trajectory)
        if _trajectory == 1:
            self.trajectory.vector = 1

        if _trajectory == -1:
            self.trajectory.vector = -1

        if _trajectory == 0:
            pass
        self.check_lines(_trajectory)

    def check_lines(self, _trajectory):
        if len(self.trajectory.lines) >= self.required_lines:
            if _trajectory < 0:
                self.ready_to_buy = True
            else:
                self.ready_to_buy = False
