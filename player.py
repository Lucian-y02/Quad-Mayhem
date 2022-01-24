from game_stuff import HealthPointsIndicator

import pygame


pygame.init()
pygame.joystick.init()


class Player(pygame.sprite.Sprite):
    def __init__(self, groups: dict, **kwargs):
        super(Player, self).__init__(groups["players"])
        self.image = pygame.Surface(kwargs.get("size", (30, 42)))
        self.image.fill(kwargs.get("color", (50, 50, 50)))
        self.rect = self.image.get_rect()
        self.rect.x = kwargs.get("x", 0)
        self.rect.y = kwargs.get("y", 0)
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

        self.speed = kwargs.get("speed", 4)  # Скорость персонажа
        self.health_points = kwargs.get("health_points", 100)
        self.groups = groups  # Словарь групп српайтов
        HealthPointsIndicator(self.groups["health_indicators"], user=self)

        # Столкновение
        self.stay = False  # Определяет находится ли игрок на какой-либо опоре
        self.jump = False  # Определяет находится ли игрок в прыжке

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
                    self.stay = True
                    self.jump = False
                    self.gravity = 0
                    self.gravity_count = 0
                    self.rect.y = wall.rect.y - self.rect.height + 1
                    move_y = 0
                # Потолок
                elif self.rect.y - wall.rect.y < 0:
                    # self.gravity += self.gravity_force
                    # self.gravity_count = 1
                    # self.rect.y = wall.rect.y + 1

                    self.rect.y = wall.rect.y + 1
                    move_y += self.jump_force * 2
                    self.gravity_count = 1
                    self.jump = False
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

        # Столкновене с другими игровыми объектами
        for item in self.groups["game_stuff"]:
            if self.rect.colliderect(item.rect):
                if item.__class__.__name__ == "HealingBox" and self.health_points != 100:
                    self.health_points += item.heal
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
                    if (self.rect.height - 2) < abs(self.rect.y - item.rect.y) and \
                            (self.gravity > self.jump_force and self.gravity != 0):
                        self.stay = True
                        self.jump = False
                        self.gravity = 0
                        self.gravity_count = 0
                        self.rect.y = item.rect.y - self.rect.height + 1
                        move_y = 0

        if self.health_points <= 0:
            try:
                self.weapon.user = None
            except AttributeError:
                pass
            self.kill()

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
        if self.gravity_count % 4 == 0:
            self.gravity += self.gravity_force if self.gravity <= self.gravity_force * 3 else 0
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

    # Способность 1
    def ability_1(self):
        pass

    # Способность 2
    def ability_2(self):
        pass

    # Отдача от оружия
    def recoil(self, recoil_force):
        self.rect.move_ip(recoil_force, 0)
