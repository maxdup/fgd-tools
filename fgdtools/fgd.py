class FGD():
    def __init__(self):
        self.classes = []

    def include(self, basefgd):
        self.classes.extend(list(basefgd.classes))


class FGD_class():
    def __init__(self, class_name):
        self.class_name = ''
        self._parent_classes = []
        self._properties = {}
