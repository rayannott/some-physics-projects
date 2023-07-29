import pygame
import math
import random

pygame.init()
WIN_SIZE = 800

R = 350
MARG = 15
N = 120
DELTA = 2 * math.pi / N
WHITE = (255, 255, 255)
RED = (255, 0, 0)


def get_coord(k: int) -> tuple[float, float]:
    return ((R-MARG) * math.cos(k*DELTA) + WIN_SIZE/2, 
            (R-MARG) * math.sin(k*DELTA) + WIN_SIZE/2)


def draw_lines(ks: list[int], screen):
    for k1, k2 in zip(ks[:-1], ks[1:]):
        pygame.draw.line(screen, RED, get_coord(k1), get_coord(k2))


screen = pygame.display.set_mode((WIN_SIZE, WIN_SIZE))
exit = False

KS = [random.choice(range(N)) for _ in range(240)] # connect 240 random nails in a sequence

while not exit:
    screen.fill((0, 0, 0))
    pygame.draw.circle(screen, WHITE, (WIN_SIZE/2, WIN_SIZE/2), R, width=4)
    for k in range(N):
        pygame.draw.circle(screen, WHITE, get_coord(k), 3)
    draw_lines(KS, screen)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit = True

    pygame.display.update()
