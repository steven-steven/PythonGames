import pygame
import random
 
# creating the data structure for pieces
# setting up global vars
# functions
# - create_grid
# - draw_grid
# - draw_window
# - rotating shape in main
# - setting up the main
 
"""
10 x 20 square grid
shapes: S, Z, I, O, J, L, T
represented in order by 0 - 6
"""
 
pygame.font.init()
 
# GLOBALS VARS
s_width = 800
s_height = 700
play_width = 300  # meaning 300 // 10 = 30 width per block
play_height = 600  # meaning 600 // 20 = 20 height per block
block_size = 30
 
top_left_x = (s_width - play_width) // 2
top_left_y = s_height - play_height
 
 
# SHAPE FORMATS
 
S = [['.....',
      '......',
      '..00..',
      '.00...',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '...0.',
      '.....']]
 
Z = [['.....',
      '.....',
      '.00..',
      '..00.',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '.0...',
      '.....']]
 
I = [['..0..',
      '..0..',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '0000.',
      '.....',
      '.....',
      '....']]

O = [['.....',
      '.....',
      '.00..',
      '.00..',
      '....']]

J = [['.....',
      '.0...',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..00.',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '...0.',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '.00..',
      '....']]

L = [['.....',
      '...0.',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '..00.',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '.0...',
      '.....'],
     ['.....',
      '.00..',
      '..0..',
      '..0..',
      '....']]

T = [['.....',
      '..0..',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '..0..',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '..0..',
      '.....']]
 
shapes = [S, Z, I, O, J, L, T]
shape_colors = [(0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 255, 0), (255, 165, 0), (0, 0, 255), (128, 0, 128)]
# index 0 - 6 represent shape
 
class Piece(object):
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = shape_colors[shapes.index(shape)]  #same index as shapes
        self.rotation = 0
 
#locked_positions = dictionary of static block position (i,j) as key, with value color
def create_grid(locked_positions={}):
    #10x20 grid. 2D list of colors
    grid = [[(0,0,0) for _ in range(10)] for _ in range(20)]
    for i in range(len(grid)): #row i
        for j in range(len(grid[i])): #col j
            if (j, i) in locked_positions:
                c = locked_positions[(j, i)] #get the color
                grid[i][j] = c #set grid color
    return grid
 
def convert_shape_format(shape): #take shape and give grid positions
    positions = [] #return val
    format = shape.shape[shape.rotation % len(shape.shape)] #get sublist of shape (with specific rotation)
    
    #loop through shape chars
    for i, line in enumerate(format):
        row = list(line) #list format
        for j, column in enumerate(row):
            if column == '0':
                #add shape'spixel to positions array
                positions.append((shape.x + j, shape.y+i))

    #for each shape pixel positions, offset them (move it left and up), shape get rendered accurately
    for i, pos in enumerate(positions):
        positions[i] = (pos[0]-2, pos[1]-4)
    return positions
 
def valid_space(shape, grid): #check grid if we are moving to valid space
    accepted_pos = [[(j, i) for j in range(10) if grid[i][j] == (0,0,0)] for i in range(20)] #all grid pixels that is empty
    accepted_pos = [j for sub in accepted_pos for j in sub] #[[(0,1)],[(2,3)]] -> [(0,1),(2,3)]
    #get shape and convert to position before we can compare with the grid position
    formatted = convert_shape_format(shape) #[(0,1),...] -> pixel position of shape

    for pos in formatted:
        if pos not in accepted_pos: # (out of screen)
            if pos[1] > -1: #ignore shape top of screen
                return False
    return True

 
def check_lost(positions): #if any positions are above screen (game over)
    #param: positions= locked_pos. Dictionary with key:position tuple val:color
    for pos in positions:
        x, y = pos
        if y < 1:
            return True
    return False #not over
 
def get_shape():
    return Piece(5, 0, random.choice(shapes)) #pick one shape, set position to middle top
 
def draw_text_middle(text, size, color, surface):
    pass
   
def draw_grid(surface, grid): #draw lines of grid
    sx = top_left_x #start x
    sy = top_left_y

    for i in range(len(grid)):
        pygame.draw.line(surface, (128,128,128), (sx,sy+i*block_size), (sx+play_width, sy+i*block_size)) #draw grey horizontal lines for each row
    for j in range(len(grid[0])):
        pygame.draw.line(surface, (128,128,128), (sx + j*block_size,sy), (sx+j*block_size, sy+play_height)) #draw grey vertical lines for each row

#called/checked when current_piece lands
#return number of cleared rows for score
def clear_rows(grid, locked):
    inc = 0
    for i in range(len(grid)-1, -1, -1):
        row = grid[i]
        if(0,0,0) not in row: #no empty pixels means line is full
            #remove locked position
            inc += 1
            ind = i
            for j in range(len(row)):
                try:
                    del locked[(j,i)]
                except:
                    continue

    #Shift position in dictionary/list
    #shift every row before the removed row, down by inc
    if inc > 0:
        #for every key in sorted locked keys based on y value. Then reverse.
        #list position tuples from highest y to lowest y (bottom to top)
        #do things bottom up so you don't overwrite when shifting down
        for key in sorted(list(locked), key = lambda x: x[1])[::-1]:
            x, y = key
            if y < ind: #if tuple is on top of deleted row, shift by inc
                newKey = (x, y+inc)
                locked[newKey] = locked.pop(key) #delete old and replace with newKey (same value)
    return inc

