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

        self.reset()

        self.playing = False
        """
            Set this to False to end the current game loop and move on to the next one
        """
        self.quit = False
        """
            Set this to True to exit the game entirely
        """

        self.ball_hit_this_shot = False
        """
            Has the player hit a ball in this shot?
        """
        self.shot = False
        """
            Is the player currently making a shot?
        """
    
    def reset(self):
        """
            Set up the board for a new game
        """
        self.holes = [[x*self.width, y*self.height] for x,y in LAYOUT["holes"]]

        self.player = Player([self.width*LAYOUT["player"][0], self.height*LAYOUT["player"][1]])
        self.entities = [self.player]
        for x,y in LAYOUT["balls"]:
            self.entities.append(
                Ball([x*self.width, y*self.height])
            )

        self.generate_walls()

        self.ball_hit_this_shot = False
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
    
    def start_shot(self):
        """
            Call this once when the player begins a shot
        """
        self.shot = True
        self.ball_hit_this_shot = False
    def end_shot(self):
        """
            Call this once when the player finishes a shot
        """
        self.shot = False
        if not self.ball_hit_this_shot:
            self.playing = False
    
    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_q):
                self.quit = True
            for entity in self.entities:
                entity.handle_event(event, self)
    
    def update(self):
        dt = self.clock.get_time()/1000 # seconds since last frame

        ball_moving = False

        new_entities = []
        for entity in self.entities:
            entity.update(self, dt)
            if isinstance(entity, Ball) and (entity.vel[0] != 0 or entity.vel[1] != 0):
                ball_moving = True
            if not entity.to_remove:
                new_entities.append(entity)
        self.entities = new_entities

        if self.shot and not ball_moving:
            self.end_shot()

    def draw(self):
        self.screen.fill(COLORS["background"])

        for entity in self.entities:
            entity.draw(self.screen)
        
        for hole in self.holes:
            pg.draw.circle(self.screen, COLORS["hole"], hole, HOLE_R)

        pg.display.flip()


    def game_over(self, fps):
        """
            Display the game over screen.
            Call this only *after* ending the current game loop by setting self.playing to False and allowing a loop to pass.
        """
        self.playing = True
        self.entities = []
        while self.playing and not self.quit:
            for event in pg.event.get():
                if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_q):
                    self.quit = True
                elif event.type == pg.KEYDOWN:
                    self.playing = False

            self.screen.fill(COLORS["background"])

            pg.display.flip()
            self.clock.tick(fps)
        
        if not self.quit:
            self.run(fps)
    
    def run(self, fps):
        self.playing = True
        self.reset()
        while self.playing and not self.quit:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(fps)

        if self.quit:
            return

        self.game_over(fps)