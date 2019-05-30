class FGD():
    def __init__(self):
        self.classes = []

    def include(self, basefgd):
        self.classes.extend(list(basefgd.classes))


class FGD_data():
    def __init__(self, data_type, data_properties):
        self._data_type = data_type
        self._super_types = []
        self._editor_properties = []


class FGD_entity(FGD_data):
    def __init__(self, data_type, data_properties,
                 entity_name, entity_description=''):
        FGD_data.__init__(self, data_type, data_properties)
        self._entity_name = entity_name
        self._entity_description = entity_description
        self._entity_properties = {}

    @property
    def entity_name(self):
        return self._entity_name

    @property
    def entity_description(self):
        return self._entity_description
