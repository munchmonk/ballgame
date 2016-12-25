import pygame

pygame.init()

pygame.mixer.init()

a = pygame.mixer.Sound("background_music.wav")
b = pygame.mixer.Sound("star_pickup.wav")
c = pygame.mixer.Sound("death.wav")
while True:
    c.play()