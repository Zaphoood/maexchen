# TODO: Do `from unittest import TestCase` instead
import unittest
import logging

from game import Game, TooFewPlayers, DuplicateId
from player import Player, DummyPlayer, AdvancedDummyPlayer, CounterDummyPlayer, ShowOffPlayer, RandomPlayer, ThresholdPlayer, TrackingPlayer
from gamelog import GameLog
import gameevent
from throw import Throw

logging.basicConfig(format='[%(levelname)s] %(message)s', level=logging.INFO)


class TestInit(unittest.TestCase):
    def test_seed(self):
        Game([DummyPlayer()], seed=123)

    def test_shuffle(self):
        Game([DummyPlayer(), DummyPlayer()], shuffle_players=False)
        Game([DummyPlayer(), DummyPlayer()], shuffle_players=True)

    def test_duplicate(self):
        # This should not work
        with self.assertRaises(DuplicateId):
            Game([DummyPlayer(player_id=0), DummyPlayer(player_id=0)], disable_assign_ids=True)
        # This should work
        game = Game([DummyPlayer(player_id=0), DummyPlayer(player_id=0)], disable_assign_ids=False)
        self.assertNotEqual(game.players[0].id, game.players[1].id)

    def test_too_few(self):
        # Game with zero players should fail
        game = Game([])
        with self.assertRaises(TooFewPlayers) as cm:
            game.init()
        self.assertEqual(cm.exception.n_players, 0)

        # Game with one player should fail
        game = Game([DummyPlayer()])
        with self.assertRaises(TooFewPlayers) as cm:
            game.init()
        self.assertEqual(cm.exception.n_players, 1)

class TestNPlayers(unittest.TestCase):
    """Testet Spiele mit verschiedenen Spielerzahlen"""

    def test_one(self):
        game = Game([])
        self.assertRaises(TooFewPlayers, game.init)
        game = Game([DummyPlayer()])
        self.assertRaises(TooFewPlayers, game.init)

    def test_three(self):
        players = [DummyPlayer() for _ in range(3)]
        self.game = Game(players)
        self.game.init()
        self.game.run()


class TestPlayerIds(unittest.TestCase):
    """Testet das verhalten der Game Klasse hinsichtlich dem vergeben einzigartiger ids"""

    def assert_unique_ids(self, game):
        ids = set()
        for p in game.players:
            self.assertFalse(p.id in ids)
            self.assertTrue(isinstance(p.id, int))
            ids.add(p.id)

    def test_assign(self):
        # No IDs assigned manually
        players = [DummyPlayer() for _ in range(10)]
        game = Game(players)
        self.assert_unique_ids(game)

    def test_partial(self):
        # Some IDs assigned manually, some to be assigned by Game
        players = [DummyPlayer(player_id=3), DummyPlayer(player_id=100), DummyPlayer(), DummyPlayer(), DummyPlayer(player_id=2)]
        game = Game(players)
        self.assert_unique_ids(game)
        self.assertTrue(any([p.id == 3 for p in game.players]))
        self.assertTrue(any([p.id == 100 for p in game.players]))
        self.assertTrue(any([p.id == 2 for p in game.players]))

    def test_conflict(self):
        # Conflicting IDs assigned manually
        players = [DummyPlayer(player_id=2), DummyPlayer(player_id=2), DummyPlayer(player_id=3), DummyPlayer(), DummyPlayer(player_id=2)]
        game = Game(players)
        self.assert_unique_ids(game)


class TestLog(unittest.TestCase):
    def test_log(self):
        log = GameLog()
        log.happen(gameevent.EventAbort())
        self.assertTrue(log.hasFinished())

        log = GameLog()
        log.happen(gameevent.EventFinish(0))
        self.assertTrue(log.hasFinished())


class EventListenerPlayer(Player):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.listensToEvents = True

    def getDoubt(lastThrow, *args, **kwargs):
        return False

    def getThrowStated(myThrow, lastThrow, *args, **kwargs):
        return Throw(2, 1) if lastThrow.is_maexchen else lastThrow + 1

    def onEvent(self, event):
        logging.info(f"EventListenerPlayer got Event: {event}")


class TestEventListening(unittest.TestCase):
    def test_methods(self):
        p = EventListenerPlayer()
        p.getDoubt(Throw(2, 1))
    def test_game(self):
        game = Game([RandomPlayer(), EventListenerPlayer()])
        game.init()
        game.run()


class TestTrackingPlayer(unittest.TestCase):
    def test_tracking(self):
        tracking_player = TrackingPlayer()
        players = [DummyPlayer(), RandomPlayer(), ThresholdPlayer(), tracking_player]
        game = Game(players)
        tracking_player.onInit(game.players)
        game.init()
        game.run()


class TestAll(unittest.TestCase):
    def test_all(self):
        tr = TrackingPlayer()
        ctp = CounterDummyPlayer()
        players = [DummyPlayer(),  AdvancedDummyPlayer(), ctp, ShowOffPlayer(), RandomPlayer(), ThresholdPlayer(), tr]
        game = Game(players)
        ctp.onInit(game.players)
        tr.onInit(game.players)
        game.init()
        game.run()
