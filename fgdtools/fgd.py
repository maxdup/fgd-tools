class FGD():
    """Contains all the data parsed from a FGD file
    """

    def __init__(self):
        self._entities = []
        self._editor_data = []

    @property
    def entities(self):
        return self._entities

    @property
    def editor_data(self):
        return self._editor_data

    def include(self, basefgd):
        self._entities.extend(list(basefgd.entities))

    def add_entity(self, fgd_entity):
        """Adds an entity to the FGD
        :param fgd_entity: a FGD_entity object to be added to FGD._entities
        :type fgd_entity: FGD_entity
        """
        # find parents
        if fgd_entity.definitions:
            if 'base' in fgd_entity.definitions:
                for p_entity in fgd_entity.definitions['base']:
                    b = next(filter(
                        lambda data: isinstance(data, FGD_entity) and
                        data.name == p_entity, self._entities), None)
                    if b:
                        fgd_entity.add_parent(b)
        self._entities.append(fgd_entity)

    def add_editor_data(self, fgd_editor_data):
        self._editor_data.append(fgd_editor_data)

    def get_entity_by_name(self, entity_name):
        results = (c for c in self._entities if isinstance(
            c, FGD_entity) and c.name == entity_name)
        return next(results, None)

    def fgd_str(self):
        fgd_str = ''
        for d in self.editor_data:
            fgd_str += d.fgd_str() + '\n\n'
        for e in self.entities:
            fgd_str += e.fgd_str() + '\n\n'
        return fgd_str


class FGD_editor_data():
    # editor data, as found in nodes like
    # @mapsize, @MaterialExclusion or @AutoVisGroup
    def __init__(self, type, name, data=None):
        self._type = type
        self._name = name
        self._data = data

    @property
    def type(self):
        return self._type

    @property
    def name(self):
        return self._name

    @property
    def data(self):
        return self._data

    def fgd_str(self):
        fgd_str = '@' + self._type
        if self._name:
            fgd_str += ' = "' + self.name + '"'
        if self._data and isinstance(self._data, tuple):
            fgd_str += '('
            for t in self._data:
                fgd_str += str(t) + ', '
            fgd_str = fgd_str.strip(', ') + ')'
        fgd_str += "\n"

        if self._data:
            if isinstance(self._data, dict):
                fgd_str += '['
                for k, v in self._data.items():
                    fgd_str += '\n\t"' + k + '"\n\t['
                    for i in v:
                        fgd_str += '\n\t\t"' + i + '"'
                    fgd_str += '\n\t]'
                fgd_str += '\n]'
            elif isinstance(self._data, list):
                fgd_str += '['
                for i in self._data:
                    fgd_str += '\n\t"' + i + '"'
                fgd_str += '\n]'
        return fgd_str


