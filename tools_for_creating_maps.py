from wall import *

import pygame


pygame.init()


# Функция для создания куба 32x32
def box(groups, x=0, y=0):
    WallHorizontal(group=groups["walls_horizontal"], x=x + 4, y=y, size=(24, 1))
    WallHorizontal(group=groups["walls_horizontal"], x=x + 4, y=y + 31, size=(24, 1))
    WallVertical(group=groups["walls_vertical"], x=x, y=y + 1, size=(1, 30))
    WallVertical(group=groups["walls_vertical"], x=x + 31, y=y + 1, size=(1, 30))
