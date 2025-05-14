import pygame as pg
from utils import *

FRICTION = 200              # strength of friction, px/s^2
COLLISION_ELASTICITY = 0.9  # percentage of energy preserved through collisions

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
        self.friction = FRICTION
        """
            Describes this entity's friction strength in px/s^2
        """
    
    def get_rect(self):
        return pg.Rect(*self.pos, *self.size)

    def update(self, game, dt):
        """ 
            Method called every frame. 
            Subclasses should override this function but still call `super().update()` afterward.
        """
        self.apply_force(set_mag(self.vel, -self.friction))

        old_pos = list(self.pos)
        self.pos = add_vectors(self.pos, scale_vector(self.vel, dt))
        normal = self.handle_collisions(game)
        if normal is not None:
            self.pos = old_pos
            # The normal force is scaled to counter the velocity, but only the component of the velocity going against the normal force
            # Hence, the dot product -- negated because we're going against the velocity, and *2 so flips rather than just being zeroed out
            dot = dot_product(normal, self.vel)
            self.apply_force(scale_vector(normal, -dot*2*COLLISION_ELASTICITY/dt))
        self.vel = add_vectors(self.vel, scale_vector(self.acc, dt))

        # Prevent annoying slow sliding by stopping entities as soon as their velocity get pretty small
        # Fifty might not seem that small, but:
        #   1. That's compared to the *square* magnitude of the velocity (v * v = |v|^2), so we're really talking about ~7 pixels per second
        #   2. pixels per *second*. If you're going less than 7 pixels every second, you're basically not moving
        if dot_product(self.vel,self.vel) <= 50:
            self.vel = [0,0]

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
    R = 10       # the player's radius
    SPEED = 2000 # player's acceleration, px/s^2

    LOW_FRICTION = 100  # the player's friction when speeding up, px/s^2
    HIGH_FRICTION = 1000 # the player's friction when slowing down, px/s^2
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
        
        # The player gets slowed down faster when they're not trying to speed up
        # That way it feels responsive both speeding up and slowing down
        if self.acc[0] != 0 or self.acc[1] != 0:
            # This checks if the acceleration is in the opposite direction to the velocity
            # if it is, high friction will go in the same direction as the player's controls, so we should do that.
            if dot_product(self.acc, self.vel) < 0:
                self.friction = Player.HIGH_FRICTION
            else:
                self.friction = Player.LOW_FRICTION
        else:
            self.friction = Player.HIGH_FRICTION

        super().update(game, dt)

    def draw(self, screen):
        pg.draw.circle(screen, BLACK, add_vectors(self.pos, [Player.R,Player.R]), Player.R)
    
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
            [pg.Rect(pos[0], pos[1]+size[1]-5, size[0], 5), [0, 1]],
        ]

    def update(self, game, dt):
        pass

    def draw(self, screen):
        pg.draw.rect(screen, BLACK, self.get_rect())
