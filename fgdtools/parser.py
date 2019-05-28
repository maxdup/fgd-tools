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

    return game_data
