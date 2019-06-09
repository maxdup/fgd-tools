from .fgd import *
import re

re_string_concat = re.compile(r'"[\t\n ]*\+[\t\n ]*"', re.IGNORECASE)
re_space_normalize = re.compile(r'[\t\n ]+', re.IGNORECASE)
re_space_normalize = re.compile(r'[\t ]+', re.IGNORECASE)
re_function_like = re.compile(r'[^\( \n\t]*\([^\(]*\)', re.IGNORECASE)
re_bracketless_return = re.compile(
    r'(?:([^\n]*=[\n\t ]*\[[^\]]*\])+)|\n', re.IGNORECASE)

re_quoteless_colon = re.compile(
    r' *: *(?=([^"]*"[^"]*")*[^"]*$)', re.IGNORECASE)

re_group_around_equal = re.compile(
    r'(?:"[^"]*"|[^=])*[^=]*', re.IGNORECASE)
re_group_around_colon = re.compile(
    r'(?:"[^"]*"|[^:])*[^:]*', re.IGNORECASE)
re_choice_definition = re.compile(r'=[\t\n ]*\[', re.IGNORECASE)


def FgdParse(file):

    reader = open(file, "r", encoding="iso-8859-1")

    game_data = FGD()

    # Search for @includes
    while True:
        current_line = reader.readline()
        if not current_line:
            break

        elif current_line.startswith('@include'):
            current_line = current_line.strip('@include').strip(' ').strip('"')
            fgdName = current_line.split('"')[0]
            base_game_data = FgdParse(fgdName)
            game_data.include(base_game_data)

    reader.seek(0)

    lines = 0
    class_definition_str = ''
    class_properties_str = ''

    step = 'definition'
    square_depth = 0

    while True:
        lines += 1

        current_line = reader.readline()

        # file ended
        if not current_line:
            break
        # skip comments
        if current_line.startswith('//'):
            continue
        # remove comment
        if '//' in current_line:
            current_line = current_line.split('//')[0]

        while current_line.strip():
            reject = True
            if current_line and '@' in current_line:

                splitted = current_line.split('@', 1)

                # otherwise it's part of a string
                if splitted[0].count('"') % 2 == 0:

                    reject = False
                    # before @
                    if step == 'definition':
                        class_definition_str += splitted[0]
                    elif step == 'properties':
                        class_properties_str += splitted[0]

                    # after @
                    if len(splitted) == 2:
                        current_line = splitted[1]
                    else:
                        current_line = ''

                    step = 'definition'

                    make_class(game_data,
                               class_definition_str,
                               class_properties_str)
                    class_definition_str = ''
                    class_properties_str = ''

            if current_line and '[' in current_line and square_depth == 0:

                splitted = current_line.split('[', 1)

                # otherwise it's part of a string
                if splitted[0].count('"') % 2 == 0:

                    square_depth += 1
                    reject = False

                    # before [
                    if step == 'definition':
                        class_definition_str += splitted[0]
                    elif step == 'properties':
                        class_properties_str += splitted[0]

                    # after [
                    if len(splitted) == 2:
                        current_line = splitted[1]
                    else:
                        current_line = ''

                    step = 'properties'

            if current_line and ']' in current_line and square_depth == 1:

                splitted = current_line.split('@', 1)

                # otherwise it's part of a string
                if splitted[0].count('"') % 2 == 0:

                    square_depth = 0
                    reject = False

                    # before ]
                    if step == 'definition':
                        class_definition_str += splitted[0]
                    elif step == 'properties':
                        class_properties_str += splitted[0]

                    # after ]
                    if len(splitted) == 2:
                        current_line = splitted[1]
                    else:
                        current_line = ''

                    step = ''

                    make_class(game_data,
                               class_definition_str,
                               class_properties_str)
                    class_definition_str = ''
                    class_properties_str = ''

            if reject:
                break

        if current_line:
            if step == 'definition':
                class_definition_str += current_line

            elif step == 'properties':
                square_depth += current_line.count(']')
                square_depth -= current_line.count('[')
                class_properties_str += current_line

    return game_data


