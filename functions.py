from objects import Wall, Teleport1, Teleport2, Player


def create_field(level, groups_data):
    players = list()
    teleports1 = list()
    teleports2 = list()
    for col, a in enumerate(level):
        for row, b in enumerate(a):
            if b == '@':
                players.append(Player(groups_data, x=32 * row, y=32 * col, gravity=11, jump_force=19))
            elif b == '#':
                Wall(groups_data["walls"], x=row * 32, y=col * 32)
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
    for player in players:
        player.teleports1 = teleports1
        player.teleports2 = teleports2
    return players


def load_level(filename):
    with open(filename, 'r', encoding='utf8') as f:
        level = f.readlines()
        for i in range(len(level)):
            level[i] = level[i].strip('\n ')
    return level
