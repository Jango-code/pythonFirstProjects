import pygame
import random
import math
import sys

# Initialize Pygame
pygame.init()

# Constants
WIDTH = 800
HEIGHT = 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 30
        self.speed = 5
        self.bullets = []
        self.lives = 3
        self.score = 0
        
    def move(self, keys):
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < WIDTH - self.width:
            self.x += self.speed
        if keys[pygame.K_UP] and self.y > HEIGHT // 2:
            self.y -= self.speed
        if keys[pygame.K_DOWN] and self.y < HEIGHT - self.height:
            self.y += self.speed
            
    def shoot(self):
        bullet = Bullet(self.x + self.width // 2, self.y, -8, YELLOW)
        self.bullets.append(bullet)
        
    def update_bullets(self):
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.y < 0:
                self.bullets.remove(bullet)
                
    def draw(self, screen):
        # Draw player ship
        points = [
            (self.x + self.width // 2, self.y),
            (self.x, self.y + self.height),
            (self.x + self.width // 4, self.y + self.height - 5),
            (self.x + self.width * 3 // 4, self.y + self.height - 5),
            (self.x + self.width, self.y + self.height)
        ]
        pygame.draw.polygon(screen, GREEN, points)
        
        # Draw bullets
        for bullet in self.bullets:
            bullet.draw(screen)

class Enemy:
    def __init__(self, x, y, enemy_type=0):
        self.x = x
        self.y = y
        self.original_x = x
        self.original_y = y
        self.width = 30
        self.height = 25
        self.speed = 1
        self.bullets = []
        self.enemy_type = enemy_type  # 0: basic, 1: fast, 2: shooter
        self.shoot_timer = 0
        self.formation_angle = 0
        self.in_formation = True
        self.dive_target = None
        self.dive_speed = 3
        
        # Set properties based on type
        if enemy_type == 0:  # Basic enemy
            self.color = RED
            self.points = 100
        elif enemy_type == 1:  # Fast enemy
            self.color = CYAN
            self.speed = 2
            self.points = 200
        else:  # Shooter enemy
            self.color = WHITE
            self.points = 300
            
    def update(self, player):
        self.formation_angle += 0.02
        
        if self.in_formation:
            # Formation flying pattern
            self.x = self.original_x + math.sin(self.formation_angle) * 20
            self.y = self.original_y + math.sin(self.formation_angle * 0.5) * 10
            
            # Occasionally dive at player
            if random.randint(1, 500) == 1:
                self.in_formation = False
                self.dive_target = (player.x, player.y)
        else:
            # Diving behavior
            if self.dive_target:
                dx = self.dive_target[0] - self.x
                dy = self.dive_target[1] - self.y
                distance = math.sqrt(dx*dx + dy*dy)
                
                if distance > 5:
                    self.x += (dx / distance) * self.dive_speed
                    self.y += (dy / distance) * self.dive_speed
                else:
                    # Return to formation or continue off screen
                    self.y += self.dive_speed
                    if self.y > HEIGHT + 50:
                        self.reset_position()
                        
        # Shooting for shooter type enemies
        if self.enemy_type == 2:
            self.shoot_timer += 1
            if self.shoot_timer > 120:  # Shoot every 2 seconds
                self.shoot()
                self.shoot_timer = 0
                
        # Update bullets
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.y > HEIGHT:
                self.bullets.remove(bullet)
                
    def shoot(self):
        bullet = Bullet(self.x + self.width // 2, self.y + self.height, 4, RED)
        self.bullets.append(bullet)
        
    def reset_position(self):
        self.x = self.original_x
        self.y = self.original_y
        self.in_formation = True
        
    def draw(self, screen):
        # Draw enemy based on type
        if self.enemy_type == 0:  # Basic enemy - simple rectangle
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        elif self.enemy_type == 1:  # Fast enemy - triangle
            points = [
                (self.x + self.width // 2, self.y + self.height),
                (self.x, self.y),
                (self.x + self.width, self.y)
            ]
            pygame.draw.polygon(screen, self.color, points)
        else:  # Shooter enemy - diamond
            points = [
                (self.x + self.width // 2, self.y),
                (self.x + self.width, self.y + self.height // 2),
                (self.x + self.width // 2, self.y + self.height),
                (self.x, self.y + self.height // 2)
            ]
            pygame.draw.polygon(screen, self.color, points)
            
        # Draw bullets
        for bullet in self.bullets:
            bullet.draw(screen)

class Bullet:
    def __init__(self, x, y, speed, color):
        self.x = x
        self.y = y
        self.speed = speed
        self.color = color
        self.width = 3
        self.height = 8
        
    def update(self):
        self.y += self.speed
        
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Galaga Clone")
        self.clock = pygame.time.Clock()
        self.player = Player(WIDTH // 2 - 20, HEIGHT - 50)
        self.enemies = []
        self.level = 1
        self.game_over = False
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.spawn_enemies()
        
    def spawn_enemies(self):
        self.enemies = []
        rows = 4 + self.level
        cols = 8
        
        for row in range(rows):
            for col in range(cols):
                x = col * 60 + 100
                y = row * 50 + 50
                enemy_type = 0
                
                # Mix enemy types
                if row == 0:
                    enemy_type = 2  # Top row shooters
                elif row == 1:
                    enemy_type = 1  # Second row fast enemies
                    
                enemy = Enemy(x, y, enemy_type)
                self.enemies.append(enemy)
                
    def handle_collisions(self):
        # Player bullets vs enemies
        for bullet in self.player.bullets[:]:
            bullet_rect = bullet.get_rect()
            for enemy in self.enemies[:]:
                enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)
                if bullet_rect.colliderect(enemy_rect):
                    self.player.bullets.remove(bullet)
                    self.enemies.remove(enemy)
                    self.player.score += enemy.points
                    break
                    
        # Enemy bullets vs player
        player_rect = pygame.Rect(self.player.x, self.player.y, self.player.width, self.player.height)
        for enemy in self.enemies:
            for bullet in enemy.bullets[:]:
                bullet_rect = bullet.get_rect()
                if bullet_rect.colliderect(player_rect):
                    enemy.bullets.remove(bullet)
                    self.player.lives -= 1
                    if self.player.lives <= 0:
                        self.game_over = True
                    break
                    
        # Enemies vs player (collision)
        for enemy in self.enemies:
            enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)
            if enemy_rect.colliderect(player_rect):
                self.player.lives -= 1
                enemy.reset_position()
                if self.player.lives <= 0:
                    self.game_over = True
                    
    def update(self):
        if not self.game_over:
            keys = pygame.key.get_pressed()
            self.player.move(keys)
            self.player.update_bullets()
            
            for enemy in self.enemies:
                enemy.update(self.player)
                
            self.handle_collisions()
            
            # Check if all enemies are destroyed
            if not self.enemies:
                self.level += 1
                self.spawn_enemies()
                
    def draw(self):
        self.screen.fill(BLACK)
        
        if not self.game_over:
            self.player.draw(self.screen)
            
            for enemy in self.enemies:
                enemy.draw(self.screen)
                
            # Draw UI
            score_text = self.small_font.render(f"Score: {self.player.score}", True, WHITE)
            lives_text = self.small_font.render(f"Lives: {self.player.lives}", True, WHITE)
            level_text = self.small_font.render(f"Level: {self.level}", True, WHITE)
            
            self.screen.blit(score_text, (10, 10))
            self.screen.blit(lives_text, (10, 35))
            self.screen.blit(level_text, (10, 60))
            
            # Instructions
            instructions = [
                "Arrow Keys: Move",
                "Space: Shoot"
            ]
            for i, instruction in enumerate(instructions):
                text = self.small_font.render(instruction, True, WHITE)
                self.screen.blit(text, (WIDTH - 150, 10 + i * 25))
        else:
            # Game Over screen
            game_over_text = self.font.render("GAME OVER", True, RED)
            score_text = self.font.render(f"Final Score: {self.player.score}", True, WHITE)
            restart_text = self.small_font.render("Press R to Restart or Q to Quit", True, WHITE)
            
            self.screen.blit(game_over_text, (WIDTH // 2 - 100, HEIGHT // 2 - 60))
            self.screen.blit(score_text, (WIDTH // 2 - 120, HEIGHT // 2 - 20))
            self.screen.blit(restart_text, (WIDTH // 2 - 120, HEIGHT // 2 + 20))
            
        pygame.display.flip()
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not self.game_over:
                    self.player.shoot()
                elif event.key == pygame.K_r and self.game_over:
                    # Restart game
                    self.__init__()
                elif event.key == pygame.K_q and self.game_over:
                    return False
        return True
        
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()

