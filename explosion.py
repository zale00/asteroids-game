import pygame
import random
import math
from constants import EXPLOSION_PARTICLES, EXPLOSION_SPEED, EXPLOSION_LIFETIME


class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y, velocity, color, size):
        if hasattr(self, "containers"):
            super().__init__(self.containers)
        else:
            super().__init__()
        
        self.position = pygame.Vector2(x, y)
        self.velocity = velocity
        self.color = color
        self.size = size
        self.lifetime = EXPLOSION_LIFETIME
        self.initial_lifetime = EXPLOSION_LIFETIME
    
    def update(self, dt):
        self.position += self.velocity * dt
        self.lifetime -= dt
        
        # Fade out
        self.size *= 0.95
        
        if self.lifetime <= 0 or self.size < 0.5:
            self.kill()
    
    def draw(self, screen):
        # Calculate alpha based on lifetime
        alpha = self.lifetime / self.initial_lifetime
        color = (
            int(self.color[0] * alpha),
            int(self.color[1] * alpha),
            int(self.color[2] * alpha)
        )
        pygame.draw.circle(screen, color, self.position, int(self.size))


def create_explosion(x, y, size, containers):
    # Set particle containers
    Particle.containers = containers
    
    # Create particles in random directions
    for _ in range(EXPLOSION_PARTICLES):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(EXPLOSION_SPEED * 0.5, EXPLOSION_SPEED)
        velocity = pygame.Vector2(
            math.cos(angle) * speed,
            math.sin(angle) * speed
        )
        
        # Random colors (orange to red)
        color = (
            random.randint(200, 255),
            random.randint(100, 200),
            random.randint(0, 50)
        )
        
        particle_size = random.uniform(size * 0.1, size * 0.3)
        Particle(x, y, velocity, color, particle_size)