class Fgd():
    """Contains all the data from an Fgd file such as
    entities and other editor informations.
    """

    def __init__(self):
        self._includes = []
        self._entities = []
        self._editor_data = []

    @property
    def includes(self):
        """A list of included :class:`fgdtools.Fgd`"""

        return self._includes

    @property
    def entities(self):
        """A list containing all :class:`fgdtools.FgdEntity`,
        including entities from @includes"""

        entities = []
        for include in self._includes:
            entities += include.entities
        entities += self._entities
        return entities

    @property
    def editor_data(self):
        """A list containing all :class:`fgdtools.FgdEditorData`,
        including data from @includes"""

        editor_data = []
        for include in self._includes:
            editor_data += include.editor_data
        editor_data += self._editor_data
        return editor_data

    def add_include(self, parent_fgd):
        """Adds a parent :class:`fgdtools.Fgd` to supplement this one"""

        if not parent_fgd:
            return
        self._includes.append(parent_fgd)

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
            for definition in fgd_entity.definitions:
                if 'args' not in definition or \
                   'name' not in definition or \
                   definition['name'] != 'base':
                    continue
                for entity_name in definition['args']:
                    try:
                        parent = self.entity_by_name(entity_name)
                        if parent and parent.name != fgd_entity.name:
                            fgd_entity._parents.append(parent)
                    except EntityNotFound:
                        pass
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

        :raises EntityNotFound: whenever an entity could not be found
        :return: An entity with matching name
        :rtype: FgdEntity
        """

        result = next((c for c in self._entities if isinstance(
            c, FgdEntity) and c.name == entity_name), None)
        if not result and self._includes:
            for include in self._includes:
                try:
                    result = include.entity_by_name(entity_name)
                    break
                except EntityNotFound:
                    pass
        if not result:
            raise EntityNotFound
        return result

    def fgd_str(self, collapse=False):
        """A string representation of the Fgd formated as in the a .fgd file

        :param collapse: If True, the content of included fgds will be included
                         in the output and @include statements will be removed.
                         If False, Include statements will be in the output
                         and the content of other Fgds will not be present.
        :type collapse: bool
        :return: Fgd formated string.
        :rtype: str
        """

        fgd_str = ''
        if collapse:
            for d in self.editor_data:
                if d.class_type == 'include':
                    continue
                fgd_str += d.fgd_str() + '\n\n'
            for e in self.entities:
                fgd_str += e.fgd_str() + '\n\n'
        else:
            for d in self._editor_data:
                fgd_str += d.fgd_str() + '\n\n'
            for e in self._entities:
                fgd_str += e.fgd_str() + '\n\n'
        return fgd_str


class FgdEditorData():
    """Editor data, as represented in a FGD file, usually of type such as:
    @mapsize, @MaterialExclusion or @AutoVisGroup

    :param class_type: The editor_data's type
                       ex: 'mapsize', 'MaterialExclusion', 'AutoVisGroup' etc...
    :type class_type: str

    :param name: The editor_data's display name.
    :type name: str

    :param data: The editor_data's data.
    :type data: tuple or list or dict
    """

    def __init__(self, class_type, name=None, data=None):
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
        if self._data:
            if isinstance(self._data, str):
                fgd_str += ' "' + self._data + '"'
            if isinstance(self._data, tuple):
                fgd_str += '('
                for t in self._data:
                    fgd_str += str(t) + ', '
                fgd_str = fgd_str.strip(', ') + ')'

            elif isinstance(self._data, dict):
                fgd_str += '\n['
                for k, v in self._data.items():
                    fgd_str += '\n\t"' + k + '"\n\t['
                    for i in v:
                        fgd_str += '\n\t\t"' + i + '"'
                    fgd_str += '\n\t]'
                fgd_str += '\n]'
            elif isinstance(self._data, list):
                fgd_str += '\n['
                for i in self._data:
                    fgd_str += '\n\t"' + i + '"'
                fgd_str += '\n]'
        return fgd_str


class FgdEntity():
    """An entity, as represented in a FGD file.

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

    :param spawnflags: The entity's spawnflags.
    :type spawnflags: list[FgdEntitySpawnflag], optional

    :param inputs: The entity's inputs.
    :type inputs: list[FgdEntityInput], optional

    :param output: The entity's output.
    :type output: list[FgdEntityOutput], optional
    """

    def __init__(self, class_type, definitions, name, description=None,
                 properties=[], spawnflags=[], inputs=[], outputs=[]):
        self._class_type = class_type
        self._definitions = definitions or []
        self._name = name
        self._description = description
        self._properties = properties
        self._spawnflags = spawnflags
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
            'properties': self.properties_schema,
            'inputs': self.inputs_schema,
            'outputs': self.outputs_schema,
            'spawnflags': self.spawnflags_schema
        }
        return schema_obj

    @property
    def properties_schema(self):
        """A schematic view of this entity's properties.

        :returns: A list of dictionaries
        :rtype: list[dict]
        """

        return [p.schema for p in self.properties] + \
            [{'name': 'classname',
              'default_value': self._name,
              'type': 'string',
              'readonly': True},
             {'name': 'id',
              'type': 'integer',
              'readonly': True}]

    @property
    def inputs_schema(self):
        """A schematic view of this entity's inputs.

        :returns: A list of dictionaries
        :rtype: list[dict]
        """

        return [i.schema for i in self.inputs]

    @property
    def outputs_schema(self):
        """A schematic view of this entity's outputs.

        :returns: A list of dictionaries
        :rtype: list[dict]
        """

        return [o.schema for o in self.outputs]

    @property
    def spawnflags_schema(self):
        """A schematic view of this entity's spanwnflags.

        :returns: A list of dictionaries
        :rtype: list[dict]
        """

        return [s.schema for s in self.spawnflags]

    @property
    def class_type(self):
        """The entity's type.

        :rtype: str"""

        return self._class_type

    @property
    def parents(self):
        """The entity's parent entities, as defined in the entity's \
        base(definition).

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

        Note: As in the way Hammer behaves,
        properties of the same name are overridden

        :rtype: list[FgdEntityProperty]"""

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
    def spawnflags(self):
        """The entity's spawnflags, including inherited spawnflags.

        Note: As in the way Hammer behaves, spawnflags definition
        will merge with inherited definitions only if there is no
        collision between values. if there is a collision, only
        the latest definition will be taken into account.

        :rtype: list[FgdEntitySpawnflag]"""

        spawnflags = [] + self._spawnflags
        ineligible_parents = []
        for p in self._parents:
            for s in p.spawnflags:
                if next((x for x in self._spawnflags if x.value == s.value), None):
                    ineligible_parents.append(p)
                    continue
            if p not in ineligible_parents:
                spawnflags += p.spawnflags
        return spawnflags

    @property
    def inputs(self):
        """The entity's inputs, including inherited inputs.

        Note: As in the way Hammer behaves, inputs cannot be overridden.
        All duplicate inputs are ignored, only the oldest is returned.

        :rtype: list[FgdEntityInput]"""

        inputs = {}
        for t in self._parents:
            for p in t.inputs:
                inputs[p.name] = p
        for p in self._inputs:
            if p.name not in inputs:
                inputs[p.name] = p

        inputs_array = []
        for k, v in inputs.items():
            inputs_array.append(v)

        return inputs_array

    @property
    def outputs(self):
        """The entity's outputs, including inherited outputs.

        Note: As in the way Hammer behaves, outputs cannot be overridden.
        All duplicate outputs are returned.

        :rtype: list[FgdEntityOutput]"""

        outputs = self._outputs or []
        for t in self._parents:
            outputs = outputs + t.outputs

        return outputs

    def property_by_name(self, prop_name):
        """Finds an entity property by its name

        :param prop_name: The entity property name to look for.
        :type prop_name: str
        :raises PropertyNotFound: whenever an entity property could not be found
        :return: An entity property with matching name.
        :rtype: FgdEntityProperty
        """

        result = next(
            (p for p in self.properties if p.name == prop_name), None)
        if not result:
            raise PropertyNotFound
        return result

    def spawnflag_by_value(self, spawnflag_value):
        """Finds a property choice by its value

        :param spawnflag_value: The property spawnflag value to look for.
        :type spawnflag_value: int
        :raises SpawnflagNotFound: Whenever an entity spawnflag could not be found.
        :return: An entity spawnflag with matching value.
        :rtype: FgdEntitySpawnflag
        """

        result = next(
            (o for o in self._spawnflags if o.value == spawnflag_value), None)
        if not result:
            raise SpawnflagNotFound
        return result

    def input_by_name(self, input_name):
        """Finds an entity input by its name

        :param input_name: The entity input name to look for.
        :type input_name: str
        :raises InputNotFound: whenever an entity input could not be found
        :return: An entity input with matching name.
        :rtype: FgdEntityInput
        """

        result = next((i for i in self.inputs if i.name == input_name), None)
        if not result:
            raise InputNotFound
        return result

    def output_by_name(self, output_name):
        """Finds an entity output by its name

        :param output_name: The entity output name to look for.
        :type output_name: str
        :raises OutputNotFound: whenever an entity output could not be found
        :return: An entity output with matching name.
        :rtype: FgdEntityOutput
        """

        result = next((o for o in self.outputs if o.name == output_name), None)
        if not result:
            raise InputNotFound
        return result

    def fgd_str(self):
        """A string representation of the FgdEntity formated as in the a .fgd file

        :return: Fgd formated string.
        :rtype: str
        """

        fgd_str = '@' + self._class_type
        for d in self._definitions:
            fgd_str += ' ' + d['name']
            if 'args' in d:
                fgd_str += "("
                for arg in d['args']:
                    fgd_str += arg + ', '
                fgd_str = fgd_str.strip(', ') + ')'

        if self._name:
            fgd_str += ' = ' + self._name
        if self._description:
            fgd_str += ' : "' + self._description + '"'
        if self._properties or self._spawnflags or \
                self._inputs or self._outputs:
            fgd_str += "\n["
            for prop in self._properties:
                fgd_str += "\n\t" + prop.fgd_str()
            if self._spawnflags:
                fgd_str += "\n\tspawnflags(flags) =\n\t["
                for flag in self._spawnflags:
                    fgd_str += "\n\t\t" + flag.fgd_str()
                fgd_str += "\n\t]"
            for input in self._inputs:
                fgd_str += "\n\t" + input.fgd_str()
            for output in self._outputs:
                fgd_str += "\n\t" + output.fgd_str()
            fgd_str += "\n]"
        else:
            fgd_str += " []"

        return fgd_str


class FgdEntityProperty():
    """An entity property, as represented in a FGD file.

    :param name: The property's name.
    :type name: str

    :param value_type: The property's value type
                       ex:'integer', 'float', 'choices', etc...
    :type value_type: str

    :param name: The property's readonly status.
    :type name: bool, optional

    :param display_name: The property's display name.
    :type display_name: str, optional

    :param default_value: The property's unparsed default value.
    :type default_value: str, optional

    :param description: The property's description.
    :type description: str, optional

    :param choices: The property's choices.
                    (applicable only to types "choices" and "flags")
    :type choices: list[FgdEntityPropertyChoice], optional
    """

    def __init__(self, name, value_type, readonly=False, display_name=None,
                 default_value=None, description=None, choices=[]):
        self._name = name
        self._value_type = value_type.lower()
        self._readonly = readonly
        self._display_name = display_name
        self._default_value = default_value
        self._description = description
        self._choices = choices

    @property
    def schema(self):
        """A schematic view of this entity property's attributes.

        :returns: A dictionary
        :rtype: dict
        """

        schema_obj = {
            'name': self._name,
            'display_name': self._display_name,
            'description': self._description,
            'readonly': self._readonly,
            'type': self._value_type,
            'default_value': self._default_value,
        }
        if self._choices:
            choices = []
            for choice in self._choices:
                o = {'value': choice.value,
                     'display_name': choice.display_name}
                if self.value_type.lower() == 'flags':
                    o['default_value'] = choice.default_value
                choices.append(o)
            schema_obj['choices'] = choices
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
    def choices(self):
        """The property's choices.

        :rtype: list[FgdEntityPropertyChoice]"""

        if self._value_type.lower() in ['choices', 'flags']:
            return self._choices
        else:
            return None

    def choice_by_value(self, choice_value):
        """Finds a property choice by its value

        :param choice_value: The property choice value to look for.
        :type choice_value: int
        :raises ChoiceNotFound: Whenever a property choice could not be found.
        :return: A property choice with matching value
        :rtype: FgdEntityPropertyChoice
        """

        result = next(
            (o for o in self._choices if o.value == choice_value), None)
        if not result:
            raise ChoiceNotFound
        return result

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
            fgd_str += ' : '
            if isinstance(self._default_value, int):
                fgd_str += str(self._default_value)
            else:
                fgd_str += '"' + str(self._default_value) + '"'

        elif self._description and \
                not isinstance(self, FgdEntityInput) and \
                not isinstance(self, FgdEntityOutput):
            fgd_str += ' :'

        # description
        if self._description:
            fgd_str += ' : "' + self._description + '"'

        # choices
        if self.choices:
            fgd_str += ' =\n\t[\n'
            for choice in self._choices:
                fgd_str += '\t\t' + choice.fgd_str() + '\n'
            fgd_str += '\t]'
        elif self._value_type.lower() in ['choices', 'flags']:
            fgd_str += ' =\n\t[\n\t]'

        return fgd_str


class FgdEntityInput():
    """An entity input, as represented in FGD file.

    :param name: The input's name.
    :type name: str

    :param value_type: The input's type.
    :type value_type: str

    :param description: The input's description.
    :type description: str
    """

    def __init__(self, name, value_type, description=''):
        self._name = name
        self._value_type = value_type
        self._description = description

    @property
    def schema(self):
        """A schematic view of this entity input's attributes.

        :returns: A dictionary
        :rtype: dict
        """

        schema_obj = {
            'name': self._name,
            'type': self._value_type,
            'description': self._description,
        }
        return schema_obj

    @property
    def name(self):
        """The input's name.

        :rtype: str"""

        return self._name

    @property
    def value_type(self):
        """The input's type.

        :rtype: str"""

        return self._value_type

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

        return 'input ' + self._name + '(' + self._value_type + ')' + \
            ' : "' + str(self.description) + '"'


class FgdEntityOutput():
    """An entity output, as represented in FGD file.

    :param name: The output's name.
    :type name: str

    :param value_type: The output's type.
    :type value_type: str

    :param description: The output's description.
    :type description: str
    """

    def __init__(self, name, value_type, description=''):
        self._name = name
        self._value_type = value_type
        self._description = description

    @property
    def schema(self):
        """A schematic view of this entity output's attributes.

        :returns: A dictionary
        :rtype: dict
        """

        schema_obj = {
            'name': self._name,
            'type': self._value_type,
            'description': self._description,
        }
        return schema_obj

    @property
    def name(self):
        """The output's name.

        :rtype: str"""

        return self._name

    @property
    def value_type(self):
        """The output's type.

        :rtype: str"""

        return self._value_type

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

        return 'output ' + self._name + '(' + self._value_type + ')' + \
            ' : "' + str(self.description) + '"'


class FgdEntityPropertyChoice():
    """A property choice, as found in entity properties of type "choices".

    :param value: The choice's value.
    :type value: str

    :param display_name: The choice's display_name.
    :type display_name: str
    """

    def __init__(self, value='', display_name='---None---'):
        self._value = value
        self._display_name = display_name

    @property
    def value(self):
        """The choice's value.

        :rtype: str"""

        return self._value

    @property
    def display_name(self):
        """The choice's display name.

        :rtype: str"""

        return self._display_name

    def fgd_str(self):
        """A string representation of the property choice
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

        return fgd_str


