class Fgd():
    """Contains all the data from an Fgd file such as
    entities and other editor informations.
    """

    def __init__(self):
        self._entities = []
        self._editor_data = []

    @property
    def entities(self):
        """A list containing all :class:`fgdtools.FgdEntity`"""

        return self._entities

    @property
    def editor_data(self):
        """A list containing all :class:`fgdtools.FgdEditorData`"""

        return self._editor_data

    def add_entity(self, fgd_entity):
        """Adds an entity to the Fgd

        :param fgd_entity: a FgdEntity object to be added
                           to this Fgd instance.
        :type fgd_entity: FgdEntity
        """

        if not fgd_entity:
            return

        # find parents
        if fgd_entity.definitions:
            if 'base' in fgd_entity.definitions:
                for p_entity in fgd_entity.definitions['base']:
                    b = next(filter(
                        lambda data: isinstance(data, FgdEntity) and
                        data.name == p_entity, self._entities), None)
                    if b:
                        fgd_entity._parents.append(b)
        self._entities.append(fgd_entity)

    def add_editor_data(self, fgd_editor_data):
        """Adds editor data to the Fgd

        :param fgd_editor_data: a FgdEditorData object to be added
                                to this Fgd instance.
        :type fgd_editor_data: FgdEditorData
        """

        if not fgd_editor_data:
            return

        self._editor_data.append(fgd_editor_data)

    def entity_by_name(self, entity_name):
        """Finds an entity by its name

        :param entity_name: The entity name to look for.
        :type entity_name: str
        :return: An entity with matching name, None if not found.
        :rtype: FgdEntity
        """

        results = (c for c in self._entities if isinstance(
            c, FgdEntity) and c.name == entity_name)
        return next(results, None)

    def fgd_str(self):
        """A string representation of the Fgd formated as in the a .fgd file

        :return: Fgd formated string.
        :rtype: str
        """

        fgd_str = ''
        for d in self.editor_data:
            fgd_str += d.fgd_str() + '\n\n'
        for e in self.entities:
            fgd_str += e.fgd_str() + '\n\n'
        return fgd_str


class FgdEditorData():
    """Editor data, as reprented in a FGD file, usually of type such as:
    @mapsize, @MaterialExclusion or @AutoVisGroup

    :param class_type: The editor_data's type
                       ex: 'mapsize', 'MaterialExclusion', 'AutoVisGroup' etc...
    :type class_type: str

    :param name: The editor_data's display name.
    :type name: str

    :param data: The editor_data's data.
    :type data: tuple or list or dict
    """

    def __init__(self, class_type, name, data):
        self._class_type = class_type
        self._name = name
        self._data = data

    @property
    def class_type(self):
        """The editor_data's type.

        :rtype: str"""

        return self._class_type

    @property
    def name(self):
        """The editor_data's name.

        :rtype: str"""

        return self._name

    @property
    def data(self):
        """The editor_data's data.

        :rtype: tuple or list or dict"""

        return self._data

    def fgd_str(self):
        """A string representation of FgdEditorData formated as in the a .fgd file.

        :return: Fgd formated string.
        :rtype: str
        """

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


