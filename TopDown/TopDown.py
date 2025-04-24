import pygame
import math
import random
import time

# Initialize Pygame
pygame.init()

# Screen dimensions
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Top-Down Shooter")

# Colors
white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
gray = (128, 128, 128)
brown = (139, 69, 19)  # Gun color

# Load Images
player_img = pygame.image.load("player.png").convert_alpha()  # Replace with your image
player_img = pygame.transform.scale(player_img, (50, 55))  # Adjust size

gun_img = pygame.image.load("gun.png").convert_alpha()  # Replace with your image
gun_img = pygame.transform.scale(gun_img, (60, 30))  # Adjust size

crate_img = pygame.image.load("crate.png").convert_alpha()  # Replace with your image
crate_img = pygame.transform.scale(crate_img, (30, 30))

# Player properties
player_size = 30
player_x = screen_width // 2
player_y = screen_height // 2
player_speed = 3
player_health = 100

# Gun properties
gun_length = 40
gun_width = 8
gun_offset_x = 65  # Offset from player center
gun_offset_y = 0

# Bullet properties
bullet_size = 5
bullet_color = white  # Bullets are now white
bullet_speed = 10
bullets = []

# Enemy properties
enemy_colors = {
    "easy": green,
    "medium": (255, 165, 0),  # Orange
    "hard": red
}

# Enemy types
enemy_types = {
    "easy": {"health": 1, "size": 20, "speed": 0.7},
    "medium": {"health": 5, "size": 30, "speed": 0.5},
    "hard": {"health": 15, "size": 40, "speed": 0.3}
}

enemies = []

# Power-up properties
powerup_types = ["health", "speed", "damage"]  # Example power-ups
powerup_duration = 5  # seconds
active_powerups = {}  # Store active powerups and their expiration times

crate = None  # No crate initially
crate_spawn_time = time.time() + random.randint(120, 180)  # First crate after 2-3 minutes

# Game variables
points = 0
wave = 1
game_over = False
font = pygame.font.Font(None, 36)

