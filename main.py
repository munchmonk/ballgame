import pygame
import sys

pygame.init()

WIDTH = 800
HEIGHT = 600


class Ball(pygame.sprite.Sprite):
    IMG = pygame.image.load("ball.png")
    STEP = 300

    def __init__(self, x, y, *groups):
        super(Ball, self).__init__(*groups)

        self.image = Ball.IMG
        self.rect = self.image.get_rect(topleft=(x, y))

        self.dx = 1
        self.dy = 0.5

    def update(self, dt, tiles):
        # move
        step_x = self.dx * Ball.STEP * (dt / 1000.0)
        step_x = int(step_x) if step_x >= 1 else step_x
        step_y = self.dy * Ball.STEP * (dt / 1000.0)
        step_y = int(step_y) if step_y >= 1 else step_y
        self.rect.x += step_x
        self.rect.y += step_y

        # bounce off screen edges
        if self.rect.left <= 0:
            self.rect.left = 0
            self.dx *= -1
        if self.rect.right >= WIDTH:
            self.rect.right = WIDTH
            self.dx *= -1
        if self.rect.top < 0:
            self.rect.top = 0
            self.dy *= -1
        if self.rect.bottom >= HEIGHT:
            self.rect.bottom = HEIGHT
            self.dy *= -1

        # bounce off walls
        hit_walls = pygame.sprite.spritecollide(self, tiles, False)
        if len(hit_walls) > 0:
            new_dx = self.dx
            new_dy = self.dy





            # NON FUNGE, devo trovare una maniera furba per far rimbalzare la palla
            # -------------------
            # -------------------
            # -------------------
            # -------------------



            for wall in hit_walls:
                if self.dx > 0 and wall.rect.left <= self.rect.right:
                    new_dx *= -1
                    print("1")
                if self.dx < 0 and wall.rect.right >= self.rect.left:
                    new_dx *= -1
                    print("2")
                if self.dy > 0 and wall.rect.top <= self.rect.bottom:
                    new_dy *= -1
                    print("3")
                if self.dy < 0 and wall.rect.bottom >= self.rect.top:
                    new_dy *= -1
                    print("4")





            # -------------------
            # -------------------
            # -------------------
            # -------------------
            # -------------------
            # -------------------









            # reassign dx and dy
            # for wall in hit_walls:
            #     if self.dx > 0 and (wall.rect.collidepoint(self.rect.topright) or
            #         wall.rect.collidepoint(self.rect.midright) or
            #         wall.rect.collidepoint(self.rect.bottomright)):
            #         new_dx *= -1
            #     if self.dx < 0 and (wall.rect.collidepoint(self.rect.topleft) or
            #         wall.rect.collidepoint(self.rect.midleft) or
            #         wall.rect.collidepoint(self.rect.bottomleft)):
            #         new_dx *= -1
            #     if self.dy > 0 and (wall.rect.collidepoint(self.rect.bottomleft) or
            #         wall.rect.collidepoint(self.rect.midbottom) or
            #         wall.rect.collidepoint(self.rect.bottomright)):
            #         new_dy *= -1
            #     if self.dy < 0 and (wall.rect.collidepoint(self.rect.topleft) or
            #         wall.rect.collidepoint(self.rect.midtop) or
            #         wall.rect.collidepoint(self.rect.topright)):
            #         new_dy *= -1

            # move back
            while pygame.sprite.spritecollide(self, tiles, False):
                if self.dx > 0:
                    self.rect.x -= 1
                elif self.dx < 0:
                    self.rect.x += 1
                if self.dy > 0:
                    self.rect.y -= 1
                elif self.dy < 0:
                    self.rect.y += 1

            self.dx = new_dx
            self.dy = new_dy


class Player(pygame.sprite.Sprite):
    IMG = pygame.image.load("player1.png")
    STEP = 100

    def __init__(self, x, y, *groups):
        super(Player, self).__init__(*groups)

        self.image = Player.IMG
        self.rect = self.image.get_rect(topleft=(x, y))

        self.up = False
        self.left = False
        self.down = False
        self.right = False

    def update(self, dt):
        step = Player.STEP * (dt / 1000.0)
        step = int(step) if step >= 1 else step
        if self.up:
            self.rect.y -= step
        if self.left:
            self.rect.x -= step
        if self.down:
            self.rect.y += step
        if self.right:
            self.rect.x += step



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
        self.tiles.add(Tile(20, 20))
        self.tiles.add(Tile(200, 20))
        self.tiles.add(Tile(450, 480))
        self.tiles.add(Tile(300, 260))
        self.tiles.add(Tile(160, 340))
        self.tiles.add(Tile(600, 380))
        self.players = pygame.sprite.Group()
        self.player1 = Player(300, 30)
        self.players.add(self.player1)
        self.balls = pygame.sprite.Group()
        self.balls.add(Ball(100, 400))

        self.clock = pygame.time.Clock()

    def play(self):
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
            self.players.update(dt)
            self.balls.update(dt, self.tiles)

            self.screen.blit(self.background, (0, 0))
            self.tiles.draw(self.screen)
            self.players.draw(self.screen)
            self.balls.draw(self.screen)

            pygame.display.flip()



if __name__ == "__main__":
    Game().play()


