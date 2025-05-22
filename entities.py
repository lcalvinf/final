import pygame as pg
import math
from colors import COLORS
from utils import add_vectors, sub_vectors, dot_product, set_mag, scale_vector, normalize_vector, square_dist, lerp, vector_size, vector_angle, rotate_vector
from layout import HOLE_R, LAYOUT
from particles import TextPopup

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
        self.to_remove = False
        self.pos = pos
        self.start_pos = list(pos)
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
        if entity is not None:
            game.play_sound("hit")
            self.pos = old_pos
            # The normal force is scaled to counter the velocity, but only the component of the velocity going against the normal force
            # That's what the dot product does. We scale by two to fully reverse rather than just cancelling it out
            # Also, the velocity is relative to the entity we're colliding with, hence why we subtract entity.vel from self.vel
            dot = dot_product(normal, sub_vectors(self.vel, entity.vel))
            force = scale_vector(normal, dot*2*COLLISION_ELASTICITY/dt)

            # We split the force over the two entities according to their portion of the system's mass.
            # Unless the entity is fixed in place, indicated by a mass of 0
            if entity.mass == 0:
                self.apply_force(scale_vector(force, -self.mass))
            else:
                total_mass = self.mass+entity.mass
                self.apply_force(scale_vector(force,-self.mass/total_mass))
                entity.apply_force(scale_vector(force,entity.mass/total_mass))

        self.vel = add_vectors(self.vel, scale_vector(self.acc, dt))

        # Prevent annoying slow sliding by stopping entities as soon as their velocity get pretty small
        # Fifty might not seem that small, but:
        #   1. That's compared to the *square* magnitude of the velocity (v * v = |v|^2), so we're really talking about ~7 pixels per second
        #   2. pixels per *second*. If you're going less than 7 pixels every second, you're basically not moving
        if dot_product(self.vel,self.vel) <= 50:
            self.vel = [0,0]

        self.acc = [0,0]
    
    def apply_force(self, force):
        self.acc = add_vectors(self.acc, scale_vector(force, 1/self.mass))
    
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
                self.collide(entity, game)
                clip = entity.get_rect().clip(self.get_rect())
                collided = entity
                for normal_zone, normal_vec in entity.normals:
                    if clip.colliderect(normal_zone):
                        normal = normal_vec
                        break
                else:
                    normal = normalize_vector(sub_vectors(self.get_rect().center, entity.get_rect().center))
        return normal, collided

    def collide(self, entity, game):
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
    
    def remove(self):
        """
            Remove this entity from the game by the next frame.
        """
        self.to_remove = True

class Ball(Entity):
    """
        A ball.
        This object is solid and circular, and has a mass of 1.
    """
    R = 15  # The ball's radius, px
    SOLID = True
    def __init__(self, pos):
        radius = type(self).R
        pos = sub_vectors(pos, [radius,radius])
        super().__init__(pos, [radius*2, radius*2])
        self.normals = []
        self.mass = 1
        self.radius = radius
        self.color = COLORS["ball"]

        self.animation = {
                "going": False
        }
        """
            Stores information about the current animation, if any
        """

        self.potted_this_shot = False
        """
            Was this ball potted during the most recent shot?
        """
    def update(self, game, dt):
        super().update(game,dt)

        for hole in game.holes:
            if square_dist(add_vectors(self.pos, [self.radius,self.radius]), hole) <= (self.R+HOLE_R)**2:
                self.pot(game)

        self.update_animation(dt)

    def update_animation(self,dt):
        if self.animation["going"]:
            self.animation["time"] += dt
            t = self.animation["time"]/self.animation["total_time"]
            if t > 1:
                self.animation["going"] = False
                self.radius = type(self).R
                self.pos = sub_vectors(self.animation["center"], [self.radius,self.radius])
            else:
                self.animation["current"] = lerp(self.animation["start"], self.animation["end"], t)
                self.pos = sub_vectors(self.animation["center"], [self.animation["current"], self.animation["current"]])

    def start_animation(self, time, start, end):
        """
            Start animating the ball's radius linearly.
            The animation lasts `time` seconds.
            `start` and `end` are the radii to start and end on, respectively.
        """
        self.animation = {
                "going": True,
                "time": 0, "current": 0,
                "total_time": time,
                "start": start, "end": end,
                "center": add_vectors(self.pos, [self.radius, self.radius])
                }
    def pot(self, game):
        """
            Method called whenever the ball is potted, meaning it enters one
            of the holes on the edges of the board.
            Subclasses need not call super().pot
        """
        game.play_sound("score")
        game.add_particle(TextPopup(game, "+1", self.color, self.pos))
        game.score += 1
        self.potted_this_shot = True
        self.remove()
    def draw(self, screen):
        if self.animation["going"]:
            r = self.animation["current"]
            self.radius = r

        if self.potted_this_shot:
            return
        loc = add_vectors(self.pos, [self.radius, self.radius])

        # Draw a little tail behind the ball
        vel_size = vector_size(self.vel)
        if vel_size >= 10:
            angle = vector_angle([self.vel[0], -self.vel[1]])
            pg.draw.polygon(screen, 
                # I can't get apha working so I'm doing it manually
                self.color.lerp(COLORS["background"],0.5),
            [
                sub_vectors(loc, rotate_vector([self.radius,0],angle+math.pi/2)),
                sub_vectors(loc, rotate_vector([self.radius*2*min(vel_size/200,2),0],angle)),
                sub_vectors(loc, rotate_vector([self.radius,0],angle-math.pi/2)),
            ])

        # Draw the actual ball
        pg.draw.circle(screen, self.color, loc, self.radius)


