import unittest
from typing import List
import logging

from player import Player, DummyPlayer, AdvancedDummyPlayer, CounterDummyPlayer, ShowOffPlayer, RandomPlayer, ThresholdPlayer, TrackingPlayer, CounterThresPlayer
from evaluate import Evaluation
from formatting import formatTable

logging.basicConfig(format='[%(levelname)s] %(message)s', level=logging.WARN)


class TestEvaluate(unittest.TestCase):
    def test_get_player_stats(self):
        ev = Evaluation([DummyPlayer()], 0, show_progress=False)
        ev.getPlayerStats(0)
        ev.run()
        print(ev.prettyResults())

    def test_randoms(self):
        ev = Evaluation([RandomPlayer() for _ in range(3)], 1000, show_progress=False)
        ev.run()
        print(ev.prettyResults())

class TestOnInitPlayer(Player):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.playersReceived = None

    def onInit(self, players: List[Player]):
        print("TestOnInitPlayer got these players:")
        print("\n".join([repr(player) for player in players]))
        self.playersReceived = players

class TestOnInit(unittest.TestCase):
    def test_player_on_init(self):
        test_player = TestOnInitPlayer()
        ev = Evaluation([DummyPlayer(), test_player], 1, deepcopy = False)
        self.assertEqual(ev.players, test_player.playersReceived)

class TestAll(unittest.TestCase):
    def test_all(self):
        players = [DummyPlayer(),  AdvancedDummyPlayer(), CounterDummyPlayer(), ShowOffPlayer(), RandomPlayer(), ThresholdPlayer(), TrackingPlayer(), CounterThresPlayer()]
        ev = Evaluation(players, 1000, show_progress = True)
        ev.run()

class TestCounterThres(unittest.TestCase):
    def test_dummy(self):
        self.ctp = CounterThresPlayer()
        self.players = [self.ctp, *[DummyPlayer() for _ in range(2)]]
        self.runSim()

    def test_thres(self):
        self.ctp = CounterThresPlayer()
        tr1 = ThresholdPlayer(lieThreshold=21) 
        tr2 = ThresholdPlayer(lieThreshold=61) 
        print(f"\nSimulation with: \n{tr1.lieThreshold=}")
        print(f"{tr2.lieThreshold=}")
        self.players = [self.ctp, tr1, tr2]
        self.runSim()

    def runSim(self):
        ev = Evaluation(self.players, 1000, show_progress=True, deepcopy=False)
        ev.run()
        print(ev.prettyResults())
        print(f"CounterThresPlayer judgement:")
        table = [["Player", "isThresPlayer", "mostFreqThrow"]]
        for player in [p for p in ev.players if p is not self.ctp]:
            if self.ctp.existsAssumption(player.id):
                if (most_freq := self.ctp.mostFreqThrow(player.id)):
                    table.append([f"{repr(player)}", "Yes",
                        f"lieThres={most_freq}\t{self.ctp.mostFreqThrowFreq(player.id):.3f}"])
            else:
                table.append([f"{repr(player)}", "No", f"({self.ctp.mostFreqThrowFreq(player.id):.3f})"])

        print(formatTable(table))

