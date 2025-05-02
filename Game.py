import pygame as pg
from entities import Player, Wall
from utils import *

class Game:
    """
        The class used to store and update the game state.
        All functionality should go through this class at some point.
        Stores the screen, clock, player, and other entities, and any other global game state.
    """
    def __init__(self, width, height):
        pg.init()

        self.width = width
        self.height = height
        self.screen = pg.display.set_mode((self.width, self.height), pg.RESIZABLE)
        self.clock = pg.time.Clock()

        self.player = Player([width/2, height/2])
        self.entities = [self.player, Wall([width/4, height/4], [width/2, 50])]

        self.playing = False
    
    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_q):
                self.playing = False
            for entity in self.entities:
                entity.handle_event(event, self)
    
    def update(self):
        dt = self.clock.get_time()/1000 # seconds since last frame
        for entity in self.entities:
            entity.update(self, dt)

    def draw(self):
        self.screen.fill(WHITE)

        for entity in self.entities:
            entity.draw(self.screen)

        pg.display.flip()

    
    def run(self, fps):
        self.playing = True
        while self.playing:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(fps)