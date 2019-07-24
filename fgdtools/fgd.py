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

    def add_entity(self, fgd_entity):
        """Adds an entity to the FGD
        :param fgd_entity: a FGD_entity object to be added to FGD._entities
        :type fgd_entity: FGD_entity
        """
        if not fgd_entity:
            return

        # find parents
        if fgd_entity.definitions:
            if 'base' in fgd_entity.definitions:
                for p_entity in fgd_entity.definitions['base']:
                    b = next(filter(
                        lambda data: isinstance(data, FGD_entity) and
                        data.name == p_entity, self._entities), None)
                    if b:
                        fgd_entity._parents.append(b)
        self._entities.append(fgd_entity)

    def add_editor_data(self, fgd_editor_data):
        if not fgd_editor_data:
            return

        self._editor_data.append(fgd_editor_data)

    def entity_by_name(self, entity_name):
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
    def __init__(self, class_type, name, data=None):
        self._class_type = class_type
        self._name = name
        self._data = data

    @property
    def class_type(self):
        return self._class_type

    @property
    def name(self):
        return self._name

    @property
    def data(self):
        return self._data

    def fgd_str(self):
        fgd_str = '@' + self._class_type
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
    def __init__(self, class_type, definitions, name, description=None,
                 properties=[], inputs=[], outputs=[]):
        self._class_type = class_type
        self._definitions = definitions or {}
        self._name = name
        self._description = description
        self._properties = properties
        self._inputs = inputs
        self._outputs = outputs

        self._parents = []

    @property
    def class_type(self):
        return self._class_type

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

    def property_by_name(self, prop_name):
        results = (p for p in self.all_properties if p.name == prop_name)
        return next(results, None)

    def input_by_name(self, input_name):
        results = (i for i in self.all_inputs if i.name == input_name)
        return next(results, None)

    def output_by_name(self, output_name):
        results = (o for o in self.all_outputs if o.name == output_name)
        return next(results, None)

    def fgd_str(self):
        fgd_str = '@' + self.class_type
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
        else:
            fgd_str += " []"

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
            schema_obj[p.name] = p.property_type
        return schema_obj

    @property
    def input_schema(self):
        schema_obj = {}
        for p in self.all_inputs:
            schema_obj[p.name] = p.property_type
        return schema_obj

    @property
    def output_schema(self):
        schema_obj = {}
        for p in self.all_outputs:
            schema_obj[p.name] = p.property_type
        return schema_obj


class FGD_property():
    # A Property in an Entity
    def __init__(self, name, property_type, readonly=False,
                 display_name=None, default_value=None, description=None,
                 options=[]):
        self._name = name
        self._property_type = property_type.lower()
        self._readonly = readonly  # usually to set property to readonly

        self._display_name = display_name
        self._default_value = default_value
        self._description = description

        self._options = options

    @property
    def name(self):
        return self._name

    @property
    def property_type(self):
        return self._property_type

    @property
    def readonly(self):
        return self._readonly

    @property
    def display_name(self):
        return self._display_name

    @property
    def default_value(self):
        return self._default_value

    @property
    def description(self):
        return self._description

    @property
    def options(self):
        if self._property_type.lower() in ['choices', 'flags']:
            return self._options
        else:
            return None

    def option_by_value(self, option_value):
        results = (o for o in self._options if o.value == option_value)
        return next(results, None)

    def fgd_str(self):
        # name
        fgd_str = self._name + '(' + self._property_type + ')'

        # readonly
        if self._readonly:
            fgd_str += ' readonly'

        # display name
        if self._display_name:
            fgd_str += ' : "' + self._display_name + '"'
        elif self._description or self._default_value and \
                not isinstance(self, FGD_input) and \
                not isinstance(self, FGD_output):
            fgd_str += ' :'

        # default_value
        if self._default_value:
            fgd_str += ' : ' + str(self._default_value)
        elif self._description and \
                not isinstance(self, FGD_input) and \
                not isinstance(self, FGD_output):
            fgd_str += ' :'

        # description
        if self._description:
            fgd_str += ' : "' + self._description + '"'

        # options
        if self.options:
            fgd_str += ' =\n\t[\n'
            for option in self._options:
                fgd_str += '\t\t' + option.fgd_str() + '\n'
            fgd_str += '\t]'
        elif self._property_type.lower() in ['choices', 'flags']:
            fgd_str += ' =\n\t[\n\t]'

        return fgd_str


class FGD_input():
    # An Input in an Entity
    def __init__(self, name, input_type, description=''):
        self._name = name
        self._input_type = input_type
        self._description = description

    @property
    def name(self):
        return self._name

    @property
    def input_type(self):
        return self._input_type

    @property
    def description(self):
        return self._description

    def fgd_str(self):
        return 'input ' + self._name + '(' + self._input_type + ')' + \
            ' : "' + str(self.description) + '"'


class FGD_output():
    # An Output in an Entity
    def __init__(self, name, output_type, description=''):
        self._name = name
        self._output_type = output_type
        self._description = description

    @property
    def name(self):
        return self._name

    @property
    def output_type(self):
        return self._output_type

    @property
    def description(self):
        return self._description

    def fgd_str(self):
        return 'output ' + self._name + '(' + self._output_type + ')' + \
            ' : "' + str(self.description) + '"'


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
