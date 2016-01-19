"""
This library implements the algorithms and ideas from
http://weblog.jamisbuck.org/2011/1/27/maze-generation-growing-tree-algorithm
"""
NORTH_DIR = 0
EAST_DIR = 1
SOUTH_DIR = 2
WEST_DIR = 3

X_OFFSETS_FROM_DIRS = (0, 1, 0, -1)
Y_OFFSETS_FROM_DIRS = (-1, 0, 1, 0)

NORTH_WALL = 1 << NORTH_DIR
EAST_WALL = 1 << EAST_DIR
SOUTH_WALL = 1 << SOUTH_DIR
WEST_WALL = 1 << WEST_DIR

WALLS_FROM_DIRS = (NORTH_WALL, EAST_WALL, SOUTH_WALL, WEST_WALL)

ALL_WALLS = NORTH_WALL | EAST_WALL | SOUTH_WALL | WEST_WALL

def error():
    print "Kevin, something is wrong!"

def opposite_wall(wall):
    if wall == NORTH_WALL:
        return SOUTH_WALL
    elif wall == EAST_WALL:
        return WEST_WALL
    elif wall == SOUTH_WALL:
        return NORTH_WALL
    elif wall == WEST_WALL:
        return EAST_WALL
    else:
        error()

def choose(max):
    # TODO - Per the white paper, multiple "flavors" of maze result
    # from different choice algorithms, including NEWEST, OLDEST, etc.
    # Today I am just implementing NEWEST
    return max - 1

# We only have byte-lists (not "full" lists), so we have to encode the x,y coords into a single byte
# Note that this restricts us to a max 16x16 maze. Other memory constraints restricted us to 15x15 ANYWAY
def encode_cell(x, y):
    return (y << 4) | x;

def extract_x(code):
    return code & 0x0F

def extract_y(code):
    return code >> 4

def generate_maze(width, height, start_x, start_y):
    global maze, maze_width, maze_height
    total_cells = width * height
    maze_width = width
    maze_height = height
    maze = []
    while total_cells:
        maze = maze + [ ALL_WALLS ]
        total_cells -= 1
    
    working_cells = [ encode_cell(start_x, start_y) ]
    while len(working_cells) > 0:
        # Pick a cell to expand out from
        index = choose(len(working_cells))
        # Build up a list of POSSIBLE expansion directions
        # Where do we still have a wall?
        # That leads to a completely unexplored cell?
        # Also keeping within the boundaries of the maze...
        code = working_cells[index]
        x = extract_x(code)
        y = extract_y(code)
        maze_index = y * maze_width + x
        walls = maze[maze_index]
        choices = []
        if (walls & NORTH_WALL) and y > 0:
            if maze[(y + Y_OFFSETS_FROM_DIRS[NORTH_DIR]) * maze_width + (x + X_OFFSETS_FROM_DIRS[NORTH_DIR])] == ALL_WALLS:
                choices = choices + [ NORTH_DIR ]
        if (walls & EAST_WALL) and x < (maze_width - 1):
            if maze[(y + Y_OFFSETS_FROM_DIRS[EAST_DIR]) * maze_width + (x + X_OFFSETS_FROM_DIRS[EAST_DIR])] == ALL_WALLS:
                choices = choices + [ EAST_DIR ]
        if (walls & SOUTH_WALL) and y < (maze_height - 1):
            if maze[(y + Y_OFFSETS_FROM_DIRS[SOUTH_DIR]) * maze_width + (x + X_OFFSETS_FROM_DIRS[SOUTH_DIR])] == ALL_WALLS:
                choices = choices + [ SOUTH_DIR ]
        if (walls & WEST_WALL) and x > 0:
            if maze[(y + Y_OFFSETS_FROM_DIRS[WEST_DIR]) * maze_width + (x + X_OFFSETS_FROM_DIRS[WEST_DIR])] == ALL_WALLS:
                choices = choices + [ WEST_DIR ]
        if len(choices) == 0:
            # No place to go, kick this cell out of the working list
            if index == 0:
                working_cells = working_cells[1:]
            elif index == (len(working_cells) - 1):
                working_cells = working_cells[0:index]
            else:
                working_cells = working_cells[0:index] + working_cells[index+1:]
        else:
            # Now randomly choose one
            choice = random() % len(choices)
            dir = choices[choice]
            wall = WALLS_FROM_DIRS[dir]
            # Knock out the wall, establishing a passageway
            maze[maze_index] = maze[maze_index] & ~wall
            x = x + X_OFFSETS_FROM_DIRS[dir]
            y = y + Y_OFFSETS_FROM_DIRS[dir]
            maze_index = y * maze_width + x
            wall = opposite_wall(wall)
            # Knock out the reciprocal wall in the adjacent cell
            maze[maze_index] = maze[maze_index] & ~wall
            # Add the newly-reached cell to the working list
            working_cells = working_cells + [ encode_cell(x, y) ]

def print_maze():
    print
    row = 0
    while row < maze_height:
        # Pass 1 - top of cell
        col = 0
        while col < maze_width:
            maze_index = row * maze_width + col
            walls = maze[maze_index]
            print '+',
            if (walls & NORTH_WALL) == 0:
                print " ",
            else:
                print '-',
            col += 1
        print "+"
        # Pass 2 - side of cell
        col = 0
        while col < maze_width:
            maze_index = row * maze_width + col
            walls = maze[maze_index]
            if (walls & (WEST_WALL)) == 0:
                print '  ',
            else:
                print '| ',
            col += 1
        print "|"
        row += 1

    col = 0
    while col < maze_width:
        print '+-',
        col += 1
    print "+"

def test_maze():
    global maze, maze_width, maze_height
    maze_width = 3
    maze_height = 3
    maze = [ ALL_WALLS ] * 9

