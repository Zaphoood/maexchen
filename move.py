import constants as c
from throw import Throw


class Move:
    move: c.ALL_MOVES
    value: Throw

    def __init__(self, move: c.ALL_MOVES, value: Throw = None):
        self.move = move  # Art des Zuges die dieser Zug darstellt (DOUBT oder THROW)
        self.value = value  # Wird nur für Züge verwendet, bei denen der Spieler würfelt.
        # Beinhaltet die Angabe des Spielers über das Würfelergebnis