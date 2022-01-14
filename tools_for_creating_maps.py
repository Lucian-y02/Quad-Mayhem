from game_stuff import WallHorizontal, WallVertical

import pygame


pygame.init()


# Шаблоны для создания геометрии уровня --------------------------------------------
# Куб 32x32
def box(groups, x=0, y=0):
    WallHorizontal(group=groups["walls_horizontal"], x=x + 4, y=y, size=(24, 1))
    WallHorizontal(group=groups["walls_horizontal"], x=x + 4, y=y + 31, size=(24, 1))
    WallVertical(group=groups["walls_vertical"], x=x, y=y + 1, size=(1, 30))
    WallVertical(group=groups["walls_vertical"], x=x + 31, y=y + 1, size=(1, 30))


# Верхний левый угол платформы
def platform_top_left(groups, x=0, y=0):
    WallHorizontal(group=groups["walls_horizontal"], x=x + 4, y=y, size=(28, 1))
    WallVertical(group=groups["walls_vertical"], x=x, y=y + 1, size=(1, 31))


# Верхний правый угол платформы
def platform_top_right(groups, x=0, y=0):
    WallHorizontal(group=groups["walls_horizontal"], x=x, y=y, size=(28, 1))
    WallVertical(group=groups["walls_vertical"], x=x + 31, y=y + 1, size=(1, 31))


# Пол
def floor(groups, x=0, y=0):
    WallHorizontal(group=groups["walls_horizontal"], x=x, y=y, size=(32, 1))


# Нижний левый угол платформы
def platform_bottom_left(groups, x=0, y=0):
    WallHorizontal(group=groups["walls_horizontal"], x=x + 4, y=y + 31, size=(28, 1))
    WallVertical(group=groups["walls_vertical"], x=x, y=y, size=(1, 31))


# Нижний правый угол платформы
def platform_bottom_right(groups, x=0, y=0):
    WallHorizontal(group=groups["walls_horizontal"], x=x, y=y + 31, size=(28, 1))
    WallVertical(group=groups["walls_vertical"], x=x + 31, y=y, size=(1, 31))


# Потолок
def ceiling(groups, x=0, y=0):
    WallHorizontal(group=groups["walls_horizontal"], x=x, y=y + 31, size=(32, 1))


# Правая стена
def right_wall(groups, x=0, y=0):
    WallVertical(group=groups["walls_vertical"], x=x, y=y, size=(1, 32))


# Левая стена
def left_wall(groups, x=0, y=0):
    WallVertical(group=groups["walls_vertical"], x=x + 31, y=y, size=(1, 32))


def floor_left(groups, x=0, y=0):
    WallHorizontal(group=groups["walls_horizontal"], x=x + 4, y=y, size=(28, 1))


def floor_right(groups, x=0, y=0):
    WallHorizontal(group=groups["walls_horizontal"], x=x, y=y, size=(28, 1))


def ceiling_left(groups, x=0, y=0):
    WallHorizontal(group=groups["walls_horizontal"], x=x + 4, y=y + 31, size=(28, 1))


def ceiling_right(groups, x=0, y=0):
    WallHorizontal(group=groups["walls_horizontal"], x=x, y=y + 31, size=(28, 1))


def left_wall_bottom(groups, x=0, y=0):
    WallVertical(group=groups["walls_vertical"], x=x + 31, y=y, size=(1, 31))


def left_wall_top(groups, x=0, y=0):
    WallVertical(group=groups["walls_vertical"], x=x + 31, y=y + 1, size=(1, 31))


def right_wall_bottom(groups, x=0, y=0):
    WallVertical(group=groups["walls_vertical"], x=x, y=y, size=(1, 31))


def right_wall_top(groups, x=0, y=0):
    WallVertical(group=groups["walls_vertical"], x=x, y=y + 1, size=(1, 31))


def platform(groups, x=0, y=0):
    WallHorizontal(group=groups["walls_horizontal"], x=x, y=y, size=(32, 1))
    WallHorizontal(group=groups["walls_horizontal"], x=x, y=y + 31, size=(32, 1))


def platform_left(groups, x=0, y=0):
    WallHorizontal(group=groups["walls_horizontal"], x=x + 4, y=y, size=(28, 1))
    WallVertical(group=groups["walls_vertical"], x=x, y=y + 1, size=(1, 30))
    WallHorizontal(group=groups["walls_horizontal"], x=x + 4, y=y + 31, size=(28, 1))


def platform_right(groups, x=0, y=0):
    WallHorizontal(group=groups["walls_horizontal"], x=x, y=y, size=(28, 1))
    WallVertical(group=groups["walls_vertical"], x=x + 31, y=y + 1, size=(1, 30))
    WallHorizontal(group=groups["walls_horizontal"], x=x, y=y + 31, size=(28, 1))
