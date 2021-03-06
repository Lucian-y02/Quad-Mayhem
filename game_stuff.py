from random import randint, choice

from constants import *

import pygame  # всем привет


pygame.init()
pygame.joystick.init()


class Mouse(pygame.sprite.Sprite):
    def __init__(self, group):
        super(Mouse, self).__init__(group)
        self.image = pygame.Surface((1, 1))
        self.rect = self.image.get_rect()

    def update(self, x, y):
        self.rect.x = x
        self.rect.y = y


class Background(pygame.sprite.Sprite):
    def __init__(self, group, image):
        super(Background, self).__init__(group)
        self.image = image
        self.rect = self.image.get_rect()


class Button(pygame.sprite.Sprite):
    def __init__(self, image, group, **kwargs):
        super(Button, self).__init__(group)
        self.image = image
        self.size = kwargs.get("size", None)
        if self.size:
            self.image = pygame.transform.scale(self.image, size)
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.x = kwargs.get("x", 0)
        self.rect.y = kwargs.get("y", 0)

    def set_image(self, image):
        self.image = image
        if self.size:
            self.image = pygame.transform.scale(self.image, size)


class Wall(pygame.sprite.Sprite):
    def __init__(self, group, **kwargs):
        super(Wall, self).__init__(group)
        self.image = pygame.Surface(kwargs.get("size", (32, 32)))
        self.rect = self.image.get_rect()
        self.rect.x = kwargs.get("x", 0)
        self.rect.y = kwargs.get("y", 0)


class WallHorizontal(Wall):
    def __init__(self, group, **kwargs):
        super(WallHorizontal, self).__init__(group, **kwargs)
        self.image = pygame.Surface(kwargs.get("size", (32, 1)))
        self.mask = pygame.mask.from_surface(self.image)
        self.speed = 0

    def set_speed(self, speed):
        self.speed = speed


class WallVertical(Wall):
    def __init__(self, group, **kwargs):
        super(WallVertical, self).__init__(group, **kwargs)
        self.image = pygame.Surface(kwargs.get("size", (1, 32)))
        self.mask = pygame.mask.from_surface(self.image)


class Teleport1(pygame.sprite.Sprite):
    def __init__(self, **kwargs):
        super(Teleport1, self).__init__()
        self.image = portal
        self.rect = self.image.get_rect()
        self.rect.x = kwargs.get("x", 0)
        self.rect.y = kwargs.get("y", 0)
        self.mask = pygame.mask.from_surface(self.image)
        self.teleports = list()
        self.timer2 = self.timer = kwargs.get("cooldown", 120)


class Teleport2(pygame.sprite.Sprite):
    def __init__(self, **kwargs):
        super(Teleport2, self).__init__()
        self.image = portal
        self.rect = self.image.get_rect()
        self.rect.x = kwargs.get("x", 0)
        self.rect.y = kwargs.get("y", 0)
        self.mask = pygame.mask.from_surface(self.image)
        self.teleports = list()
        self.timer2 = self.timer = kwargs.get("cooldown", 120)


