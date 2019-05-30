from . import fgd
import re

re_string_concat = re.compile(r'"[\t\n ]*\+[\t\n ]*"', re.IGNORECASE)
re_space_normalize = re.compile(r'[\t\n ]+', re.IGNORECASE)
re_function_like = re.compile(r'[^\( \n\t]*\([^\(]*\)', re.IGNORECASE)


def FgdParse(file):

    reader = open(file, "r", encoding="iso-8859-1")

    eof = False
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
    while not eof:
        current_line = reader.readline()
        if not current_line:
            break

        class_definition_str = ''
        class_properties_str = ''

        lines += 1

        # Skip comments
        while current_line.startswith('//') or not current_line.strip():
            current_line = reader.readline()

        if '//' in current_line:
            current_line = current_line.split('//')[0]

        # Get class definition
        if current_line.startswith('@'):
            class_definition_str += current_line
            current_line = reader.readline().strip()
            while True:
                if '@' in current_line:
                    current_line_parts = current_line.split('@', 1)
                    class_definition_str += current_line_parts[0].strip()
                    if len(current_line_parts) > 1:
                        current_line = current_line_parts[1]
                    else:
                        current_line = ''
                    break
                elif '[' in current_line:
                    current_line_parts = current_line.split('[', 1)
                    class_definition_str += current_line_parts[0].strip()
                    if len(current_line_parts) > 1:
                        current_line = current_line_parts[1]
                    else:
                        current_line = ''
                    break
                elif '//' in current_line:
                    current_line = current_line.split('//')[0].strip()
                if current_line:
                    class_definition_str += current_line

                current_line = reader.readline()

            class_definition_str = class_definition_clean(class_definition_str)
            if class_definition_str:
                class_definition_parse(class_definition_str)

        # Get class properties
        if '[' in current_line:
            depth = 0
            while ']' not in current_line or depth > 1:
                if not current_line.startswith('//'):
                    if current_line.strip().startswith('['):
                        depth += 1
                        current_line = current_line.strip('[')
                    elif current_line.strip().startswith(']'):
                        depth -= 1
                        current_line = current_line.strip(']')
                    if current_line.strip():
                        class_properties_str += current_line.strip() + '\n'
                current_line = reader.readline()
            if class_properties_str and False:
                print('---------------')
                print(class_properties_str)
    return game_data


def class_definition_clean(class_definition):
    class_definition = class_definition.strip()
    class_definition = class_definition.replace('\n', ' ')
    class_definition = class_definition.replace('\t', ' ')
    class_definition = re.sub(re_string_concat, "", class_definition)
    class_definition = re.sub(re_space_normalize, " ", class_definition)
    return class_definition


def class_definition_parse(class_definition):
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
            data_properties.update(data_property_parse(p))

    if len(entity_args) > 1 and entity_args[1].strip('"'):
        print(entity_args)
        fgd_data = fgd.FGD_entity(data_type, data_properties,
                                  entity_args[0],
                                  entity_args[1].strip('"'))
    else:
        fgd_data = fgd.FGD_data(data_type, data_properties)

    '''
    if data_type == '@include' or \
       data_type == '@mapsize' or \
       data_type == '@AutoVisGroup' or \
       data_type == '@MaterialExclusion':
        fgd_data = fgd.FGD_data(data_type, data_properties)
    elif data_type == '@BaseClass':
        pass
    elif class_definition.startswith('@SolidClass'):
        pass
    elif class_definition.startswith('@PointClass'):
        pass
    elif class_definition.startswith('@FilterClass'):
        pass
    elif class_definition.startswith('@KeyFrameClass'):
        pass
    elif class_definition.startswith('@MoveClass'):
        pass
    elif class_definition.startswith('@NPCClass'):
        pass
    '''
    return fgd_data


def data_property_parse(property_str):
    property = {}
    property_parts = property_str.split('(')
    property_name = property_parts[0].strip()
    property_params = property_parts[1].strip().strip(')')

    if (property_params):
        property[property_name] = property_params.split(',')
    else:
        property[property_name] = []
    return property


def classPropertiesParse(reader, node):

    current_line = reader.readline()

    while ']' not in current_line:

        current_line = reader.readline()