class FGD_entity():
    # An entity in the FGD
    def __init__(self, e_type, definitions, name, description=None):
        self._type = e_type
        self._definitions = definitions or {}
        self._name = name
        self._description = description
        self._parents = []

        # only for entities
        self._properties = []
        self._inputs = []
        self._outputs = []

    @property
    def type(self):
        return self._type

    @property
    def definitions(self):
        return self._definitions

    @property
    def parents(self):
        return self._parents

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        if not self._description:
            for parent in self._parents:
                if parent._description:
                    return parent._description

        return self._description

    @property
    def properties(self):
        return self._properties

    @property
    def inputs(self):
        return self._inputs

    @property
    def outputs(self):
        return self._outputs

    @property
    def all_properties(self):
        properties = {}
        for t in self._parents:
            if isinstance(t, FGD_entity):
                for p in t.all_properties:
                    properties[p.name] = p
        for p in self._properties:
            properties[p.name] = p

        properties_array = []
        for k, v in properties.items():
            properties_array.append(v)

        return properties_array

    @property
    def all_inputs(self):
        inputs = {}
        for t in self._parents:
            if isinstance(t, FGD_entity):
                for p in t.all_inputs:
                    inputs[p.name] = p
        for p in self._inputs:
            inputs[p.name] = p

        inputs_array = []
        for k, v in inputs.items():
            inputs_array.append(v)

        return inputs_array

    @property
    def all_outputs(self):
        outputs = {}
        for t in self._parents:
            if isinstance(t, FGD_entity):
                for p in t.all_outputs:
                    outputs[p.name] = p
        for p in self._outputs:
            outputs[p.name] = p

        outputs_array = []
        for k, v in outputs.items():
            outputs_array.append(v)

        return outputs_array

    def add_definition(self, property):
        self.definitions.append(property)

    def add_parent(self, parent):
        self._parents.append(parent)

    def fgd_str(self):
        fgd_str = '@' + self.type
        for k, v in self._definitions.items():
            fgd_str += ' ' + k + "("
            for arg in v:
                fgd_str += arg + ', '
            fgd_str = fgd_str.strip(', ')
            fgd_str += ")"

        if self._name:
            fgd_str += ' = ' + self._name
        if self._description:
            fgd_str += ' : "' + self._description + '"'

        if self._properties or \
           self._inputs or self._outputs:
            fgd_str += "\n["
            for prop in self._properties:
                fgd_str += "\n\t" + prop.fgd_str()
            for input in self._inputs:
                fgd_str += "\n\t" + input.fgd_str()
            for output in self._outputs:
                fgd_str += "\n\t" + output.fgd_str()
            fgd_str += "\n]"

        return fgd_str

    @property
    def schema(self):
        schema_obj = {
            'properties': self.property_schema,
            'inputs': self.input_schema,
            'outputs': self.output_schema
        }
        return schema_obj

    @property
    def property_schema(self):
        schema_obj = {'classname': 'string', 'id': 'integer'}
        for p in self.all_properties:
            schema_obj[p.name] = p.type
        return schema_obj

    @property
    def input_schema(self):
        schema_obj = {}
        for p in self.all_inputs:
            schema_obj[p.name] = p.type
        return schema_obj

    @property
    def output_schema(self):
        schema_obj = {}
        for p in self.all_outputs:
            schema_obj[p.name] = p.type
        return schema_obj

    def add_property(self, prop):
        if (isinstance(prop, FGD_input)):
            self._inputs.append(prop)
        elif (isinstance(prop, FGD_output)):
            self._outputs.append(prop)
        elif (isinstance(prop, FGD_property)):
            self._properties.append(prop)


class FGD_property():
    # A Property in an Entity
    def __init__(self, p_name, p_type, p_attr, p_args=[], p_options=[]):
        self._name = p_name
        self._type = p_type
        self._attr = p_attr
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
        if self._type in ['choices', 'flags']:
            return self._options
        else:
            return None

    def fgd_str(self):
        fgd_str = self._name + '(' + self._type + ')'
        if self._attr:
            fgd_str += ' ' + self._attr
        for arg in self._args:
            fgd_str += ' :'
            if arg:
                fgd_str += ' ' + arg

        if self.options:
            fgd_str += ' =\n\t[\n'
            for option in self._options:
                fgd_str += '\t\t' + option.fgd_str() + '\n'
            fgd_str += '\t]'
        return fgd_str


class FGD_input(FGD_property):
    # An Input in an Entity
    def __init__(self, p_name, p_type, p_attr, p_args=['""']):
        FGD_property.__init__(self, p_name, p_type, p_attr, p_args)

    def fgd_str(self):
        return 'input ' + FGD_property.fgd_str(self)


class FGD_output(FGD_property):
    # An Output in an Entity
    def __init__(self, p_name, p_type, p_attr, p_args=['""']):
        FGD_property.__init__(self, p_name, p_type, p_attr, p_args)

    def fgd_str(self):
        return 'output ' + FGD_property.fgd_str(self)


class FGD_property_option():
    # An Option within an Entity Property
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

    def fgd_str(self):
        fgd_str = ''
        if isinstance(self._value, int):
            fgd_str += str(self._value)
        else:
            fgd_str += '"' + self._value + '"'
        fgd_str += ' : "' + self._display_name + '"'

        if self._default_value != None:
            fgd_str += ' : '
            if isinstance(self._default_value, int):
                fgd_str += str(self._default_value)
            else:
                fgd_str += '"' + self._default_value + '"'

        return fgd_str
