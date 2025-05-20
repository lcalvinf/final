import pygame as pg
from entities import Player, Wall, Ball
import random
from utils import *
from colors import *
from layout import *

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

        self.player = Player([width*LAYOUT["player"][0], height*LAYOUT["player"][1]])
        self.entities = [self.player]
        self.holes = [[x*self.width, y*self.height] for x,y in LAYOUT["holes"]]
        for x,y in LAYOUT["balls"]:
            self.entities.append(
                Ball([x*self.width, y*self.height])
            )
        self.generate_walls()

        self.playing = False
    def generate_walls(self):
        """
            Make walls around the edges of the screen. Called during __init__ and whenever resetting entities.
        """
        thickness = 10
        self.entities.extend([
            Wall([0,-thickness], [self.width, thickness]),
            Wall([-thickness,0], [thickness, self.height]),
            Wall([0,self.height], [self.width, thickness]),
            Wall([self.width,0], [thickness, self.height]),
        ])
    
    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_q):
                self.playing = False
            for entity in self.entities:
                entity.handle_event(event, self)
    
    def update(self):
        dt = self.clock.get_time()/1000 # seconds since last frame
        new_entities = []
        for entity in self.entities:
            entity.update(self, dt)
            if not entity.to_remove:
                new_entities.append(entity)
        self.entities = new_entities

    def draw(self):
        self.screen.fill(COLORS["background"])

        for entity in self.entities:
            entity.draw(self.screen)
        
        for hole in self.holes:
            pg.draw.circle(self.screen, COLORS["hole"], hole, HOLE_R)

        pg.display.flip()

    
    def run(self, fps):
        self.playing = True
        while self.playing:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(fps)