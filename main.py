# next: use shield (golden)

# steal 1
# remove all (no steal)
# shield
# slow down


import pygame
import sys
import math
import random
import time

import const


class Powerup(pygame.sprite.Sprite):
    INTERVAL = 7
    SHIELD = 0
    TIME = 1
    TYPE = [SHIELD, TIME]
    IMG = {SHIELD: pygame.image.load("shield.png"),
           TIME: pygame.image.load("time.png")}

    def __init__(self, x, y, powerup_type, *groups):
        super(Powerup, self).__init__(*groups)

        self.image = Powerup.IMG[powerup_type]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.powerup_type = powerup_type


class Ball(pygame.sprite.Sprite):
    IMG = pygame.image.load("ball.png")
    STEP = 400

    def __init__(self, x, y, dx, dy, *groups):
        super(Ball, self).__init__(*groups)

        self.image = Ball.IMG
        self.rect = self.image.get_rect(topleft=(x, y))

        self.dx = dx
        self.dy = dy

    def update(self, dt, tiles, balls):
        # X axis first
        # movement
        step_x = self.dx * Ball.STEP * (dt / 1000.0)
        step_x = int(step_x) if step_x >= 1 else step_x
        self.rect.x += step_x

        # bounce off walls
        if pygame.sprite.spritecollide(self, tiles, False):
            while pygame.sprite.spritecollide(self, tiles, False):
                self.rect.x += (-math.copysign(1, self.dx))
            self.dx *= -1

        # bounce off screen edges
        if self.rect.left <= 0:
            self.rect.left = 0
            self.dx *= -1
        if self.rect.right >= const.WIDTH:
            self.rect.right = const.WIDTH
            self.dx *= -1

        # Y axis second
        # movement
        step_y = self.dy * Ball.STEP * (dt / 1000.0)
        step_y = int(step_y) if step_y >= 1 else step_y
        self.rect.y += step_y

        # bounce off walls
        if pygame.sprite.spritecollide(self, tiles, False):
            while pygame.sprite.spritecollide(self, tiles, False):
                self.rect.y += (-math.copysign(1, self.dy))
            self.dy *= -1

        # bounce off screen edges
        if self.rect.top < 0:
            self.rect.top = 0
            self.dy *= -1
        if self.rect.bottom > const.PLAY_HEIGHT:
            self.rect.bottom = const.PLAY_HEIGHT
            self.dy *= -1

        # collision with other balls
        for ball in balls:
            if ball == self:
                continue
            if ball.rect.colliderect(self.rect):
                while ball.rect.colliderect(self.rect):
                    self.rect.x += (-math.copysign(1, self.dx))
                    self.rect.y += (-math.copysign(1, self.dy))
                self.dx *= -1
                self.dy *= -1
                break


class Tile(pygame.sprite.Sprite):
    IMG = pygame.image.load("tile.png")

    def __init__(self, x, y, *groups):
        super(Tile, self).__init__(*groups)

        self.image = Tile.IMG
        self.rect = self.image.get_rect(topleft=(x, y))


