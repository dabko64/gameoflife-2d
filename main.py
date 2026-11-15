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




#load the selected pattern and reset the simulation
def load_pattern(name, near_edge=False):
    global board, initial_board, pattern_name, generation, running, history, comparison

    pattern_name = name
    board = np.zeros((N, N), dtype=np.uint8)

    if name == "random":
        board = (np.random.random((N, N)) < 0.18).astype(np.uint8)
    else:
        pattern = pattern_array(name)
        h, w = pattern.shape

        #place the pattern in the center or near the bottom right edge
        y = N - h - 1 if near_edge else (N - h) // 2
        x = N - w - 1 if near_edge else (N - w) // 2

        board[y:y+h, x:x+w] = pattern

    initial_board = board.copy()
    generation = 0
    running = False
    history = [int(board.sum())]
    comparison = None




#calculate the next generation and update population history
def step():
    global board, generation, history

    board = next_generation(board, rule, boundary)
    generation += 1

    history.append(int(board.sum()))

    if len(history) > 200:
        history.pop(0)




#compare both rules after thirty generations
def compare_30():
    global comparison

    a = initial_board.copy()
    b = initial_board.copy()

    for _ in range(30):
        a = next_generation(a, "conway", boundary)
        b = next_generation(b, "custom", boundary)

    comparison = (
        int(a.sum()),
        int(b.sum()),
        int(np.count_nonzero(a != b))
    )

    print("comparison after 30 generations")
    print("conway B3/S23:", comparison[0], "live cells")
    print("custom B34/S23:", comparison[1], "live cells")
    print("different cells:", comparison[2])




#handle user actions and simulation controls
def action(name):
    global running, board, initial_board, pattern_name, generation
    global history, speed, rule, boundary, comparison, last_step_time

    #select the initial pattern
    if name.startswith("pattern:"):
        load_pattern(name.split(":", 1)[1])

    #move the selected pattern near the board edge
    elif name == "edge":
        if pattern_name in PATTERN_NAMES and pattern_name != "random":
            load_pattern(pattern_name, near_edge=True)

    #select boundary conditions
    elif name == "periodic":
        boundary = "periodic"
        comparison = None

    elif name == "reflect":
        boundary = "reflective"
        comparison = None

    #select transition rules
    elif name == "conway":
        rule = "conway"
        comparison = None

    elif name == "custom":
        rule = "custom"
        comparison = None

    #start or pause the simulation
    elif name == "toggle":
        running = not running
        last_step_time = pygame.time.get_ticks()

    #execute a single generation
    elif name == "step":
        running = False
        step()

    #restore the initial board
    elif name == "reset":
        board = initial_board.copy()
        generation = 0
        running = False
        history = [int(board.sum())]
        comparison = None

    #clear all cells
    elif name == "clear":
        board = np.zeros((N, N), dtype=np.uint8)
        initial_board = board.copy()
        pattern_name = "empty"
        generation = 0
        running = False
        history = [0]
        comparison = None

    #adjust simulation speed
    elif name == "faster":
        speed = min(30, speed + 2)

    elif name == "slower":
        speed = max(1, speed - 2)

    #compare the transition rules
    elif name == "compare":
        compare_30()





#render text on the screen
def draw_text(message, x, y, color=TEXT, text_font=None):
    text_font = text_font or font
    screen.blit(text_font.render(str(message), True, color), (x, y))


#draw an interactive button
def draw_button(label, x, y, w, h, command, selected=False):
    rect = pygame.Rect(x, y, w, h)
    hovered = rect.collidepoint(pygame.mouse.get_pos())

    pygame.draw.rect( screen, ACTIVE if selected else (HOVER if hovered else BUTTON), rect, border_radius=8)

    if selected:
        pygame.draw.rect(screen, ALIVE, rect, width=1, border_radius=8)

    label_surface = small_font.render(label, True, TEXT)
    screen.blit(label_surface, label_surface.get_rect(center=rect.center))

    buttons.append((rect, command))


#draw the live cell population chart
def draw_chart(values, rect):
    pygame.draw.rect(screen, (25, 36, 51), rect, border_radius=6)

    pygame.draw.line(screen,(58, 71, 88),(rect.left, rect.bottom - 2),(rect.right, rect.bottom - 2) )

    if len(values) < 2:
        return

    values = values[-100:]
    lo, hi = min(values), max(values)
    scale = max(hi - lo, 1)
    points = []

    for i, value in enumerate(values):
        x = rect.left + 5 + i * (rect.width - 10) / (len(values) - 1)
        y = rect.bottom - 5 - (value - lo) * (rect.height - 10) / scale

        points.append((int(x), int(y)))

    pygame.draw.lines(screen, ALIVE, False, points, 2)