# Function to calculate angle between two points
def calculate_angle(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    return math.atan2(dy, dx)

# Function to create an enemy
def create_enemy(enemy_type):
    size = enemy_types[enemy_type]["size"]
    x = random.choice([random.randint(0, size), random.randint(screen_width - size, screen_width),
                       random.randint(0, screen_width), random.randint(0, screen_width)])
    y = random.choice([random.randint(0, size), random.randint(screen_height - size, screen_height),
                       random.randint(0, screen_height), random.randint(0, screen_height)])

    if x < size:
        x = size
    elif x > screen_width - size:
        x = screen_width - size

    if y < size:
        y = size
    elif y > screen_height - size:
        y = screen_height - size

    return {
        "x": x,
        "y": y,
        "size": size,
        "color": enemy_colors[enemy_type],
        "health": enemy_types[enemy_type]["health"],
        "speed": enemy_types[enemy_type]["speed"],
        "type": enemy_type
    }

# Function to generate a wave of enemies
def generate_wave(wave_number):
    num_easy = wave_number * 2
    num_medium = wave_number
    num_hard = wave_number // 3  # Fewer hard enemies

    for _ in range(num_easy):
        enemies.append(create_enemy("easy"))
    for _ in range(num_medium):
        enemies.append(create_enemy("medium"))
    for _ in range(num_hard):
        enemies.append(create_enemy("hard"))

# Function to create a crate
def create_crate():
    x = random.randint(50, screen_width - 50)
    y = random.randint(50, screen_height - 50)
    return {"x": x, "y": y, "type": random.choice(powerup_types)}

# Function to apply a power-up
def apply_powerup(powerup_type):
    global player_speed, bullet_speed, player_health
    if powerup_type == "health":
        player_health = min(100, player_health + 25)  # Heal up to 100
    elif powerup_type == "speed":
        player_speed *= 1.5
        active_powerups["speed"] = time.time() + powerup_duration
    elif powerup_type == "damage":
        bullet_speed *= 2
        active_powerups["damage"] = time.time() + powerup_duration

# Function to check for expired power-ups
def check_powerups():
    global player_speed, bullet_speed
    now = time.time()
    if "speed" in active_powerups and now > active_powerups["speed"]:
        player_speed /= 1.5
        del active_powerups["speed"]
    if "damage" in active_powerups and now > active_powerups["damage"]:
        bullet_speed /= 2
        del active_powerups["damage"]

# Game loop
running = True
clock = pygame.time.Clock()

generate_wave(wave)  # Generate the first wave

while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_x, mouse_y = pygame.mouse.get_pos()
                angle = calculate_angle(player_x, player_y, mouse_x, mouse_y)
                bullets.append({
                    "x": player_x,
                    "y": player_y,
                    "angle": angle
                })

    # Game logic
    if not game_over:
        # Player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            player_x -= player_speed
        if keys[pygame.K_d]:
            player_x += player_speed
        if keys[pygame.K_w]:
            player_y -= player_speed
        if keys[pygame.K_s]:
            player_y += player_speed

        # Keep player within bounds
        player_x = max(player_size // 2, min(player_x, screen_width - player_size // 2))
        player_y = max(player_size // 2, min(player_y, screen_height - player_size // 2))

        # Bullet movement
        for bullet in bullets:
            bullet["x"] += bullet_speed * math.cos(bullet["angle"])
            bullet["y"] += bullet_speed * math.sin(bullet["angle"])

        # Enemy movement and collision
        for enemy in enemies:
            angle = calculate_angle(enemy["x"], enemy["y"], player_x, player_y)
            enemy["x"] += enemy["speed"] * math.cos(angle)
            enemy["y"] += enemy["speed"] * math.sin(angle)

            # Player-enemy collision
            distance = math.sqrt((player_x - enemy["x"]) ** 2 + (player_y - enemy["y"]) ** 2)
            if distance < player_size / 2 + enemy["size"] / 2:
                player_health -= 10  # Adjust damage as needed
                enemies.remove(enemy)
                if player_health <= 0:
                    game_over = True

        # Bullet-enemy collision
        for bullet in bullets[:]:  # Iterate over a copy to allow removal
            for enemy in enemies[:]:
                distance = math.sqrt((bullet["x"] - enemy["x"]) ** 2 + (bullet["y"] - enemy["y"]) ** 2)
                if distance < bullet_size + enemy["size"] / 2:
                    enemy["health"] -= 1
                    bullets.remove(bullet)
                    if enemy["health"] <= 0:
                        enemies.remove(enemy)
                        if enemy["type"] == "easy":
                            points += 10
                        elif enemy["type"] == "medium":
                            points += 25
                        else:
                            points += 50
                    break  # Only hit one enemy per bullet

        # Remove off-screen bullets
        bullets = [bullet for bullet in bullets if 0 < bullet["x"] < screen_width and 0 < bullet["y"] < screen_height]

        # Wave management
        if not enemies:
            wave += 1
            generate_wave(wave)
            print(f"Wave {wave} started!")

        # Crate spawning
        if crate is None and time.time() > crate_spawn_time:
            crate = create_crate()
            crate_spawn_time = time.time() + random.randint(120, 180)  # Next crate

        # Crate collision
        if crate:
            distance = math.sqrt((player_x - crate["x"]) ** 2 + (player_y - crate["y"]) ** 2)
            if distance < player_size / 2 + 15:  # 15 is half the crate size
                apply_powerup(crate["type"])
                crate = None

        # Check for expired power-ups
        check_powerups()

    # Drawing
    screen.fill(black)  # Set background to black

    # Draw player
    screen.blit(player_img, (player_x - player_img.get_width() // 2, player_y - player_img.get_height() // 2))

    # Draw gun
    mouse_x, mouse_y = pygame.mouse.get_pos()
    angle = calculate_angle(player_x, player_y, mouse_x, mouse_y)

    # Calculate gun position with offset
    gun_x = player_x + math.cos(angle) * gun_offset_x - math.sin(angle) * gun_offset_y
    gun_y = player_y + math.sin(angle) * gun_offset_x + math.cos(angle) * gun_offset_y

    # Rotate the gun image
    rotated_gun = pygame.transform.rotate(gun_img, -math.degrees(angle))
    gun_rect = rotated_gun.get_rect(center=(int(gun_x), int(gun_y)))  # Center the rotation

    screen.blit(rotated_gun, gun_rect)

    # Draw bullets
    for bullet in bullets:
        pygame.draw.circle(screen, bullet_color, (int(bullet["x"]), int(bullet["y"])), bullet_size)

    # Draw enemies (circles)
    for enemy in enemies:
        pygame.draw.circle(screen, enemy["color"], (int(enemy["x"]), int(enemy["y"])), enemy["size"] // 2)

    # Draw crate
    if crate:
        screen.blit(crate_img, (crate["x"] - crate_img.get_width() // 2, crate["y"] - crate_img.get_height() // 2))

    # Display score, wave, and health
    score_text = font.render(f"Points: {points}", True, white)  # Text is now white
    wave_text = font.render(f"Wave: {wave}", True, white)  # Text is now white
    health_text = font.render(f"Health: {player_health}", True, white)  # Text is now white

    screen.blit(score_text, (10, 10))
    screen.blit(wave_text, (10, 50))
    screen.blit(health_text, (10, 90))

    # Display active powerups
    powerup_text = font.render(f"Powerups: {', '.join(active_powerups.keys())}", True, white)  # Text is now white
    screen.blit(powerup_text, (10, 130))

    # Game over screen
    if game_over:
        game_over_text = font.render("Game Over!", True, red)
        restart_text = font.render("Press SPACE to restart", True, white)  # Text is now white
        screen.blit(game_over_text, (screen_width // 2 - 80, screen_height // 2 - 20))
        screen.blit(restart_text, (screen_width // 2 - 120, screen_height // 2 + 20))

        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            # Reset game variables
            points = 0
            wave = 1
            player_health = 100
            enemies = []
            bullets = []
            game_over = False
            crate = None
            active_powerups = {}
            player_speed = 3
            bullet_speed = 10
            generate_wave(wave)
            crate_spawn_time = time.time() + random.randint(120, 180)

    # Update display
    pygame.display.flip()

    # Control frame rate
    clock.tick(60)

# Quit Pygame gun_offset
pygame.quit()
