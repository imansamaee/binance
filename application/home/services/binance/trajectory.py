class Trajectory:
    def __init__(self, occurrence, max_rounds):
        self.lines = []
        self.lines.append(Line())
        self._vector = 1
        self.rounds = 0
        self.occurrence = occurrence
        self.max_rounds = max_rounds
        self.current_round = 0


    @property
    def vector(self):
        return self._vector

    @vector.setter
    def vector(self, _vector):
       # print(f"{_vector} ==== {self._vector}")
        if _vector * self._vector == 1:  # continue trajectory
            self.lines[-1].points.append(_vector)

        else:
            if len(self.lines[-1].points) >= self.occurrence:
                self.lines.append(Line(_vector))
            else:
                # reset Lines
                if len(self.lines) > 1:
                    self.lines.remove(self.lines[-1])




           # print(len(self.lines))
        self._vector = _vector


    # def reset(self):
    #     self.lines = []
    #     self.lines.append(Line())
    #     self._vector = 1
    #     self.rounds = 0


class Line:
    def __init__(self, p1=0):
        self.points = [p1]  # float


