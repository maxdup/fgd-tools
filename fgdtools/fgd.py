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
                for p_class in fgd_class.data_properties['base']:
                    b = next(filter(
                        lambda data: isinstance(data, FGD_entity) and
                        data.entity_name == p_class, self._classes), None)
                    if b:
                        fgd_class.add_parent_data(b)
        self._classes.append(fgd_class)


class FGD_data():
    def __init__(self, data_type, data_properties):
        self._data_type = data_type
        self._data_properties = data_properties or []
        self._parent_data_types = []

    @property
    def data_type(self):
        return self._data_type

    @property
    def parent_data_types(self):
        # and parent's parent's parent's....
        return self._parent_data_types

    @property
    def data_properties(self):
        # and parent's parent's parent's....
        return self._data_properties

    def add_property(self, property):
        self.properties.append(property)

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
        self._entity_inputs = []
        self._entity_outputs = []

    @property
    def entity_name(self):
        return self._entity_name

    @property
    def entity_description(self):
        # ? and parent's parent's parent's....
        return self._entity_description

    @property
    def entity_properties(self):
        # and parent's parent's parent's....
        return self._entity_properties

    def add_property(self, prop):
        if (isinstance(prop, FGD_entity_input)):
            self._entity_inputs.append(prop)
        elif (isinstance(prop, FGD_entity_ouput)):
            self._entity_outputs.append(prop)
        elif (isinstance(FGD_entity_property)):
            self._entity_properties.append(prop)

    def __repr__(self):
        return self._entity_name


class FGD_entity_property():
    def __init__(self, p_name, p_type, args=[], options=None):
        self._name = p_name
        self._type = p_type
        self._args = []
        for arg in args:
            self._args.append(arg.strip())
        self._options = options

    def set_options(self, options):
        self.options = options

    def __repr__(self):
        rep_str = self._name + '(' + self._type + ')'
        for arg in self._args:
            rep_str += ' :'
            if arg:
                rep_str += ' ' + arg
        return rep_str


class FGD_entity_property_options(FGD_entity_property):
    def __init__(self, p_name, p_type, args=[], options=[]):
        FGD_entity_property.__init__(self, p_name, p_type, args)
        self._options = options

    def __repr__(self):
        rep_str = FGD_entity_property.__repr__(self)
        rep_str += ' =\n[\n'
        for option in self._options:
            rep_str += option[0] + ' : ' + option[1] + '\n'
        rep_str += ']'
        return rep_str


class FGD_entity_input(FGD_entity_property):
    def __init__(self, p_name, p_type, args=['""']):
        args = args or ['""']
        FGD_entity_property.__init__(self, p_name, p_type, args)

    def __repr__(self):
        return 'input ' + FGD_entity_property.__repr__(self)


class FGD_entity_output(FGD_entity_property):
    def __init__(self, p_name, p_type, args=['""']):
        args = args or ['""']
        FGD_entity_property.__init__(self, p_name, p_type, args)

    def __repr__(self):
        return 'output ' + FGD_entity_property.__repr__(self)
