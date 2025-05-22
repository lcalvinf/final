import pygame as pg
from entities import Player, Wall, Ball, RedBall, BlueBall, BlackBall, GoldBall
from utils import vector_size, DEBUG, scale_vector, sub_vectors, SOUNDS
from colors import COLORS
from layout import LAYOUT, HOLE_R


class Game:
    """
        The class used to store and update the game state.
        All functionality should go through this class at some point.
        Stores the screen, clock, player, and other entities, and any other
        global game state.
    """

    def __init__(self, width, height):
        pg.init()

        self.width = width
        self.height = height
        self.screen = pg.display.set_mode(
                (self.width, self.height),
                pg.RESIZABLE
        )
        self.clock = pg.time.Clock()

        self.font = pg.font.SysFont("sans-serif", 50)
        self.smallfont = pg.font.SysFont("sans-serif", 30)

        self.load_sounds()

        self.reset()

        self.playing = False
        """
            Set this to False to end the current game loop and move on to
            the next one
        """
        self.quit = False
        """
            Set this to True to exit the game entirely
        """

        self.shots_left = 0
        """
            The number of shots the player has before the game ends
        """
        self.shot = False
        """
            Is the player currently making a shot?
        """

    def reset(self):
        """
            Set up the board for a new game
        """
        self.holes = [
                [x*self.width, y*self.height]
                for x, y in LAYOUT["holes"]
        ]

        self.player = Player(
                [self.width*LAYOUT["player"][0],
                 self.height*LAYOUT["player"][1]]
        )
        self.entities = [self.player]
        self.ents_to_add = []
        for x, y in LAYOUT["red-balls"]:
            self.entities.append(RedBall([x*self.width, y*self.height]))
        for x, y in LAYOUT["blue-balls"]:
            self.entities.append(BlueBall([x*self.width, y*self.height]))

        self.entities.extend([
            BlackBall(
                [self.width*LAYOUT["black-ball"][0],
                 self.height*LAYOUT["black-ball"][1]]
            ),
            GoldBall(
                [self.width*LAYOUT["gold-ball"][0],
                 self.height*LAYOUT["gold-ball"][1]]
            )
        ])

        self.generate_walls()

        self.particles = []

        self.shots_left = 30
        self.score = 0
        self.shot = False

    def load_sounds(self):
        if not SOUNDS:
            return
        self.sounds = {}
        pg.mixer.init()
        sounds = {
            "hit": "hit.wav",
            "score": "score.wav",
            "player_sink": "player_sink.wav",
            "reset": "reset.wav"
        }
        for sound in sounds:
            self.sounds[sound] = pg.mixer.Sound(f"./sounds/{sounds[sound]}")
    def play_sound(self, sound):
        if not SOUNDS:
            return
        self.sounds[sound].play()

    def generate_walls(self):
        """
            Make walls around the edges of the screen. Called during __init__
            and whenever resetting entities.
        """
        thickness = 10
        self.entities.extend([
            Wall([0, -thickness], [self.width, thickness]),
            Wall([-thickness, 0], [thickness, self.height]),
            Wall([0, self.height], [self.width, thickness]),
            Wall([self.width, 0], [thickness, self.height]),
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
        self.shots_left -= 1
        if self.shots_left <= 0:
            self.playing = False

    def add_entity(self, ent):
        """
            Add an entity to the game before the next update loop
        """
        self.ents_to_add.append(ent)

    def add_particle(self, particle):
        # The entities all update before the particles, so whenever add_particle
        # gets called we haven't started updating the particles and this is safe
        self.particles.append(particle)

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT or (
                    event.type == pg.KEYDOWN and event.key == pg.K_q
            ):
                self.quit = True
            for entity in self.entities:
                entity.handle_event(event, self)

    def update(self):
        dt = self.clock.get_time()/1000  # seconds since last frame

        ball_moving = False

        new_entities = []
        for entity in self.entities:
            entity.update(self, dt)
            if isinstance(entity, Ball) and (vector_size(entity.vel) != 0):
                ball_moving = True
            if not entity.to_remove:
                new_entities.append(entity)
        self.entities = new_entities
        self.entities.extend(self.ents_to_add)
        self.ents_to_add = []

        new_particles = []
        for particle in self.particles:
            particle.update(self, dt)
            if not particle.to_remove:
                new_particles.append(particle)
        self.particles = new_particles


        if self.shot and not ball_moving and not pg.mouse.get_pressed()[0]:
            self.end_shot()

    def draw(self):
        self.screen.fill(COLORS["background"])

        for x, y in LAYOUT["red-balls"]+LAYOUT["blue-balls"]+[LAYOUT["black-ball"],LAYOUT["gold-ball"],LAYOUT["player"]]:
            pg.draw.circle(self.screen, COLORS["markers"], [x*self.width, y*self.height], 2)

        for entity in self.entities:
            entity.draw(self.screen)

        self.draw_HUD()

        for particle in self.particles:
            particle.draw(self.screen)

        pg.display.flip()

    def draw_HUD(self):
        for hole in self.holes:
            pg.draw.circle(self.screen, COLORS["hole"], hole, HOLE_R)

        self.draw_centered_text(
                self.font, "Score: "+str(self.score), COLORS["foreground"],
                [LAYOUT["score"][0]*self.width, LAYOUT["score"][1]*self.height]
        )

        self.draw_centered_text(
                self.font, "Shots Left: "+str(self.shots_left), COLORS["foreground"],
                [LAYOUT["shot_count"][0]*self.width, LAYOUT["shot_count"][1]*self.height]
        )
        if DEBUG:
            self.screen.blit(
                    self.font.render(str(round(self.clock.get_fps())), True, pg.Color(128,128,128)),
                    [self.width/8, self.height-50]
            )

    def draw_centered_text(self,font, text, color, center_pos):
        size = font.size(text)
        self.screen.blit(font.render(text, True, color), sub_vectors(center_pos, scale_vector(size,0.5)))


    def game_over(self, fps):
        """
            Display the game over screen.
            Call this only *after* ending the current game loop by setting
            self.playing to False and allowing a loop to pass.
        """
        self.playing = True
        self.entities = []
        while self.playing and not self.quit:
            for event in pg.event.get():
                if event.type == pg.QUIT or (
                        event.type == pg.KEYDOWN and event.key == pg.K_q
                ):
                    self.quit = True
                elif event.type == pg.KEYDOWN:
                    self.playing = False
                elif event.type == pg.MOUSEBUTTONDOWN:
                    self.playing = False

            self.screen.fill(COLORS["background"])
            self.draw_centered_text(
                    self.font, "Final Score:", COLORS["foreground"],
                    [self.width/2, self.height/8-30]
            )
            self.draw_centered_text(
                    self.font, str(self.score), COLORS["highlight"],
                    [self.width/2, self.height/8]
            )
            self.draw_centered_text(
                    self.font, "Game Over", COLORS["foreground"],
                    [self.width/2, self.height/3]
            )
            self.draw_centered_text(
                    self.smallfont,
                    "Press any key to play again",
                    COLORS["foreground"],
                    [self.width/2, self.height/2]
            )

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
