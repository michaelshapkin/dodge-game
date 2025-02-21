import pygame
import random
import asyncio
import json

# Initialize Pygame and mixer
pygame.init()
pygame.mixer.init()

# Load sound effects
try:
    point_sound = pygame.mixer.Sound("point.wav")
    gameover_sound = pygame.mixer.Sound("gameover.wav")
except pygame.error as e:
    print(f"Warning: Could not load sounds - {e}")
    point_sound = None
    gameover_sound = None

# Load font
try:
    font_path = "PressStart2P-Regular.ttf"
    font_small = pygame.font.Font(font_path, 24)
    font_large = pygame.font.Font(font_path, 36)  # Reduced from 48 to 36
except:
    font_small = pygame.font.Font(None, 36)
    font_large = pygame.font.Font(None, 54)  # Adjusted fallback too

# Set up the display
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dodge the Blocks")

# Colors
WHITE = (255, 255, 255)
RED = (200, 50, 50)
BLUE = (50, 100, 255)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
GREEN = (0, 255, 0)

# Player properties
PLAYER_WIDTH = 40
PLAYER_HEIGHT = 40
player_x = WIDTH // 2 - PLAYER_WIDTH // 2
player_y = HEIGHT - PLAYER_HEIGHT - 10
player_speed = 5

# Block properties
BLOCK_WIDTH = 50
BLOCK_HEIGHT = 50
BLOCK_SPEED = 5
block_frequency = 25

# Game variables
score = 0
blocks = []
clock = pygame.time.Clock()

# Leaderboard functions
def load_leaderboard():
    try:
        return json.loads(pygame.display.get_driver() or '[]')
    except:
        return []

def save_leaderboard(score):
    leaderboard = load_leaderboard()
    leaderboard.append(score)
    leaderboard = sorted(leaderboard, reverse=True)[:10]  # Top 10 scores
    try:
        pygame.display.set_driver(json.dumps(leaderboard))
    except:
        pass
    return leaderboard

def draw_gradient_background():
    for y in range(HEIGHT):
        r = 100
        g = min(255, 150 + y // 4)
        b = max(0, 255 - y // 3)
        color = (r, g, b)
        pygame.draw.line(screen, color, (0, y), (WIDTH, y))

def draw_leaderboard(leaderboard):
    draw_gradient_background()
    title = font_large.render("Leaderboard", True, BLACK)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
    
    for i, score in enumerate(leaderboard[:10]):
        text = font_small.render(f"{i+1}. {score}", True, BLACK)
        screen.blit(text, (WIDTH//2 - text.get_width()//2, 150 + i * 40))
    
    # Restart button
    button_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT - 100, 200, 60)
    pygame.draw.rect(screen, GREEN, button_rect)
    pygame.draw.rect(screen, BLACK, button_rect, 3)
    button_text = font_small.render("Restart", True, BLACK)
    screen.blit(button_text, (WIDTH//2 - button_text.get_width()//2, HEIGHT - 85))
    return button_rect

def spawn_block():
    x = random.randint(0, WIDTH - BLOCK_WIDTH)
    return {'x': x, 'y': -BLOCK_HEIGHT}

# Main game loop as an async function
async def main():
    global player_x, score, blocks
    while True:  # Outer loop for restart
        running = True
        frame_count = 0
        score = 0
        blocks = []
        player_x = WIDTH // 2 - PLAYER_WIDTH // 2

        while running:
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return

            # Player movement
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] and player_x > 0:
                player_x -= player_speed
            if keys[pygame.K_RIGHT] and player_x < WIDTH - PLAYER_WIDTH:
                player_x += player_speed

            # Spawn blocks
            frame_count += 1
            if frame_count % block_frequency == 0:
                blocks.append(spawn_block())

            # Update blocks
            for block in blocks[:]:
                block['y'] += BLOCK_SPEED
                if block['y'] > HEIGHT:
                    blocks.remove(block)
                    score += 1
                    if point_sound:
                        point_sound.play()

            # Collision detection
            player_rect = pygame.Rect(player_x, player_y, PLAYER_WIDTH, PLAYER_HEIGHT)
            for block in blocks:
                block_rect = pygame.Rect(block['x'], block['y'], BLOCK_WIDTH, BLOCK_HEIGHT)
                if player_rect.colliderect(block_rect):
                    if gameover_sound:
                        gameover_sound.play()
                    running = False

            # Drawing
            draw_gradient_background()
            pygame.draw.rect(screen, BLUE, (player_x, player_y, PLAYER_WIDTH, PLAYER_HEIGHT))
            pygame.draw.rect(screen, BLACK, (player_x, player_y, PLAYER_WIDTH, PLAYER_HEIGHT), 2)
            for block in blocks:
                pygame.draw.rect(screen, RED, (block['x'], block['y'], BLOCK_WIDTH, BLOCK_HEIGHT))
                pygame.draw.rect(screen, BLACK, (block['x'], block['y'], BLOCK_WIDTH, BLOCK_HEIGHT), 2)

            # Draw score
            score_text = font_small.render(f"Score: {score}", True, BLACK)
            screen.blit(score_text, (10, 10))

            # Update display
            pygame.display.flip()
            clock.tick(60)
            await asyncio.sleep(0)

        # Game over screen
        game_over_text = font_large.render(f"Game Over! Score: {score}", True, BLACK)
        screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 20))
        pygame.display.flip()
        await asyncio.sleep(2)

        # Leaderboard with restart
        leaderboard = save_leaderboard(score)
        restart = False
        while not restart:
            draw_gradient_background()
            button_rect = draw_leaderboard(leaderboard)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if button_rect.collidepoint(event.pos):
                        restart = True

            await asyncio.sleep(0)

# Run the async main function
asyncio.run(main())
pygame.quit()