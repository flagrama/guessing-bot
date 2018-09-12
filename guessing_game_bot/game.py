from collections import deque

class GuessingGame():
    def __init__(self, guessables):
        self.running = False
        self.mode = []
        self.guesses = {
            "items": deque()
        }
        for guessable in guessables.types:
            self.guesses[guessable] = deque()
