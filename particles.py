import pygame as pg
import random
from utils import smooth

class Particle:
    """
        A class for objects that appear temporarily on-screen but are not entities in the world.
        For example, text popups when the player scores.
    """
    def __init__(self, pos, lifetime):
        self.pos = pos

        self.to_remove = False

        self.lifetime = lifetime
        """
            The particle's remaining lifetime in seconds
        """
        self.total_lifetime = lifetime
        """
            The particle's initial lifetime in seconds
        """

    def update(self, game, dt):
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.remove()

    def remove(self):
        self.to_remove = True

    def draw(self, screen):
        pass

class TextPopup(Particle):
    LIFETIME = 0.4
    def __init__(self, game, text, color, pos):
        super().__init__(pos, TextPopup.LIFETIME*(0.5+random.random()))

        # Move the text in a little if it's too close to the edges
        # The bottom and right are -50 because pos is from the top left
        padding = 30
        if self.pos[0] < padding:
            self.pos[0] = padding+random.random()*padding
        elif self.pos[0] > game.width-padding-50:
            self.pos[0] = game.width-padding-50-random.random()*padding
        if self.pos[1] < padding:
            self.pos[1] = padding+random.random()*padding
        elif self.pos[1] > game.height-padding-50:
            self.pos[1] = game.height-padding-50-random.random()*padding

        self.text = text
        self.color = color
        self.image = pg.transform.scale_by(
            pg.transform.rotate(
                game.font.render(text, True, color), 
                random.random()*180-90
            ),
            random.random()*1.5+1
        )

    def draw(self, screen):
        t = self.lifetime/self.total_lifetime
        if t>0.5:
            scale = (1-t)*2
            screen.blit(pg.transform.scale_by(self.image, scale), self.pos)
        else:
            alpha = 1-abs(t-0.5)*2
            self.image.set_alpha(alpha*255)
            screen.blit(self.image, self.pos)
