class FGD():
    def __init__(self):
        self.classes = []

    def include(self, basefgd):
        self.classes.extend(list(basefgd.classes))
