import pygame
import random
from misc import SCREEN_WIDTH as WIDTH, SCREEN_HEIGHT as HEIGHT, TILE_SIZE
from collections import deque
from tilemap import TileMap
from spritesheet_loader import SpriteSheet
from colours import *


def play_first_quest():
    pygame.init()
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Rabbit-hole!")
    FPS = 60

    # Load TMX map
    tmx = TileMap("resources/quest1map.tmx")

    print("=== Tiled Objects ===")
    for obj in tmx.tmx_data.objects:
        print(f"name: {obj.name}, type: {obj.type}, text: {getattr(obj, 'text', None)}")


    platform = None
    walls = []
    obstacles = []
    floor = None
    texts = []

    for obj in tmx.interactables:
        obj_type = obj["type"].lower()
        rect = obj["rect"]
        if obj_type == "spawn":
            PLAYER_SIZE = 32
            player = pygame.Rect(rect.x, rect.y, PLAYER_SIZE, PLAYER_SIZE)
        elif obj_type == "platform":
            platform = rect
        elif obj_type == "wall":
            walls.append(rect)
        elif obj_type == "floor":
            floor = rect
        elif obj_type == "obstacle":
            obstacles.append(rect)
    
    print("--- Tiled Objects ---")
    for obj in tmx.tmx_data.objects:
        print(f"name: {obj.name}, type: {obj.type}, text: {getattr(obj, 'text', None)}")


    # Game loop variables
    camera_offset = 0
    clock = pygame.time.Clock()
    run = True
    falling = False
    on_floor = False
    scroll_speed = 8
    player_speed = 7
    quest_result = None

    font = pygame.font.SysFont(None, 24)

    while run:
        clock.tick(FPS)
        win.fill(WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                quest_result = "quit"

        def can_move(new_rect):
            for wall in walls:
                wall_moved = wall.copy()
                wall_moved.y -= camera_offset  # adjust for scroll
                if new_rect.colliderect(wall_moved):
                    return False
            return True

        # Input
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            new_pos = player.move(-player_speed, 0)
            if can_move(new_pos):
                player = new_pos
        if keys[pygame.K_d]:
            new_pos = player.move(player_speed, 0)
            if can_move(new_pos):
                player = new_pos

        # Begin falling when space pressed
        if not falling and keys[pygame.K_SPACE]:
            falling = True

        # Simulate fall by scrolling map upward
        if falling and not on_floor:
            if floor.top - camera_offset <= player.bottom:
                on_floor = True
                print("You landed on the floor! Press E to win.")
            else:
                camera_offset += scroll_speed

        # --- DRAW TILEMAP BACKGROUND ---
        tmx.draw(win, pygame.Vector2(0, camera_offset))

        test_font = pygame.font.SysFont(None, 30)
        test_surface = test_font.render("TEST TEXT", True, (255, 0, 0))
        win.blit(test_surface, (50, 50))


        tmx.draw_texts(win, pygame.Vector2(0, camera_offset))

        # --- DRAW OBSTACLES ---
        # Check collision with invisible obstacle areas
        for obs in obstacles:
            draw_obs = obs.copy()
            draw_obs.y -= camera_offset
            if player.colliderect(draw_obs):
                print("You hit an obstacle. Game over!")
                quest_result = "lose"
                run = False

        # --- DRAW PLAYER ---
        pygame.draw.rect(win, PLAYER_COLOR, player)


        # Win condition
        if on_floor and keys[pygame.K_e]:
            print("You completed the quest!")
            quest_result = "win"
            run = False

        pygame.display.update()

    pygame.quit()
    return quest_result

play_first_quest()