class FGD():
    def __init__(self):
        self._classes = []

    @property
    def classes(self):
        return self._classes

    @property
    def fgd_str(self):
        fgd_str = ''
        for c in self.classes:
            fgd_str += c.fgd_str + '\n\n'
        return fgd_str

    def include(self, basefgd):
        self._classes.extend(list(basefgd.classes))

    def get_entity_by_name(self, entity_name):
        results = (c for c in self._classes if isinstance(
            c, FGD_entity) and c.name == entity_name)
        return next(results, None)

    def add_class(self, fgd_class):
        # find parents
        if fgd_class.data_properties:
            if 'base' in fgd_class.data_properties:
                for p_class in fgd_class.data_properties['base']:
                    b = next(filter(
                        lambda data: isinstance(data, FGD_entity) and
                        data.name == p_class, self._classes), None)
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
        return self._parent_data_types

    @property
    def data_properties(self):
        return self._data_properties

    @property
    def fgd_str(self):
        fgd_str = '@' + self.data_type
        for k, v in self._data_properties.items():
            fgd_str += ' ' + k + "("
            for arg in v:
                fgd_str += arg + ', '
            fgd_str = fgd_str.strip(', ')
            fgd_str += ")"

        return fgd_str

    def add_data_property(self, property):
        self.data_properties.append(property)

    def add_parent_data(self, parent):
        self._parent_data_types.append(parent)


class FGD_entity(FGD_data):
    def __init__(self, data_type, data_properties,
                 name, description=''):
        FGD_data.__init__(self, data_type, data_properties)

        self._name = name
        self._description = description

        self._properties = []
        self._inputs = []
        self._outputs = []

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        if not self._description:
            for parent in self._description:
                if parent._description:
                    return parent._description

        return self._description

    @property
    def properties(self):
        return self._properties

    @property
    def all_properties(self):
        properties = {}
        for t in self._parent_data_types:
            if isinstance(t, FGD_entity):
                for p in t._properties:
                    properties[p.name] = p
        for p in self._properties:
            properties[p.name] = p

        properties_array = []
        for k, v in properties.items():
            properties_array.append(v)

        return properties_array

    @property
    def inputs(self):
        return self._inputs

    @property
    def all_inputs(self):
        inputs = {}
        for t in self._parent_data_types:
            if isinstance(t, FGD_entity):
                for p in t._inputs:
                    inputs[p.name] = p
        for p in self._inputs:
            inputs[p.name] = p

        inputs_array = []
        for k, v in inputs.items():
            inputs_array.append(v)

        return inputs_array

    @property
    def outputs(self):
        return self._outputs

    @property
    def all_outputs(self):
        outputs = {}
        for t in self._parent_data_types:
            if isinstance(t, FGD_entity):
                for p in t._outputs:
                    outputs[p.name] = p
        for p in self._outputs:
            outputs[p.name] = p

        outputs_array = []
        for k, v in outputs.items():
            outputs_array.append(v)

        return outputs_array

    @property
    def fgd_str(self):
        fgd_str = FGD_data.fgd_str(self)
        fgd_str += ' = ' + self._name + ' : "' + \
            self._description + '"'

        if self._properties or \
           self._inputs or self._outputs:
            fgd_str += "\n["
            for prop in self._properties:
                fgd_str += "\n\t" + prop.fgd_str
            for input in self._inputs:
                fgd_str += "\n\t" + input.fgd_str
            for output in self._outputs:
                fgd_str += "\n\t" + output.fgd_str
            fgd_str += "\n]"

        return fgd_str

    def add_property(self, prop):
        if (isinstance(prop, FGD_input)):
            self._inputs.append(prop)
        elif (isinstance(prop, FGD_output)):
            self._outputs.append(prop)
        elif (isinstance(prop, FGD_property)):
            self._properties.append(prop)


class FGD_property():
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

    @property
    def fgd_str(self):
        fdg_str = self._name + '(' + self._type + ')'
        for arg in self._args:
            fdg_str += ' :'
            if arg:
                fdg_str += ' ' + arg
        return fdg_str


class FGD_input(FGD_property):
    def __init__(self, p_name, p_type, p_args=['""']):
        FGD_property.__init__(self, p_name, p_type, p_args)

    @property
    def fgd_str(self):
        return 'input ' + FGD_property.fgd_str(self)


class FGD_output(FGD_property):
    def __init__(self, p_name, p_type, p_args=['""']):
        FGD_property.__init__(self, p_name, p_type, p_args)

    @property
    def fgd_str(self):
        return 'output ' + FGD_property.fgd_str(self)


class FGD_property_options(FGD_property):
    def __init__(self, p_name, p_type, p_args=[], p_options=[]):
        FGD_property.__init__(self, p_name, p_type, p_args)
        self._options = p_options

    @property
    def fgd_str(self):
        fdg_str = FGD_property.fgd_str(self)
        fdg_str += ' =\n\t[\n'
        for option in self._options:
            fdg_str += '\t\t' + option.fgd_str + '\n'
        fdg_str += '\t]'
        return fdg_str


class FGD_property_option():
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

    @property
    def fgd_str(self):
        fdg_str = ''
        if isinstance(self._value, int):
            fdg_str += str(self._value)
        else:
            fdg_str += '"' + self._value + '"'
        fdg_str += ' : "' + self._display_name + '"'

        if self._default_value:
            fdg_str += ' : '
            if isinstance(self._default_value, int):
                fdg_str += str(self._default_value)
            else:
                fdg_str += '"' + self._default_value + '"'

        return fdg_str
