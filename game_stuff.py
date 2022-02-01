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
        self.image = pygame.image.load("Weapons/SemiAutomaticSniperRifle.png").convert_alpha()
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
        self.bullet_image = pygame.Surface((32, 2))  # Изображение пули
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
        self.image = pygame.image.load("Weapons/MachineGun.png").convert_alpha()
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
        self.bullet_image = pygame.Surface((32, 2))  # Изображение пули
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
        self.image = pygame.image.load("Weapons/SniperRifle.png").convert_alpha()
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
        self.bullet_image = pygame.Surface((64, 2))  # Изображение пули
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
        self.image = pygame.image.load("Weapons/SubMachineGun.png").convert_alpha()
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
        self.bullet_image = pygame.Surface((16, 2))  # Изображение пули
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
        self.image.fill(kwargs.get("color", (150, 150, 150)))
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
        self.image.fill(kwargs.get("color", (0, 150, 0)))
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
        self.rect.x = kwargs.get("x", 0) + (32 - self.rect.width) // 2
        self.rect.y = kwargs.get("y", 0) + 32 - self.rect.height

        self.cool_down = kwargs.get("cool_down", 200)  # Интервал появления предметов
        self.weapon_list = kwargs.get("weapon_list", [Weapon])  # Список пояляющихся предметов
        self.weapon = kwargs.get("weapon", None)  # Находящийся в спаунере предмет

        self.mirror = kwargs.get("mirror", False)

        self.groups = groups

        self.time = 0
        TimeIndicator(self.groups["game_stuff"], size=(self.rect.width, self.rect.height),
                      max_time=self.cool_down, shift_vertical=-self.rect.height - 6,
                      color=(0, 150, 0), user=self)

    def update(self):
        if not self.weapon:
            self.time += 1
        if self.time >= self.cool_down:
            self.time = 1
            chosen_weapon = choice(self.weapon_list)
            chosen_weapon(self.groups, x=self.rect.x - self.rect.width // 2,
                          y=self.rect.y - 24, gravity=0, spawner=self,
                          mirror=self.mirror)
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


# Флаг для режима "Захват флага"
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

        self.team = kwargs.get("team", "0")  # Чьей команде принадлежит точка
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


# Силовое поле Джаспера
class JasperProtect(pygame.sprite.Sprite):
    def __init__(self, groups: dict, **kwargs):
        super(JasperProtect, self).__init__(groups["game_stuff"])
        self.user = kwargs.get("user", None)
        self.image = pygame.Surface(kwargs.get("size", (32, 44)))
        self.image.fill((250, 0, 250))
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
        self.image = pygame.Surface(kwargs.get("size", (96, 30)))
        self.image.fill(kwargs.get("color", (0, 250, 0)))
        self.image.set_alpha(45)
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
        self.image = pygame.Surface(kwargs.get("size", (24, 24)))
        self.image.fill(kwargs.get("color", (0, 150, 0)))
        self.rect = self.image.get_rect()
        self.rect.x = self.user.rect.x
        self.rect.y = self.user.rect.y + self.user.rect.height - self.rect.height

        # Изображение пули
        self.bullet_image = pygame.Surface((8, 6))

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


class Door(pygame.sprite.Sprite):
    def __init__(self, groups: dict, **kwargs):
        super(Door, self).__init__(groups["doors"])
        self.image = pygame.Surface(kwargs.get("size", (24, 64)))
        self.image.fill(kwargs.get("color", (100, 100, 100)))
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

        for bullet in self.bullets:
            if (self.rect.colliderect(bullet.rect) and not self.is_open and
                    not bullet.through_the_doors):
                bullet.kill()
