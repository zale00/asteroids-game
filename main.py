import pygame
import random
from constants import *
from player import Player
from asteroid import Asteroid
from asteroidfield import AsteroidField
from shot import Shot
from explosion import create_explosion
from powerup import PowerUp, maybe_spawn_powerup


def draw_text(screen, text, size, x, y, color="white"):
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.center = (x, y)
    screen.blit(text_surface, text_rect)


def create_stars():
    stars = []
    for _ in range(STAR_COUNT):
        x = random.randint(0, SCREEN_WIDTH)
        y = random.randint(0, SCREEN_HEIGHT)
        brightness = random.randint(50, 255)
        stars.append((x, y, brightness))
    return stars


def draw_stars(screen, stars):
    for x, y, brightness in stars:
        color = (brightness, brightness, brightness)
        pygame.draw.circle(screen, color, (x, y), 1)


def main():
    pygame.init()
    pygame.display.set_caption("Asteroids")
    print("Starting Asteroids!")
    print(f"Screen width: {SCREEN_WIDTH}")
    print(f"Screen height: {SCREEN_HEIGHT}")
    
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    dt = 0
    
    # Initialize groups
    updatable = pygame.sprite.Group()
    drawable = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    shots = pygame.sprite.Group()
    particles = pygame.sprite.Group()
    powerups = pygame.sprite.Group()
    
    Player.containers = (updatable, drawable)
    Asteroid.containers = (asteroids, updatable, drawable)
    AsteroidField.containers = updatable
    Shot.containers = (shots, updatable, drawable)
    PowerUp.containers = (powerups, updatable, drawable)
    
    # Game state
    score = 0
    lives = PLAYER_LIVES
    game_over = False
    
    # Create stars for background
    stars = create_stars()
    
    # Create initial objects
    x = SCREEN_WIDTH / 2
    y = SCREEN_HEIGHT / 2
    player = Player(x, y)
    asteroid_field = AsteroidField()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
        
        if not game_over:
            updatable.update(dt)
            
            # Check player-asteroid collisions
            if player and not player.invulnerable:
                for asteroid in asteroids:
                    if asteroid.position.distance_to(player.position) < player.radius + asteroid.radius:
                        if player.has_shield:
                            # Shield absorbs the hit
                            player.has_shield = False
                            player.shield_time = 0
                            # Push asteroid away
                            direction = (asteroid.position - player.position).normalize()
                            asteroid.velocity = direction * 200
                            # Create small explosion
                            create_explosion(asteroid.position.x, asteroid.position.y, 10, 
                                           (particles, updatable, drawable))
                        else:
                            lives -= 1
                            # Create explosion at player position
                            create_explosion(player.position.x, player.position.y, player.radius * 2, 
                                           (particles, updatable, drawable))
                            player.kill()
                            
                            if lives > 0:
                                # Respawn player
                                player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
                                player.make_invulnerable(RESPAWN_INVULNERABILITY_TIME)
                            else:
                                game_over = True
                                player = None
                        break
            
            # Check player-powerup collisions
            if player:
                for powerup in powerups:
                    if powerup.position.distance_to(player.position) < player.radius + powerup.radius:
                        if powerup.power_type == "shield":
                            player.activate_shield()
                        elif powerup.power_type == "speed":
                            player.activate_speed_boost()
                        powerup.kill()
                        score += 50  # Bonus points for collecting power-ups
            
            # Check shot-asteroid collisions
            for asteroid in asteroids:
                for shot in shots:
                    if shot.position.distance_to(asteroid.position) < shot.radius + asteroid.radius:
                        shot.kill()
                        # Award points based on asteroid size
                        score += ASTEROID_POINTS.get(int(asteroid.radius), 0)
                        # Create explosion effect
                        create_explosion(asteroid.position.x, asteroid.position.y, asteroid.radius, 
                                       (particles, updatable, drawable))
                        # Maybe spawn a power-up
                        maybe_spawn_powerup(asteroid.position.x, asteroid.position.y, 
                                          (powerups, updatable, drawable))
                        asteroid.split()
                        break
        
        # Drawing
        screen.fill("black")
        draw_stars(screen, stars)
        
        for obj in drawable:
            obj.draw(screen)
        
        # Draw UI
        draw_text(screen, f"Score: {score}", 36, 100, 30)
        draw_text(screen, f"Lives: {lives}", 36, 100, 70)
        
        # Draw active power-ups
        y_offset = 110
        if player and player.has_shield:
            remaining = int(player.shield_time)
            draw_text(screen, f"Shield: {remaining}s", 24, 100, y_offset, (100, 200, 255))
            y_offset += 30
        if player and player.has_speed_boost:
            remaining = int(player.speed_boost_time)
            draw_text(screen, f"Speed: {remaining}s", 24, 100, y_offset, (255, 255, 100))
            y_offset += 30
        
        if game_over:
            draw_text(screen, "GAME OVER", 72, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            draw_text(screen, "Press R to restart", 36, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
            
            keys = pygame.key.get_pressed()
            if keys[pygame.K_r]:
                # Reset game
                score = 0
                lives = PLAYER_LIVES
                game_over = False
                
                # Clear all sprites
                for sprite in updatable:
                    sprite.kill()
                
                # Recreate player and asteroid field
                player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
                asteroid_field = AsteroidField()
        
        pygame.display.flip()
        dt = clock.tick(60) / 1000


if __name__ == "__main__":
    main()
