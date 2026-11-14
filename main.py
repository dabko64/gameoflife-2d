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