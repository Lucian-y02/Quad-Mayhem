from class_wall import Wall
from class_player import Player


def create_field(level, groups_data):
    players = list()
    for col, a in enumerate(level):
        for row, b in enumerate(a):
            if b == '@':
                players.append(Player(groups_data, x=32 * row, y=32 * col, gravity=11, jump_force=19))
            elif b == '#':
                Wall(groups_data["walls"], x=row * 32, y=col * 32)
    return players


def load_level(filename):
    with open(filename, 'r', encoding='utf8') as f:
        level = f.readlines()
        for i in range(len(level)):
            level[i] = level[i].strip('\n ')
    return level