#render the board and application interface
def draw():
    buttons.clear()
    screen.fill(BG)

    #convert the board into a pygame surface
    pixels = np.empty((N, N, 3), dtype=np.uint8)
    pixels[:] = DEAD
    pixels[board.T.astype(bool)] = ALIVE

    tiny = pygame.surfarray.make_surface(pixels)
    big = pygame.transform.scale(tiny, (BOARD_PX, BOARD_PX))

    screen.blit(big, (BOARD_X, BOARD_Y))
    screen.blit(grid_overlay, (BOARD_X, BOARD_Y))

    pygame.draw.rect(screen,(91, 114, 135),pygame.Rect(BOARD_X, BOARD_Y, BOARD_PX, BOARD_PX),1 )

    #display keyboard shortcuts
    draw_text("mouse: draw cells  |  SPACE: start/pause  |  N: step  |  R: reset  |  E: edge", BOARD_X, 822, MUTED, small_font)

    x = PANEL_X
    cw = (PANEL_W - 9) // 2

    #application title
    draw_text("GAME OF LIFE", x, 17, TEXT, title_font)
    draw_text("200 x 200  |  moore neighborhood", x, 54, MUTED, small_font)

    #initial pattern selection
    draw_text("INITIAL PATTERNS", x, 87, TEXT, heading_font)

    for i, name in enumerate(PATTERN_NAMES):
        bx = x + (i % 2) * (cw + 9)
        by = 116 + (i // 2) * 41

        draw_button(name.title(), bx, by, cw, 34,"pattern:" + name,pattern_name == name)

    #boundary condition selection
    draw_text("BOUNDARY CONDITIONS", x, 249, TEXT, heading_font)
    draw_button("periodic", x, 275, cw, 34,"periodic", boundary == "periodic")
    draw_button( "reflective", x + cw + 9, 275, cw, 34, "reflect", boundary == "reflective")

    #transition rule selection
    draw_text("TRANSITION RULES", x, 320, TEXT, heading_font)
    draw_button("conway B3/S23", x, 347, cw, 34,"conway", rule == "conway")
    draw_button("custom B34/S23", x + cw + 9, 347, cw, 34,"custom", rule == "custom")

    #simulation controls
    draw_text("CONTROLS", x, 394, TEXT, heading_font)
    draw_button("pause" if running else "start", x, 421, cw, 34, "toggle")
    draw_button("next step (N)", x + cw + 9, 421, cw, 34, "step")
    draw_button("reset (R)", x, 463, cw, 34, "reset")
    draw_button("clear", x + cw + 9, 463, cw, 34, "clear")

    draw_button("move pattern near edge (E)", x, 505, PANEL_W, 34, "edge")

    #simulation speed controls
    draw_text("SIMULATION SPEED", x, 551, TEXT, heading_font)
    draw_button("slower -", x, 578, cw, 32, "slower")
    draw_button("faster +", x + cw + 9, 578, cw, 32, "faster")
    draw_text(f"{speed} generations/s", x, 613, MUTED, small_font)

    #display simulation statistics
    draw_text("STATISTICS", x, 639, TEXT, heading_font)
    draw_text(f"generation: {generation}  |  alive: {int(board.sum())}", x, 664, TEXT, small_font)
    draw_text("minimum 30 generations: " + ("OK" if generation >= 30 else "not yet"),x, 684,ALIVE if generation >= 30 else MUTED,small_font)
    draw_chart(history, pygame.Rect(x, 708, PANEL_W, 42))

    #display rule comparison results
    draw_button( "COMPARE RULES AFTER 30 STEPS", x, 758, PANEL_W, 34, "compare")

    if comparison is None:
        draw_text("comparison from the same initial state", x, 801, MUTED, small_font)
    else:
        draw_text( f"conway: {comparison[0]}  |  custom: {comparison[1]}", x, 800, TEXT, small_font)

        draw_text(f"different cells after 30 steps: {comparison[2]}", x, 820, MUTED, small_font )

    pygame.display.flip()





#render text on the screen
def draw_text(message, x, y, color=TEXT, text_font=None):
    text_font = text_font or font
    screen.blit(text_font.render(str(message), True, color), (x, y))


#draw an interactive button
def draw_button(label, x, y, w, h, command, selected=False):
    rect = pygame.Rect(x, y, w, h)
    hovered = rect.collidepoint(pygame.mouse.get_pos())

    pygame.draw.rect(screen,ACTIVE if selected else (HOVER if hovered else BUTTON),rect,border_radius=8)

    if selected:
        pygame.draw.rect(screen, ALIVE, rect, width=1, border_radius=8)

    label_surface = small_font.render(label, True, TEXT)
    screen.blit(label_surface, label_surface.get_rect(center=rect.center))

    buttons.append((rect, command))


#draw the live cell population chart
def draw_chart(values, rect):
    pygame.draw.rect(screen, (25, 36, 51), rect, border_radius=6)

    pygame.draw.line(screen,(58, 71, 88),(rect.left, rect.bottom - 2),(rect.right, rect.bottom - 2))

    if len(values) < 2:
        return

    values = values[-100:]
    lo, hi = min(values), max(values)
    scale = max(hi - lo, 1)
    points = []

    for i, value in enumerate(values):
        x = rect.left + 5 + i * (rect.width - 10) / (len(values) - 1)
        y = rect.bottom - 5 - (value - lo) * (rect.height - 10) / scale

        points.append((int(x), int(y)))

    pygame.draw.lines(screen, ALIVE, False, points, 2)


#render the board and application interface
def draw():
    buttons.clear()
    screen.fill(BG)

    #convert the board into a pygame surface
    pixels = np.empty((N, N, 3), dtype=np.uint8)
    pixels[:] = DEAD
    pixels[board.T.astype(bool)] = ALIVE

    tiny = pygame.surfarray.make_surface(pixels)
    big = pygame.transform.scale(tiny, (BOARD_PX, BOARD_PX))

    screen.blit(big, (BOARD_X, BOARD_Y))
    screen.blit(grid_overlay, (BOARD_X, BOARD_Y))

    pygame.draw.rect( screen, (91, 114, 135), pygame.Rect(BOARD_X, BOARD_Y, BOARD_PX, BOARD_PX), 1)

    #display keyboard shortcuts
    draw_text("mouse: draw cells  |  SPACE: start/pause  |  N: step  |  R: reset  |  E: edge", BOARD_X, 822, MUTED, small_font)

    x = PANEL_X
    cw = (PANEL_W - 9) // 2

    #application title
    draw_text("GAME OF LIFE", x, 17, TEXT, title_font)
    draw_text("200 x 200  |  moore neighborhood", x, 54, MUTED, small_font)

    #initial pattern selection
    draw_text("INITIAL PATTERNS", x, 87, TEXT, heading_font)

    for i, name in enumerate(PATTERN_NAMES):
        bx = x + (i % 2) * (cw + 9)
        by = 116 + (i // 2) * 41

        draw_button( name.title(), bx, by, cw, 34, "pattern:" + name, pattern_name == name )

    #boundary condition selection
    draw_text("BOUNDARY CONDITIONS", x, 249, TEXT, heading_font)
    draw_button("periodic", x, 275, cw, 34,"periodic", boundary == "periodic" )
    draw_button("reflective", x + cw + 9, 275, cw, 34,"reflect", boundary == "reflective")

    #transition rule selection
    draw_text("TRANSITION RULES", x, 320, TEXT, heading_font)

    draw_button( "conway B3/S23", x, 347, cw, 34,"conway", rule == "conway")

    draw_button("custom B34/S23", x + cw + 9, 347, cw, 34,"custom", rule == "custom" )

    #simulation controls
    draw_text("CONTROLS", x, 394, TEXT, heading_font)

    draw_button( "pause" if running else "Start", x, 421, cw, 34, "toggle")

    draw_button("next step (N)", x + cw + 9, 421, cw, 34, "step")

    draw_button("reset (R)", x, 463, cw, 34, "reset")
    draw_button("clear", x + cw + 9, 463, cw, 34, "clear")

    draw_button("move pattern near edge (E)",x, 505, PANEL_W, 34, "edge")

    #simulation speed controls
    draw_text("SIMULATION SPEED", x, 551, TEXT, heading_font)

    draw_button("slower -", x, 578, cw, 32, "slower")
    draw_button("faster +", x + cw + 9, 578, cw, 32, "faster")

    draw_text(f"{speed} generations/s", x, 613, MUTED, small_font)

    #display simulation statistics
    draw_text("STATISTICS", x, 639, TEXT, heading_font)

    draw_text(f"generation: {generation}  |  Alive: {int(board.sum())}", x, 664, TEXT, small_font)

    draw_text( "minimum 30 generations: " + ("OK" if generation >= 30 else "not yet"), x, 684, ALIVE if generation >= 30 else MUTED, small_font)

    draw_chart(history, pygame.Rect(x, 708, PANEL_W, 42))

    #display rule comparison results
    draw_button("COMPARE RULES AFTER 30 STEPS", x, 758, PANEL_W, 34, "compare")

    if comparison is None:
        draw_text("comparison from the same initial state",x, 801, MUTED, small_font)
    else:
        draw_text( f"conway: {comparison[0]}  |  custom: {comparison[1]}", x, 800, TEXT, small_font)

        draw_text(    f"different cells after 30 steps: {comparison[2]}",  x, 820, MUTED, small_font)

    pygame.display.flip()