class RedBall(Ball):
    """
        The least valuable kind of ball, worth only 1 point.
    """
    R = Ball.R
    SOLID = True
    def __init__(self, pos):
        super().__init__(pos)
        self.color = COLORS["red-ball"]
    def update(self, game, dt):
        if self.potted_this_shot:
            if not game.shot:
                for x, y in LAYOUT["red-balls"]:
                    ball = RedBall([x*game.width, y*game.height])
                    game.add_entity(ball)
                    ball.start_animation(0.125,0,RedBall.R)
                self.remove()
            return
        super().update(game, dt)
    def pot(self, game):
        if self.potted_this_shot:
            return

        if all([not isinstance(ent, RedBall) or ent == self for ent in game.entities]):
            game.play_sound("reset")
            # Sinking all five reds gives you  4+this number total points
            # That needs to be significantly more than sinking all five blues to be worth it
            # 5 blues times 4 points per blue is 20 points for sinking all the blues
            # So this number has to be at least 16 just to break even
            # It should be more to make going for the reds appealing as a gamble
            game.score += 20
            game.add_particle(TextPopup(game, "Red Clear!", self.color, [game.width/2-50,game.height/2-25]))
            self.vel = [0,0]
            self.potted_this_shot = True
        else:
            super().pot(game)


class BlueBall(Ball):
    """
        The more valuable kind of ball, which respawns when potted.
    """
    R = Ball.R
    SOLID = True
    def __init__(self, pos):
        super().__init__(pos)
        self.color = COLORS["blue-ball"]
    def update(self, game, dt):
        if self.potted_this_shot:
            if not game.shot:
                self.potted_this_shot = False
                self.pos = list(self.start_pos)
                self.start_animation(0.125, 0, BlueBall.R)
            else:
                return
        super().update(game, dt)
    def pot(self, game):
        if self.potted_this_shot:
            return
        game.play_sound("score")
        game.score += 4
        game.add_particle(TextPopup(game, "+4", self.color, self.pos))
        self.vel = [0,0]
        self.potted_this_shot = True

class BlackBall(Ball):
    """
        The smallest ball, which respawns and loses you points when potted.
    """
    R = Ball.R*0.75
    SOLID = True
    def __init__(self, pos):
        super().__init__(pos)
        self.color = COLORS["black-ball"]
        # Realistically, a sphere's volume is proportional to the cube of its radius
        # And mass is directly proportional to volume (if the object's density is constant)
        # So we should cube the ratio of radii to find the mass
        # But the game is 2D so it feels right to square it instead
        self.mass = (BlackBall.R/Ball.R)**2
        self.start_pos = list(pos)
    def update(self, game, dt):
        if self.potted_this_shot:
            if not game.shot:
                self.potted_this_shot = False
                self.pos = list(self.start_pos)
                self.start_animation(0.125, 0, BlackBall.R)
            else:
                return
        super().update(game, dt)
    def pot(self, game):
        if self.potted_this_shot:
            return
        game.play_sound("score")
        game.score = max(game.score-5, 0)
        game.add_particle(TextPopup(game, "-5", self.color, self.pos))
        self.vel = [0,0]
        self.potted_this_shot = True

class GoldBall(Ball):
    """
        The largest ball, which respawns and adds 7 points when potted.
    """
    R = Ball.R*1.5
    def __init__(self, pos):
        super().__init__(pos)
        self.color = COLORS["gold-ball"]
        # See BlackBall.__init__ for an explanation of what the square is doing here
        self.mass = (GoldBall.R/Ball.R)**2
        self.start_pos = list(pos)
    def update(self, game, dt):
        if self.potted_this_shot:
            if not game.shot:
                self.potted_this_shot = False
                self.pos = list(self.start_pos)
                self.start_animation(0.125, 0, GoldBall.R)
            else:
                return
        super().update(game, dt)
    def pot(self, game):
        if self.potted_this_shot:
            return
        game.play_sound("score")
        game.score += 7
        game.add_particle(TextPopup(game, "+7", self.color, self.pos))
        self.vel = [0,0]
        self.potted_this_shot = True



class Player(Ball):
    """
        The class representing the player. Only one instance of this class should exist at any time.
    """
    SPEED = 2000 # player's maximum acceleration, px/s^2

    SOLID = True
    def __init__(self, pos):
        super().__init__(pos)
        self.speed = Player.SPEED
        self.color = COLORS["player"]
    
    def update(self, game, dt):
        if pg.mouse.get_pressed()[0]:
            if not game.shot:
                game.start_shot()
            if self.speed > 0:
                self.acc = set_mag(sub_vectors(pg.mouse.get_pos(), self.pos), self.speed)
                # The player accelerates less the longer they hold down the mouse
                self.speed -= 1000*dt
        elif not game.shot:
            self.speed = Player.SPEED
        

        super().update(game, dt)

    def pot(self, game):
        game.play_sound("player_sink")
        self.pos = list(self.start_pos)
        self.start_animation(0.125, 0, self.radius)
    
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
        pg.draw.rect(screen, COLORS["foreground"], self.get_rect())
