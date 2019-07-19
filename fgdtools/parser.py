from .fgd import *
import re

re_string_concat = re.compile(r'"[\t\n ]*\+[\t\n ]*"', re.IGNORECASE)
re_property_concat = re.compile(r'\:[\t ]*\n[\t\n ]', re.IGNORECASE)
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

    class_definition_str = ''
    class_properties_str = ''

    step = 'definition'
    square_depth = 0

    while True:
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
            current_line += '\n'

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

            if current_line and ']' in current_line and square_depth == 1 and \
               '[' not in current_line:
                splitted = current_line.split(']', 1)

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
                square_depth -= current_line.count('[')
                square_depth += current_line.count(']')
                class_properties_str += current_line

    return game_data


def make_class(game_data, meta_str, prop_str):
    class_metadatas_str = meta_str.strip()
    class_metadatas_str = class_metadatas_str.replace('\n', ' ')
    class_metadatas_str = class_metadatas_str.replace('\t', ' ')
    class_metadatas_str = re.sub(re_string_concat, "", class_metadatas_str)
    class_metadatas_str = re.sub(re_space_normalize, " ", class_metadatas_str)
    if class_metadatas_str:
        c = class_metadatas_parse(class_metadatas_str)
        if c:
            game_data.add_class(c)

            # if isinstance(c, FGD_entity):
            if prop_str:
                if c.type == 'MaterialExclusion' or \
                   c.type == 'AutoVisGroup':
                    for editor_data in editor_datas_parse(prop_str):
                        c.add_editor_data(editor_data)
                else:
                    for property_ in properties_parse(prop_str):
                        c.add_property(property_)


def class_metadatas_parse(class_metadatas_str):

    type = class_metadatas_str.split(' ', 1)[0].split('(')[0]
    class_metadatas_str = class_metadatas_str[len(type):]

    definitions = {}
    entity_args = []
    fgd_data = None

    if type == 'include':
        return None

    if '=' in class_metadatas_str:
        class_metadatas_str = class_metadatas_str.split('=', 1)
        definitions_str = class_metadatas_str[0].strip()
        entity_args = re.split('[\t\n ]*:[\t\n ]"',
                               class_metadatas_str[1].strip())

    else:
        definitions_str = class_metadatas_str

    definitions_strs = re.findall(re_function_like, definitions_str)
    if definitions_strs:
        for d in definitions_strs:
            definitions.update(definition_parse(d))

    if type == 'mapsize' or \
       type == 'AutoVisGroup' or \
       type == 'MaterialExclusion':
        if entity_args:
            name = entity_args[0].strip('')
        else:
            name = None

        fgd_data = FGD_entity(type, definitions, name)
    else:
        name = entity_args[0].strip()
        if len(entity_args) == 2:
            description = entity_args[1].strip('"').strip()
        else:
            description = ''

        fgd_data = FGD_entity(type, definitions,
                              name, description)

    return fgd_data


def definition_parse(definition_str):
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


def editor_datas_parse(editor_datas_str):
    editor_datas = []
    editor_datas_str = re.sub(re_string_concat, "", editor_datas_str)
    editor_datas_str = editor_datas_str.strip('\n\t ').strip('[]')
    editor_data_strs = editor_datas_str.split(']')
    for s in editor_data_strs:
        if s:
            editor_data = editor_data_parse(s)
            if editor_data:
                editor_datas.append(editor_data)

    return editor_datas


def editor_data_parse(editor_data_str):
    editor_data_strs = editor_data_str.split('[')
    if len(editor_data_strs) == 1:
        name = editor_data_str.strip('\n\t "')
        if not name:
            return None
        editor_data = FGD_editor_data(name)
    else:
        name = editor_data_strs[0].strip('\n\t "')
        if not name:
            return None
        options_strs = editor_data_strs[1].split('\n')
        options = []

        for option_str in options_strs:
            o_s = option_str.strip('\n\t "')
            if o_s:
                options.append(o_s)
        editor_data = FGD_editor_data(name, options)
    return editor_data


def properties_parse(properties_str):
    properties = []
    properties_str = re.sub(re_string_concat, "", properties_str)
    properties_str = re.sub(re_property_concat, ": ", properties_str)
    properties_str = re.sub(re_choice_definition, "= [", properties_str)
    properties_str = properties_str.strip('\n\t ')
    properties_strs = re.split(re_bracketless_return, properties_str)
    for p_str in properties_strs:
        if (p_str):
            p_str = p_str.strip('\n\t ]')
            p_str = re.sub(r'[\t ]+', " ", p_str)
            p_str = re.sub(r'\n ', "\n", p_str)
        if (p_str):
            prop = property_parse(p_str)
            properties.append(prop)

    return properties


def property_parse(property_str):
    property_parts = re.findall(re_group_around_equal, property_str)
    entity_property = None

    if not property_parts:
        return

    p_definition_str = property_parts[0].strip()

    if len(property_parts) <= 2:
        if (p_definition_str.startswith('output ')):
            p_data = property_definition_parse(p_definition_str[7:])
            entity_property = FGD_output(*p_data)

        elif (p_definition_str.startswith('input ')):
            p_data = property_definition_parse(p_definition_str[6:])
            entity_property = FGD_input(*p_data)

        else:
            p_data = property_definition_parse(p_definition_str)
            entity_property = FGD_property(*p_data)

    elif len(property_parts) > 2:

        p_options_str = property_parts[2].strip()
        p_options = property_options_parse(property_parts[2].strip())

        p_data = property_definition_parse(p_definition_str)
        entity_property = FGD_property_options(*p_data, p_options)

    return entity_property


def property_definition_parse(p_definition_str):
    p_definition_str = p_definition_str.strip()
    args = re.split(
        r'''[ ]*:[ ]*(?=(?:[^'"]|'[^']*'|"[^"]*")*$)+''', p_definition_str)

    definition_args = args[0].split('(', 1)
    p_name_str = definition_args[0].strip()

    definition_args = definition_args[1].split(')', 1)
    p_type_str = definition_args[0].strip()
    p_attr_str = definition_args[1].strip() or None

    if (len(args) > 1):
        p_args = args[1:]
    else:
        p_args = []

    return (p_name_str, p_type_str, p_attr_str, p_args)


def property_options_parse(p_options_str):
    p_options = []
    p_options_str = p_options_str.strip('[] \n\t')
    if not p_options_str:
        return p_options
    p_options_strs = p_options_str.split('\n')

    for p_option_str in p_options_strs:
        p_option = property_option_parse(p_option_str)

        if p_option:
            p_options.append(p_option)

    return p_options


def property_option_parse(p_option_str):
    p_option_str = p_option_str.strip()

    if not p_option_str:
        return None

    option = None
    p_option_parts = re.findall(re_group_around_colon, p_option_str)

    option_val = p_option_parts[0].strip()
    try:
        option_val = int(option_val)
    except:
        option_val = option_val.strip("\'\" \n\t")

    option_desc = p_option_parts[2].strip("\'\" \n\t")

    option_default = None
    if len(p_option_parts) > 4:
        default_str = p_option_parts[4].strip()

        try:
            option_default = int(default_str)
        except:
            option_default = default_str.strip("\'\" \n\t")
        option = FGD_property_option((option_val,
                                      option_desc,
                                      option_default))
    else:
        option = FGD_property_option((option_val,
                                      option_desc))

    return option
