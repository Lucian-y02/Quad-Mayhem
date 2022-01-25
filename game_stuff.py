from random import randint, choice

import pygame


pygame.init()


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


# Стена
class Wall(pygame.sprite.Sprite):
    def __init__(self, group, **kwargs):
        super(Wall, self).__init__(group)
        self.image = pygame.Surface(kwargs.get("size", (32, 32)))
        self.rect = self.image.get_rect()
        self.rect.x = kwargs.get("x", 0)
        self.rect.y = kwargs.get("y", 0)


# Горизонатльая стена
class WallHorizontal(Wall):
    def __init__(self, group, **kwargs):
        super(WallHorizontal, self).__init__(group, **kwargs)
        self.image = pygame.Surface(kwargs.get("size", (32, 1)))


# Вертикальная стена
class WallVertical(Wall):
    def __init__(self, group, **kwargs):
        super(WallVertical, self).__init__(group, **kwargs)
        self.image = pygame.Surface(kwargs.get("size", (1, 32)))


# Спаунер предметов
class ItemsSpawner(pygame.sprite.Sprite):
    def __init__(self, groups: dict, **kwargs):
        super(ItemsSpawner, self).__init__(groups["game_stuff"])
        self.image = pygame.Surface(kwargs.get("size", (28, 7)))
        self.rect = self.image.get_rect()
        self.rect.x = kwargs.get("x", 0) + 32 - self.rect.width // 2
        self.rect.y = kwargs.get("y", 0) + 32 - self.rect.height

        self.cool_down = kwargs.get("cool_down", 8)  # Интервал появления предметов
        self.weapon_list = kwargs.get("weapon_list", [Weapon])  # Список пояляющихся предметов
        self.weapon = kwargs.get("weapon", None)  # Находяееся в спаунере предмет

        self.groups = groups

        self.WEAPON_SPAWN = pygame.USEREVENT + 1
        pygame.time.set_timer(self.WEAPON_SPAWN, 1000 * self.cool_down)

    def update(self):
        if not self.weapon:
            pygame.time.set_timer(self.WEAPON_SPAWN, 1000 * self.cool_down)
        for event in pygame.event.get():
            if event.type == self.WEAPON_SPAWN:
                chosen_weapon = choice(self.weapon_list)
                chosen_weapon(self.groups, x=self.rect.x - self.rect.width // 2,
                              y=self.rect.y - 24, gravity=0, spawner=self)
                self.weapon = chosen_weapon
                pygame.time.set_timer(self.WEAPON_SPAWN, 0)


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


# Стекло
class Glass(pygame.sprite.Sprite):
    def __init__(self, group, **kwargs):
        super(Glass, self).__init__(group)


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
        self.team = kwargs.get("team", "0")  # Чьей команде принадлежит точка
        self.end_function = kwargs.get("end_function", None)  # Функция окончания игровой сессии

        self.timer = 0

    def update(self):
        for player in self.players_data:
            if self.rect.colliderect(player.rect) and player.team != self.team:
                self.timer += 1

        if self.timer % 1 == 0 and self.timer != 0:
            self.health_points -= 1
            self.timer = 0

        if self.health_points <= 0:
            self.end_function(f"team 2 win!")
