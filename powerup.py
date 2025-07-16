import pygame
import random
import math
from circleshape import CircleShape
from constants import *


class PowerUp(CircleShape):
    def __init__(self, x, y, power_type):
        super().__init__(x, y, POWERUP_RADIUS)
        self.power_type = power_type
        self.lifetime = 10.0  # Power-ups disappear after 10 seconds
        self.pulse_time = 0
        
        # Random initial velocity
        angle = random.uniform(0, 2 * math.pi)
        self.velocity = pygame.Vector2(
            math.cos(angle) * POWERUP_SPEED,
            math.sin(angle) * POWERUP_SPEED
        )
    
    def draw(self, screen):
        # Pulsing effect
        pulse = math.sin(self.pulse_time * 5) * 0.2 + 0.8
        radius = int(self.radius * pulse)
        
        # Different colors for different power-ups
        if self.power_type == "shield":
            color = (100, 200, 255)  # Blue
            # Draw shield icon (circle with inner circle)
            pygame.draw.circle(screen, color, self.position, radius, 2)
            pygame.draw.circle(screen, color, self.position, radius // 2, 2)
        elif self.power_type == "speed":
            color = (255, 255, 100)  # Yellow
            # Draw speed icon (arrow)
            pygame.draw.circle(screen, color, self.position, radius, 2)
            # Draw arrow inside
            tip = self.position + pygame.Vector2(0, -radius * 0.6)
            left = self.position + pygame.Vector2(-radius * 0.4, radius * 0.3)
            right = self.position + pygame.Vector2(radius * 0.4, radius * 0.3)
            pygame.draw.lines(screen, color, False, [left, tip, right], 2)
    
    def update(self, dt):
        self.position += self.velocity * dt
        self.wrap_position()
        
        self.pulse_time += dt
        self.lifetime -= dt
        
        if self.lifetime <= 0:
            self.kill()


def maybe_spawn_powerup(x, y, containers):
    """Randomly spawn a power-up with POWERUP_SPAWN_CHANCE probability"""
    if random.random() < POWERUP_SPAWN_CHANCE:
        PowerUp.containers = containers
        power_type = random.choice(["shield", "speed"])
        PowerUp(x, y, power_type)