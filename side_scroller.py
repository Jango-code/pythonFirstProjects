import pygame
import random

# Initialize pygame
pygame.init()

# Game constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRAVITY = 1
SCROLL_THRESHOLD = 200  # How close to the edge the player can get before the screen scrolls

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

# Create the game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("2D Side Scroller")
clock = pygame.time.Clock()

class Player:
    def __init__(self):
        # Player properties
        self.width = 40
        self.height = 60
        self.x = 100
        self.y = SCREEN_HEIGHT - self.height - 100
        self.velocity_y = 0
        self.speed = 5
        self.jumping = False
        self.facing_right = True
        
        # For animation/display purposes (simple rectangle for now)
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
    def move(self, dx):
        # Update player direction
        if dx > 0:
            self.facing_right = True
        elif dx < 0:
            self.facing_right = False
            
        # Move the player horizontally
        self.x += dx
        
    def jump(self):
        # Player can only jump if not already jumping
        if not self.jumping:
            self.velocity_y = -15
            self.jumping = True
            
    def update(self, platforms):
        # Apply gravity
        self.velocity_y += GRAVITY
        
        # Update vertical position
        self.y += self.velocity_y
        
        # Check for collision with platforms
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                # If falling down or standing
                if self.velocity_y >= 0:
                    self.y = platform.rect.top - self.height
                    self.velocity_y = 0
                    self.jumping = False
        
        # Prevent player from going off the left edge of the screen
        if self.x < 0:
            self.x = 0
        
    def draw(self, scroll):
        # Draw the player on the screen (adjusted for scrolling)
        self.rect = pygame.Rect(self.x - scroll, self.y, self.width, self.height)
        pygame.draw.rect(screen, BLUE, self.rect)

class Platform:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        
    def draw(self, scroll):
        # Draw the platform on the screen (adjusted for scrolling)
        draw_rect = pygame.Rect(self.rect.x - scroll, self.rect.y, self.rect.width, self.rect.height)
        pygame.draw.rect(screen, GREEN, draw_rect)

def main():
    # Initialize game variables
    player = Player()
    scroll = 0
    
    # Create platforms
    platforms = []
    # Ground platform
    platforms.append(Platform(0, SCREEN_HEIGHT - 50, 1000, 50))
    
    # Add some random platforms
    for i in range(10):
        platforms.append(Platform(random.randint(400, 3000), 
                                random.randint(SCREEN_HEIGHT - 300, SCREEN_HEIGHT - 100), 
                                random.randint(100, 300), 30))
    
    # Main game loop
    running = True
    while running:
        # Process events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.jump()
        
        # Get key states for continuous movement
        keys = pygame.key.get_pressed()
        
        # Horizontal movement
        dx = 0
        if keys[pygame.K_LEFT]:
            dx = -player.speed
        if keys[pygame.K_RIGHT]:
            dx = player.speed
        
        player.move(dx)
        
        # Update player
        player.update(platforms)
        
        # Handle scrolling
        if player.x > SCREEN_WIDTH - SCROLL_THRESHOLD:
            scroll += player.speed
        
        # Clear the screen
        screen.fill(WHITE)
        
        # Draw platforms
        for platform in platforms:
            platform.draw(scroll)
        
        # Draw player
        player.draw(scroll)
        
        # Update display
        pygame.display.flip()
        
        # Control game speed
        clock.tick(60)

# Run the game
if __name__ == "__main__":
    main()
    pygame.quit()

