from objects import Wall, Teleport1, Teleport2, Player


def create_field(level, groups_data):
    players = list()
    teleport1 = teleport2 = None
    for col, a in enumerate(level):
        for row, b in enumerate(a):
            if b == '@':
                players.append(Player(groups_data, x=32 * row, y=32 * col, gravity=11, jump_force=19))
            elif b == '#':
                Wall(groups_data["walls"], x=row * 32, y=col * 32)
            elif b == 'v':
                teleport1 = Teleport1(groups_data["teleports"], x=row * 32, y=col * 32)
            elif b == 'V':
                teleport2 = Teleport2(groups_data["teleports"], x=row * 32, y=col * 32)
    for player in players:
        player.teleport1_mask = teleport1.mask
        player.teleport2_mask = teleport2.mask
        player.teleport1 = teleport1
        player.teleport2 = teleport2
    return players


def load_level(filename):
    with open(filename, 'r', encoding='utf8') as f:
        level = f.readlines()
        for i in range(len(level)):
            level[i] = level[i].strip('\n ')
    return level
