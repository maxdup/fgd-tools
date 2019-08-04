import os
from pyparsing import *
from .fgd import *


# Basic parsers

pp_name = Word(alphanums+'_')
pp_nums = Word(nums+'-.')
pp_value = Word(nums+'-. ')  # maybe space delimited vertex

pp_quoted = Combine(QuotedString(
    '"') + Optional(OneOrMore(Suppress('+') + QuotedString('"'))), adjacent=False)
pp_comment = Literal('//') + SkipTo(lineEnd)

pp_default_value = QuotedString('"') | pp_nums

# property options parsers


def make_EntityPropertyOption(data):
    return FgdEntityPropertyOption(**data)


pp_EntityPropertyOptionValue = pp_nums.setParseAction(tokenMap(int)) | pp_quoted
pp_EntityPropertyOption = pp_EntityPropertyOptionValue.setResultsName('value') + \
    ':' + QuotedString('"').setResultsName('display_name') + \
    Optional(
        ':' + pp_nums.setResultsName('default_value').setParseAction(tokenMap(int))) + Optional(Suppress(pp_comment))
pp_EntityPropertyOption

pp_EntityPropertyOptions = Suppress('[') + \
    Optional(OneOrMore(pp_EntityPropertyOption.setParseAction(
        make_EntityPropertyOption)).setResultsName('options')) + \
    Suppress(']')


# Property parsers

def make_EntityProperty(property_data):
    prop = FgdEntityProperty(**property_data.asDict())
    return prop


pp_description = Optional(pp_quoted.setResultsName('description'))
pp_property_name = pp_name.setResultsName('name')
pp_property_value_type = pp_name.setResultsName('value_type')
pp_property_display_name = Optional(pp_quoted.setResultsName('display_name'))
pp_property_default = Optional(pp_default_value.setResultsName('default_value'))
pp_property_readonly = Literal('readonly').setParseAction(
    bool).setResultsName('readonly')


pp_EntityProperty = pp_property_name + '(' + pp_property_value_type + ')' + \
    Optional(pp_property_readonly) + \
    Optional(':' + pp_property_display_name) + \
    Optional(':' + pp_property_default) + \
    Optional(':' + pp_description) + \
    Optional('=' + pp_EntityPropertyOptions)
pp_EntityProperty.setParseAction(make_EntityProperty)


def make_EntityIO(io_data):
    data = io_data.asDict()
    io_type = data.pop('io_type')
    if io_type == 'input':
        return FgdEntityInput(**data)
    elif io_type == 'output':
        return FgdEntityOutput(**data)
    return None


pp_io_type = (Literal('output') | Literal('input')).setResultsName('io_type')

pp_EntityIO = pp_io_type + pp_property_name + \
    '(' + pp_property_value_type + ')' + ':' + pp_description
pp_EntityIO.setParseAction(make_EntityIO)

pp_properties = Suppress(pp_comment) | pp_EntityIO | pp_EntityProperty
pp_EntityProperties = Suppress('[') + \
    Optional(OneOrMore(pp_properties).setResultsName('properties')) + \
    Suppress(']')


# Entity parsers

def make_Entity(entity_data):
    dataDict = entity_data.asDict()
    if 'definitions' not in dataDict:
        dataDict['definitions'] = []
    entity = FgdEntity(**dataDict)
    return entity


def make_Entity_definition(definition):
    return definition.asDict()


pp_entity_class_type = pp_name.setResultsName('class_type')
pp_entity_name = pp_name.setResultsName('name')
pp_entity_description = Optional(':' + pp_description)

pp_entity_definition_arg = pp_value | pp_name | QuotedString(
    '"', unquoteResults=False)
pp_entity_definition_args = Optional(delimitedList(
    pp_entity_definition_arg))

pp_entity_definition = pp_name.setResultsName('name') + \
    Optional(Suppress('(') + pp_entity_definition_args +
             Suppress(')')).setResultsName('args')


pp_entity_definitions = Optional(
    OneOrMore(pp_entity_definition.setParseAction(make_Entity_definition))).setResultsName('definitions')

pp_entity = Suppress('@') + pp_entity_class_type + \
    pp_entity_definitions + '=' + pp_entity_name + \
    pp_entity_description + pp_EntityProperties
pp_entity.setParseAction(make_Entity)


# Editor data parsers

def make_include(include):
    return FgdEditorData(**include.asDict())


pp_include = Literal('@') + Literal('include').setResultsName('class_type') + \
    pp_quoted.setResultsName('data')
pp_include.setParseAction(make_include)


def make_editor_data(results):
    try:
        editor_data = FgdEditorData(**results.asDict())
    except Exception as e:
        print(e)
        return None
    return editor_data


def make_mapsize(results):
    res = results.asDict()
    res['data'] = tuple(res['data'])
    editor_data = FgdEditorData(**res)
    return editor_data


pp_mapsize_data = pp_nums + Suppress(',') + pp_nums
pp_mapsize = Literal('@') + \
    Literal('mapsize').setResultsName('class_type') + \
    Suppress(
        '(') + pp_mapsize_data.setResultsName('data') + Suppress(')')
pp_mapsize.setParseAction(make_mapsize)

pp_material_ex_data = OneOrMore(QuotedString('"'))
pp_material_ex = Literal('@') + \
    Literal('MaterialExclusion').setResultsName('class_type') + \
    Suppress(
    '[') + Optional(pp_material_ex_data).setResultsName('data') + Suppress(']')
pp_material_ex.setParseAction(make_editor_data)


def make_autovisgroup(results):
    return {results['key']: results['value']}


def make_autovisgroups(results):
    data = {}
    for r in results:
        data.update(r)
    return data


pp_autovisgroup_data_list = QuotedString('"').setResultsName('key') + \
    Suppress('[') + \
    Optional(OneOrMore(QuotedString('"'))).setResultsName('value') + \
    Suppress(']')
pp_autovisgroup_data = Suppress('[') + \
    Optional(OneOrMore(pp_autovisgroup_data_list.setParseAction(
        make_autovisgroup))).setParseAction(make_autovisgroups).setResultsName('data') + Suppress(']')
pp_autovisgroup = Literal('@') + \
    Literal('AutoVisGroup').setResultsName('class_type') + \
    Literal('=') + pp_quoted.setResultsName('name') + pp_autovisgroup_data
pp_autovisgroup.setParseAction(make_editor_data)

pp_fgd = OneOrMore(pp_mapsize | pp_include | pp_material_ex |
                   pp_autovisgroup | pp_entity).ignore(pp_comment)


def FgdParse(filename):
    """Parse a .fgd file and return a FGD object
    :param filename: A path to the .fgd file to be parsed
    :type filename: string
    :return: a FGD object
    :rtype: FGD
    """
    game_data = Fgd()

    filepath = os.path.abspath(filename)
    filedir = os.path.dirname(filepath)

    try:
        results = pp_fgd.parseFile(open(filename, "r", encoding="iso-8859-1"))
    except Exception as e:
        raise

    for i in results:
        if isinstance(i, FgdEditorData):
            if i.class_type == 'include':
                include_path = os.path.join(filedir, i.data)
                base_game_data = FgdParse(include_path)
                game_data._entities.extend(list(base_game_data.entities))
                game_data._editor_data.extend(list(base_game_data.editor_data))
            else:
                game_data.add_editor_data(i)
    for i in results:
        if isinstance(i, FgdEntity):
            game_data.add_entity(i)

    return game_data