class FgdEntity():
    """An entity, as reprented in a FGD file.

    :param class_type: The entity's type
                       ex: 'BaseClass', 'SolidClass', 'PointClass' etc...
    :type class_type: str

    :param definitions: Information defining the entity within the editor.
                       ex: 'base()', 'size()', 'line()', 'studioprop()' etc...
    :type definitions: dict

    :param name: The entity's name.
    :type name: str

    :param description: The entity's description.
    :type description: str, optional

    :param properties: The entity's properties.
    :type properties: list[FgdEntityProperty], optional

    :param inputs: The entity's inputs.
    :type inputs: list[FgdEntityInput], optional

    :param output: The entity's output.
    :type output: list[FgdEntityOutput], optional
    """

    def __init__(self, class_type, definitions, name, description=None,
                 properties=[], inputs=[], outputs=[]):
        self._class_type = class_type
        self._definitions = definitions or []
        self._name = name
        self._description = description
        self._properties = properties
        self._inputs = inputs
        self._outputs = outputs

        self._parents = []

    @property
    def schema(self):
        """A schematic view of this entity's attributes.

        :returns: A dictionary
        :rtype: dict
        """

        schema_obj = {
            'properties': self.property_schema,
            'inputs': self.input_schema,
            'outputs': self.output_schema
        }
        return schema_obj

    @property
    def property_schema(self):
        """A schematic view of this entity's properties.

        :returns: A dictionary
        :rtype: dict
        """

        schema_obj = {'classname': {'default_value': self._name,
                                    'type': 'string',
                                    'readonly': True},
                      'id': {'type': 'integer',
                             'readonly': True}}
        for p in self.properties:
            schema_obj[p.name] = p.schema
        return schema_obj

    @property
    def input_schema(self):
        """A schematic view of this entity's inputs.

        :returns: A dictionary
        :rtype: dict
        """

        schema_obj = {}
        for i in self.inputs:
            schema_obj[i.name] = i.schema
        return schema_obj

    @property
    def output_schema(self):
        """A schematic view of this entity's outputs.

        :returns: A dictionary
        :rtype: dict
        """

        schema_obj = {}
        for o in self.outputs:
            schema_obj[o.name] = o.schema
        return schema_obj

    @property
    def class_type(self):
        """The entity's type.

        :rtype: str"""

        return self._class_type

    @property
    def parents(self):
        """The entity's parent entities, as defined in the entity's base(definition).

        :rtype: list[FgdEntity]"""

        return self._parents

    @property
    def name(self):
        """The entity's type.

        :rtype: str"""

        return self._name

    @property
    def description(self):
        """The entity's description.

        :rtype: str"""

        if not self._description:
            for parent in self._parents:
                if parent._description:
                    return parent._description

        return self._description

    @property
    def definitions(self):
        """The entity's definitions, including inherited definitions.

        :rtype: list[dict]"""

        definitions = []
        for t in self._parents:
            definitions += t.definitions
        definitions += self._definitions
        return definitions

    @property
    def properties(self):
        """The entity's properties, including inherited inputs.

        :rtype: list[FgdEntityOutput]"""

        properties = {}
        for t in self._parents:
            for p in t.properties:
                properties[p.name] = p
        for p in self._properties:
            properties[p.name] = p

        properties_array = []
        for k, v in properties.items():
            properties_array.append(v)

        return properties_array

    @property
    def inputs(self):
        """The entity's inputs, including inherited inputs.

        :rtype: list[FgdEntityInput]"""

        inputs = {}
        for t in self._parents:
            for p in t.inputs:
                inputs[p.name] = p
        for p in self._inputs:
            inputs[p.name] = p

        inputs_array = []
        for k, v in inputs.items():
            inputs_array.append(v)

        return inputs_array

    @property
    def outputs(self):
        """The entity's outputs, including inherited outputs.

        :rtype: list[FgdEntityOutput]"""

        outputs = {}
        for t in self._parents:
            for p in t.outputs:
                outputs[p.name] = p
        for p in self._outputs:
            outputs[p.name] = p

        outputs_array = []
        for k, v in outputs.items():
            outputs_array.append(v)

        return outputs_array

        return self._outputs

    def property_by_name(self, prop_name):
        """Finds an entity property by its name

        :param prop_name: The entity property name to look for.
        :type prop_name: str
        :return: An entity property with matching name, None if not found.
        :rtype: FgdEntityProperty
        """

        results = (p for p in self.properties if p.name == prop_name)
        return next(results, None)

    def input_by_name(self, input_name):
        """Finds an entity input by its name

        :param input_name: The entity input name to look for.
        :type input_name: str
        :return: An entity input with matching name, None if not found.
        :rtype: FgdEntityInput
        """

        results = (i for i in self.inputs if i.name == input_name)
        return next(results, None)

    def output_by_name(self, output_name):
        """Finds an entity output by its name

        :param output_name: The entity output name to look for.
        :type output_name: str
        :return: An entity output with matching name, None if not found.
        :rtype: FgdEntityOutput
        """

        results = (o for o in self.outputs if o.name == output_name)
        return next(results, None)

    def fgd_str(self):
        """A string representation of the FgdEntity formated as in the a .fgd file

        :return: Fgd formated string.
        :rtype: str
        """

        fgd_str = '@' + self.class_type
        for d in self._definitions:
            fgd_str += ' ' + d['name'] + "("
            for arg in d['args']:
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


