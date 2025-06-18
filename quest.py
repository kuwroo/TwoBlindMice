import pygame
import random
from misc import SCREEN_WIDTH as WIDTH, SCREEN_HEIGHT as HEIGHT

def play_first_quest():
    pygame.init()
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Fall Without Hitting")

    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    PLAYER_COLOR = (0, 0, 255)
    GREEN = (0, 200, 0)
    BROWN = (139, 69, 19)

    player_size = 30
    player_x = WIDTH // 2
    player_y = HEIGHT // 2
    player = pygame.Rect(player_x, player_y, player_size, player_size)
    player_speed = 7
    scroll_speed = 8

    # --- STARTING PLATFORM ---
    platform_width = WIDTH
    platform_height = 20
    platform_x = player_x - platform_width // 2
    platform_y = player_y + player_size  # just below player
    platform = pygame.Rect(platform_x, platform_y, platform_width, platform_height)

    # Adjust player to stand directly on the platform
    player.bottom = platform.top

    # --- OBSTACLES ---
    obstacles = []
    obstacle_height = 20
    gap = 200
    start_offset = 750  # moved further down
    num_obstacles = 10

    for i in range(num_obstacles):
        obstacle_width = random.randint(50, 200)
        x = random.randint(0, WIDTH - obstacle_width)
        y = i * gap + start_offset
        obstacles.append(pygame.Rect(x, y, obstacle_width, obstacle_height))

    ground_height = 30
    ground_y = num_obstacles * gap + start_offset
    ground = pygame.Rect(0, ground_y, WIDTH, ground_height)

    camera_offset = 0
    clock = pygame.time.Clock()
    run = True
    quest_result = None
    on_ground = False
    falling = False  # player must press SPACE to start falling

    while run:
        clock.tick(60)
        win.fill(WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                quest_result = "quit"

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.left > 0:
            player.x -= player_speed
        if keys[pygame.K_d] and player.right < WIDTH:
            player.x += player_speed

        if not falling and keys[pygame.K_SPACE]:
            falling = True  # start fall when SPACE is pressed 

        if falling and not on_ground:
            if ground.top - camera_offset <= player.bottom:
                on_ground = True
                print("You landed safely! Press E to return.")
            else:
                camera_offset += scroll_speed

        # --- DRAW OBSTACLES ---
        for obs in obstacles:
            draw_rect = obs.copy()
            draw_rect.y -= camera_offset
            pygame.draw.rect(win, RED, draw_rect)
            if player.colliderect(draw_rect):
                print("Game Over!")
                quest_result = "lose"
                run = False

        # --- DRAW GROUND ---
        draw_ground = ground.copy()
        draw_ground.y -= camera_offset
        pygame.draw.rect(win, GREEN, draw_ground)

        # --- DRAW STARTING PLATFORM ---
        draw_platform = platform.copy()
        draw_platform.y -= camera_offset
        pygame.draw.rect(win, BROWN, draw_platform)

        # --- INTERACT AFTER LANDING ---
        if on_ground and keys[pygame.K_e]:
            quest_result = "win"
            run = False

        # --- DRAW PLAYER ---
        pygame.draw.rect(win, PLAYER_COLOR, player)
        pygame.display.update()

    return quest_result
