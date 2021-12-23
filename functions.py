from class_wall import Wall
from class_player import Player


def create_field(level, groups_data):
    players_coords = dict()  # Словарь вида "Игрок: его координаты"
    for row, lab in enumerate(level):
        for col, sim in enumerate(lab):
            if sim == '#':
                Wall(groups_data, x=col * 32, y=row * 32)
            elif sim == '@':
                players_coords[(Player(groups_data,
                                       x=col * 32, y=row * 32))] = (col, row)
    return players_coords
