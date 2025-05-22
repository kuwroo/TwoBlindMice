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

    player_size = 30
    player = pygame.Rect(WIDTH//2, 50, player_size, player_size)
    player_speed = 5
    fall_speed = 2

    obstacles = []
    obstacle_width = 100
    obstacle_height = 20
    gap = 200
    start_offset = 400

    for i in range(10):
        x = random.randint(0, WIDTH - obstacle_width)
        y = i * gap + start_offset
        obstacles.append(pygame.Rect(x, y, obstacle_width, obstacle_height))

    clock = pygame.time.Clock()
    run = True
    quest_result = None  # Will store "win" or "lose"

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

        player.y += fall_speed

        for obs in obstacles:
            obs.y -= fall_speed
            pygame.draw.rect(win, RED, obs)
            if player.colliderect(obs):
                print("Game Over!")
                quest_result = "lose"
                run = False

        if player.y > HEIGHT:
            print("You Win!")
            quest_result = "win"
            run = False

        pygame.draw.rect(win, PLAYER_COLOR, player)
        pygame.display.update()

    # Close quest window and return result
    pygame.display.quit()  # Close quest display window
    return quest_result
