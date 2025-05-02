import pygame as pg
from utils import *

FRICTION = 200 # strength of friction, px/s^2

class Entity:
    """
        The base class for all entities.
        This is an abstract class--it does not constitute a functional entity on its own.
        Subclasses can define a property `SOLID` to make other objects collide with them.
        Solid entities should also define on each instance a list of normal vectors for collisions. Each item of the list is a pair of values:
            - A `Rect` indicating where the normal vector applies
            - A normalized vector pointing in the direction of the normal
    """
    SOLID = False
    def __init__(self, pos, size):
        self.pos = pos
        self.size = size
        self.vel = [0,0]
        self.acc = [0,0]
    
    def get_rect(self):
        return pg.Rect(*self.pos, *self.size)

    def update(self, game, dt):
        """ 
            Method called every frame. 
            Subclasses should override this function but still call `super().update()` afterward.
        """
        self.apply_force(set_mag(self.vel, -FRICTION))

        old_pos = list(self.pos)
        self.pos = add_vectors(self.pos, scale_vector(self.vel, dt))
        normal = self.handle_collisions(game)
        if normal is not None:
            self.pos = old_pos
            self.apply_force(scale_vector(normal, vector_size(self.vel)*2/dt))
        self.vel = add_vectors(self.vel, scale_vector(self.acc, dt))

        self.acc = [0,0]
    
    def apply_force(self, force):
        self.acc = add_vectors(self.acc, force)
    
    def handle_collisions(self, game):
        """
            Checks for collision with all solid entities in the game.
            Returns `None` if no collisions were found, otherwise returns a normal vector indicating which
            way the normal force from the collisions should point. The normal vector is normalized.
        """
        normal = None
        for entity in game.entities:
            entity: Entity
            if entity == self:
                continue
            if not type(entity).SOLID:
                continue
            if entity.get_rect().colliderect(self.get_rect()):
                self.collide(entity)
                clip = entity.get_rect().clip(self.get_rect())
                for normal_zone, normal_vec in entity.normals:
                    if clip.colliderect(normal_zone):
                        normal = normal_vec
                        break
                else:
                    normal = normalize_vector(sub_vectors(self.get_rect().center, entity.get_rect().center))
        return normal

    def collide(self, entity):
        """
            Method to handle each collision with a solid entity.
            Subclasses should override this method if they want to do anything other than bounce off of entities.
        """
        pass

    def draw(self):
        """
            Method called every frame.
            Subclasses should override this function and do not need to call `super().draw()`.
        """
        pass

    def handle_event(self, event, game):
        """
            Method called every time an event is registered.
            Subclasses can override this function to detect events, and do not need to call `super().handle_event()`.
        """
        pass

class Player(Entity):
    """
        The class representing the player. Only one instance of this class should exist at any time.
    """
    R = 10 # the player's radius
    SPEED = 1000 # player's acceleration, px/s^2
    def __init__(self, pos):
        super().__init__(pos, [Player.R*2, Player.R*2])
    
    def update(self, game, dt):
        keys = pg.key.get_pressed()
        if keys[pg.K_w]:
            self.acc[1] = -Player.SPEED
        if keys[pg.K_s]:
            self.acc[1] = Player.SPEED
        if keys[pg.K_d]:
            self.acc[0] = Player.SPEED
        if keys[pg.K_a]:
            self.acc[0] = -Player.SPEED

        super().update(game, dt)

    def draw(self, screen):
        pg.draw.circle(screen, BLACK, self.pos, Player.R)
    
class Wall(Entity):
    """
        A stationary obstacle.
    """
    SOLID = True
    def __init__(self, pos, size):
        super().__init__(pos, size)
        self.normals = [
            [pg.Rect(*pos, size[0], 5), [0, -1]],
            [pg.Rect(*pos, 5, size[1]), [-1, 0]],
            [pg.Rect(pos[0]+size[0]-5, pos[1], 5, size[1]), [1, 0]],
            [pg.Rect(pos[0], pos[1]+size[1]-5, size[0], 5), [0, -1]],
        ]

    def update(self, game, dt):
        pass

    def draw(self, screen):
        pg.draw.rect(screen, BLACK, self.get_rect())
