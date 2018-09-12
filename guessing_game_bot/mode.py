class Mode():
    def __init__(self, name, *items):
        self.name = name
        self.items = []
        for item in items:
            self.items += [item]
        if not self.items:
            raise ValueError('mode must have items associated')
