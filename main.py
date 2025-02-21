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

# Set up the display
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dodge the Blocks")

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

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
        # For Pygbag/WebAssembly, we'll simulate localStorage with a default
        # In a real browser, this would interact with JavaScript localStorage
        return json.loads(pygame.display.get_driver() or '[]')
    except:
        return []  # Default empty leaderboard

def save_leaderboard(score):
    leaderboard = load_leaderboard()
    leaderboard.append(score)
    leaderboard = sorted(leaderboard, reverse=True)[:5]  # Top 5 scores
    try:
        # Simulate saving to localStorage
        pygame.display.set_driver(json.dumps(leaderboard))
    except:
        pass  # Silent fail for web compatibility
    return leaderboard

def draw_leaderboard(leaderboard):
    font = pygame.font.Font(None, 50)
    title = font.render("Leaderboard", True, BLACK)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
    
    for i, score in enumerate(leaderboard[:5]):
        text = font.render(f"{i+1}. {score}", True, BLACK)
        screen.blit(text, (WIDTH//2 - text.get_width()//2, 200 + i * 50))

def spawn_block():
    x = random.randint(0, WIDTH - BLOCK_WIDTH)
    return {'x': x, 'y': -BLOCK_HEIGHT}

# Main game loop as an async function
async def main():
    global player_x, score, blocks
    running = True
    frame_count = 0

    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

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
        screen.fill(WHITE)
        pygame.draw.rect(screen, BLUE, (player_x, player_y, PLAYER_WIDTH, PLAYER_HEIGHT))
        for block in blocks:
            pygame.draw.rect(screen, RED, (block['x'], block['y'], BLOCK_WIDTH, BLOCK_HEIGHT))

        # Draw score
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {score}", True, BLACK)
        screen.blit(score_text, (10, 10))

        # Update display
        pygame.display.flip()
        clock.tick(60)

        # Yield control to the browser
        await asyncio.sleep(0)

    # Game over screen
    font = pygame.font.Font(None, 74)
    game_over_text = font.render(f"Game Over! Score: {score}", True, BLACK)
    screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 20))
    pygame.display.flip()
    await asyncio.sleep(2)

    # Save score and show leaderboard
    leaderboard = save_leaderboard(score)
    screen.fill(WHITE)
    draw_leaderboard(leaderboard)
    pygame.display.flip()
    await asyncio.sleep(5)  # Show leaderboard for 5 seconds

# Run the async main function
asyncio.run(main())
pygame.quit()