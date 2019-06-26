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
        self._parent_data_types = []
        self._data_properties = data_properties or {}

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

    def add_data_property(self, property):
        self.data_properties.append(property)

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

        self._entity_properties = []
        self._entity_inputs = []
        self._entity_outputs = []

    @property
    def entity_name(self):
        return self._entity_name

    @property
    def entity_description(self):
        if not self._entity_description:
            for parent in self._entity_description:
                if parent._entity_description:
                    return parent._entity_description

        return self._entity_description

    @property
    def entity_properties(self):
        properties = {}
        for t in self._parent_data_types:
            if isinstance(t, FGD_entity):
                for p in t._entity_properties:
                    properties[p.name] = p
        for p in self._entity_properties:
            properties[p.name] = p

        return properties

    @property
    def entity_inputs(self):
        inputs = {}
        for t in self._parent_data_types:
            if isinstance(t, FGD_entity):
                for p in t._entity_inputs:
                    inputs[p.name] = p
        for p in self._entity_inputs:
            inputs[p.name] = p

        return inputs

    @property
    def entity_outputs(self):
        outputs = {}
        for t in self._parent_data_types:
            if isinstance(t, FGD_entity):
                for p in t._entity_outputs:
                    outputs[p.name] = p
        for p in self._entity_outputs:
            outputs[p.name] = p

        return outputs

    def add_entity_property(self, prop):
        if (isinstance(prop, FGD_entity_input)):
            self._entity_inputs.append(prop)
        elif (isinstance(prop, FGD_entity_output)):
            self._entity_outputs.append(prop)
        elif (isinstance(prop, FGD_entity_property)):
            self._entity_properties.append(prop)

    def __repr__(self):
        sref = '@' + self.data_type
        for k, v in self.data_properties.items():
            sref += ' ' + k + "("
            for arg in v:
                sref += arg + ', '
            sref = sref.strip(', ')
            sref += ")"
        sref += ' = ' + self._entity_name + ' : "' + \
            self._entity_description + '"'

        if self._entity_properties or \
           self._entity_inputs or self._entity_outputs:
            sref += "\n["
            for prop in self._entity_properties:
                sref += "\n\t" + repr(prop)
            for input in self._entity_inputs:
                sref += "\n\t" + repr(input)
            for output in self._entity_outputs:
                sref += "\n\t" + repr(output)
            sref += "\n]"

        return sref


class FGD_entity_property():
    def __init__(self, p_name, p_type, p_args=[], p_options=None):
        self._name = p_name
        self._type = p_type
        self._args = []
        for arg in p_args:
            self._args.append(arg.strip())
        self._options = p_options

    @property
    def name(self):
        return self._name

    @property
    def type(self):
        return self._type

    @property
    def args(self):
        return self._args

    @property
    def options(self):
        return self._options

    def __repr__(self):
        rep_str = self._name + '(' + self._type + ')'
        for arg in self._args:
            rep_str += ' :'
            if arg:
                rep_str += ' ' + arg
        return rep_str


class FGD_entity_input(FGD_entity_property):
    def __init__(self, p_name, p_type, p_args=['""']):
        FGD_entity_property.__init__(self, p_name, p_type, p_args)

    def __repr__(self):
        return 'input ' + FGD_entity_property.__repr__(self)


class FGD_entity_output(FGD_entity_property):
    def __init__(self, p_name, p_type, p_args=['""']):
        FGD_entity_property.__init__(self, p_name, p_type, p_args)

    def __repr__(self):
        return 'output ' + FGD_entity_property.__repr__(self)


class FGD_entity_property_options(FGD_entity_property):
    def __init__(self, p_name, p_type, p_args=[], p_options=[]):
        FGD_entity_property.__init__(self, p_name, p_type, p_args)
        self._options = p_options

    def __repr__(self):
        rep_str = FGD_entity_property.__repr__(self)
        rep_str += ' =\n\t[\n'
        for option in self._options:
            rep_str += '\t\t' + repr(option) + '\n'
        rep_str += '\t]'
        return rep_str


class FGD_entity_property_option():
    def __init__(self, tupple):
        self._value = tupple[0]
        self._display_name = tupple[1]
        if len(tupple) > 2:
            self._default_value = tupple[2]
        else:
            self._default_value = None

    @property
    def value(self):
        return self._value

    @property
    def display_name(self):
        return self._display_name

    @property
    def default_value(self):
        return self._default_value

    def __repr__(self):
        repr_str = ''
        if isinstance(self._value, int):
            repr_str += str(self._value)
        else:
            repr_str += '"' + self._value + '"'
        repr_str += ' : "' + self._display_name + '"'

        if self._default_value:
            repr_str += ' : '
            if isinstance(self._default_value, int):
                repr_str += str(self._default_value)
            else:
                repr_str += '"' + self._default_value + '"'

        return repr_str