class FgdEntitySpawnflag():
    """An entity Spawnflag.

    :param value: The spawnflag's value.
    :type value: int

    :param display_name: The spawnflag's display_name.
    :type display_name: str

    :param default_value: The spawnflag's default_value.
    :type default_value: bool
    """

    def __init__(self, value='', display_name='', default_value=None):
        self._value = value
        self._display_name = display_name
        self._default_value = default_value

    @property
    def value(self):
        """The spawnflag's value.

        :rtype: int"""

        return self._value

    @property
    def display_name(self):
        """The spawnflag's display name.

        :rtype: str"""

        return self._display_name

    @property
    def default_value(self):
        """The spawnflag's default value.

        :rtype: int"""

        return self._default_value

    @property
    def schema(self):
        """A schematic view of this Spawnflag.

        :returns: A dictionary
        :rtype: dict
        """

        schema_obj = {
            'value': self._value,
            'display_name': self._display_name,
            'default_value': self._default_value
        }
        return schema_obj

    def fgd_str(self):
        """A string representation of the spawnflag
        formated as in the a .fgd file

        :return: Fgd formated string.
        :rtype: str
        """

        fgd_str = str(self._value) + ' : "'
        fgd_str += self._display_name + '" : '
        fgd_str += str(int(self.default_value))

        return fgd_str


class EntityNotFound(Exception):
    """Raised when an entity could not be found"""
    pass


class PropertyNotFound(Exception):
    """Raised when an entity property could not be found"""
    pass


class InputNotFound(Exception):
    """Raised when an entity input could not be found"""
    pass


class OutputNotFound(Exception):
    """Raised when an entity output could not be found"""
    pass


class SpawnflagNotFound(Exception):
    """Raised when an entity Spawnflag could not be found"""
    pass


class ChoiceNotFound(Exception):
    """Raised when a property choice could not be found"""
    pass
