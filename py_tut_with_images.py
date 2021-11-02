# Import the pygame module
import pygame

# Import random for random numbers
import random

# Import pygame.locals for easier access to key coordinates
# Updated to conform to flake8 and black standards
# from pygame.locals import *
from pygame.locals import (
    RLEACCEL,
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    KEYDOWN,
    QUIT,
    K_SPACE
)


# Define constants for the screen width and height
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Define framerate 
# Higher values (300+) may cause issues with movement
FRAMERATE = 60

# Define the Player object extending pygame.sprite.Sprite
# Instead of a surface, we use an image for a better looking sprite
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super(Player, self).__init__()
        self.surf = pygame.image.load("jet.png").convert()
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.surf.get_rect()

        self.health = 3
        self.bullet_timer = 1 # Shooting cooldown (in seconds)
        self.score = 0


    def shoot(self, position, velocity):
        """ Makes plane shoot missile """
        if self.bullet_timer <= 0: # Shoots if not on cooldown      
            self.bullet_timer = 1 # Resets cooldown 
            bullet = Bullet(position, velocity)
            bullets.add(bullet)
            all_sprites.add(bullet)


    # Move the sprite based on keypresses
    # Velocity is rounded to reduce truncation errors at higher framerates and make
    # movement more precise at all framerates, due to how Rect objects truncate all decimals
    # Multiply velocity by step to make it independent of framerate (as much as possible)
    def update(self, pressed_keys):
        if pressed_keys[K_UP]:
            self.rect.move_ip(0, round(-5 * step))
            move_up_sound.play()
        if pressed_keys[K_DOWN]:
            self.rect.move_ip(0, round(5 * step))
            move_down_sound.play()
        if pressed_keys[K_LEFT]:
            self.rect.move_ip(round(-5 * step), 0)
        if pressed_keys[K_RIGHT]:
            self.rect.move_ip(round(5 * step), 0)

        # Keep player on the screen
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top <= 0:
            self.rect.top = 0
        elif self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

        # Shoots when space is pressed
        if pressed_keys[K_SPACE]:
            self.shoot(self.rect.midright, 5)

        # Reduces shooting cooldown by (1 / framerate) per frame, if on cooldown
        self.bullet_timer -= 1/FRAMERATE if self.bullet_timer > 0 else self.bullet_timer


# Define the enemy object extending pygame.sprite.Sprite
# Instead of a surface, we use an image for a better looking sprite
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super(Enemy, self).__init__()
        self.surf = pygame.image.load("missile.png").convert()
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        # The starting position is randomly generated, as is the speed
        self.rect = self.surf.get_rect(
            center=(
                random.randint(SCREEN_WIDTH + 20, SCREEN_WIDTH + 100),
                random.randint(0, SCREEN_HEIGHT),
            )
        )
        self.speed = random.randint(5, 20)

    # Move the enemy based on speed
    # Remove it when it passes the left edge of the screen
    def update(self):
        self.rect.move_ip(round(-self.speed * step), 0)
        if self.rect.right < 0:
            self.kill()


# Define the cloud object extending pygame.sprite.Sprite
# Use an image for a better looking sprite
class Cloud(pygame.sprite.Sprite):
    def __init__(self):
        super(Cloud, self).__init__()
        self.surf = pygame.image.load("cloud.png").convert()
        self.surf.set_colorkey((0, 0, 0), RLEACCEL)
        # The starting position is randomly generated
        self.rect = self.surf.get_rect(
            center=(
                random.randint(SCREEN_WIDTH + 20, SCREEN_WIDTH + 100),
                random.randint(0, SCREEN_HEIGHT),
            )
        )

    # Move the cloud based on a constant speed
    # Remove it when it passes the left edge of the screen
    def update(self):
        self.rect.move_ip(round(-5 * step), 0)
        if self.rect.right < 0:
            self.kill()


class Bullet(pygame.sprite.Sprite):
    """ Extends pygame.sprite.Sprite class and handles aspects specific to player bullets """
    def __init__(self, position, velocity):
        super(Bullet, self).__init__()
        self.surf = pygame.image.load("player_missile.png").convert()
        self.surf.set_colorkey((0, 0, 0), RLEACCEL)
        self.velocity = velocity
        # Position is dependent on where plane was when shot
        self.rect = self.surf.get_rect(center=(position))

    def update(self):
        """ Update bullet speed """
        self.rect.move_ip(round(self.velocity * step), 0)

        if self.rect.left > SCREEN_WIDTH:
            self.kill()


class Explosion(pygame.sprite.Sprite):
    """ Extends pygame.sprite.Sprite class and handles aspects specific to explosions """
    def __init__(self, position, lifetime):
        super(Explosion, self).__init__()
        self.surf = pygame.image.load("explosion.png").convert()
        self.surf.set_colorkey((0, 0, 0), RLEACCEL)
        self.rect = self.surf.get_rect(center=(position))
        self.lifetime = lifetime # How long the explosions will stay (in seconds)

    def update(self):
        """ Update explosion timer """
        self.lifetime -= 1/FRAMERATE if self.lifetime > 0 else self.lifetime

        if self.lifetime <= 0: # When lifetime runs out, remove explosion
            self.kill()


