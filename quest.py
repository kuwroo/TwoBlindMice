import pygame
import random

def play_first_quest():
    pygame.init()
    WIDTH, HEIGHT = 400, 600
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Fall Without Hitting")

    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    PLAYER_COLOR = (0, 0, 255)
    GREEN = (0, 200, 0)

    player_size = 30
    player_x = WIDTH // 2
    player_y = HEIGHT // 2  # Fixed vertical position (center screen)
    player = pygame.Rect(player_x, player_y, player_size, player_size)
    player_speed = 5
    scroll_speed = 3  # how fast we scroll obstacles and ground up

    obstacles = []
    obstacle_height = 20
    gap = 200
    start_offset = 400
    num_obstacles = 5

    for i in range(num_obstacles):
        obstacle_width = random.randint(100, 200)
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

        # Scroll everything up until the ground reaches player's y
        if not on_ground:
            if ground.top - camera_offset <= player.bottom:
                on_ground = True
                print("You landed safely! Press E to return.")
            else:
                camera_offset += scroll_speed  # simulate falling by scrolling scene up

        # Draw obstacles with camera offset
        for obs in obstacles:
            draw_rect = obs.copy()
            draw_rect.y -= camera_offset
            pygame.draw.rect(win, RED, draw_rect)
            if player.colliderect(draw_rect):
                print("Game Over!")
                quest_result = "lose"
                run = False

        # Draw ground with offset
        draw_ground = ground.copy()
        draw_ground.y -= camera_offset
        pygame.draw.rect(win, GREEN, draw_ground)

        if on_ground and keys[pygame.K_e]:
            quest_result = "win"
            run = False

        # Draw player
        pygame.draw.rect(win, PLAYER_COLOR, player)
        pygame.display.update()

    return quest_result
