import pygame
from circleshape import CircleShape
from constants import *
from shot import Shot


class Player(CircleShape):
    def __init__(self, x, y):
        super().__init__(x, y, PLAYER_RADIUS)
        self.rotation = 0
        self.invulnerable = False
        self.invulnerable_time = 0
        self.shoot_cooldown = 0
        self.thrust = False
        
        # Power-ups
        self.has_shield = False
        self.shield_time = 0
        self.has_speed_boost = False
        self.speed_boost_time = 0
    
    # in the player class
    def triangle(self):
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        right = pygame.Vector2(0, 1).rotate(self.rotation + 90) * self.radius / 1.5
        a = self.position + forward * self.radius
        b = self.position - forward * self.radius - right
        c = self.position - forward * self.radius + right
        return [a, b, c]
    
    def draw(self, screen):
        # Flash when invulnerable
        if self.invulnerable and int(self.invulnerable_time * 10) % 2:
            return
        
        color = "white"
        if self.invulnerable:
            color = (100, 100, 255)  # Blue tint when invulnerable
            
        pygame.draw.polygon(screen, color, self.triangle(), 2)
        
        # Draw shield
        if self.has_shield:
            shield_color = (100, 200, 255, 128)  # Semi-transparent blue
            pygame.draw.circle(screen, shield_color, self.position, self.radius + 10, 2)
        
        # Speed boost effect - draw trail
        if self.has_speed_boost:
            trail_color = (255, 255, 100)  # Yellow
            pygame.draw.circle(screen, trail_color, self.position, self.radius + 5, 1)
        
        # Draw thrust flame
        if self.thrust:
            forward = pygame.Vector2(0, 1).rotate(self.rotation)
            flame_base = self.position - forward * self.radius
            flame_tip = flame_base - forward * 10
            flame_left = flame_base - forward * 5 + pygame.Vector2(0, 1).rotate(self.rotation + 90) * 5
            flame_right = flame_base - forward * 5 - pygame.Vector2(0, 1).rotate(self.rotation + 90) * 5
            pygame.draw.polygon(screen, "orange", [flame_base, flame_left, flame_tip, flame_right], 0)
    
    def rotate(self, dt):
        self.rotation += PLAYER_TURN_SPEED * dt
    
    def move(self, dt):
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        # Use acceleration instead of direct movement
        acceleration = PLAYER_ACCELERATION
        max_speed = PLAYER_MAX_SPEED
        
        # Apply speed boost if active
        if self.has_speed_boost:
            acceleration *= SPEED_BOOST_MULTIPLIER
            max_speed *= SPEED_BOOST_MULTIPLIER
        
        self.velocity += forward * acceleration * dt
        
        # Limit max speed
        if self.velocity.length() > max_speed:
            self.velocity = self.velocity.normalize() * max_speed
    
    def shoot(self):
        if self.shoot_cooldown <= 0:
            shot = Shot(self.position.x, self.position.y)
            shot.velocity = pygame.Vector2(0, 1).rotate(self.rotation) * PLAYER_SHOOT_SPEED
            self.shoot_cooldown = 0.3  # 0.3 seconds between shots
    
    def make_invulnerable(self, duration):
        self.invulnerable = True
        self.invulnerable_time = duration
    
    def activate_shield(self):
        self.has_shield = True
        self.shield_time = SHIELD_DURATION
    
    def activate_speed_boost(self):
        self.has_speed_boost = True
        self.speed_boost_time = SPEED_BOOST_DURATION
    
    def update(self, dt):
        keys = pygame.key.get_pressed()
        
        # Rotation
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.rotate(-dt)
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.rotate(dt)
        
        # Thrust
        self.thrust = False
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.move(dt)
            self.thrust = True
        
        # Shooting
        if keys[pygame.K_SPACE]:
            self.shoot()
        
        # Update position with velocity
        self.position += self.velocity * dt
        
        # Apply friction
        self.velocity *= PLAYER_FRICTION
        
        # Wrap around screen
        self.wrap_position()
        
        # Update invulnerability
        if self.invulnerable:
            self.invulnerable_time -= dt
            if self.invulnerable_time <= 0:
                self.invulnerable = False
        
        # Update shoot cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= dt
        
        # Update power-ups
        if self.has_shield:
            self.shield_time -= dt
            if self.shield_time <= 0:
                self.has_shield = False
        
        if self.has_speed_boost:
            self.speed_boost_time -= dt
            if self.speed_boost_time <= 0:
                self.has_speed_boost = False