def reset():
    """ Resets game data and returns new player object """
    # Print blank line to separate score displays
    print()

    # Empty sprite groups
    enemies.empty()
    clouds.empty()
    bullets.empty()
    explosions.empty()
    all_sprites.empty()

    # Reset player data
    player = Player()
    all_sprites.add(player)

    return player

# Setup for sounds, defaults are good
pygame.mixer.init()

# Initialize pygame
pygame.init()

# Setup the clock for a decent framerate
clock = pygame.time.Clock()

# Create the screen object
# The size is determined by the constant SCREEN_WIDTH and SCREEN_HEIGHT
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Import from other files
import scorescreen

# Create custom events for adding a new enemy and cloud
ADDENEMY = pygame.USEREVENT + 1
pygame.time.set_timer(ADDENEMY, 250)
ADDCLOUD = pygame.USEREVENT + 2
pygame.time.set_timer(ADDCLOUD, 1000)

# Create our 'player'
player = Player()

# Create groups to hold enemy sprites, cloud sprites, and all sprites
# - enemies is used for collision detection and position updates
# - clouds is used for position updates
# - bullets is used for position updates
# - explosions is used for lifetime updates on explosions
# - all_sprites isused for rendering
enemies = pygame.sprite.Group()
clouds = pygame.sprite.Group()
bullets = pygame.sprite.Group()
explosions = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
all_sprites.add(player)


# Load and play our background music
# Sound source: http://ccmixter.org/files/Apoxode/59262
# License: https://creativecommons.org/licenses/by/3.0/
pygame.mixer.music.load("Apoxode_-_Electric_1.mp3")
pygame.mixer.music.play(loops=-1)

# Load all our sound files
# Sound sources: Jon Fincher
move_up_sound = pygame.mixer.Sound("Rising_putter.ogg")
move_down_sound = pygame.mixer.Sound("Falling_putter.ogg")
collision_sound = pygame.mixer.Sound("Collision.ogg")

# Set the base volume for all sounds
move_up_sound.set_volume(0.5)
move_down_sound.set_volume(0.5)
collision_sound.set_volume(0.5)

# Variable to keep our main loop running
running = True
score_screen = False

# Our main loop
while running:
    # Code that runs during score screen
    while score_screen:
        (score_screen, running) = scorescreen.display_screen(screen, final_score)

    # Look at every event in the queue
    for event in pygame.event.get():
        # Did the user hit a key?
        if event.type == KEYDOWN:
            # Was it the Escape key? If so, stop the loop
            if event.key == K_ESCAPE:
                running = False

        # Did the user click the window close button? If so, stop the loop
        elif event.type == QUIT:
            running = False

        # Should we add a new enemy?
        elif event.type == ADDENEMY:
            # Create the new enemy, and add it to our sprite groups
            new_enemy = Enemy()
            enemies.add(new_enemy)
            all_sprites.add(new_enemy)

        # Should we add a new cloud?
        elif event.type == ADDCLOUD:
            # Create the new cloud, and add it to our sprite groups
            new_cloud = Cloud()
            clouds.add(new_cloud)
            all_sprites.add(new_cloud)

    # Get the set of keys pressed and check for user input
    pressed_keys = pygame.key.get_pressed()
    player.update(pressed_keys)

    # Update the position of our enemies and clouds
    enemies.update()
    clouds.update()

    # Update the bullets and explosions
    bullets.update()
    explosions.update()

    # Fill the screen with sky blue
    screen.fill((135, 206, 250))

    # Draw all our sprites
    for entity in all_sprites:
        screen.blit(entity.surf, entity.rect)

    # Check if any enemies have collided with the player
    player_col = pygame.sprite.spritecollide(player, enemies, True)
    
    if player_col:
        # If so, reduce the player's HP
        player.health -= 1
        collision_sound.play()

        new_explosion = Explosion(player.rect.center, .25)
        explosions.add(new_explosion)
        all_sprites.add(new_explosion)

        # If out of HP, end game
        if player.health <= 0:
            player.kill()

            # Stop any moving sounds and play the collision sound
            move_up_sound.stop()
            move_down_sound.stop()
            collision_sound.play()

            # Go to score screen and reset game
            final_score = player.score
            player = reset()
            score_screen = True

    # Check if any bullets have collided with an enemy and removes both if so
    bullet_col = pygame.sprite.groupcollide(bullets, enemies, True, True)

    # For every collision, create an explosion at give position
    for bullet in bullet_col.keys():
        new_explosion = Explosion(bullet.rect.center, .5)
        explosions.add(new_explosion)
        all_sprites.add(new_explosion)

        player.score += 10
        print(player.score)

    # Flip everything to the display
    pygame.display.flip()

    # Ensure we maintain a FRAMERATE frames per second rate
    delta = clock.tick(FRAMERATE)
    step = delta / 25 # Can be tweaked to change velocities

# At this point, we're done, so we can stop and quit the mixer
pygame.mixer.music.stop()
pygame.mixer.quit()
