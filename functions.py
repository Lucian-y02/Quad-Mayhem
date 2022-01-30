from random import shuffle

from game_stuff import *
import tools_for_creating_maps as t


def create_field(level, prototype, name):  # Создание поля
    players = list()
    teleports1 = list()
    teleports2 = list()
    spots = list()
    team1 = list()
    team2 = list()
    for col, a in enumerate(level):
        for row, b in enumerate(a):
            if b == '@' and name == 'FFA':
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
            elif b == 'а':
                t.box(prototype.groups_data, x=row * 32, y=col * 32)
            elif b == 'б':
                t.platform_top_left(prototype.groups_data, x=row * 32, y=col * 32)
            elif b == 'д':
                t.platform_bottom_left(prototype.groups_data, x=row * 32, y=col * 32)
            elif b == 'е':
                t.platform_top_right(prototype.groups_data, x=row * 32, y=col * 32)
            elif b == ',':
                t.platform_bottom_right(prototype.groups_data, x=row * 32, y=col * 32)
            elif b == 'ё':
                t.floor(prototype.groups_data, x=row * 32, y=col * 32)
            elif b == 'ж':
                t.ceiling(prototype.groups_data, x=row * 32, y=col * 32)
            elif b == 'з':
                t.right_wall(prototype.groups_data, x=row * 32, y=col * 32)
            elif b == 'и':
                t.left_wall(prototype.groups_data, x=row * 32, y=col * 32)
            elif b == '+':
                Barrel(prototype, x=row * 32, y=col * 32)
            elif b == '-':
                ToxicBarrel(prototype, x=row * 32, y=col * 32)
            elif b == '=':
                SuperJump(prototype.groups_data['game_stuff'], x=row * 32, y=col * 32)
            elif b == 'й':
                t.floor_left(prototype.groups_data, x=row * 32, y=col * 32)
            elif b == 'к':
                t.floor_right(prototype.groups_data, x=row * 32, y=col * 32)
            elif b == 'л':
                t.ceiling_left(prototype.groups_data, x=row * 32, y=col * 32)
            elif b == 'м':
                t.ceiling_right(prototype.groups_data, x=row * 32, y=col * 32)
            elif b == 'н':
                t.left_wall_bottom(prototype.groups_data, x=row * 32, y=col * 32)
            elif b == 'о':
                t.left_wall_top(prototype.groups_data, x=row * 32, y=col * 32)
            elif b == 'п':
                t.right_wall_bottom(prototype.groups_data, x=row * 32, y=col * 32)
            elif b == 'р':
                t.right_wall_top(prototype.groups_data, x=row * 32, y=col * 32)
            elif b == 'с':
                t.platform(prototype.groups_data, x=row * 32, y=col * 32)
            elif b == 'т':
                t.platform_left(prototype.groups_data, x=row * 32, y=col * 32)
            elif b == 'у':
                t.platform_right(prototype.groups_data, x=row * 32, y=col * 32)
            elif b == 'ф':
                t.platform_top(prototype.groups_data, x=row * 32, y=col * 32)
            elif b == 'х':
                t.platform_bottom(prototype.groups_data, x=row * 32, y=col * 32)
            elif b == '1':
                ItemsSpawner(prototype.groups_data, x=row * 32, y=col * 32)
            elif b == '2':
                Ammo(prototype.groups_data, x=row * 32, y=col * 32)
            elif b == '3':
                HealingBox(prototype.groups_data, x=row * 32, y=col * 32)
            elif b == '4' and name == 'CTF':
                team2.append((row * 32, col * 32))
            elif b == '5' and name == 'CTF':
                team1.append((row * 32, col * 32))
            elif b == '6':
                TeamFlag(prototype.groups_data, x=row*32, y=col*32, team='1')

    prototype.teleports1 = teleports1
    prototype.teleports2 = teleports2
    if name == 'FFA':
        HorizontalPlatform(prototype, prototype.screen, x=11 * 32, y=6 * 32, x2=16 * 32, speed=1)
        HorizontalPlatform(prototype, prototype.screen, x=35 * 32, y=6 * 32, x2=30 * 32, speed=-1)
        HorizontalPlatform(prototype, prototype.screen, x=12 * 32, y=10 * 32, x2=17 * 32, speed=1)
        HorizontalPlatform(prototype, prototype.screen, x=34 * 32, y=10 * 32, x2=29 * 32, speed=-1)
        shuffle(spots)
        return spots
    elif name == 'CTF':
        HorizontalPlatform(prototype, prototype.screen, x=9 * 32, y=11 * 32, x2=13 * 32, speed=1)
        shuffle(team1)
        shuffle(team2)
        TeamFlag(prototype.groups_data, x=32 * 26, y=32 * 8)
        return team1, team2


def load_level(filename):
    with open(filename, 'r', encoding='utf8') as f:
        level = f.readlines()
        for i in range(len(level)):
            level[i] = ''.join(level[i].strip('\n ').split())
    return level
