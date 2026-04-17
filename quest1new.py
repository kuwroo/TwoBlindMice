import pygame
import asyncio
import random
from misc import SCREEN_WIDTH as WIDTH, SCREEN_HEIGHT as HEIGHT, TILE_SIZE
import sys
from collections import deque
from tilemap import TileMap
from spritesheet_loader import SpriteSheet
from colours import *
from spritesheet_loader import *
from player import PlayerMovement
from dialogueview import DialogueView
import pytmx

async def play_first_quest(screen):
    import pygame
    import asyncio

    FPS = 60
    clock = pygame.time.Clock()

    # Map legend
    # 1 = solid wall/platform
    # 0 = empty air
    # X = obstacle
    # B = bottom landing zone
    # S = spawn
    map_data = [
        "1111111111111111111111111",
        "100000000000S000000000001",
        "1000000000001000000000001",
        "1000000000000000000X00001",
        "1000000000000000000100001",
        "100000000X0000000X0000001",
        "1000000001000000010000001",
        "1000X0000000000000000X001",
        "100010000000X000000001001",
        "1000000000001000000000001",
        "100000X000000000000X00001",
        "1000001000000000000100001",
        "1000000000000X00000000001",
        "1000X0000000010000000X001",
        "1000100000000000000000001",
        "100000000X000000000000001",
        "1000000001000000000X00001",
        "1000000000000000000100001",
        "10000000000BBBBB000000001",
        "1111111111111111111111111",
    ]

    # Assets
    sky_img = pygame.image.load("resources/quest1/sky.png").convert_alpha()
    wall_img = pygame.image.load("resources/quest1/wall.png").convert_alpha()
    obstacle_img = pygame.image.load("resources/quest1/obstacle.png").convert_alpha()
    bottom_img = pygame.image.load("resources/quest1/bottom.png").convert_alpha()

    sky_img = pygame.transform.scale(sky_img, (TILE_SIZE, TILE_SIZE))
    wall_img = pygame.transform.scale(wall_img, (TILE_SIZE, TILE_SIZE))
    obstacle_img = pygame.transform.scale(obstacle_img, (TILE_SIZE, TILE_SIZE))
    bottom_img = pygame.transform.scale(bottom_img, (TILE_SIZE, TILE_SIZE))

    # Build level
    floor_tiles = []
    obstacles = []
    bottom_tiles = []
    player_spawn = None

    PLAYER_SIZE = 32

    rows = len(map_data)
    cols = len(map_data[0])
    map_height_px = rows * TILE_SIZE

    for y, row in enumerate(map_data):
        for x, cell in enumerate(row):
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)

            if cell == "1":
                floor_tiles.append(rect)
            elif cell == "X":
                obstacles.append(rect)
            elif cell == "B":
                bottom_tiles.append(rect)
                floor_tiles.append(rect)
            elif cell == "S":
                player_spawn = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, PLAYER_SIZE, PLAYER_SIZE)

    if not player_spawn or not bottom_tiles:
        raise ValueError("Map missing spawn or bottom zone.")

    bottom_rect = bottom_tiles[0].unionall(bottom_tiles[1:]) if len(bottom_tiles) > 1 else bottom_tiles[0]

    # Player
    player_sprite = PlayerMovement(WIDTH, HEIGHT, WIDTH)
    player_sprite.player_x = player_spawn.x
    player_sprite.player_y = player_spawn.y
    player_sprite.rect.topleft = (player_spawn.x, player_spawn.y)

    camera_offset_y = 0
    run = True
    falling = False
    on_floor = False
    quest_result = None
    showing_dialogue = False
    dialogue_box = None
    BUFFER = 5

    while run:
        clock.tick(FPS)
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                quest_result = "quit"
            elif event.type == pygame.KEYDOWN and showing_dialogue:
                if dialogue_box.handle_input(event.key) == "CLOSE":
                    showing_dialogue = False
                    run = False

        if not showing_dialogue:
            player_sprite.handle_input(keys)
            player_sprite.apply_gravity()
            player_sprite.update_position(floor_tiles, [])
            player_sprite.update_animation(keys)

        # Start falling if no tile below
        if not falling and not on_floor:
            feet_rect = player_sprite.rect.copy()
            feet_rect.y += 1
            if not any(feet_rect.colliderect(tile) for tile in floor_tiles):
                falling = True

        # Landing check
        if falling and not on_floor:
            if player_sprite.rect.bottom >= bottom_rect.top and player_sprite.rect.colliderect(bottom_rect):
                on_floor = True
                player_sprite.rect.bottom = bottom_rect.top
                quest_result = "win"
                font_path = "resources/Minecraft.ttf"
                dialogue_text = "Congrats! You landed safely. Press E to exit."
                dialogue_box = DialogueView(font_path, dialogue_text, mode="quest_win")
                showing_dialogue = True

        # Obstacle collisions
        player_collision_rect = pygame.Rect(
            player_sprite.rect.x + (player_sprite.PLAYER_WIDTH - player_sprite.COLLISION_WIDTH) // 2 + BUFFER // 2,
            player_sprite.rect.y + (player_sprite.PLAYER_HEIGHT - player_sprite.COLLISION_HEIGHT) // 2 + BUFFER // 2,
            player_sprite.COLLISION_WIDTH - BUFFER,
            player_sprite.COLLISION_HEIGHT - BUFFER
        )

        if not showing_dialogue:
            for obs in obstacles:
                obs_buf = obs.inflate(-BUFFER, -BUFFER)
                if player_collision_rect.colliderect(obs_buf):
                    quest_result = "lose"
                    font_path = "resources/Minecraft.ttf"
                    dialogue_text = "Oops! You hit an obstacle. Press E to exit."
                    dialogue_box = DialogueView(font_path, dialogue_text, mode="quest_fail")
                    showing_dialogue = True
                    falling = False
                    break

        # Camera follow
        target_offset = player_sprite.rect.centery - HEIGHT // 2
        camera_offset_y = max(0, min(target_offset, map_height_px - HEIGHT))

        # Draw
        screen.fill((0, 0, 0))

        for y, row in enumerate(map_data):
            for x, cell in enumerate(row):
                draw_x = x * TILE_SIZE
                draw_y = y * TILE_SIZE - camera_offset_y

                # Skip off-screen tiles for speed
                if draw_y < -TILE_SIZE or draw_y > HEIGHT:
                    continue

                if cell == "1":
                    screen.blit(wall_img, (draw_x, draw_y))
                elif cell == "X":
                    screen.blit(obstacle_img, (draw_x, draw_y))
                elif cell == "B":
                    screen.blit(bottom_img, (draw_x, draw_y))
                else:
                    screen.blit(sky_img, (draw_x, draw_y))

        player_sprite.draw(screen, keys, pygame.Vector2(0, camera_offset_y))

        if showing_dialogue:
            dialogue_box.update()
            dialogue_box.draw(screen)

        await asyncio.sleep(0)
        pygame.display.update()

    return quest_result



async def main():
    pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Third Quest Test")

    result = await play_first_quest(screen)
    print("Quest result:", result)

    pygame.quit()

asyncio.run(main())