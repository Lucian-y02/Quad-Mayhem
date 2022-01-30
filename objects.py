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

    def btn_not_clicked(self):
        pass

    def btn_def_clicked(self):
        pass

    def btn_attack_clicked(self):
        pass


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
        self.image = pygame.Surface(kwargs.get("teleport_size", (32, 64)))
        self.image.fill('blue')
        self.rect = self.image.get_rect()
        self.rect.x = kwargs.get("x", 0)
        self.rect.y = kwargs.get("y", 0)
        self.mask = pygame.mask.from_surface(self.image)
        self.teleports = list()
        self.timer2 = self.timer = kwargs.get("cooldown", 120)


class Teleport2(pygame.sprite.Sprite):
    def __init__(self, **kwargs):
        super(Teleport2, self).__init__()
        self.image = pygame.Surface(kwargs.get("teleport_size", (32, 64)))
        self.image.fill('blue')
        self.rect = self.image.get_rect()
        self.rect.x = kwargs.get("x", 0)
        self.rect.y = kwargs.get("y", 0)
        self.mask = pygame.mask.from_surface(self.image)
        self.teleports = list()
        self.timer2 = self.timer = kwargs.get("cooldown", 120)


class Player(pygame.sprite.Sprite):
    def __init__(self, groups: dict, **kwargs):
        super(Player, self).__init__(groups["players"])
        self.pixel_font = pygame.font.Font("PixelFont.ttf", 26)
        self.image = pygame.Surface(kwargs.get("size", (30, 42)))
        self.image.fill(kwargs.get("color", (50, 50, 50)))
        self.rect = self.image.get_rect()
        self.rect.x = kwargs.get("x", 0) + 1
        self.rect.y = kwargs.get("y", 0) - self.rect.height + 33
        self.mirror = kwargs.get("mirror", False)

        # Определение, чем урпавляется пересонаж
        self.control_function = self.keyboard_1_check_pressing
        if kwargs.get("controller", "keyboard_1") == "joystick":
            self.joystick = pygame.joystick.Joystick(0)
            self.control_function = self.joystick_check_pressing
        elif kwargs.get("controller", "keyboard_1") == "joystick":
            self.joystick = pygame.joystick.Joystick(1)
            self.control_function = self.joystick_check_pressing
        elif kwargs.get("controller", "keyboard_1") == "keyboard_2":
            self.control_function = self.keyboard_2_check_pressing

        # Возрождение
        self.lives = kwargs.get("lives", -1) - 1  # Количество возрождений
        # Места, где игрок может возродиться
        self.recovery_places = kwargs.get("recovery_places",
                                          [(kwargs.get("x", 0), kwargs.get("y", 0) - 32)])
        self.killing_zone = kwargs.get("killing_zone", 800)

        self.screen = kwargs.get("screen", None)
        self.team = kwargs.get("team", "0")  # В какой команде находится игрок
        self.speed = kwargs.get("speed", 4)  # Скорость персонажа
        self.max_health_points = kwargs.get("max_health_points", 100)
        self.health_points = self.max_health_points
        self.groups = groups  # Словарь групп српайтов
        HealthPointsIndicator(self.groups["game_stuff"], user=self)

        # Столкновение
        self.stay = False  # Определяет находится ли игрок на какой-либо опоре
        self.jump = False  # Определяет находится ли игрок в прыжке
        self.on_beam = False  # Определяет может ли игрок проходить сквозь платформу

        # Оружие
        self.weapon = None  # Используемое игроком оружие
        self.grab_timer = 0

        # Гравитация
        self.gravity_force = kwargs.get("gravity", 8)  # Ускорение свободного падения
        self.gravity_count = 0
        self.gravity = 0  # Скорость падения

        # Прыжок
        self.jump_force = kwargs.get("jump_force", 16)

    def update(self):
        # Показатели смещения
        move_x = 0
        move_y = self.gravity - (self.jump_force if self.jump else 0)

        self.stay = False
        # Столкновения
        for wall in self.groups["walls_horizontal"]:
            if self.rect.colliderect(wall):
                # Пол
                if abs(self.rect.y + self.rect.height - wall.rect.y) < abs(self.rect.y -
                                                                           wall.rect.y):
                    if not self.on_beam:
                        self.stay = True
                        self.gravity = 0
                        self.gravity_count = 0
                        self.jump = False
                        move_y = 0
                    self.rect.y = wall.rect.y - self.rect.height + 1

                # Потолок
                elif self.rect.y - wall.rect.y < 0 and not self.on_beam:
                    # self.gravity += self.gravity_force
                    # self.gravity_count = 1
                    # self.rect.y = wall.rect.y + 1

                    self.rect.y = wall.rect.y + 1
                    self.gravity_count = 1
                    self.jump = False if self.gravity <= self.gravity_force else True
        for wall in self.groups["walls_vertical"]:
            if self.rect.colliderect(wall):
                # Левая стена
                if abs(self.rect.x - wall.rect.x) < abs(self.rect.x +
                                                        self.rect.width - wall.rect.x):
                    self.rect.x = wall.rect.x + self.speed
                # Правая стена
                else:
                    self.rect.x = wall.rect.x - self.speed - self.rect.width + 1

        # Столкновение с пулями
        for bullet in self.groups["bullets"]:
            if self.rect.colliderect(bullet.rect):
                self.health_points -= bullet.damage
                bullet.kill()

        self.on_beam = False
        # Столкновене с другими игровыми объектами
        for item in self.groups["game_stuff"]:
            if self.rect.colliderect(item.rect):
                if item.__class__.__name__ == "HealingBox" and self.health_points != 100:
                    self.health_points += min(item.heal,
                                              self.max_health_points - self.health_points)
                    item.kill()
                elif item.__class__.__name__ == "SuperJump":
                    move_y -= self.jump_force * item.super_jump_force
                    self.stay = False
                elif item.__class__.__name__ == "Spikes" and not self.stay:
                    self.health_points -= item.damage
                elif item.__class__.__name__ == "Ammo" and self.weapon and \
                        self.weapon.bullet_count != self.weapon.bullet_count_max:
                    self.weapon.bullet_count = self.weapon.bullet_count_max
                    item.kill()
                elif item.__class__.__name__ == "Beam":
                    # if abs(self.rect.y + self.rect.height - item.rect.y) < abs(self.rect.y -
                    #                                                            item.rect.y):
                    # if (self.rect.height - 1) < abs(self.rect.y - item.rect.y):
                    #     self.stay = True
                    #     self.jump = False
                    #     self.gravity = 0
                    #     self.gravity_count = 0
                    #     self.rect.y = item.rect.y - self.rect.height + 1
                    #     move_y = 0
                    self.on_beam = True

        # Уничтожение игрока
        if self.health_points <= 0 or self.rect.y > self.killing_zone:
            try:
                self.weapon.user = None
            except AttributeError:
                pass
            self.weapon = None
            if self.lives != 0:
                self.lives -= 1
                self.recovery()
            else:
                self.kill()

        # Отображение количества жизней у игрока
        if self.lives > 0:
            self.screen.blit(self.pixel_font.render(str(self.lives), False, (10, 10, 10)),
                             (self.rect.x + 1, self.rect.y - 16))

        # Отслеживание нажатий
        move_x, move_y = self.control_function(move_x, move_y)

        if move_x > 0:
            self.mirror = False
        elif move_x < 0:
            self.mirror = True

        try:
            self.weapon.mirror = self.mirror
        except AttributeError:
            pass

        # Смещение персонажа
        self.rect.move_ip(move_x, move_y)

        # Влияния ускорения свободного падения
        self.gravity_count += 1
        if self.gravity_count == 4 and self.gravity_count != 0:
            self.gravity += self.gravity_force if self.gravity <= self.gravity_force * 2 else 0
            self.gravity_count = 0

        # Таймеры
        self.grab_timer -= 1 if self.grab_timer > 0 else 0

    def joystick_check_pressing(self, move_x, move_y):
        if abs(self.joystick.get_axis(0)) > 0.1:
            move_x += self.speed * self.joystick.get_axis(0)
        if self.joystick.get_button(0) and self.stay:
            move_y -= self.jump_force
            self.stay = False
            self.jump = True
        if self.joystick.get_button(5) and self.weapon:
            self.weapon.shot()
        for gun in self.groups["weapons"]:
            if (self.rect.colliderect(gun.rect) and self.joystick.get_button(4) and
                    not gun.user and self.grab_timer == 0):
                gun.user = self
                try:
                    if self.weapon.bullet_count == 0:
                        self.weapon.kill()
                    self.weapon.user = None
                except AttributeError:
                    pass
                self.weapon = gun
                if self.weapon.spawner:
                    self.weapon.gravity_force = self.gravity_force
                    self.weapon.spawner.weapon = None
                    self.weapon.spawner = None
                self.grab_timer = 20
        return move_x, move_y

    def keyboard_1_check_pressing(self, move_x, move_y):
        key = pygame.key.get_pressed()
        if key[pygame.K_a]:
            move_x -= self.speed
        if key[pygame.K_d]:
            move_x += self.speed
        if key[pygame.K_w] and self.stay:
            move_y -= self.jump_force
            self.stay = False
            self.jump = True
        if key[pygame.K_v] and self.weapon:
            self.weapon.shot()
        for gun in self.groups["weapons"]:
            if (self.rect.colliderect(gun.rect) and key[pygame.K_c] and
                    not gun.user and self.grab_timer == 0):
                gun.user = self
                try:
                    if self.weapon.bullet_count == 0:
                        self.weapon.kill()
                    self.weapon.user = None
                except AttributeError:
                    pass
                self.weapon = gun
                if self.weapon.spawner:
                    self.weapon.gravity_force = self.gravity_force
                    self.weapon.spawner.weapon = None
                    self.weapon.spawner = None
                self.grab_timer = 20
        return move_x, move_y

    def keyboard_2_check_pressing(self, move_x, move_y):
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT]:
            move_x -= self.speed
        if key[pygame.K_RIGHT]:
            move_x += self.speed
        if key[pygame.K_UP] and self.stay:
            move_y -= self.jump_force
            self.stay = False
            self.jump = True
        if key[pygame.K_KP3] and self.weapon:
            self.weapon.shot()
        for gun in self.groups["weapons"]:
            if (self.rect.colliderect(gun.rect) and key[pygame.K_KP2] and
                    not gun.user and self.grab_timer == 0):
                gun.user = self
                try:
                    if self.weapon.bullet_count == 0:
                        self.weapon.kill()
                    self.weapon.user = None
                except AttributeError:
                    pass
                self.weapon = gun
                if self.weapon.spawner:
                    self.weapon.gravity_force = self.gravity_force
                    self.weapon.spawner.weapon = None
                    self.weapon.spawner = None
                self.grab_timer = 20
        return move_x, move_y

    # Возрождение
    def recovery(self):
        self.health_points = self.max_health_points
        chosen_place = choice(self.recovery_places)  # Выбранное место возраждения
        self.rect.x = chosen_place[0] + 1
        self.rect.y = chosen_place[1] - self.rect.height + 33
        self.gravity = 0
        self.gravity_count = 0
        self.stay = False
        self.jump = False
        self.on_beam = False

    # Способность 1
    def ability_1(self):
        pass

    # Отдача от оружия
    def recoil(self, recoil_force):
        self.rect.move_ip(recoil_force, 0)


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

        # rect для обработки столкновения со стенами
        self.second_rect = pygame.Rect((self.rect.x + self.rect.width // 2, self.rect.y),
                                       (self.rect.width // 2, self.rect.height))

        self.groups = groups

        # Кем используется
        self.user = kwargs.get("user", None)

        self.recoil = kwargs.get("recoil", 1)  # Отдача
        self.bullet_speed = kwargs.get("bullet_speed", 32)  # Скорость пуль
        self.can_shot = True  # Возможность стрельбы
        self.bullet_count = kwargs.get("bullet_count", 10)  # Максимальное количество пуль
        self.bullet_count_max = self.bullet_count  # Начальое количество пуль
        self.spawner = kwargs.get("spawner", None)  # Спавнер предметов

        # Гравитация
        self.gravity_force = kwargs.get("gravity", 8)  # Ускорение свободного падения
        self.gravity_count = 0
        self.gravity = 0  # Скорость падения

        self.shot_timer = 0

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
                self.rect.x = self.user.rect.x - 7
                self.second_rect.x = self.rect.x + self.rect.width // 2
            else:
                self.rect.x = self.user.rect.x - (self.rect.width - 7 - self.user.rect.width)
                self.second_rect.x = self.rect.x
            self.rect.y = self.user.rect.y + 20
            self.second_rect.y = self.rect.y

    def shot(self):
        self.can_shot = True
        if pygame.sprite.spritecollideany(self, self.groups["walls_vertical"]):
            for wall in self.groups["walls_vertical"]:
                if self.second_rect.colliderect(wall.rect):
                    self.can_shot = False
                    break
        if self.shot_timer == 0 and self.can_shot and self.bullet_count != 0:
            if not self.mirror:
                Bullet(self.groups, x=self.rect.x + self.rect.width - self.bullet_speed,
                       y=self.rect.y + self.rect.height // 2, mirror=False,
                       speed=self.bullet_speed)
                self.user.recoil(-self.recoil)
            else:
                Bullet(self.groups, x=self.rect.x, y=self.rect.y + self.rect.height // 2,
                       mirror=True, speed=self.bullet_speed)
                self.user.recoil(self.recoil)
            self.shot_timer = 20
            self.bullet_count -= 1


# Пуля
class Bullet(pygame.sprite.Sprite):
    def __init__(self, groups: dict, **kwargs):
        super(Bullet, self).__init__(groups["bullets"])
        self.image = pygame.Surface(kwargs.get("size", (32, 2)))
        self.image.fill((150, 150, 150))
        self.rect = self.image.get_rect()
        self.rect.x = kwargs.get("x", 0)
        self.rect.y = kwargs.get("y", 0)

        self.groups = groups

        self.scatter_write = kwargs.get("scatter", (-2, 2))
        self.scatter = randint(self.scatter_write[0], self.scatter_write[1])
        self.speed = kwargs.get("speed", 32) * (-1 if kwargs.get("mirror", False) else 1)
        self.damage = kwargs.get("damage", 25)

    def update(self):
        self.rect.move_ip(self.speed, self.scatter)

        if (pygame.sprite.spritecollideany(self, self.groups["walls_vertical"]) or
                pygame.sprite.spritecollideany(self, self.groups["walls_horizontal"]) or
                (0 >= self.rect.x >= 2000) or ((0 + self.rect.height) >= self.rect.y >= 1500)):
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
        self.image = pygame.Surface(kwargs.get("size", (25, 25)))
        self.image.fill((0, 100, 0))
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
        self.image = pygame.Surface(kwargs.get("size", (28, 7)))
        self.rect = self.image.get_rect()
        self.rect.x = kwargs.get("x", 0) + (32 - self.rect.width) // 2
        self.rect.y = kwargs.get("y", 0) + 32 - self.rect.height

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
            chosen_weapon(self.groups, x=self.rect.x - self.rect.width // 2,
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
class Ammo(HealingBox):
    def __init__(self, group, **kwargs):
        super(Ammo, self).__init__(group, **kwargs)
        self.image.fill((150, 150, 150))


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
        self.image = pygame.Surface(kwargs.get("size", (6, 64)))
        self.image.fill((150, 100, 150))
        self.rect = self.image.get_rect()
        self.rect.x = kwargs.get("x", 0) + 16 - self.image.get_width() // 2
        self.rect.y = kwargs.get("y", 0) + 32

        self.players_data = groups["players"]

        self.health_points = kwargs.get("health_points", 1000)
        HealthPointsIndicator(groups["game_stuff"], user=self, max_health_points=1000,
                              size=(96, 3), shift_horizontal=48 - self.rect.width // 2,
                              shift_vertical=-67)
        self.time = kwargs.get("time", 1000)
        TimeIndicator(groups["game_stuff"], user=self, max_time=1000,
                      size=(96, 3), shift_horizontal=48 - self.rect.width // 2,
                      shift_vertical=-73, color=(0, 0, 150))

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


class HorizontalPlatform(pygame.sprite.Sprite):
    def __init__(self, prototype, class_screen: pygame.Surface, **kwargs):
        super(HorizontalPlatform, self).__init__(prototype.groups_data['platforms'])
        self.screen = class_screen
        self.going = True
        self.x = kwargs.get("x", 0)
        self.y = kwargs.get("y", 0)
        self.x2 = kwargs.get("x2", 100)
        self.speed = kwargs.get("speed", 0)
        if self.speed < 0:
            self.going = False
        self.list = list()
        a = WallHorizontal(group=prototype.groups_data['walls_horizontal'], speed=self.speed,
                           x=self.x + 1, y=self.y, size=(62, 1))
        self.list.append(a)
        prototype.horizontal_platforms.append(a)
        self.list.append(WallHorizontal(group=prototype.groups_data['walls_horizontal'],
                                        x=self.x + 1, y=self.y + 29, size=(62, 1)))
        self.list.append(WallVertical(group=prototype.groups_data['walls_vertical'],
                                      x=self.x, y=self.y + 1, size=(1, 28)))
        self.list.append(WallVertical(group=prototype.groups_data['walls_vertical'],
                                      x=self.x + 64, y=self.y + 1, size=(1, 28)))

    def update(self):
        self.list[0].set_speed(self.speed)
        for platform in self.list:
            platform.rect.move_ip(self.speed, 0)
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
        for platform in self.list:
            platform.rect.move_ip(0, self.speed)
        if self.going and (self.y2 <= self.list[-1].rect.y):
            self.speed *= -1
            self.going = False
            self.y2, self.y = self.y, self.y2
        elif (not self.going) and (self.y2 >= self.list[-1].rect.y):
            self.speed *= -1
            self.going = True
            self.y2, self.y = self.y, self.y2
