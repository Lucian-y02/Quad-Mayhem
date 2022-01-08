from random import shuffle

from objects import Player, Teleport1, Teleport2, Barrel, ToxicBarrel
import tools_for_creating_maps as t


def create_field(level, prototype):  # Создание поля
    players = list()
    teleports1 = list()
    teleports2 = list()
    spots = list()
    for col, a in enumerate(level):
        for row, b in enumerate(a):
            if b == '@':
                spots.append((32 * row, 32 * col))
            elif b == 'a':
                teleports1.append(Teleport1(x=row * 32, y=col * 32))
            elif b == 'A':
                teleports2.append(Teleport2(x=row * 32, y=col * 32))
            elif b == 'b':
                teleports1.append(Teleport1(x=row * 32, y=col * 32))
            elif b == 'B':
                teleports2.append(Teleport2(x=row * 32, y=col * 32))
            elif b == 'b':
                teleports1.append(Teleport1(x=row * 32, y=col * 32))
            elif b == 'B':
                teleports2.append(Teleport2(x=row * 32, y=col * 32))
            elif b == 'c':
                teleports1.append(Teleport1(x=row * 32, y=col * 32))
            elif b == 'C':
                teleports2.append(Teleport2(x=row * 32, y=col * 32))
            elif b == 'd':
                teleports1.append(Teleport1(x=row * 32, y=col * 32))
            elif b == 'D':
                teleports2.append(Teleport2(x=row * 32, y=col * 32))
            elif b == '1':
                t.box(prototype.groups_data, x=row * 32, y=col * 32)
            elif b == '2':
                t.platform_top_left(prototype.groups_data, x=row * 32, y=col * 32)
            elif b == '5':
                t.platform_bottom_left(prototype.groups_data, x=row * 32, y=col * 32)
            elif b == '3':
                t.platform_top_right(prototype.groups_data, x=row * 32, y=col * 32)
            elif b == '6':
                t.platform_bottom_right(prototype.groups_data, x=row * 32, y=col * 32)
            elif b == '4':
                t.floor(prototype.groups_data, x=row * 32, y=col * 32)
            elif b == '7':
                t.ceiling(prototype.groups_data, x=row * 32, y=col * 32)
            elif b == '8':
                t.right_wall(prototype.groups_data, x=row * 32, y=col * 32)
            elif b == '9':
                t.left_wall(prototype.groups_data, x=row * 32, y=col * 32)
            elif b == '+':
                Barrel(prototype, x=row * 32, y=col * 32)
            elif b == '-':
                ToxicBarrel(prototype, x=row * 32, y=col * 32)
    prototype.teleports1 = teleports1
    prototype.teleports2 = teleports2
    shuffle(spots)
    players.append(Player(prototype.groups_data, x=spots[0][0], y=spots[0][1],
                   gravity=11, jump_force=19, controller="keyboard_1", color="yellow"))
    players.append(Player(prototype.groups_data, x=spots[1][0], y=spots[1][1],
                          gravity=11, jump_force=19, controller="keyboard_2", color="green"))
    return players


def load_level(filename):
    with open(filename, 'r', encoding='utf8') as f:
        level = f.readlines()
        for i in range(len(level)):
            level[i] = ''.join(level[i].strip('\n ').split())
    return level
