from . import fgd


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

        class_definition = ''
        class_properties = ''

        lines += 1
        if not current_line:
            eof = True
            break

        # Skip comments
        while current_line.startswith('//') or not current_line.strip():
            current_line = reader.readline()

        if '//' in current_line:
            current_line = current_line.split('//')[0]

        # Get class definition
        if current_line.startswith('@'):
            class_definition += current_line
            current_line = reader.readline()
            while '@' not in current_line and '[' not in current_line:
                if not current_line.startswith('//') and current_line.strip():
                    class_definition += current_line.strip()
                current_line = reader.readline()
            class_definition = class_definition.strip()
            if class_definition:
                print('---------------')
                print(class_definition)

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
                        class_properties += current_line.strip() + '\n'
                current_line = reader.readline()
            if class_properties:
                print('---------------')
                print(class_properties)
    return game_data


def strip_line(line):
    line = line.strip()
    return line


def classDefinitionParse(class_definition):
    fc = fgd.FGD_class()
    return fc


def classPropertiesParse(reader, node):

    current_line = reader.readline()

    while ']' not in current_line:

        current_line = reader.readline()
        if current_line.strip().startswith('//'):
            pass
        elif '//' in current_line:
            current_line = current_line.split('//')[0]
        elif current_line.startswith('@include'):
            pass
        elif current_line.startswith('@mapsize'):
            pass
        elif current_line.startswith('@AutoVisGroup'):
            pass
        elif current_line.startswith('@MaterialExclusion'):
            pass
        elif current_line.startswith('@BaseClass'):
            pass
        elif current_line.startswith('@SolidClass'):
            pass
        elif current_line.startswith('@PointClass'):
            pass
        elif current_line.startswith('@FilterClass'):
            pass
        elif current_line.startswith('@KeyFrameClass'):
            pass
        elif current_line.startswith('@MoveClass'):
            pass
        elif current_line.startswith('@NPCClass'):
            pass
