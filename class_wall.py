import pygame


pygame.init()


class Wall(pygame.sprite.Sprite):
    def __init__(self, groups: dict, **kwargs):
        super(Wall, self).__init__(groups["walls"])
        self.image = pygame.Surface(kwargs.get("wall_size", (32, 32)))
        self.rect = self.image.get_rect()
        self.rect.x = kwargs.get("x", 0)
        self.rect.y = kwargs.get("y", 0)
