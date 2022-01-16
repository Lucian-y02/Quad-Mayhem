from random import randint

import pygame  # всем привет


pygame.init()
pygame.joystick.init()


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
        self.image = pygame.Surface((40, 60))
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
        elif kwargs.get("controller", "keyboard_1") == "keyboard_2":
            self.control_function = self.keyboard_2_check_pressing

        self.speed = kwargs.get("speed", 4)  # Скорость персонажа
        self.health_points = kwargs.get("health_points", 100)
        self.groups = groups  # Словарь групп српайтов
        HealthPointsIndicator(self.groups["health_indicators"], user=self)

        # Столкновение
        self.stay = False  # Определяет находится ли игрок на какой-либо опоре

        # Оружие
        self.weapon = None  # Используемое игроком оружие
        self.grab_timer = 0

        # Гравитация
        self.gravity_force = kwargs.get("gravity", 8)  # Ускорение свободного падения
        self.gravity_count = 0
        self.gravity = 0  # Скорость падения

        # Прыжок
        self.jump_force = kwargs.get("jump", 16)

    def update(self):
        # Показатели смещения
        move_x = 0
        move_y = self.gravity - (self.jump_force if not self.stay else 0)

        # Столкновения
        for wall in self.groups["walls_horizontal"]:
            if self.rect.colliderect(wall):
                # Пол
                if abs(self.rect.y + self.rect.height - wall.rect.y) < abs(self.rect.y -
                                                                           wall.rect.y):
                    self.stay = True
                    self.gravity = 0
                    self.gravity_count = 0
                    self.rect.y = wall.rect.y - self.rect.height + 1
                    move_y = 0
                # Потолок
                elif self.rect.y - wall.rect.y < 0:
                    self.gravity += self.gravity_force
                    self.gravity_count = 1
                    self.rect.y = wall.rect.y + 1
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
            if (self.rect.colliderect(item.rect) and item.__class__.__name__ == "HealingBox" and
                    self.health_points != 100):
                self.health_points += item.heal
                item.kill()
            elif self.rect.colliderect(item.rect) and item.__class__.__name__ == "SuperJump":
                move_y -= self.jump_force * item.super_jump_force
                self.stay = False

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
        if self.gravity_count % 6 == 0:
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
        self.can_shot = True
        self.bullet_count = kwargs.get("bullet_count", 10)

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


class HealthPointsIndicator(pygame.sprite.Sprite):
    def __init__(self, group, **kwargs):
        super(HealthPointsIndicator, self).__init__(group)
        self.image = pygame.Surface((40, 3))
        self.image.fill((0, 150, 0))
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = 0

        self.user = kwargs.get("user", None)

    def update(self):
        if self.user.health_points <= 0:
            self.kill()
        self.image = pygame.transform.scale(self.image,
                                            (max(int(40 * (self.user.health_points / 100)), 0), 3))
        self.rect.x = self.user.rect.x
        self.rect.y = self.user.rect.y - 6


# Аптечка
class HealingBox(pygame.sprite.Sprite):
    def __init__(self, groups: dict, **kwargs):
        super(HealingBox, self).__init__(groups["game_stuff"])
        self.image = pygame.Surface((25, 25))
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


class SuperJump(pygame.sprite.Sprite):
    def __init__(self, group, **kwargs):
        super(SuperJump, self).__init__(group)
        self.image = pygame.Surface((kwargs.get("size", (32, 4))))
        self.image.fill((100, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.x = kwargs.get("x", 0)
        self.rect.y = kwargs.get("y", 0) + 32 - self.rect.height

        self.super_jump_force = kwargs.get("super_jump_force", 4)


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
                                          self.prototype.images, x=self.rect.x - 46,
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
                                          self.prototype.images, x=self.rect.x - 46,
                                          y=self.rect.y - 38, duration=120))
            self.kill()
            collision.kill()


class Gas(pygame.sprite.Sprite):
    def __init__(self, group, mode, images, **kwargs):
        super(Gas, self).__init__(group)
        self.max_size = kwargs.get("size", (108, 108))
        if mode == 'normal':
            self.image = images[0]
        elif mode == 'toxic':
            self.image = images[1]
        self.rect = self.image.get_rect()
        self.rect.x = kwargs.get("x", 0)
        self.rect.y = kwargs.get("y", 0)
        self.duration = kwargs.get("duration", 120)
        self.appear = True
        self.size = 1
        self.image = pygame.transform.scale(self.image, self.max_size)


class HorizontalPlatform(pygame.sprite.Sprite):
    def __init__(self, groups: dict, screen: pygame.Surface, **kwargs):
        super(HorizontalPlatform, self).__init__(groups['platforms'])
        self.screen = screen
        self.going = True
        self.x = kwargs.get("x", 0)
        self.y = kwargs.get("y", 0)
        self.x2 = kwargs.get("x2", 100)
        self.speed = kwargs.get("speed", 0)
        if self.speed < 0:
            self.going = False
        self.list = list()
        self.list.append(WallHorizontal(group=groups['walls_horizontal'], x=self.x + 4, y=self.y, size=(48, 1)))
        self.list.append(WallHorizontal(group=groups['walls_horizontal'], x=self.x + 4, y=self.y + 31, size=(48, 1)))
        self.list.append(WallVertical(group=groups['walls_vertical'], x=self.x, y=self.y + 1, size=(1, 30)))
        self.list.append(WallVertical(group=groups['walls_vertical'], x=self.x + 55, y=self.y + 1, size=(1, 30)))

    def update(self):
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
    def __init__(self, groups: dict, screen: pygame.Surface, **kwargs):
        super(VerticalPlatform, self).__init__(groups['platforms'])
        self.screen = screen
        self.going = True
        self.x = kwargs.get("x", 0)
        self.y = kwargs.get("y", 0)
        self.y2 = kwargs.get("y2", 100)
        self.speed = kwargs.get("speed", 0)
        if self.speed < 0:
            self.going = False
        self.list = list()
        self.list.append(WallHorizontal(group=groups['walls_horizontal'], x=self.x + 4, y=self.y, size=(48, 1)))
        self.list.append(WallHorizontal(group=groups['walls_horizontal'], x=self.x + 4, y=self.y + 31, size=(48, 1)))
        self.list.append(WallVertical(group=groups['walls_vertical'], x=self.x, y=self.y + 1, size=(1, 30)))
        self.list.append(WallVertical(group=groups['walls_vertical'], x=self.x + 55, y=self.y + 1, size=(1, 30)))

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
