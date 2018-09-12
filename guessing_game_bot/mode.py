class Mode():
    def __init__(self, name, *items):
        self.name = name
        self.items = []
        for item in items:
            for item_name in item:
                self.items += [item_name]
        if not self.items:
            raise ValueError('mode must have items associated')
