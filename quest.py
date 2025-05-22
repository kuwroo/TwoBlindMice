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
    player = pygame.Rect(WIDTH // 2, 50, player_size, player_size)
    player_speed = 5
    fall_speed = 3

    obstacles = []
    obstacle_height = 20
    gap = 200
    start_offset = 400
    num_obstacles = 5

    for i in range(num_obstacles):
        obstacle_width = random.randint(100, 150)
        x = random.randint(0, WIDTH - obstacle_width)
        y = i * gap + start_offset
        obstacles.append(pygame.Rect(x, y, obstacle_width, obstacle_height))

    ground_height = 30
    ground_y = num_obstacles * gap + start_offset
    ground = pygame.Rect(0, ground_y, WIDTH, ground_height)

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

        if not on_ground:
            # Check if player's bottom after falling will hit or pass the ground top
            if player.bottom + fall_speed >= ground.top:
                player.bottom = ground.top  # Snap player exactly on top of the ground
                on_ground = True
                print("You landed safely! Press E to return.")
            else:
                player.y += fall_speed

        for obs in obstacles:
            obs.y -= fall_speed
            pygame.draw.rect(win, RED, obs)
            if player.colliderect(obs):
                print("Game Over!")
                quest_result = "lose"
                run = False

        ground.y -= fall_speed
        if ground.y < HEIGHT:
            pygame.draw.rect(win, GREEN, ground)

        if on_ground and keys[pygame.K_e]:
            quest_result = "win"
            run = False

        pygame.draw.rect(win, PLAYER_COLOR, player)
        pygame.display.update()

    pygame.display.quit()
    return quest_result
