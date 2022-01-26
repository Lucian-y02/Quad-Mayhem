from random import choice

from game_stuff import HealthPointsIndicator

import pygame


pygame.init()
pygame.joystick.init()


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