#show next shape. called in main
def draw_next_shape(shape, surface):
    font = pygame.font.SysFont("comicsans", 30)
    label = font.render("Next Shape", 1, (255,255,255))
    #position to render text
    sx = top_left_x + play_width + 50
    sy = top_left_y + play_height/2 -100
    format = shape.shape[shape.rotation % len(shape.shape)] #get format of the shape

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                #don't care about position in grid, just need to draw them
                pygame.draw.rect(surface, shape.color, (sx+j*block_size, sy+i*block_size, block_size, block_size), 0)
    #blit/draw label
    surface.blit(label, (sx+10, sy-30))
 
def draw_window(surface, grid, score = 0):
    #surface: to draw
    surface.fill((0,0,0)) #fill surface with black
    
    pygame.font.init() #setup font
    font = pygame.font.SysFont('comicsans', 60)
    label = font.render('Tetris', 1, (255,255,255)) #white text, antialias=1

    #position text
    surface.blit(label, (top_left_x + play_width/2 - label.get_width()/2, 30))

    #render score
    font = pygame.font.SysFont("comicsans", 30)
    label = font.render("Score: " + str(score), 1, (255,255,255))
    sx = top_left_x + play_width + 50
    sy = top_left_y + play_height/2 -100
    surface.blit(label, (sx+20, sy+160))
    
    #draw grid rectangle
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            #draw rect on surface with specific color at positions
            pygame.draw.rect(surface, grid[i][j], (top_left_x + j*block_size, top_left_y + i*block_size, block_size, block_size))
    #red border size 4
    pygame.draw.rect (surface, (255,0,0), (top_left_x, top_left_y, play_width, play_height), 4)

    draw_grid(surface, grid) #draw grid lines
 
def main(win):
    #setup some variables
    locked_positions = {}
    grid = create_grid(locked_positions)

    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.27 #smaller the value, faster
    level_time = 0
    score = 0

    while run:
        grid = create_grid(locked_positions) #every movement, locked_positions can be changed. So update grid
        fall_time += clock.get_rawtime() #time since last clock.tick() (ms)
        level_time += clock.get_rawtime()
        clock.tick()

        #change falling speed. Increase speed every five seconds
        if level_time/1000 > 5: #every 5 seconds
            level_time = 0
            if fall_speed > 0.12:   #terminal max speed
                fall_speed -= 0.005

        if fall_time/1000 > fall_speed:    #move down every fall_speed milliseconds
            fall_time = 0
            current_piece.y += 1 #move piece down
            if not (valid_space(current_piece, grid)) and current_piece.y > 0:
                #hit bottom, or hit another piece
                current_piece.y -= 1 #move back up
                change_piece = True #lock all positions and move on to new piece

        for evt in pygame.event.get():
            if evt.type == pygame.constants.QUIT:
                run = False
            elif evt.type == pygame.constants.KEYDOWN:
                if evt.key == pygame.constants.K_LEFT:
                    current_piece.x -= 1
                    if not (valid_space(current_piece, grid)):
                        current_piece.x += 1
                if evt.key == pygame.constants.K_RIGHT:
                    current_piece.x += 1
                    if not (valid_space(current_piece, grid)):
                        current_piece.x -= 1
                if evt.key == pygame.constants.K_DOWN:
                    current_piece.y += 1
                    if not (valid_space(current_piece, grid)):
                        current_piece.y -= 1
                if evt.key == pygame.constants.K_UP:
                    current_piece.rotation += 1 #rotate
                    if not (valid_space(current_piece, grid)):
                        current_piece.rotation -= 1
        
        shape_pos = convert_shape_format(current_piece) #get piece position. check if we need to lock it
        
        #draw piece
        for i in range(len(shape_pos)): #for every pixels in piece draw them
            x, y = shape_pos[i]
            if y > -1:
                grid[y][x] = current_piece.color

        #Landed
        if change_piece:    
            #update locked_positions to include pos of current piece
            for pos in shape_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color
                #locked positions is a dictionary (position tuple):(color)
                #pass this to create_grid so the color at these positions in grid is set
            #change piece
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False
            #check for clear rows and update score
            score += clear_rows(grid, locked_positions) * 10

        draw_window(win, grid, score)
        draw_next_shape(next_piece, win)
        pygame.display.update()

        #check lost
        if check_lost(locked_positions):
            run = False
    
    #outside of run, exit the game
    pygame.display.quit()

def main_menu(win):
    main(win)

#setup display window/surface
win = pygame.display.set_mode((s_width, s_height))
pygame.display.set_caption('Tetris')

main_menu(win)  # start game