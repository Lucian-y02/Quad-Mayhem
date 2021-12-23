from class_wall import Wall
from class_player import Player


def create_field(level, groups_data):
    players_coords = dict()  # Словарь вида "Игрок: его координаты"
    for row, lab in enumerate(level):
        for col, sim in enumerate(lab):
            if sim == '#':
                Wall(groups_data, x=col * 32, y=row * 32)
            elif sim == '@':
                players_coords[(Player(groups_data,  # Создание экземпляра класса Player
                                       x=col * 32, y=row * 32))] = (col, row)
    return players_coords


def load_level(filename):
    with open(filename, 'r', encoding='utf8') as f:
        level = f.readlines()
        max_len = 0
        for i in range(len(level)):
            level[i] = level[i].strip('\n ')
            max_len = max(max_len, len(level[i]))
        level = map(lambda x: x.ljust(max_len, '.'), level)
    return level
