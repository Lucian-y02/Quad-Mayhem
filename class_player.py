import pygame


pygame.init()


class Player(pygame.sprite.Sprite):
    def __init__(self, groups: dict, **kwargs):
        super(Player, self).__init__(groups["players"])
        self.image = pygame.Surface((40, 60))
        self.rect = self.image.get_rect()
        self.rect.x = kwargs.get("x", 0)
        self.rect.y = kwargs.get("y", 0)

        self.groups = groups

        self.speed = kwargs.get("speed", 5)  # Скорость персонажа
        self.gravity = kwargs.get("gravity", 10)  # Значение гравитации
        self.resistance = 0  # Значение реакции опоры
        self.jump_force_count = kwargs.get("jump_force", 10)  # Начальное значение jump_force
        self.jump_force = 0  # Сила прыжка

    def update(self):
        key = pygame.key.get_pressed()
        move_x = 0

        # Проверка на столкновение
        if pygame.sprite.spritecollideany(self, self.groups["walls"]):
            self.resistance = -self.gravity
        elif not pygame.sprite.spritecollideany(self, self.groups["walls"]):
            self.resistance = 0

        # Прыжок
        self.jump_force -= 1 if self.jump_force > 0 else 0
        if key[pygame.K_w] and self.resistance:
            self.jump_force = self.jump_force_count

        # Передвижение вправо и влево
        if key[pygame.K_a]:
            move_x -= self.speed
        if key[pygame.K_d]:
            move_x += self.speed

        # Смещение персонажа
        self.rect.move_ip(move_x, self.resistance + self.gravity - (self.jump_force ** 1.2))