def make_class(game_data, def_str, prop_str):
    class_definition = def_str.strip()
    class_definition = class_definition.replace('\n', ' ')
    class_definition = class_definition.replace('\t', ' ')
    class_definition = re.sub(re_string_concat, "", class_definition)
    class_definition = re.sub(re_space_normalize, " ", class_definition)
    if class_definition:
        c = data_definitions_parse(class_definition)
        if c:
            game_data.add_class(c)
            data_properties_parse(prop_str)


def data_definitions_parse(class_definitions):

    data_type = class_definitions.split(' ', 1)[0].split('(')[0]
    data_properties = {}
    class_definitions = class_definitions[len(data_type):]
    entity_args = []
    fgd_data = None

    if '=' in class_definitions:
        class_definitions = class_definitions.split('=', 1)
        data_properties_str = class_definitions[0].strip()
        entity_args = re.split('[\t\n ]*:[\t\n ]"',
                               class_definitions[1].strip())

    else:
        data_properties_str = class_definitions

    data_properties_str = re.findall(re_function_like, data_properties_str)
    if data_properties_str:
        for p in data_properties_str:
            data_properties.update(data_definition_parse(p))

    if data_type == 'include' or \
            data_type == 'mapsize' or \
            data_type == 'AutoVisGroup' or \
            data_type == 'MaterialExclusion':
        fgd_data = FGD_data(data_type, data_properties)
    else:
        entity_name = entity_args[0].strip()
        if len(entity_args) == 2:
            entity_desc = entity_args[1].strip('"').strip()
        else:
            entity_desc = ''

        fgd_data = FGD_entity(data_type, data_properties,
                              entity_name, entity_desc)

    return fgd_data


def data_definition_parse(definition_str):
    definition = {}
    definition_parts = definition_str.split('(')
    definition_name = definition_parts[0].strip()
    definition_params = definition_parts[1].strip().strip(')').strip()

    if (definition_params):
        definition[definition_name] = re.split(
            '[\t\n ]*\,[\t\n ]*', definition_params)
    else:
        definition[definition_name] = []
    return definition


def data_properties_parse(properties_str):
    properties = {}
    properties_str = re.sub(re_string_concat, "", properties_str)
    properties_str = re.sub(re_choice_definition, "= [", properties_str)
    properties_str = properties_str.strip().strip(']').strip()
    properties_strs = re.split(re_bracketless_return, properties_str)

    for p_str in properties_strs:
        if (p_str):
            p_str = p_str.strip()
            p_str = re.sub(r'[\t ]+', " ", p_str)
            p_str = re.sub(r'\n ', "\n", p_str)
        if (p_str):
            data_property_parse(p_str)


def data_property_parse(property_str):
    property_parts = re.findall(re_group_around_equal, property_str)
    entity_property = None

    if not property_parts:
        return

    p_definition_str = property_parts[0].strip()

    if len(property_parts) <= 2:
        if (p_definition_str.startswith('output ')):
            p_data = data_property_definition_parse(p_definition_str[7:])
            entity_property = FGD_entity_output(*p_data)

        elif (p_definition_str.startswith('input ')):
            p_data = data_property_definition_parse(p_definition_str[6:])
            entity_property = FGD_entity_input(*p_data)

        else:
            p_data = data_property_definition_parse(p_definition_str)
            entity_property = FGD_entity_property(*p_data)

    elif len(property_parts) > 2:

        p_options_str = property_parts[2].strip()
        p_options = data_property_options_parse(property_parts[2].strip())

        p_data = data_property_definition_parse(p_definition_str)
        entity_property = FGD_entity_property_options(*p_data, p_options)

    return entity_property


def data_property_definition_parse(p_definition_str):
    p_definition_str = p_definition_str.strip()

    args = re.split(
        r'''[ ]*:[ ]*(?=(?:[^'"]|'[^']*'|"[^"]*")*$)+''', p_definition_str)
    p_name_str = args[0].split('(')[0]
    p_type_str = args[0][len(p_name_str):].strip('()').strip()

    if (len(args) > 1):
        p_args = args[1:]
    else:
        p_args = []

    return (p_name_str, p_type_str, p_args)


def data_property_options_parse(p_options_str):
    return []
