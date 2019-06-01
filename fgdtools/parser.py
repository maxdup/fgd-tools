from . import fgd
import re

re_string_concat = re.compile(r'"[\t\n ]*\+[\t\n ]*"', re.IGNORECASE)
re_space_normalize = re.compile(r'[\t\n ]+', re.IGNORECASE)
re_function_like = re.compile(r'[^\( \n\t]*\([^\(]*\)', re.IGNORECASE)


def FgdParse(file):

    reader = open(file, "r", encoding="iso-8859-1")

    game_data = fgd.FGD()

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
        c = data_definition_parse(class_definition)
        if c:
            game_data.add_class(c)

            # todo parse properties


def data_definition_parse(class_definition):

    data_type = class_definition.split(' ', 1)[0].split('(')[0]
    data_properties = {}
    class_definition = class_definition[len(data_type):]
    entity_args = []
    fgd_data = None

    if '=' in class_definition:
        class_definition = class_definition.split('=', 1)
        data_properties_str = class_definition[0].strip()
        entity_args = re.split('[\t\n ]*:[\t\n ]"', class_definition[1].strip())

    else:
        data_properties_str = class_definition

    data_properties_str = re.findall(re_function_like, data_properties_str)
    if data_properties_str:
        for p in data_properties_str:
            data_properties.update(data_properties_parse(p))

    if data_type == 'include' or \
       data_type == 'mapsize' or \
       data_type == 'AutoVisGroup' or \
       data_type == 'MaterialExclusion':
        fgd_data = fgd.FGD_data(data_type, data_properties)
    else:
        entity_name = entity_args[0].strip()
        if len(entity_args) == 2:
            entity_desc = entity_args[1].strip('"').strip()
        else:
            entity_desc = ''

        fgd_data = fgd.FGD_entity(data_type, data_properties,
                                  entity_name, entity_desc)

    return fgd_data


def data_properties_parse(property_str):
    property = {}
    property_parts = property_str.split('(')
    property_name = property_parts[0].strip()
    property_params = property_parts[1].strip().strip(')').strip()

    if (property_params):
        property[property_name] = re.split(
            '[\t\n ]*\,[\t\n ]*', property_params)
    else:
        property[property_name] = []
    return property
