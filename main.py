import pygame
import numpy as np


#board and application configuration

#cellular automaton grid settings
N = 200                     #number of rows and columns
CELL = 4
BOARD_PX = N * CELL

#window dimensions and element positioning
WIDTH, HEIGHT = 1200, 850   #application window dimensions
BOARD_X, BOARD_Y = 16, 16   #top-left corner position of the board
PANEL_X = 838               #horizontal position of the control panel
PANEL_W = 346               #width of the control panel

#interface colors (RGB)
BG = (14, 21, 33)           #application background color
DEAD = (25, 36, 51)         #dead cell color
ALIVE = (57, 222, 172)      #live cell color
TEXT = (233, 242, 250)      #primary text color
MUTED = (148, 165, 183)     #secondary text color
BUTTON = (40, 55, 75)       #default button color
HOVER = (54, 76, 100)       #button color when hovered
ACTIVE = (33, 113, 96)      #active button color



#initialize window and fonts

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("GAME OF LIFE")
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 17)
small_font = pygame.font.SysFont("arial", 15)
heading_font = pygame.font.SysFont("arial", 19, bold=True)
title_font = pygame.font.SysFont("arial", 28, bold=True)



#draw the cell grid once and reuse it in every frame
grid_overlay = pygame.Surface((BOARD_PX, BOARD_PX), pygame.SRCALPHA)
for pos in range(0, BOARD_PX + 1, CELL):
    pygame.draw.line(grid_overlay, (255, 255, 255, 13), (pos, 0), (pos, BOARD_PX))
    pygame.draw.line(grid_overlay, (255, 255, 255, 13), (0, pos), (BOARD_PX, pos))



#available initial patterns
PATTERN_NAMES = ["glider", "block", "r-pentomino", "pulsar", "gosper gun", "random"]




def pattern_array(name):
    #0 = dead 1 = alive
    if name == "glider":
        return np.array([[0, 1, 0],
                         [0, 0, 1],
                         [1, 1, 1]], dtype=np.uint8)
    if name == "block":
        return np.array([[1, 1],
                         [1, 1]], dtype=np.uint8)
    if name == "r-pentomino":
        return np.array([[0, 1, 1],
                         [1, 1, 0],
                         [0, 1, 0]], dtype=np.uint8)
    if name == "pulsar":
        p = np.zeros((13, 13), dtype=np.uint8)
        for row in [0, 5, 7, 12]:
            p[row, [2, 3, 4, 8, 9, 10]] = 1
        for row in [2, 3, 4, 8, 9, 10]:
            p[row, [0, 5, 7, 12]] = 1
        return p                          #48 live cells period of 3
    if name == "gosper gun":
        p = np.zeros((9, 36), dtype=np.uint8)
        coords = [
            (0, 24),
            (1, 22), (1, 24),
            (2, 12), (2, 13), (2, 20), (2, 21), (2, 34), (2, 35),
            (3, 11), (3, 15), (3, 20), (3, 21), (3, 34), (3, 35),
            (4, 0), (4, 1), (4, 10), (4, 16), (4, 20), (4, 21),
            (5, 0), (5, 1), (5, 10), (5, 14), (5, 16), (5, 17), (5, 22), (5, 24),
            (6, 10), (6, 16), (6, 24),
            (7, 11), (7, 15),
            (8, 12), (8, 13),
        ]
        for y, x in coords:
            p[y, x] = 1
        return p                          #additional large pattern (36 cells)
    raise ValueError("unknown pattern: " + name)



def next_generation(state, rule, boundary):

    padding = "wrap" if boundary == "periodic" else "reflect"
    padded = np.pad(state, 1, mode=padding)

    #count all eight neighbors without including the current cell
    neighbours = np.zeros_like(state, dtype=np.uint8)

    for dy in range(3):
        for dx in range(3):
            if dy == 1 and dx == 1:
                continue
            neighbours += padded[dy:dy + N, dx:dx + N]

    #conway: B3/S23; custom rule: B34/S23
    birth = (neighbours == 3)

    if rule == "custom":
        birth = birth | (neighbours == 4)

    born = (state == 0) & birth
    survive = (state == 1) & ((neighbours == 2) | (neighbours == 3))

    return (born | survive).astype(np.uint8)


#current simulation state
board = np.zeros((N, N), dtype=np.uint8)
initial_board = board.copy()
pattern_name = "glider"
rule = "conway"
boundary = "periodic"
generation = 0
running = False
speed = 8
history = [0]
comparison = None
last_step_time = pygame.time.get_ticks()
buttons = []
painting = None

