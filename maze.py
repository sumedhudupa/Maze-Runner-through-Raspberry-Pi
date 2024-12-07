import pygame
import sys
import RPi.GPIO as GPIO
import time

# GPIO Pin Setup
IR_SENSOR_A = 17  # Left
IR_SENSOR_W = 27  # Up
IR_SENSOR_D = 22  # Right
IR_SENSOR_S = 23  # Down
SERVO_PIN = 18    # Servo control pin

GPIO.setmode(GPIO.BCM)
GPIO.setup(IR_SENSOR_A, GPIO.IN)
GPIO.setup(IR_SENSOR_W, GPIO.IN)
GPIO.setup(IR_SENSOR_D, GPIO.IN)
GPIO.setup(IR_SENSOR_S, GPIO.IN)
GPIO.setup(SERVO_PIN, GPIO.OUT)

# Servo setup
servo = GPIO.PWM(SERVO_PIN, 50)  # 50 Hz
servo.start(0)  # Initial position (0 degrees)

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 400, 400
CELL_SIZE = SCREEN_WIDTH // 20
FPS = 30
TIME_LIMIT = 30  # in seconds
MOVE_AMOUNT = 1  # Move by 1 step

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)

# Maze layout
maze_layout = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]

# Player properties
player_pos = [1.0, 1.0]
time_left = TIME_LIMIT

# Initialize Pygame
pygame.init()

# Setup the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Maze Game")

# Function to draw the starting interface
def draw_start_interface():
    screen.fill(WHITE)
    font = pygame.font.Font(None, 48)
    title_text = font.render("Welcome to the Maze Game!", True, GREEN)
    start_text = font.render("Press ENTER to Start", True, BLACK)

    # Draw button
    button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 70, SCREEN_HEIGHT // 2 + 20, 140, 40)
    pygame.draw.rect(screen, GREEN, button_rect)
    button_text = font.render("Start Game", True, WHITE)
    screen.blit(button_text, (button_rect.x + 10, button_rect.y + 5))

    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 2 - 40))
    screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, SCREEN_HEIGHT // 2 + 70))
    pygame.display.flip()

def draw_maze():
    for row in range(len(maze_layout)):
        for col in range(len(maze_layout[row])):
            if maze_layout[row][col] == 1:  # Wall
                pygame.draw.rect(screen, BLACK, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))
            if (row, col) == (1, 1):
                pygame.draw.rect(screen, GREEN, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))  # Start
            if (row, col) == (5, 18):
                pygame.draw.rect(screen, RED, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))  # End

def draw_player():
    pygame.draw.rect(screen, YELLOW, (player_pos[0] * CELL_SIZE, player_pos[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE))

def reset_game():
    global player_pos, time_left
    player_pos = [1.0, 1.0]  # Reset to start position
    time_left = TIME_LIMIT

def read_sensors():
    left = GPIO.input(IR_SENSOR_A)
    up = GPIO.input(IR_SENSOR_W)
    right = GPIO.input(IR_SENSOR_D)
    down = GPIO.input(IR_SENSOR_S)
    return left, up, right, down

# Function to check win status
def check_win_status():
    end_x, end_y = 5, 18
    return (int(round(player_pos[0])) == end_x) and (int(round(player_pos[1])) == end_y)

# Function to rotate servo
def rotate_servo():
    servo.ChangeDutyCycle(7)  # Rotate servo to 90 degrees
    time.sleep(1)  # Hold position for a moment
    servo.ChangeDutyCycle(0)  # Stop sending signal

# Main game loop
def game_loop():
    global time_left

    reset_game()
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                GPIO.cleanup()
                pygame.quit()
                sys.exit()

        left, up, right, down = read_sensors()

        # Movement logic based on sensor input
        moved = False
        if left == 0 and maze_layout[int(player_pos[1])][int(player_pos[0] - MOVE_AMOUNT)] == 0:
            player_pos[0] -= MOVE_AMOUNT
            moved = True
        if up == 0 and maze_layout[int(player_pos[1] - MOVE_AMOUNT)][int(player_pos[0])] == 0:
            player_pos[1] -= MOVE_AMOUNT
            moved = True
        if right == 0 and maze_layout[int(player_pos[1])][int(player_pos[0] + MOVE_AMOUNT)] == 0:
            player_pos[0] += MOVE_AMOUNT
            moved = True
        if down == 0 and maze_layout[int(player_pos[1] + MOVE_AMOUNT)][int(player_pos[0])] == 0:
            player_pos[1] += MOVE_AMOUNT
            moved = True

        # Check for win condition immediately after movement
        if check_win_status():
            rotate_servo()  # Rotate servo to indicate win
            display_message("You Win!")
            break

        # Delay for 1 second if the player moved
        if moved:
            pygame.time.delay(1000)

        # Update time left
        time_left -= 1 / FPS
        if time_left <= 0:
            time_left = 0  # Player loses

        # Drawing
        screen.fill(WHITE)
        draw_maze()
        draw_player()

        # Draw timer
        font = pygame.font.Font(None, 36)
        timer_text = font.render(f'Time Left: {int(time_left)}', True, (0, 0, 0))
        screen.blit(timer_text, (10, 10))

        # Display Game Over message if time runs out
        if time_left == 0:
            game_over_text = font.render('Game Over', True, RED)
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2))

        pygame.display.flip()
        clock.tick(FPS)

    # Quit the game after displaying the win message or game over
    pygame.time.delay(2000)
    GPIO.cleanup()
    pygame.quit()
    sys.exit()

# Function to display a message
def display_message(message):
    font = pygame.font.Font(None, 72)
    text = font.render(message, True, GREEN)
    screen.fill(WHITE)
    screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - text.get_height() // 2))
    pygame.display.flip()

# Function for the welcome screen
def welcome_screen():
    while True:
        draw_start_interface()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                GPIO.cleanup()
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                return  # Exit the welcome screen

# Run the welcome screen first
welcome_screen()
# Run the game
game_loop()