# Оружие
class Weapon(pygame.sprite.Sprite):
    def __init__(self, groups: dict, **kwargs):
        super(Weapon, self).__init__(groups["weapons"])
        self.image = pygame.Surface(kwargs.get("size", (65, 16)))
        self.image.fill((150, 150, 150))
        self.rect = self.image.get_rect()
        self.rect.x = kwargs.get("x", 0)
        self.rect.y = kwargs.get("y", 0)
        self.mirror = kwargs.get("mirror", False)
        self.old_value_mirror = self.mirror
        if self.mirror:
            self.image = pygame.transform.flip(self.image, True, False)

        # rect для обработки столкновения со стенами
        self.second_rect = pygame.Rect((self.rect.x + self.rect.width // 2, self.rect.y),
                                       (self.rect.width // 2, self.rect.height))

        self.groups = groups

        # Кем используется
        self.user = kwargs.get("user", None)

        # Основные характеристики
        self.recoil = kwargs.get("recoil", 1)  # Отдача
        self.bullet_speed = kwargs.get("bullet_speed", 32)  # Скорость пуль
        self.can_shot = True  # Возможность стрельбы
        self.bullet_count = kwargs.get("bullet_count", 10)  # Начальое количество пуль
        self.bullet_count_max = self.bullet_count  # Максимальное количество пуль
        self.bullet_image = pygame.Surface(kwargs.get("bullet_size", (32, 2)))  # Изображение пули
        self.spawner = kwargs.get("spawner", None)  # Спавнер предметов
        self.scatter = kwargs.get("scatter", (-2, 2))  # Разброс
        self.distance = kwargs.get("distance", 1000)  # Дальность выстрела
        self.bullet_damage = kwargs.get("damage", 25)  # Урон
        # Простреливает сквозь двери
        self.shoots_through_doors = kwargs.get("shoots_through_doors", False)

        self.shift_bullets = kwargs.get("shift_bullets", 2)  # Смещение места появления пуль
        self.shift_weapon_x = kwargs.get("shift_weapon_x", 7)  # Смещение пушки в руках игрока (OX)
        self.shift_weapon_y = kwargs.get("shift_weapon_y", 16)  # Смещение пушки в руках игрока (OY)

        # Гравитация
        self.gravity_force = kwargs.get("gravity", 8)  # Ускорение свободного падения
        self.gravity_count = 0
        self.gravity = 0  # Скорость падения

        # Промежуток между выстрелами
        self.shot_timer = 0
        self.shot_cool_down = kwargs.get("cool_down", 20)

        # Влияние на скорость игрока
        self.impact_on_player_speed = kwargs.get("player_speed", 0)

    def update(self):
        if not self.user:
            self.shot_timer = 0
            move_y = self.gravity

            # Столкновение
            for wall in self.groups["walls_horizontal"]:
                if self.rect.colliderect(wall.rect):
                    self.gravity = 0
                    self.gravity_count = 0
                    self.rect.y = wall.rect.y - self.rect.height + 1
                    move_y = 0

            # Смещение
            self.rect.move_ip(0, move_y)

            # Влияния ускорения свободного падения
            self.gravity_count += 1
            if self.gravity_count % 6 == 0:
                self.gravity += self.gravity_force if self.gravity <= self.gravity_force * 3 else 0
                self.gravity_count = 0

            self.second_rect.x = self.rect.x + self.rect.width // 2
            self.second_rect.y = self.rect.y
        else:
            self.shot_timer -= 1 if self.shot_timer > 0 else 0
            if not self.mirror:
                self.rect.x = self.user.rect.x - self.shift_weapon_x
                self.second_rect.x = self.rect.x + self.rect.width // 2
            else:
                self.rect.x = self.user.rect.x - (self.rect.width -
                                                  self.shift_weapon_x - self.user.rect.width)
                self.second_rect.x = self.rect.x
            if self.old_value_mirror != self.mirror:
                self.image = pygame.transform.flip(self.image, True, False)
            self.rect.y = self.user.rect.y + self.shift_weapon_y
            self.second_rect.y = self.rect.y
            self.old_value_mirror = self.mirror

    def shot(self):
        self.can_shot = True
        for wall in self.groups["walls_vertical"]:
            if self.second_rect.colliderect(wall.rect):
                self.can_shot = False
                break
        for door in self.groups["doors"]:
            if self.second_rect.colliderect(door.rect) and not door.is_open:
                self.can_shot = False
                break
        if self.shot_timer == 0 and self.can_shot and self.bullet_count != 0:
            if not self.mirror:
                Bullet(self.groups, x=self.rect.x + self.rect.width - self.bullet_speed,
                       y=self.rect.y + self.shift_bullets, mirror=False,
                       speed=self.bullet_speed,
                       scatter=self.scatter, distance=self.distance,
                       damage=self.bullet_damage, bullet_image=self.bullet_image,
                       through_the_doors=self.shoots_through_doors)
                self.user.recoil(-self.recoil)
            else:
                Bullet(self.groups, x=self.rect.x - self.bullet_speed // 2,
                       y=self.rect.y + self.shift_bullets,
                       mirror=True, speed=self.bullet_speed,
                       scatter=self.scatter, distance=self.distance,
                       damage=self.bullet_damage, bullet_image=self.bullet_image,
                       through_the_doors=self.shoots_through_doors)
                self.user.recoil(self.recoil)
            self.shot_timer = self.shot_cool_down
            self.bullet_count -= 1


# Полуавтоматическая снайперская винтовка
class SemiAutomaticSniperRifle(Weapon):
    def __init__(self, groups, **kwargs):
        super(Weapon, self).__init__(groups["weapons"])
        self.image = semi_automatic_sniper_rifle
        self.rect = self.image.get_rect()
        self.rect.x = kwargs.get("x", 0)
        self.rect.y = kwargs.get("y", 0)
        self.mirror = kwargs.get("mirror", False)
        self.old_value_mirror = self.mirror
        if self.mirror:
            self.image = pygame.transform.flip(self.image, True, False)

        # rect для обработки столкновения оружия со стенами
        self.second_rect = pygame.Rect((self.rect.x + self.rect.width // 2, self.rect.y),
                                       (self.rect.width // 2, self.rect.height))

        self.groups = groups

        # Кем используется
        self.user = kwargs.get("user", None)

        # Основные характеристики
        self.recoil = 2  # Отдача
        self.bullet_speed = 32  # Скорость пуль
        self.can_shot = True  # Возможность стрельбы
        self.bullet_count = 5  # Начальое количество пуль
        self.bullet_count_max = self.bullet_count  # Максимальное количество пуль
        self.bullet_image = semiauto_machinegun_bullet
        self.spawner = kwargs.get("spawner", None)  # Спавнер предметов
        self.scatter = (0, 0)  # Разброс
        self.distance = 800  # Дальность вытсрела
        self.bullet_damage = 35  # Урон
        # Простреливает сквозь двери
        self.shoots_through_doors = False

        self.shift_bullets = 2  # Смещение места появления пуль
        self.shift_weapon_x = 7  # Смещение пушки в руках игрока (OX)
        self.shift_weapon_y = 18  # Смещение пушки в руках игрока (OY)

        # Гравитация
        self.gravity_force = kwargs.get("gravity", 8)  # Ускорение свободного падения
        self.gravity_count = 0
        self.gravity = 0  # Скорость падения

        # Промежуток между выстрелами
        self.shot_timer = 0
        self.shot_cool_down = 75

        # Влияние на скорость игрока
        self.impact_on_player_speed = 0


# Пулемёт
class MachineGun(Weapon):
    def __init__(self, groups, **kwargs):
        super(Weapon, self).__init__(groups["weapons"])
        self.image = machine_gun
        self.rect = self.image.get_rect()
        self.rect.x = kwargs.get("x", 0)
        self.rect.y = kwargs.get("y", 0)
        self.mirror = kwargs.get("mirror", False)
        self.old_value_mirror = self.mirror
        if self.mirror:
            self.image = pygame.transform.flip(self.image, True, False)

        # rect для обработки столкновения оружия со стенами
        self.second_rect = pygame.Rect((self.rect.x + self.rect.width // 2, self.rect.y),
                                       (self.rect.width // 2, self.rect.height))

        self.groups = groups

        # Кем используется
        self.user = kwargs.get("user", None)

        # Основные характеристики
        self.recoil = 2  # Отдача
        self.bullet_speed = 32  # Скорость пуль
        self.can_shot = True  # Возможность стрельбы
        self.bullet_count = 40  # Начальое количество пуль
        self.bullet_count_max = self.bullet_count  # Максимальное количество пуль
        self.bullet_image = semiauto_machinegun_bullet
        self.spawner = kwargs.get("spawner", None)  # Спавнер предметов
        self.scatter = (-2, 2)  # Разброс
        self.distance = 550  # Дальность вытсрела
        self.bullet_damage = 5  # Урон
        # Простреливает сквозь двери
        self.shoots_through_doors = False

        self.shift_bullets = 3  # Смещение места появления пуль
        self.shift_weapon_x = 6  # Смещение пушки в руках игрока (OX)
        self.shift_weapon_y = 18  # Смещение пушки в руках игрока (OY)

        # Гравитация
        self.gravity_force = kwargs.get("gravity", 8)  # Ускорение свободного падения
        self.gravity_count = 0
        self.gravity = 0  # Скорость падения

        # Промежуток между выстрелами
        self.shot_timer = 0
        self.shot_cool_down = 10

        # Влияние на скорость игрока
        self.impact_on_player_speed = 1


# Снайперская винтовка
class SniperRifle(Weapon):
    def __init__(self, groups, **kwargs):
        super(Weapon, self).__init__(groups["weapons"])
        self.image = sniper_rifle
        self.rect = self.image.get_rect()
        self.rect.x = kwargs.get("x", 0)
        self.rect.y = kwargs.get("y", 0)
        self.mirror = kwargs.get("mirror", False)
        self.old_value_mirror = self.mirror
        if self.mirror:
            self.image = pygame.transform.flip(self.image, True, False)

        # rect для обработки столкновения оружия со стенами
        self.second_rect = pygame.Rect((self.rect.x + self.rect.width // 2, self.rect.y),
                                       (self.rect.width // 2, self.rect.height))

        self.groups = groups

        # Кем используется
        self.user = kwargs.get("user", None)

        # Основные характеристики
        self.recoil = 4  # Отдача
        self.bullet_speed = 64  # Скорость пуль
        self.can_shot = True  # Возможность стрельбы
        self.bullet_count = 3  # Начальое количество пуль
        self.bullet_count_max = self.bullet_count  # Максимальное количество пуль
        self.bullet_image = sniper_rifle_bullet
        self.spawner = kwargs.get("spawner", None)  # Спавнер предметов
        self.scatter = (0, 0)  # Разброс
        self.distance = 2000  # Дальность вытсрела
        self.bullet_damage = 100  # Урон
        # Простреливает сквозь двери
        self.shoots_through_doors = True

        self.shift_bullets = 2  # Смещение места появления пуль
        self.shift_weapon_x = 7  # Смещение пушки в руках игрока (OX)
        self.shift_weapon_y = 18  # Смещение пушки в руках игрока (OY)

        # Гравитация
        self.gravity_force = kwargs.get("gravity", 8)  # Ускорение свободного падения
        self.gravity_count = 0
        self.gravity = 0  # Скорость падения

        # Промежуток между выстрелами
        self.shot_timer = 0
        self.shot_cool_down = 100

        # Влияние на скорость игрока
        self.impact_on_player_speed = 1


# Пистолет пулемёт
class SubMachineGun(Weapon):
    def __init__(self, groups, **kwargs):
        super(Weapon, self).__init__(groups["weapons"])
        self.image = sub_machine_gun
        self.rect = self.image.get_rect()
        self.rect.x = kwargs.get("x", 0)
        self.rect.y = kwargs.get("y", 0)
        self.mirror = kwargs.get("mirror", False)
        self.old_value_mirror = self.mirror
        if self.mirror:
            self.image = pygame.transform.flip(self.image, True, False)

        # rect для обработки столкновения оружия со стенами
        self.second_rect = pygame.Rect((self.rect.x + self.rect.width // 2, self.rect.y),
                                       (self.rect.width // 2, self.rect.height))

        self.groups = groups

        # Кем используется
        self.user = kwargs.get("user", None)

        # Основные характеристики
        self.recoil = 0  # Отдача
        self.bullet_speed = 16  # Скорость пуль
        self.can_shot = True  # Возможность стрельбы
        self.bullet_count = 16  # Начальое количество пуль
        self.bullet_count_max = self.bullet_count  # Максимальное количество пуль
        self.bullet_image = sub_machine_gun_bullet
        self.spawner = kwargs.get("spawner", None)  # Спавнер предметов
        self.scatter = (-1, 1)  # Разброс
        self.distance = 150  # Дальность вытсрела
        self.bullet_damage = 16  # Урон
        # Простреливает сквозь двери
        self.shoots_through_doors = False

        self.shift_bullets = 3  # Смещение места появления пуль
        self.shift_weapon_x = 2  # Смещение пушки в руках игрока (OX)
        self.shift_weapon_y = 18  # Смещение пушки в руках игрока (OY)

        # Гравитация
        self.gravity_force = kwargs.get("gravity", 8)  # Ускорение свободного падения
        self.gravity_count = 0
        self.gravity = 0  # Скорость падения

        # Промежуток между выстрелами
        self.shot_timer = 0
        self.shot_cool_down = 20

        # Влияние на скорость игрока
        self.impact_on_player_speed = 0


# Пуля
class Bullet(pygame.sprite.Sprite):
    def __init__(self, groups: dict, **kwargs):
        super(Bullet, self).__init__(groups["bullets"])
        self.image = kwargs.get("bullet_image", None)
        self.rect = self.image.get_rect()
        self.rect.x = kwargs.get("x", 0)
        self.rect.y = kwargs.get("y", 0)

        # Начальная координата, нужная для отлеживаня расстояния, которое пролетела пуля
        self.old_x = self.rect.x
        # Максимальное расстояние, которое может пролететь пуля
        self.distance = kwargs.get("distance", 1000)

        self.groups = groups

        # Разброс
        self.scatter_write = kwargs.get("scatter", (-2, 2))
        self.scatter = randint(self.scatter_write[0], self.scatter_write[1])

        # Скорость пули
        self.speed = kwargs.get("speed", 32) * (-1 if kwargs.get("mirror", False) else 1)

        # Урон
        self.damage = kwargs.get("damage", 25)

        # Может ли пуля проходить сквозь двери
        self.through_the_doors = kwargs.get("through_the_doors", False)

    def update(self):
        self.rect.move_ip(self.speed, self.scatter)

        if (pygame.sprite.spritecollideany(self, self.groups["walls_vertical"]) or
                pygame.sprite.spritecollideany(self, self.groups["walls_horizontal"]) or
                (0 >= self.rect.x >= 2000) or ((0 + self.rect.height) >= self.rect.y >= 1500) or
                abs(self.rect.x - self.old_x) >= self.distance):
            self.kill()


# Полоска здоровья
class HealthPointsIndicator(pygame.sprite.Sprite):
    def __init__(self, group, **kwargs):
        super(HealthPointsIndicator, self).__init__(group)
        self.image = pygame.Surface(kwargs.get("size", (30, 3)))
        self.image.fill((0, 150, 0))
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = 0

        self.shift_horizontal = kwargs.get("shift_horizontal", 0)
        self.shift_vertical = kwargs.get("shift_vertical", 6)
        self.user = kwargs.get("user", None)

        self.max_health_points = kwargs.get("max_health_points", 100)

    def update(self):
        if self.user.health_points <= 0:
            self.kill()
        self.image = pygame.transform.scale(self.image,
                                            (max(int(self.rect.width *
                                                     (self.user.health_points /
                                                      self.max_health_points)), 0), 3))
        self.rect.x = self.user.rect.x - self.shift_horizontal
        self.rect.y = self.user.rect.y - self.shift_vertical


# Таймер
class TimeIndicator(HealthPointsIndicator):
    def __init__(self, group, **kwargs):
        super(TimeIndicator, self).__init__(group, **kwargs)
        self.max_time = kwargs.get("max_time", 1000)
        self.image.fill(kwargs.get("color", (0, 0, 150)))

    def update(self):
        if self.user.time <= 0:
            self.kill()
        self.image = pygame.transform.scale(self.image,
                                            (max(int(self.rect.width *
                                                     (self.user.time /
                                                      self.max_time)), 0), 3))
        self.rect.x = self.user.rect.x - self.shift_horizontal
        self.rect.y = self.user.rect.y - self.shift_vertical


# Аптечка
class HealingBox(pygame.sprite.Sprite):
    def __init__(self, groups: dict, **kwargs):
        super(HealingBox, self).__init__(groups["game_stuff"])
        self.image = healing_box
        self.rect = self.image.get_rect()
        self.rect.x = kwargs.get("x", 0)
        self.rect.y = kwargs.get("y", 0)

        self.heal = kwargs.get("heal", 25)
        self.walls = groups["walls_horizontal"]

        # Гравитация
        self.gravity_force = kwargs.get("gravity", 8)  # Ускорение свободного падения
        self.gravity_count = 0
        self.gravity = 0  # Скорость падения

    def update(self):
        move_y = self.gravity

        # Столкновение
        for wall in self.walls:
            if self.rect.colliderect(wall.rect):
                self.gravity = 0
                self.gravity_count = 0
                self.rect.y = wall.rect.y - self.rect.height + 1
                move_y = 0

        # Смещение
        self.rect.move_ip(0, move_y)

        # Влияния ускорения свободного падения
        self.gravity_count += 1
        if self.gravity_count % 6 == 0:
            self.gravity += self.gravity_force if self.gravity <= self.gravity_force * 3 else 0
            self.gravity_count = 0


# Спаунер предметов
class ItemsSpawner(pygame.sprite.Sprite):
    def __init__(self, groups: dict, **kwargs):
        super(ItemsSpawner, self).__init__(groups["game_stuff"])
        self.image = items_spawner
        self.rect = self.image.get_rect()
        self.rect.x = kwargs.get("x", 0) + (32 - self.rect.width) // 2
        self.rect.y = kwargs.get("y", 0) + 32 - self.rect.height
        self.shift = kwargs.get("shift", self.rect.width // 2)

        self.cool_down = kwargs.get("cool_down", 200)  # Интервал появления предметов
        self.weapon_list = kwargs.get("weapon_list", [Weapon])  # Список пояляющихся предметов
        self.weapon = kwargs.get("weapon", None)  # Находящийся в спаунере предмет

        self.groups = groups

        self.timer = 0

    def update(self):
        if not self.weapon:
            self.timer += 1
        if self.timer >= self.cool_down:
            self.timer = 0
            chosen_weapon = choice(self.weapon_list)
            chosen_weapon(self.groups, x=self.rect.x - self.shift,
                          y=self.rect.y - 24, gravity=0, spawner=self)
            self.weapon = chosen_weapon


# Платформа для супер прыжка
class SuperJump(pygame.sprite.Sprite):
    def __init__(self, group, **kwargs):
        super(SuperJump, self).__init__(group)
        self.image = pygame.Surface((kwargs.get("size", (32, 4))))
        self.image.fill((100, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.x = kwargs.get("x", 0)
        self.rect.y = kwargs.get("y", 0) + 32 - self.rect.height

        self.super_jump_force = kwargs.get("super_jump_force", 4)


# Шипы
class Spikes(pygame.sprite.Sprite):
    def __init__(self, group, **kwargs):
        super(Spikes, self).__init__(group)
        self.image = pygame.Surface(kwargs.get("size", (32, 16)))
        self.image.fill((175, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.x = kwargs.get("x", 0)
        self.rect.y = kwargs.get("y", 0) + 32 - self.rect.height

        self.damage = kwargs.get("damage", 15)


# Боеприпасы
class Ammo(pygame.sprite.Sprite):
    def __init__(self, groups: dict, **kwargs):
        super(Ammo, self).__init__(groups["game_stuff"])
        self.image = ammo
        self.rect = self.image.get_rect()
        self.rect.x = kwargs.get("x", 0)
        self.rect.y = kwargs.get("y", 0)
        self.walls = groups["walls_horizontal"]
        # Гравитация
        self.gravity_force = kwargs.get("gravity", 8)  # Ускорение свободного падения
        self.gravity_count = 0
        self.gravity = 0  # Скорость падения

    def update(self):
        move_y = self.gravity

        # Столкновение
        for wall in self.walls:
            if self.rect.colliderect(wall.rect):
                self.gravity = 0
                self.gravity_count = 0
                self.rect.y = wall.rect.y - self.rect.height + 1
                move_y = 0

        # Смещение
        self.rect.move_ip(0, move_y)

        # Влияния ускорения свободного падения
        self.gravity_count += 1
        if self.gravity_count % 6 == 0:
            self.gravity += self.gravity_force if self.gravity <= self.gravity_force * 3 else 0
            self.gravity_count = 0


# Балка
class Beam(pygame.sprite.Sprite):
    def __init__(self, groups: dict, **kwargs):
        super(Beam, self).__init__(groups["game_stuff"])
        self.image = pygame.Surface(kwargs.get("size", (32, 15)))
        self.image.fill((100, 100, 100))
        self.rect = self.image.get_rect()
        self.rect.x = kwargs.get("x", 0)
        self.rect.y = kwargs.get("y", 0) + 1
        WallHorizontal(groups["walls_horizontal"], x=self.rect.x, y=self.rect.y - 1)


class TeamFlag(pygame.sprite.Sprite):
    def __init__(self, groups: dict, **kwargs):
        super(TeamFlag, self).__init__(groups["game_stuff"])
        self.image = team_flag
        self.rect = self.image.get_rect()
        self.rect.x = kwargs.get("x", 0) + 16 - self.image.get_width() // 2
        self.rect.y = kwargs.get("y", 0) + 32

        self.players_data = groups["players"]

        self.health_points = kwargs.get("health_points", 1000)
        HealthPointsIndicator(groups["game_stuff"], user=self, max_health_points=1000,
                              size=(96, 3), shift_horizontal=48 - self.rect.width // 2,
                              shift_vertical=4)
        self.time = kwargs.get("time", 1000)
        TimeIndicator(groups["game_stuff"], user=self, max_time=1000,
                      size=(96, 3), shift_horizontal=48 - self.rect.width // 2,
                      shift_vertical=8, color=(0, 0, 150))

        self.team = kwargs.get("team", "1")  # Чьей команде принадлежит точка
        self.end_function = kwargs.get("end_function", None)  # Функция окончания игровой сессии

        self.timer_health = 0  # Уменьшение HP
        self.simple_timer = 0  # Уменшьение времени для захвата

    def update(self):
        self.simple_timer += 1
        for player in self.players_data:
            if self.rect.colliderect(player.rect) and player.team != self.team:
                self.timer_health += 1

        if self.timer_health % 1 == 0 and self.timer_health != 0:
            self.health_points -= 1
            self.timer_health = 0

        if self.simple_timer % 6 == 0 and self.simple_timer != 0:
            self.time -= 1
            self.simple_timer = 0

        if self.health_points <= 0:
            self.end_function("Команда атаки победила!")
        elif self.time <= 0:
            self.end_function("Команда защиты победила!")


class Barrel(pygame.sprite.Sprite):
    def __init__(self, prototype, **kwargs):
        super(Barrel, self).__init__(prototype.groups_data['barrels'])
        self.size = kwargs.get("size", (16, 32))
        self.image = pygame.Surface(self.size)
        self.image.fill((150, 75, 0))
        self.rect = self.image.get_rect()
        self.rect.x = kwargs.get("x", 0)
        self.rect.y = kwargs.get("y", 0)
        self.prototype = prototype

    def update(self):
        collision = pygame.sprite.spritecollideany(self, self.prototype.groups_data['bullets'])
        if collision:
            self.prototype.gas.append(Gas(self.prototype.groups_data['gas'], 'normal',
                                          images, x=self.rect.x - 46,
                                          y=self.rect.y - 38, duration=30))
            self.kill()
            collision.kill()


class ToxicBarrel(pygame.sprite.Sprite):
    def __init__(self, prototype, **kwargs):
        super(ToxicBarrel, self).__init__(prototype.groups_data['toxic_barrels'])
        self.size = kwargs.get("size", (16, 32))
        self.image = pygame.Surface(self.size)
        self.image.fill((0, 120, 0))
        self.rect = self.image.get_rect()
        self.rect.x = kwargs.get("x", 0)
        self.rect.y = kwargs.get("y", 0)
        self.prototype = prototype

    def update(self):
        collision = pygame.sprite.spritecollideany(self, self.prototype.groups_data['bullets'])
        if collision:
            self.prototype.gas.append(Gas(self.prototype.groups_data['gas'], 'toxic',
                                          images, x=self.rect.x - 46,
                                          y=self.rect.y - 38, duration=120))
            self.kill()
            collision.kill()


class Gas(pygame.sprite.Sprite):
    def __init__(self, group, mode, class_images, **kwargs):
        super(Gas, self).__init__(group)
        self.max_size = kwargs.get("size", (108, 108))
        if mode == 'normal':
            self.image = class_images[0]
        elif mode == 'toxic':
            self.image = class_images[1]
        self.rect = self.image.get_rect()
        self.rect.x = kwargs.get("x", 0)
        self.rect.y = kwargs.get("y", 0)
        self.duration = kwargs.get("duration", 120)
        self.appear = True
        self.mode = mode
        self.size = 1
        self.image = pygame.transform.scale(self.image, self.max_size)


class Door(pygame.sprite.Sprite):
    def __init__(self, groups: dict, **kwargs):
        super(Door, self).__init__(groups["doors"])
        self.image = door_closed
        self.rect = self.image.get_rect()
        self.rect.x = kwargs.get("x", 0) + (32 - self.rect.width) // 2
        self.rect.y = kwargs.get("y", 0)

        # Игроки
        self.players_data = groups["players"]

        # Пули
        self.bullets = groups["bullets"]

        # Открыта или закрыта
        self.is_open = kwargs.get("is_open", False)

    def update(self):
        self.is_open = True if pygame.sprite.spritecollideany(self, self.players_data) else False
        if self.is_open:
            self.image = door_open
        else:
            self.image = door_closed
        for bullet in self.bullets:
            if (self.rect.colliderect(bullet.rect) and not self.is_open and
                    not bullet.through_the_doors):
                bullet.kill()


class HorizontalPlatform(pygame.sprite.Sprite):
    def __init__(self, prototype, class_screen: pygame.Surface, **kwargs):
        super(HorizontalPlatform, self).__init__(prototype.groups_data['platforms'])
        self.image = platform
        self.rect = self.image.get_rect()
        self.screen = class_screen
        self.going = True
        self.x = kwargs.get("x", 0)
        self.y = kwargs.get("y", 0)
        self.rect.x = self.x
        self.rect.y = self.y
        self.x2 = kwargs.get("x2", 100)
        self.speed = kwargs.get("speed", 0)
        if self.speed < 0:
            self.going = False
        self.list = list()
        skibidi_wapapa = WallHorizontal(group=prototype.groups_data['walls_horizontal'], speed=self.speed,
                                        x=self.x + 1, y=self.y, size=(62, 1))
        self.list.append(skibidi_wapapa)
        prototype.horizontal_platforms.append(skibidi_wapapa)
        self.list.append(WallHorizontal(group=prototype.groups_data['walls_horizontal'],
                                        x=self.x + 1, y=self.y + 29, size=(62, 1)))
        self.list.append(WallVertical(group=prototype.groups_data['walls_vertical'],
                                      x=self.x, y=self.y + 1, size=(1, 28)))
        self.list.append(WallVertical(group=prototype.groups_data['walls_vertical'],
                                      x=self.x + 64, y=self.y + 1, size=(1, 28)))

    def update(self):
        self.list[0].set_speed(self.speed)
        for amogus in self.list:
            amogus.rect.move_ip(self.speed, 0)
        self.rect.move_ip(self.speed, 0)
        if self.going and (self.x2 <= self.list[-1].rect.x):
            self.speed *= -1
            self.going = False
            self.x2, self.x = self.x, self.x2
        elif (not self.going) and (self.x2 >= self.list[-1].rect.x):
            self.speed *= -1
            self.going = True
            self.x2, self.x = self.x, self.x2


class VerticalPlatform(pygame.sprite.Sprite):
    def __init__(self, groups: dict, class_screen: pygame.Surface, **kwargs):
        super(VerticalPlatform, self).__init__(groups['platforms'])
        self.screen = class_screen
        self.going = True
        self.x = kwargs.get("x", 0)
        self.y = kwargs.get("y", 0)
        self.y2 = kwargs.get("y2", 100)
        self.speed = kwargs.get("speed", 0)
        if self.speed < 0:
            self.going = False
        self.list = list()
        self.list.append(WallHorizontal(group=groups['walls_horizontal'], x=self.x + 1, y=self.y, size=(62, 1)))
        self.list.append(WallHorizontal(group=groups['walls_horizontal'], x=self.x + 1, y=self.y + 29, size=(62, 1)))
        self.list.append(WallVertical(group=groups['walls_vertical'], x=self.x, y=self.y + 1, size=(1, 30)))
        self.list.append(WallVertical(group=groups['walls_vertical'], x=self.x + 64, y=self.y + 1, size=(1, 28)))

    def update(self):
        for sus in self.list:
            sus.rect.move_ip(0, self.speed)
        if self.going and (self.y2 <= self.list[-1].rect.y):
            self.speed *= -1
            self.going = False
            self.y2, self.y = self.y, self.y2
        elif (not self.going) and (self.y2 >= self.list[-1].rect.y):
            self.speed *= -1
            self.going = True
            self.y2, self.y = self.y, self.y2


# Силовое поле Джаспера
class JasperProtect(pygame.sprite.Sprite):
    def __init__(self, groups: dict, **kwargs):
        super(JasperProtect, self).__init__(groups["game_stuff"])
        self.user = kwargs.get("user", None)
        self.image = jasper_protect
        self.image.set_alpha(75)
        self.image.convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x = self.user.rect.x - 1
        self.rect.y = self.user.rect.y - 1

        # Группа пуль
        self.bullets_group = groups["bullets"]

        # Прочность силового поля
        self.max_health_points = kwargs.get("health_points", 30)
        self.health_points = self.max_health_points
        HealthPointsIndicator(groups["game_stuff"], max_health_points=self.max_health_points,
                              shift_vertical=8, color=(200, 0, 200), user=self)

    def update(self):
        # Перемещение
        self.rect.x = self.user.rect.x - 1
        self.rect.y = self.user.rect.y - 1

        if self.health_points <= 0:
            self.user.ability_recovery = 1
            self.user.protect = None
            self.user.immortal = False
            self.kill()

        for bullet in self.bullets_group:
            if self.rect.colliderect(bullet.rect):
                self.health_points -= bullet.damage
                bullet.kill()


# Ядовитое облако Винцента
class VincentPoisonRay(pygame.sprite.Sprite):
    def __init__(self, groups: dict, **kwargs):
        super(VincentPoisonRay, self).__init__(groups["game_stuff"])
        self.user = kwargs.get("user", None)
        self.image = vincent_poison_ray
        self.image.convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x = self.user.rect.x - 33
        self.rect.y = self.user.rect.y + (self.user.rect.height - 32)

        # Исчезновение
        self.max_time = kwargs.get("time", 1000)
        self.time = self.max_time
        self.timer = TimeIndicator(groups["game_stuff"], user=self, max_time=self.max_time,
                                   shift_vertical=-38, shift_horizontal=-32)
        self.decay_rate = kwargs.get("decay_rate", 2)  # Скорость распада

        # Список игроков
        self.players_list = groups["players"]

        self.damage = kwargs.get("damage", 1)  # Урок

    def update(self):
        if self.time <= 0:
            self.timer.kill()
            self.kill()

        self.time -= self.decay_rate

        for player in self.players_list:
            if player.__class__.__name__ == "Jasper" and player.protect:
                player.protect.health_points -= self.damage
            elif (self.rect.colliderect(player.rect) and not player.immortal and
                  player.__class__.__name__ != self.user.__class__.__name__):
                player.health_points -= self.damage


# Турель Гуидо
class TurretOfGuido(pygame.sprite.Sprite):
    def __init__(self, groups: dict, **kwargs):
        super(TurretOfGuido, self).__init__(groups["game_stuff"])
        self.user = kwargs.get("user", None)
        self.image = turret_of_guido
        self.rect = self.image.get_rect()
        self.rect.x = self.user.rect.x
        self.rect.y = self.user.rect.y + self.user.rect.height - self.rect.height

        # Изображение пули
        self.bullet_image = turret_of_guido_bullet
        # Исчезновение
        self.max_time = kwargs.get("time", 1750)
        self.time = self.max_time
        self.timer = TimeIndicator(groups["game_stuff"], user=self, max_time=self.max_time,
                                   size=(self.rect.width, 3))
        self.decay_rate = kwargs.get("decay_rate", 1)  # Скорость распада

        self.mirror = self.user.mirror
        self.groups = groups

        # Выстрел турели
        self.cool_down_of_shot = kwargs.get("cool_down", 100)
        self.shot_time = 0

    def update(self):
        if self.time <= 0:
            self.timer.kill()
            self.kill()
        if self.shot_time == self.cool_down_of_shot:
            self.shot_time = 0
            if not self.mirror:
                Bullet(self.groups, distance=170, scatter=(0, 0), damage=10,
                       speed=4, color=(150, 0, 0), mirror=self.mirror,
                       x=self.rect.x + (self.rect.width - 8),
                       y=self.rect.y + 2,
                       bullet_image=self.bullet_image)
            elif self.mirror:
                Bullet(self.groups, distance=170, scatter=(0, 0), damage=10,
                       speed=4, color=(150, 0, 0), mirror=self.mirror,
                       x=self.rect.x,
                       y=self.rect.y + 2,
                       bullet_image=self.bullet_image)

        self.time -= self.decay_rate
        self.shot_time += 1
