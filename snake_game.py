import os
import msvcrt
import random
import time
import ctypes
import ctypes.wintypes

# Windows console functions
STD_OUTPUT_HANDLE = -11
stdout_handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)

def set_cursor_position(x, y):
    """Set the cursor position on the console."""
    ctypes.windll.kernel32.SetConsoleCursorPosition(stdout_handle, 
                                                ctypes.wintypes._COORD(x, y))

def write_console(text):
    """Write text to the console at the current cursor position."""
    ctypes.windll.kernel32.WriteConsoleA(stdout_handle, 
                                    text.encode(), 
                                    len(text), 
                                    ctypes.byref(ctypes.c_ulong()), 
                                    None)

# Game settings
WIDTH = 150
HEIGHT = 50
SNAKE_CHAR = 'O'
HEAD_CHAR = '@'
FOOD_CHAR = 'z'
WALL_CHAR = 'X'
EMPTY_CHAR = ' '
SPEED = 0.1  # lower is faster

# Key mappings
UP = 72      # Arrow Up
DOWN = 80    # Arrow Down
LEFT = 75    # Arrow Left
RIGHT = 77   # Arrow Right
W = 119      # W key
A = 97       # A key
S = 115      # S key
D = 100      # D key
ESC = 27     # Escape key

class Snake:
    def __init__(self):
        self.body = [(WIDTH // 2, HEIGHT // 2)]
        self.direction = RIGHT
        self.grow = False
        self.score = 0

    def move(self):
        head_x, head_y = self.body[0]
        
        if self.direction == UP or self.direction == W:
            new_head = (head_x, head_y - 1)
        elif self.direction == DOWN or self.direction == S:
            new_head = (head_x, head_y + 1)
        elif self.direction == LEFT or self.direction == A:
            new_head = (head_x - 1, head_y)
        elif self.direction == RIGHT or self.direction == D:
            new_head = (head_x + 1, head_y)
        
        self.body.insert(0, new_head)
        
        if not self.grow:
            self.body.pop()
        else:
            self.grow = False
            self.score += 1
    
    def change_direction(self, new_direction):
        # Prevent 180-degree turns
        if (new_direction == UP or new_direction == W) and (self.direction == DOWN or self.direction == S):
            return
        elif (new_direction == DOWN or new_direction == S) and (self.direction == UP or self.direction == W):
            return
        elif (new_direction == LEFT or new_direction == A) and (self.direction == RIGHT or self.direction == D):
            return
        elif (new_direction == RIGHT or new_direction == D) and (self.direction == LEFT or self.direction == A):
            return
        
        self.direction = new_direction
    
    def get_head(self):
        return self.body[0]
    
    def check_collision(self):
        head_x, head_y = self.get_head()
        
        # Check wall collision
        if head_x <= 0 or head_x >= WIDTH - 1 or head_y <= 0 or head_y >= HEIGHT - 1:
            return True
        
        # Check self collision (excluding head)
        if self.get_head() in self.body[1:]:
            return True
        
        return False
    
    def check_food(self, food_pos):
        return self.get_head() == food_pos

def generate_food(snake):
    while True:
        food_pos = (random.randint(1, WIDTH - 2), random.randint(1, HEIGHT - 2))
        if food_pos not in snake.body:
            return food_pos

def initialize_game_board(snake, food_pos):
    """Initialize the full game board at the start."""
    os.system('cls')
    
    # Create an empty board
    board = [[EMPTY_CHAR for _ in range(WIDTH)] for _ in range(HEIGHT)]
    
    # Draw walls
    for x in range(WIDTH):
        board[0][x] = WALL_CHAR
        board[HEIGHT - 1][x] = WALL_CHAR
    for y in range(HEIGHT):
        board[y][0] = WALL_CHAR
        board[y][WIDTH - 1] = WALL_CHAR
    
    # Draw snake
    for i, (x, y) in enumerate(snake.body):
        if i == 0:  # Head
            board[y][x] = HEAD_CHAR
        else:  # Body
            board[y][x] = SNAKE_CHAR
    
    # Draw food
    food_x, food_y = food_pos
    board[food_y][food_x] = FOOD_CHAR
    
    # Print the board
    for row in board:
        print(''.join(row))
    
    # Print score and controls (fixed position below the board)
    print(f"Score: {snake.score}")
    print("Controls: Arrow keys or WASD, ESC to quit")
    
    return board

def draw_game(snake, food_pos, prev_board=None, prev_snake_body=None, prev_food_pos=None):
    """Update only the parts of the board that have changed."""
    # Create current board state
    current_board = [[EMPTY_CHAR for _ in range(WIDTH)] for _ in range(HEIGHT)]
    
    # Set walls (these don't change)
    for x in range(WIDTH):
        current_board[0][x] = WALL_CHAR
        current_board[HEIGHT - 1][x] = WALL_CHAR
    for y in range(HEIGHT):
        current_board[y][0] = WALL_CHAR
        current_board[y][WIDTH - 1] = WALL_CHAR
    
    # If this is the first draw, initialize the whole board
    if prev_board is None:
        return initialize_game_board(snake, food_pos), current_board, snake.body.copy(), food_pos
    
    # Clear previous snake positions (except those that are part of the current snake)
    positions_to_update = []
    
    # Find positions where the previous snake was but current snake isn't
    if prev_snake_body:
        for x, y in prev_snake_body:
            if (x, y) not in snake.body:
                positions_to_update.append((x, y, EMPTY_CHAR))
    
    # Add current snake positions to be updated
    for i, (x, y) in enumerate(snake.body):
        if i == 0:  # Head
            current_board[y][x] = HEAD_CHAR
            positions_to_update.append((x, y, HEAD_CHAR))
        else:  # Body
            current_board[y][x] = SNAKE_CHAR
            positions_to_update.append((x, y, SNAKE_CHAR))
    
    # Update food position if it changed
    food_x, food_y = food_pos
    current_board[food_y][food_x] = FOOD_CHAR
    
    if prev_food_pos and prev_food_pos != food_pos:
        prev_x, prev_y = prev_food_pos
        positions_to_update.append((prev_x, prev_y, EMPTY_CHAR))
        positions_to_update.append((food_x, food_y, FOOD_CHAR))
    elif not prev_food_pos:
        positions_to_update.append((food_x, food_y, FOOD_CHAR))
    
    # Update only the positions that changed
    for x, y, char in positions_to_update:
        set_cursor_position(x, y)
        write_console(char)
    
    # Update score
    set_cursor_position(0, HEIGHT)
    write_console(f"Score: {snake.score}" + " " * 10)  # Padding to clear any previous longer score
    
    return prev_board, current_board, snake.body.copy(), food_pos

def check_keyboard():
    if msvcrt.kbhit():
        key = ord(msvcrt.getch())
        if key == 224:  # Special keys (arrows)
            key = ord(msvcrt.getch())
            return key
        return key
    return None

def main():
    snake = Snake()
    food_pos = generate_food(snake)
    running = True
    
    # Initialize board state trackers
    prev_board = None
    current_board = None
    prev_snake_body = None
    prev_food_pos = None
    
    while running:
        # Draw game with buffered updates
        prev_board, current_board, prev_snake_body, prev_food_pos = draw_game(
            snake, food_pos, prev_board, prev_snake_body, prev_food_pos
        )
        
        # Check for keyboard input
        start_time = time.time()
        while time.time() - start_time < SPEED:
            key = check_keyboard()
            if key is not None:
                if key == ESC:
                    running = False
                    break
                elif key in [UP, DOWN, LEFT, RIGHT, W, A, S, D]:
                    snake.change_direction(key)
        
        # Move snake
        snake.move()
        
        # Check for collisions
        if snake.check_collision():
            running = False
        
        # Check for food
        if snake.check_food(food_pos):
            snake.grow = True
            food_pos = generate_food(snake)
    
    os.system('cls')
    print("Game Over!")
    print(f"Final Score: {snake.score}")
    print("Press any key to exit...")
    msvcrt.getch()

if __name__ == "__main__":
    main()