class FgdEntityProperty():
    """An entity property, as reprented in a FGD file.

    :param name: The property's name.
    :type name: str

    :param value_type: The property's value type
                    ex: 'integer', 'float', 'choices', etc...
    :type value_type: str

    :param name: The property's readonly status.
    :type name: bool, optional

    :param display_name: The property's display name.
    :type display_name: str, optional

    :param default_value: The property's unparsed default value.
    :type default_value: str, optional

    :param description: The property's description.
    :type description: str, optional

    :param options: The property's options. (applicable only to types "choices" and "flags")
    :type options: list[FgdEntityPropertyOption], optional
    """

    def __init__(self, name, value_type, readonly=False,
                 display_name=None, default_value=None, description=None,
                 options=[]):
        self._name = name
        self._value_type = value_type.lower()
        self._readonly = readonly

        self._display_name = display_name
        self._default_value = default_value
        self._description = description

        self._options = options

    @property
    def schema(self):
        """A schematic view of this entity property's attributes.

        :returns: A dictionary
        :rtype: dict
        """

        schema_obj = {
            'display_name': self._value_type,
            'description': self._description,
            'readonly': self._readonly,
            'type': self._value_type,
            'default_value': self._default_value,
        }
        if self._options:
            options = []
            for option in self._options:
                o = {'value': option.value,
                     'display_name': option.display_name}
                if self.value_type.lower() == 'flags':
                    o['default_value'] = option.default_value
                options.append(o)
            schema_obj['options'] = options
        return schema_obj

    @property
    def name(self):
        """The property's name.

        :rtype: str"""

        return self._name

    @property
    def value_type(self):
        """The property's type.

        :rtype: str"""

        return self._value_type

    @property
    def readonly(self):
        """The property's readonly status.

        :rtype: bool"""

        return self._readonly

    @property
    def display_name(self):
        """The property's display_name.

        :rtype: str"""

        return self._display_name

    @property
    def default_value(self):
        """The property's unparsed default_value.

        :rtype: str"""

        return self._default_value

    @property
    def description(self):
        """The property's description.

        :rtype: str"""

        return self._description

    @property
    def options(self):
        """The property's options.

        :rtype: list[FgdEntityPropertyOption]"""

        if self._value_type.lower() in ['choices', 'flags']:
            return self._options
        else:
            return None

    def option_by_value(self, option_value):
        """Finds a property option by its value

        :param option_value: The property option value to look for.
        :type option_value: int
        :return: A property option with matching value, None if not found, None if option_value is not of type int
        :rtype: FgdEntityPropertyOption
        """

        if not isinstance(option_value, int):
            return None

        results = (o for o in self._options if o.value == option_value)
        return next(results, None)

    def fgd_str(self):
        """A string representation of the entity property
        formated as in the a .fgd file

        :return: Fgd formated string.
        :rtype: str
        """

        # name
        fgd_str = self._name + '(' + self._value_type + ')'

        # readonly
        if self._readonly:
            fgd_str += ' readonly'

        # display name
        if self._display_name:
            fgd_str += ' : "' + self._display_name + '"'
        elif self._description or self._default_value and \
                not isinstance(self, FgdEntityInput) and \
                not isinstance(self, FgdEntityOutput):
            fgd_str += ' :'

        # default_value
        if self._default_value:
            fgd_str += ' : ' + str(self._default_value)
        elif self._description and \
                not isinstance(self, FgdEntityInput) and \
                not isinstance(self, FgdEntityOutput):
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
        elif self._value_type.lower() in ['choices', 'flags']:
            fgd_str += ' =\n\t[\n\t]'

        return fgd_str


class FgdEntityInput():
    """An entity input, as reprented in FGD file.

    :param name: The input's name.
    :type name: str

    :param input_type: The input's type.
    :type input_type: str

    :param description: The input's description.
    :type description: str
    """

    def __init__(self, name, input_type, description=''):
        self._name = name
        self._input_type = input_type
        self._description = description

    @property
    def schema(self):
        """A schematic view of this entity input's attributes.

        :returns: A dictionary
        :rtype: dict
        """

        schema_obj = {
            'type': self._input_type,
            'description': self._description,
        }
        return schema_obj

    @property
    def name(self):
        """The input's name.

        :rtype: str"""

        return self._name

    @property
    def input_type(self):
        """The input's type.

        :rtype: str"""

        return self._input_type

    @property
    def description(self):
        """The input's description.

        :rtype: str"""

        return self._description

    def fgd_str(self):
        """A string representation of the entity input
        formated as in the a .fgd file

        :return: Fgd formated string.
        :rtype: str
        """

        return 'input ' + self._name + '(' + self._input_type + ')' + \
            ' : "' + str(self.description) + '"'


class FgdEntityOutput():
    """An entity output, as reprented in FGD file.

    :param name: The output's name.
    :type name: str

    :param output_type: The output's type.
    :type output_type: str

    :param description: The output's description.
    :type description: str
    """

    def __init__(self, name, output_type, description=''):
        self._name = name
        self._output_type = output_type
        self._description = description

    @property
    def schema(self):
        """A schematic view of this entity output's attributes.

        :returns: A dictionary
        :rtype: dict
        """

        schema_obj = {
            'type': self._output_type,
            'description': self._description,
        }
        return schema_obj

    @property
    def name(self):
        """The output's name.

        :rtype: str"""
        return self._name

    @property
    def output_type(self):
        """The output's type.

        :rtype: str"""

        return self._output_type

    @property
    def description(self):
        """The output's description.

        :rtype: str"""

        return self._description

    def fgd_str(self):
        """A string representation of the entity output
        formated as in the a .fgd file

        :return: Fgd formated string.
        :rtype: str
        """

        return 'output ' + self._name + '(' + self._output_type + ')' + \
            ' : "' + str(self.description) + '"'


class FgdEntityPropertyOption():
    """A property option, as found in entity properties of type "choices" or "flags".

    :param value: The entity's value.
    :type value: str

    :param display_name: The entity's display_name.
    :type display_name: str

    :param default_value: The entity's default_value.
    :type default_value: str, optional
    """

    def __init__(self, value, display_name, default_value=None):
        self._value = value
        self._display_name = display_name
        self._default_value = default_value

    @property
    def value(self):
        """The option's value.

        :rtype: str"""

        return self._value

    @property
    def display_name(self):
        """The option's display name.

        :rtype: str"""

        return self._display_name

    @property
    def default_value(self):
        """The option's default value.

        :rtype: int"""

        return self._default_value

    def fgd_str(self):
        """A string representation of the property option
        formated as in the a .fgd file

        :return: Fgd formated string.
        :rtype: str
        """

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
