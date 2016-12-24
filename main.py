import pygame
import sys
import math

pygame.init()

WIDTH = 800
HEIGHT = 600
TILESIZE = 40


class Ball(pygame.sprite.Sprite):
    IMG = pygame.image.load("ball.png")
    STEP = 300

    def __init__(self, x, y, *groups):
        super(Ball, self).__init__(*groups)

        self.image = Ball.IMG
        self.rect = self.image.get_rect(topleft=(x, y))

        self.dx = 1.6
        self.dy = 1.3

    def update(self, dt, tiles):
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
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
            self.dy *= -1


class Player(pygame.sprite.Sprite):
    IMG = pygame.image.load("player1.png")
    STEP = 100

    def __init__(self, x, y, *groups):
        super(Player, self).__init__(*groups)

        self.image = Player.IMG
        self.rect = self.image.get_rect(topleft=(x, y))

        self.spawnpoint = (x, y)

        self.left = False
        self.right = False
        self.up = False
        self.down = False

    def update(self, dt, tiles, balls):
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
            if self.rect.bottom > HEIGHT:
                self.rect.bottom = HEIGHT

        if pygame.sprite.spritecollide(self, balls, False):
            self.rect.topleft = (self.spawnpoint[0], self.spawnpoint[1])


class Tile(pygame.sprite.Sprite):
    IMG = pygame.image.load("tile.png")

    def __init__(self, x, y, *groups):
        super(Tile, self).__init__(*groups)

        self.image = Tile.IMG
        self.rect = self.image.get_rect(topleft=(x, y))


class Game:
    FPS = 30

    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.background = pygame.image.load("background.png")
        pygame.display.set_caption("Ball Game")

        self.tiles = pygame.sprite.Group()
        self.players = pygame.sprite.Group()
        self.player1 = None
        self.player2 = None
        self.balls = pygame.sprite.Group()

        self.clock = pygame.time.Clock()

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
                    self.player1 = Player(x, y)
                    self.players.add(self.player1)
                if char == "O":
                    self.balls.add(Ball(x, y))
                x += TILESIZE
            x = 0
            y += TILESIZE




    def play(self):
        self.setup()

        while True:
            dt = self.clock.tick(Game.FPS)
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

                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_w:
                        self.player1.up = False
                    if event.key == pygame.K_a:
                        self.player1.left = False
                    if event.key == pygame.K_s:
                        self.player1.down = False
                    if event.key == pygame.K_d:
                        self.player1.right = False



            self.tiles.update(dt)
            self.players.update(dt, self.tiles, self.balls)
            self.balls.update(dt, self.tiles)

            self.screen.blit(self.background, (0, 0))
            self.tiles.draw(self.screen)
            self.players.draw(self.screen)
            self.balls.draw(self.screen)

            pygame.display.flip()



if __name__ == "__main__":
    Game().play()