class Game:
    pygame.init()
    pygame.mixer.init()

    def __init__(self):
        self.screen = pygame.display.set_mode((const.WIDTH, const.HEIGHT))
        self.background = pygame.image.load("background.png")
        pygame.display.set_caption("Ball Game")

        # Sprite groups
        self.tiles = pygame.sprite.Group()
        self.players = pygame.sprite.Group()
        self.player1 = None
        self.player2 = None
        self.balls = pygame.sprite.Group()
        self.stars = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()

        # Time
        self.clock = pygame.time.Clock()
        self.paused = False
        self.pause_time = 0
        self.lastpowerup = 0

        # Music
        pygame.mixer.music.load("background_music.wav")
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(-1, 0.0)

        # Joystick
        pygame.joystick.init()
        self.stick = pygame.joystick.Joystick(0)
        self.stick.init()
        self.stick_buttons = self.stick.get_numbuttons()
        self.stick_axes = self.stick.get_numaxes()

    def setup(self):
        level_file = "level1.txt"
        level = open(level_file, "r")
        lines_list = []
        for line in level:
            lines_list.append(line.rstrip("\r\n"))
        level.close()

        x = 0
        y = 0
        for line in lines_list:
            for char in line:
                if char == " ":
                    continue
                if char == "#":
                    self.tiles.add(Tile(x, y))
                if char == "1":
                    self.player1 = Player(x, y, const.PLAYER1)
                    self.players.add(self.player1)
                if char == "2":
                    self.player2 = Player(x, y, const.PLAYER2)
                    self.players.add(self.player2)
                if char == "h":
                    self.balls.add(Ball(x, y, -1, 0))
                if char == "H":
                    self.balls.add(Ball(x, y, 1, 0))
                if char == "v":
                    self.balls.add(Ball(x, y, 0, -1))
                if char == "V":
                    self.balls.add(Ball(x, y, 0, 1))
                if char == "r":
                    dx = random.random()
                    dy = 1 - dx
                    self.balls.add(Ball(x, y, dx, dy))
                x += const.TILESIZE
            x = 0
            y += const.TILESIZE

    def showwinner(self, player):
        Player.VICTORY_SOUND.play()
        sansbold = pygame.font.Font("freesansbold.ttf", 100)
        winner_string = "Player "
        if player.side == const.PLAYER1:
            winner_string += "1 wins!!!"
        if player.side == const.PLAYER2:
            winner_string += "2 wins!!!"

        final = sansbold.render(winner_string, True, (255, 0, 0))
        self.screen.blit(final, final.get_rect(center=(const.WIDTH // 2, const.HEIGHT // 2)))

    def showinfotext(self):
        sansbold = pygame.font.Font("freesansbold.ttf", 28)

        # Player 1
        player1_string = "SCORE: " + str(self.player1.score) + "   P/UP: "
        if self.player1.powerup is None:
            player1_string += "N/A"
        if self.player1.powerup == Powerup.TYPE[Powerup.SHIELD]:
            player1_string += "SHIELD"
        if self.player1.powerup == Powerup.TYPE[Powerup.TIME]:
            player1_string += "TIME"
        player1_score = sansbold.render(player1_string, True, (0, 0, 0))
        self.screen.blit(player1_score, player1_score.get_rect(topleft=(10, const.HEIGHT - const.TILESIZE + 4)))

        # Player 2
        player2_string = "SCORE: " + str(self.player2.score) + "   P/UP: "
        if self.player2.powerup is None:
            player2_string += "N/A"
        if self.player2.powerup == Powerup.TYPE[Powerup.SHIELD]:
            player2_string += "SHIELD"
        if self.player2.powerup == Powerup.TYPE[Powerup.TIME]:
            player2_string += "TIME"
        player2_score = sansbold.render(player2_string, True, (0, 0, 0))
        self.screen.blit(player2_score, player2_score.get_rect(topleft=(const.WIDTH - 360, const.HEIGHT - const.TILESIZE + 4)))

    def checkvictory(self):
        if not (self.player1.winner or self.player2.winner):
            return

        winner = self.player1 if self.player1.winner else self.player2
        self.showwinner(winner)

        for player in self.players:
            player.powerup = None
            player.score = 0
            player.winner = False
            player.rect.topleft = (player.spawnpoint[0], player.spawnpoint[1])
            player.invulnerable = False
            player.image = Player.IMG[player.side]
            player.current_step = Player.STEP
            player.slow_start = 0

        self.paused = True
        self.pause_time = time.time()

    def isoccupied(self, x, y):
        # returns True if a point (x, y) belongs to a tile
        for tile in self.tiles:
            x_axis = range(tile.rect.left, tile.rect.right)
            y_axis = range(tile.rect.top, tile.rect.bottom)
            if x in x_axis and y in y_axis:
                return True
        return False

    def spawnpowerup(self):
        x = -1
        y = -1
        rand_type = random.choice(Powerup.TYPE)
        right = Powerup.IMG[rand_type].get_rect(topleft=(x, y)).right
        bottom = Powerup.IMG[rand_type].get_rect(topleft=(x, y)).bottom
        while (x < 0 or y < 0 or
               self.isoccupied(x, y) or self.isoccupied(right, y) or
               self.isoccupied(x, bottom) or self.isoccupied(right, bottom) or
               right >= const.WIDTH or bottom >= const.PLAY_HEIGHT):
            x = random.randint(0, const.WIDTH)
            y = random.randint(0, const.PLAY_HEIGHT)
            right = Powerup.IMG[rand_type].get_rect(topleft=(x, y)).right
            bottom = Powerup.IMG[rand_type].get_rect(topleft=(x, y)).bottom

        self.powerups.add(Powerup(x, y, rand_type))
        self.lastpowerup = time.time() + random.randint(1, 8)

    def play(self):
        self.setup()

        while True:
            dt = self.clock.tick(const.FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                # Check input
                elif event.type == pygame.JOYAXISMOTION and not self.paused:
                    if self.stick.get_axis(const.PLAYER1_HOR_AXIS) < -0.9:
                        self.player1.left = True
                    else:
                        self.player1.left = False

                    if self.stick.get_axis(const.PLAYER1_HOR_AXIS) > 0.9:
                        self.player1.right = True
                    else:
                        self.player1.right = False

                    if self.stick.get_axis(const.PLAYER1_VER_AXIS) < -0.9:
                        self.player1.up = True
                    else:
                        self.player1.up = False

                    if self.stick.get_axis(const.PLAYER1_VER_AXIS) > 0.9:
                        self.player1.down = True
                    else:
                        self.player1.down = False

                    if self.stick.get_axis(const.PLAYER2_HOR_AXIS) < -0.9:
                        self.player2.left = True
                    else:
                        self.player2.left = False

                    if self.stick.get_axis(const.PLAYER2_HOR_AXIS) > 0.9:
                        self.player2.right = True
                    else:
                        self.player2.right = False

                    if self.stick.get_axis(const.PLAYER2_VER_AXIS) < -0.9:
                        self.player2.up = True
                    else:
                        self.player2.up = False

                    if self.stick.get_axis(const.PLAYER2_VER_AXIS) > 0.9:
                        self.player2.down = True
                    else:
                        self.player2.down = False

                elif event.type == pygame.JOYBUTTONDOWN and not self.paused:
                    if self.stick.get_button(const.PLAYER1_X) and self.player1.powerup is not None:
                        self.player1.use_powerup = True
                    if self.stick.get_button(const.PLAYER2_X) and self.player2.powerup is not None:
                        self.player2.use_powerup = True

            # Spawn stars
            if len(self.stars) == 0 and not self.paused:
                self.stars.add(Star(random.randint(const.TILESIZE, const.WIDTH - const.TILESIZE),
                                    random.randint(const.TILESIZE, const.PLAY_HEIGHT - const.TILESIZE)))
            # Spawn powerups
            if len(self.powerups) < 3 and time.time() - self.lastpowerup >= Powerup.INTERVAL and not self.paused:
                self.spawnpowerup()

            # Keep game going
            if not self.paused:
                self.tiles.update(dt)
                self.players.update(dt, self.tiles, self.balls, self.stars, self.powerups, self.players)
                self.balls.update(dt, self.tiles, self.balls)
                self.stars.update(dt)

                self.screen.blit(self.background, (0, 0))
                self.tiles.draw(self.screen)
                self.powerups.draw(self.screen)
                self.balls.draw(self.screen)
                self.stars.draw(self.screen)
                self.players.draw(self.screen)
                self.showinfotext()

                self.checkvictory()

            # Unpause
            if self.paused and time.time() - self.pause_time > const.PAUSETIME:
                self.paused = False

            pygame.display.flip()


class Star(pygame.sprite.Sprite):
    IMG = pygame.image.load("star.png")
    STEP = 200
    MINTIME = 1
    PICKUP_SOUND = pygame.mixer.Sound("star_pickup.wav")
    PICKUP_SOUND.set_volume(0.9)

    def __init__(self, x, y, *groups):
        super(Star, self).__init__(*groups)

        self.image = Star.IMG
        self.rect = self.image.get_rect(topleft=(x, y))

        self.dx = random.random()
        self.dy = 1 - self.dx

        self.last_change = 0
        self.next_change = Star.MINTIME + random.randint(1, 3)

    def update(self, dt):
        step_x = self.dx * Star.STEP * (dt / 1000.0)
        step_y = self.dy * Star.STEP * (dt / 1000.0)
        step_x = int(step_x) if step_x >= 1 else step_x
        step_y = int(step_y) if step_y >= 1 else step_y
        self.rect.x += step_x
        self.rect.y += step_y

        change = False

        if time.time() - self.last_change >= self.next_change:
            self.dx = random.random()
            self.dy = 1 - self.dx
            change = True

        if self.rect.left <= const.TILESIZE:
            self.rect.left = const.TILESIZE
            self.dx *= -1
            change = True

        if self.rect.right >= const.WIDTH - const.TILESIZE:
            self.rect.right = const.WIDTH - const.TILESIZE
            self.dx *= -1
            change = True

        if self.rect.top <= const.TILESIZE:
            self.rect.top = const.TILESIZE
            self.dy *= -1
            change = True

        if self.rect.bottom >= const.PLAY_HEIGHT - const.TILESIZE:
            self.rect.bottom = const.PLAY_HEIGHT - const.TILESIZE
            self.dy *= -1
            change = True

        if change:
            self.last_change = time.time()
            self.next_change = Star.MINTIME + random.randint(1, 3)


class Player(pygame.sprite.Sprite):
    IMG = {const.PLAYER1: pygame.image.load("player1.png"),
           const.PLAYER2: pygame.image.load("player2.png"),
           const.INVIS:   pygame.image.load("invis_player.png"),
           const.GOLDEN:  pygame.image.load("golden_player.png")}
    STEP = 220
    INV_TIME = 2.2
    BLINK_INTERVAL = 0.2
    SLOWED_TIME = 5
    DEATH_SOUND = pygame.mixer.Sound("death.wav")
    DEATH_SOUND.set_volume(0.2)
    VICTORY_SOUND = pygame.mixer.Sound("victory.wav")
    VICTORY_SOUND.set_volume(0.8)

    def __init__(self, x, y, side, *groups):
        super(Player, self).__init__(*groups)

        self.image = Player.IMG[side]
        self.rect = self.image.get_rect(topleft=(x, y))

        self.spawnpoint = (x, y)
        self.side = side

        self.left = False
        self.right = False
        self.up = False
        self.down = False

        self.use_powerup = False
        self.current_step = Player.STEP
        self.slow_start = 0

        self.score = 0
        self.winner = False
        self.invulnerable = False
        self.invulnerable_time = 0
        self.invulnerable_blink = 0
        self.powerup = None

    def update(self, dt, tiles, balls, stars, powerups, players):
        # Movement
        step = self.current_step * (dt / 1000.0)
        step = int(step) if step >= 1 else step

        if self.left:
            self.rect.x -= step
            while pygame.sprite.spritecollide(self, tiles, False):
                self.rect.x += 1
            if self.rect.left < 0:
                self.rect.left = 0

        if self.right:
            self.rect.x += step
            while pygame.sprite.spritecollide(self, tiles, False):
                self.rect.x -= 1
            if self.rect.right > const.WIDTH:
                self.rect.right = const.WIDTH

        if self.up:
            self.rect.y -= step
            while pygame.sprite.spritecollide(self, tiles, False):
                self.rect.y += 1
            if self.rect.top < 0:
                self.rect.top = 0

        if self.down:
            self.rect.y += step
            while pygame.sprite.spritecollide(self, tiles, False):
                self.rect.y -= 1
            if self.rect.bottom > const.PLAY_HEIGHT:
                self.rect.bottom = const.PLAY_HEIGHT

        # Using powerups
        if self.use_powerup:
            print("BAAAAAAANG!!!" + str(self.powerup))
            if self.powerup == Powerup.TYPE[Powerup.TIME]:
                for player in players:
                    if player.side != self.side:
                        player.current_step /= 2
                        player.slow_start = time.time()

            if self.powerup == Powerup.TYPE[Powerup.SHIELD]:
                pass  # -------------------------------------------------------------------------------------------

            self.use_powerup = False
            self.powerup = None

        # Slowed
        if self.current_step < Player.STEP and time.time() - self.slow_start >= Player.SLOWED_TIME:
            self.current_step = Player.STEP

        # Invulnerability time over
        if self.invulnerable and time.time() - self.invulnerable_time >= Player.INV_TIME:
            self.invulnerable = False
            self.image = Player.IMG[self.side]

        # Invulnerability blink animation
        if self.invulnerable and time.time() - self.invulnerable_blink >= Player.BLINK_INTERVAL:
            self.image = Player.IMG[self.side] if self.image == Player.IMG[const.INVIS] else Player.IMG[const.INVIS]
            self.invulnerable_blink = time.time()

        # Collision with balls
        if pygame.sprite.spritecollide(self, balls, False) and not self.invulnerable:
            Player.DEATH_SOUND.play()
            self.rect.topleft = (self.spawnpoint[0], self.spawnpoint[1])
            self.score = 0
            self.powerup = None
            self.invulnerable = True
            self.invulnerable_time = time.time()
            self.invulnerable_blink = 0
            self.current_step = Player.STEP

        # Collision with stars
        if pygame.sprite.spritecollide(self, stars, True):
            Star.PICKUP_SOUND.play()
            self.score += 1
            if self.score >= 3:
                self.winner = True

        # Collision with powerups
        for powerup in powerups:
            if self.rect.colliderect(powerup.rect):
                self.powerup = powerup.powerup_type
                powerups.remove(powerup)
                break


if __name__ == "__main__":
    Game().play()