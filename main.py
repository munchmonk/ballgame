import pygame
import sys
import math
import random
import time

WIDTH = 800
HEIGHT = 600
TILESIZE = 40
PLAY_HEIGHT = HEIGHT - TILESIZE
PLAYER1 = 0
PLAYER2 = 1
FPS = 60

PLAYER1_HOR_AXIS = 6
PLAYER1_VER_AXIS = 7
PLAYER2_HOR_AXIS = 2
PLAYER2_VER_AXIS = 3


class Star(pygame.sprite.Sprite):
    IMG = pygame.image.load("star.png")
    STEP = 200
    MINTIME = 1

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

        if self.rect.left <= TILESIZE:
            self.rect.left = TILESIZE
            self.dx *= -1
            change = True

        if self.rect.right >= WIDTH - TILESIZE:
            self.rect.right = WIDTH - TILESIZE
            self.dx *= -1
            change = True

        if self.rect.top <= TILESIZE:
            self.rect.top = TILESIZE
            self.dy *= -1
            change = True

        if self.rect.bottom >= PLAY_HEIGHT - TILESIZE:
            self.rect.bottom = PLAY_HEIGHT - TILESIZE
            self.dy *= -1
            change = True

        if change:
            self.last_change = time.time()
            self.next_change = Star.MINTIME + random.randint(1, 3)


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
        if self.rect.right >= WIDTH:
            self.rect.right = WIDTH
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
        if self.rect.bottom > PLAY_HEIGHT:
            self.rect.bottom = PLAY_HEIGHT
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


class Player(pygame.sprite.Sprite):
    IMG = {PLAYER1: pygame.image.load("player1.png"),
           PLAYER2: pygame.image.load("player2.png")}
    STEP = 160

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

        self.points = 0

    def update(self, dt, tiles, balls, stars):
        step = Player.STEP * (dt / 1000.0)
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
            if self.rect.right > WIDTH:
                self.rect.right = WIDTH

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
            if self.rect.bottom > PLAY_HEIGHT:
                self.rect.bottom = PLAY_HEIGHT

        if pygame.sprite.spritecollide(self, balls, False):
            self.rect.topleft = (self.spawnpoint[0], self.spawnpoint[1])
            self.points = 0

        if pygame.sprite.spritecollide(self, stars, True):
            self.points += 1
            if self.points >= 3:
                print("VICTORY!")


class Tile(pygame.sprite.Sprite):
    IMG = pygame.image.load("tile.png")

    def __init__(self, x, y, *groups):
        super(Tile, self).__init__(*groups)

        self.image = Tile.IMG
        self.rect = self.image.get_rect(topleft=(x, y))


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.background = pygame.image.load("background.png")
        pygame.display.set_caption("Ball Game")

        self.tiles = pygame.sprite.Group()
        self.players = pygame.sprite.Group()
        self.player1 = None
        self.player2 = None
        self.balls = pygame.sprite.Group()
        self.stars = pygame.sprite.Group()

        self.clock = pygame.time.Clock()

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
                    self.player1 = Player(x, y, PLAYER1)
                    self.players.add(self.player1)
                if char == "2":
                    self.player2 = Player(x, y, PLAYER2)
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
                x += TILESIZE
            x = 0
            y += TILESIZE

    def play(self):
        self.setup()

        while True:
            dt = self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_w:
                        self.player1.up = True
                    if event.key == pygame.K_a:
                        self.player1.left = True
                    if event.key == pygame.K_s:
                        self.player1.down = True
                    if event.key == pygame.K_d:
                        self.player1.right = True

                    if event.key == pygame.K_UP:
                        self.player2.up = True
                    if event.key == pygame.K_LEFT:
                        self.player2.left = True
                    if event.key == pygame.K_DOWN:
                        self.player2.down = True
                    if event.key == pygame.K_RIGHT:
                        self.player2.right = True

                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_w:
                        self.player1.up = False
                    if event.key == pygame.K_a:
                        self.player1.left = False
                    if event.key == pygame.K_s:
                        self.player1.down = False
                    if event.key == pygame.K_d:
                        self.player1.right = False

                    if event.key == pygame.K_UP:
                        self.player2.up = False
                    if event.key == pygame.K_LEFT:
                        self.player2.left = False
                    if event.key == pygame.K_DOWN:
                        self.player2.down = False
                    if event.key == pygame.K_RIGHT:
                        self.player2.right = False

                elif event.type == pygame.JOYAXISMOTION:
                    if self.stick.get_axis(PLAYER1_HOR_AXIS) < -0.9:
                        self.player1.left = True
                    else:
                        self.player1.left = False

                    if self.stick.get_axis(PLAYER1_HOR_AXIS) > 0.9:
                        self.player1.right = True
                    else:
                        self.player1.right = False

                    if self.stick.get_axis(PLAYER1_VER_AXIS) < -0.9:
                        self.player1.up = True
                    else:
                        self.player1.up = False

                    if self.stick.get_axis(PLAYER1_VER_AXIS) > 0.9:
                        self.player1.down = True
                    else:
                        self.player1.down = False

                if self.stick.get_axis(PLAYER2_HOR_AXIS) < -0.9:
                        self.player2.left = True
                else:
                    self.player2.left = False

                if self.stick.get_axis(PLAYER2_HOR_AXIS) > 0.9:
                    self.player2.right = True
                else:
                    self.player2.right = False

                if self.stick.get_axis(PLAYER2_VER_AXIS) < -0.9:
                    self.player2.up = True
                else:
                    self.player2.up = False

                if self.stick.get_axis(PLAYER2_VER_AXIS) > 0.9:
                    self.player2.down = True
                else:
                    self.player2.down = False

            if len(self.stars) == 0:
                self.stars.add(Star(random.randint(TILESIZE, WIDTH - TILESIZE),
                                    random.randint(TILESIZE, PLAY_HEIGHT - TILESIZE)))

            self.tiles.update(dt)
            self.players.update(dt, self.tiles, self.balls, self.stars)
            self.balls.update(dt, self.tiles, self.balls)
            self.stars.update(dt)

            self.screen.blit(self.background, (0, 0))
            self.tiles.draw(self.screen)
            self.balls.draw(self.screen)
            self.stars.draw(self.screen)
            self.players.draw(self.screen)

            pygame.display.flip()


if __name__ == "__main__":
    Game().play()


