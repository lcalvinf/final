import pygame as pg
from utils import *

FRICTION = 400              # strength of friction, px/s^2
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
        """
            A vector representing the entity's width and height in pixels
        """

        self.vel = [0,0]
        self.acc = [0,0]

        self.friction = FRICTION
        """
            Describes this entity's friction strength in px/s^2
        """

        self.mass = 0
        """
            Describes this entity's mass, in an arbitrary unit.
            Set mass to 0 to indicate the entity cannot move.
        """

        self.radius = 0
        """
            The entity's radius in pixels, if it is circular (or should use circle-based collisions)
            To treat the entity as a rectangle, set this to 0
        """
    
    def get_rect(self):
        return pg.Rect(*self.pos, *self.size)

    def update(self, game, dt):
        """ 
            Method called every frame. 
            Subclasses should override this function but still call `super().update()` afterward.
        """

        # The first time update is called dt=0, which means when we divide by dt it doesn't work.
        # Nobody's gonna miss one update call, right?
        if dt == 0:
            return
        self.apply_force(set_mag(self.vel, -self.friction*self.mass))

        old_pos = list(self.pos)
        self.pos = add_vectors(self.pos, scale_vector(self.vel, dt))
        normal, entity = self.handle_collisions(game)
        if normal is not None:
            self.pos = old_pos
            # The normal force is scaled to counter the velocity, but only the component of the velocity going against the normal force
            # That's what the dot product does. We scale by two to fully reverse rather than just cancelling it out
            # Also, the velocity is relative to the entity we're colliding with, hence why we subtract entity.vel from self.vel
            dot = dot_product(normal, sub_vectors(self.vel, entity.vel))
            force = scale_vector(normal, dot*2*COLLISION_ELASTICITY/dt)

            # We split the force over the two entities according to their portion of the system's mass.
            total_mass = self.mass+entity.mass
            self.apply_force(scale_vector(force, -self.mass/total_mass))
            entity.apply_force(scale_vector(force, entity.mass/total_mass))

        self.vel = add_vectors(self.vel, scale_vector(self.acc, dt))

        # Prevent annoying slow sliding by stopping entities as soon as their velocity get pretty small
        # Fifty might not seem that small, but:
        #   1. That's compared to the *square* magnitude of the velocity (v * v = |v|^2), so we're really talking about ~7 pixels per second
        #   2. pixels per *second*. If you're going less than 7 pixels every second, you're basically not moving
        if dot_product(self.vel,self.vel) <= 50:
            self.vel = [0,0]

        self.acc = [0,0]
    
    def apply_force(self, force):
        self.acc = add_vectors(self.acc, scale_vector(force, self.mass))
    
    def handle_collisions(self, game):
        """
            Checks for collision with all solid entities in the game.
            Returns `None, None` if no collisions were found, otherwise returns a normal vector indicating which
            way the normal force from the collisions should point and the entity collided with.
            The normal vector is normalized.
        """
        normal = None
        collided = None
        for entity in game.entities:
            if entity == self:
                continue
            if not type(entity).SOLID:
                continue
            did_collide = False
            if self.radius != 0 and entity.radius != 0:
                self_pos = self.get_rect().center
                ent_pos = entity.get_rect().center
                did_collide = square_dist(self_pos, ent_pos) <= (self.radius+entity.radius)**2
            else:
                did_collide = entity.get_rect().colliderect(self.get_rect())

            if did_collide:
                self.collide(entity)
                clip = entity.get_rect().clip(self.get_rect())
                collided = entity
                for normal_zone, normal_vec in entity.normals:
                    if clip.colliderect(normal_zone):
                        normal = normal_vec
                        break
                else:
                    normal = normalize_vector(sub_vectors(self.get_rect().center, entity.get_rect().center))
        return normal, collided

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

class Ball(Entity):
    """
        A ball.
        This object is solid and circular, and has a mass of 1.
    """
    R = 10  # The ball's radius
    SOLID = True
    def __init__(self, pos):
        super().__init__(pos, [Ball.R*2, Ball.R*2])
        self.normals = []
        self.mass = 1
        self.radius = Ball.R
    def draw(self, screen):
        pg.draw.circle(screen, BLACK, add_vectors(self.pos, [self.radius,self.radius]), self.radius)

class Player(Ball):
    """
        The class representing the player. Only one instance of this class should exist at any time.
    """
    SPEED = 3000 # player's maximum acceleration, px/s^2

    SOLID = True
    def __init__(self, pos):
        super().__init__(pos)
        self.speed = Player.SPEED
    
    def update(self, game, dt):
        if pg.mouse.get_pressed()[0]:
            if self.speed > 0:
                self.acc = set_mag(sub_vectors(pg.mouse.get_pos(), self.pos), self.speed)
                # The player accelerates less the longer they hold down the mouse
                self.speed -= 1000*dt
        else:
            self.speed = Player.SPEED
        

        super().update(game, dt)

    def draw(self, screen):
        pg.draw.circle(screen, RED, add_vectors(self.pos, [self.radius,self.radius]), self.radius)
    
class Wall(Entity):
    """
        A stationary obstacle.
        Has mass set to 0, indicating that it cannot move.
        Ignores attempts to apply force or update.
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
        self.mass = 0

    def update(self, game, dt):
        pass
    
    def apply_force(self, force):
        pass

    def draw(self, screen):
        pg.draw.rect(screen, BLACK, self.get_rect())
