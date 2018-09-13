from collections import deque

class GuessingGame():
    def __init__(self, guessables, modes, multi_guess):
        self.running = False
        self.mode = []
        self.guesses = {
            "items": deque()
        }
        for guess_type in multi_guess:
            self.guesses[guess_type] = deque()
