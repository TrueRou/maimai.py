# MIT license
# Reference: https://github.com/Diving-Fish/maimaidx-prober

SCORE_COEFFICIENT_TABLE = [
    [0, 0, "d"],
    [10, 1.6, "d"],
    [20, 3.2, "d"],
    [30, 4.8, "d"],
    [40, 6.4, "d"],
    [50, 8.0, "c"],
    [60, 9.6, "b"],
    [70, 11.2, "bb"],
    [75, 12.0, "bbb"],
    [79.9999, 12.8, "bbb"],
    [80, 13.6, "a"],
    [90, 15.2, "aa"],
    [94, 16.8, "aaa"],
    [96.9999, 17.6, "aaa"],
    [97, 20.0, "s"],
    [98, 20.3, "sp"],
    [98.9999, 20.6, "sp"],
    [99, 20.8, "ss"],
    [99.5, 21.1, "ssp"],
    [99.9999, 21.4, "ssp"],
    [100, 21.6, "sss"],
    [100.4999, 22.2, "sss"],
    [100.5, 22.4, "sssp"],
]


class ScoreCoefficient:
    def __init__(self, achievements):
        for i in range(len(SCORE_COEFFICIENT_TABLE)):
            if i == len(SCORE_COEFFICIENT_TABLE) - 1 or achievements < SCORE_COEFFICIENT_TABLE[i + 1][0]:
                self.r = SCORE_COEFFICIENT_TABLE[i][2]
                self.c = SCORE_COEFFICIENT_TABLE[i][1]
                self.min = SCORE_COEFFICIENT_TABLE[i][0]
                self.a = achievements
                return

    def ra(self, ds):
        return int(self.c * ds * min(100.5, self.a) / 100)
