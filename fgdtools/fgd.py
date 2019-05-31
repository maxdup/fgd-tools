class FGD():
    def __init__(self):
        self._classes = []

    @property
    def classes(self):
        return self._classes

    def include(self, basefgd):
        self._classes.extend(list(basefgd.classes))

    def add_class(self, fgd_class):
        # find parents
        if fgd_class.data_properties:
            if 'base' in fgd_class.data_properties:
                for base in fgd_class.data_properties['base']:
                    base = next(filter(
                        lambda data: isinstance(data, FGD_entity) and
                        data.entity_name == base, self._classes), None)
                    fgd_class.add_parent_data(base)
        self._classes.append(fgd_class)


class FGD_data():
    def __init__(self, data_type, data_properties):
        self._data_type = data_type
        self._data_properties = data_properties
        self._parent_data_types = []

    @property
    def data_type(self):
        return self._data_type

    @property
    def parent_data_types(self):
        return self._parent_data_types

    @property
    def data_properties(self):
        return self._data_properties

    def add_parent_data(self, parent):
        self._parent_data_types.append(parent)

    def __repr__(self):
        return self._data_type


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

    @property
    def entity_properties(self):
        return self._entity_properties

    def __repr__(self):
        return self._entity_name
