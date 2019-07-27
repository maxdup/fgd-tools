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
    """Parse a .fgd file and return a FGD object

    :param file: A path to the .fgd file to be parsed
    :type file: string
    :return: a FGD object
    :rtype: FGD
    """
    reader = open(file, "r", encoding="iso-8859-1")

    game_data = Fgd()

    # Search for @includes
    while True:
        current_line = reader.readline()
        if not current_line:
            break

        elif current_line.startswith('@include'):
            current_line = current_line.strip('@include').strip(' ').strip('"')
            fgdName = current_line.split('"')[0]
            base_game_data = FgdParse(fgdName)
            game_data._entities.extend(list(base_game_data.entities))
            game_data._editor_data.extend(list(base_game_data.editor_data))

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
        if class_metadatas_str.startswith('include'):
            return
        if class_metadatas_str.startswith('MaterialExclusion') or \
           class_metadatas_str.startswith('AutoVisGroup') or \
           class_metadatas_str.startswith('mapsize'):
            return
            editor_data = editor_data_parse(class_metadatas_str, prop_str)
            if editor_data:
                game_data.add_editor_data(editor_data)
        else:
            entity = entity_parse(class_metadatas_str, prop_str)
            if entity:
                game_data.add_entity(entity)


def editor_data_parse(meta_str, prop_str):
    d_type = ''
    d_name = None
    d_data = None

    d_type = re.split('[ =\(]', meta_str)[0]
    meta_str = meta_str[len(d_type):].strip()
    if meta_str.startswith('='):
        meta_str = meta_str.lstrip('= "')
        d_name = meta_str.split('"', 1)[0]
        meta_str = meta_str[len(d_name):].lstrip('"\n\t ')
    if meta_str.startswith('('):
        d_data = ()
        tups = meta_str.strip('()\n\t ').split(',')
        for t in tups:
            d_data = d_data + (t.strip(),)
    elif prop_str.strip():
        if '[' in prop_str:
            d_data = {}
            datas = prop_str.split(']')

            for data in datas:
                if not data.strip():
                    continue
                ds = data.strip().split('[', 1)

                d_list = []
                d_key = ds[0].strip('" \n\t')
                dl = ds[1].split('\n')
                for d in dl:
                    d_val = d.strip('" \n\t')
                    if d_val:
                        d_list.append(d.strip('" \n\t'))
                d_data[d_key] = d_list
        else:
            d_data = []
            datas = prop_str.split('\n')
            for data in datas:
                d = data.strip('" \n\t')
                if d:
                    d_data.append(d.strip())
    data = FgdEditorData(d_type, d_name, d_data)
    return data


def entity_parse(meta_str, prop_str):
    properties = []
    inputs = []
    outputs = []

    e_type = meta_str.split(' ', 1)[0].split('(')[0]
    meta_str = meta_str[len(e_type):]

    definitions = []
    entity_args = []
    fgd_data = None

    if '=' in meta_str:
        meta_str = meta_str.split('=', 1)
        definitions_str = meta_str[0].strip()
        entity_args = re.split('[\t\n ]*:[\t\n ]"',
                               meta_str[1].strip())

    else:
        definitions_str = meta_str

    definitions_strs = re.findall(re_function_like, definitions_str)
    if definitions_strs:
        for d in definitions_strs:
            definitions.append(definition_parse(d))

    name = entity_args[0].strip()
    if len(entity_args) == 2:
        description = entity_args[1].strip('"').strip()
    else:
        description = ''

    for property_ in properties_parse(prop_str):
        if (isinstance(property_, FgdEntityInput)):
            inputs.append(property_)
        elif (isinstance(property_, FgdEntityOutput)):
            outputs.append(property_)
        elif (isinstance(property_, FgdEntityProperty)):
            properties.append(property_)

    if not e_type or not name:
        return None

    entity = FgdEntity(e_type, definitions, name, description,
                       properties, inputs, outputs)

    return entity


def definition_parse(definition_str):
    definition = {}
    definition_parts = definition_str.split('(')
    definition['name'] = definition_parts[0].strip()
    definition_params = definition_parts[1].strip().strip(')').strip()

    if (definition_params):
        definition['args'] = re.split(
            '[\t\n ]*\,[\t\n ]*', definition_params)
    else:
        definition['args'] = []

    return definition


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
            if 'display_name' in p_data:
                p_data['description'] = p_data.pop('display_name')
            p_data['output_type'] = p_data.pop('value_type')
            entity_property = FgdEntityOutput(**p_data)

        elif (p_definition_str.startswith('input ')):
            p_data = property_definition_parse(p_definition_str[6:])
            if 'display_name' in p_data:
                p_data['description'] = p_data.pop('display_name')
            p_data['input_type'] = p_data.pop('value_type')
            entity_property = FgdEntityInput(**p_data)

        else:
            p_data = property_definition_parse(p_definition_str)
            entity_property = FgdEntityProperty(**p_data)

    elif len(property_parts) > 2:

        p_options_str = property_parts[2].strip()
        p_options = property_options_parse(property_parts[2].strip())
        p_data = property_definition_parse(p_definition_str)
        p_data['options'] = p_options
        entity_property = FgdEntityProperty(**p_data)

    return entity_property


def property_definition_parse(p_definition_str):
    p_definition_str = p_definition_str.strip()
    args = re.split(
        r'''[ ]*:[ ]*(?=(?:[^'"]|'[^']*'|"[^"]*")*$)+''', p_definition_str)

    definition_args = args[0].split('(', 1)
    p_name_str = definition_args[0].strip()

    definition_args = definition_args[1].split(')', 1)
    p_type_str = definition_args[0].strip()
    p_readonly = bool(definition_args[1].strip() or False)

    kargs = {
        'name': p_name_str,
        'value_type': p_type_str,
    }
    if p_readonly:
        kargs['readonly'] = True
    if (len(args) > 1):
        kargs['display_name'] = args[1].strip('" \n\t')
    if (len(args) > 2):
        kargs['default_value'] = args[2].strip()
    if (len(args) > 3):
        kargs['description'] = args[3].strip('" \n\t')
    return kargs


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
    option = FgdEntityPropertyOption(option_val,
                                     option_desc,
                                     option_default)

    return option
