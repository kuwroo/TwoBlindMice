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



async def play_third_quest(screen):
    import pygame
    import asyncio

    clock = pygame.time.Clock()
    FPS = 60

    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    MAGENTA = (255, 0, 255)
    RED = (200, 60, 60)
    GREEN = (60, 200, 80)
    GREY = (70, 70, 70)
    FLOOR = (200, 200, 200)

    draw_offset_x = 80
    draw_offset_y = 48

    maze_data = [
        "11111111111111111111",
        "1S000000000100000001",
        "10001110000000011101",
        "10001110011101000101",
        "10000000011101000001",
        "10111000000000011101",
        "10111011100111000101",
        "10000011100000000001",
        "10000000000000000001",
        "10111100111101111001",
        "100000001000000000E1",
        "11100110100011000101",
        "10000110000011000001",
        "11111111111111111111",
    ]

    walls = []
    exit_rects = []
    player = None
    PLAYER_SIZE = 24

    for y, row in enumerate(maze_data):
        for x, cell in enumerate(row):
            tile_rect = pygame.Rect(
                draw_offset_x + x * TILE_SIZE,
                draw_offset_y + y * TILE_SIZE,
                TILE_SIZE,
                TILE_SIZE
            )

            if cell == "1":
                walls.append(tile_rect)
            elif cell == "S":
                player = pygame.Rect(
                    draw_offset_x + x * TILE_SIZE + (TILE_SIZE - PLAYER_SIZE) // 2,
                    draw_offset_y + y * TILE_SIZE + (TILE_SIZE - PLAYER_SIZE) // 2,
                    PLAYER_SIZE,
                    PLAYER_SIZE
                )
            elif cell == "E":
                exit_rects.append(tile_rect)

    cats = [
        {
            "name": "guard1",
            "rect": pygame.Rect(draw_offset_x + 10 * TILE_SIZE + 4, draw_offset_y + 2 * TILE_SIZE + 4, TILE_SIZE - 8, TILE_SIZE - 8),
            "path": [(10, 2), (15, 2), (15, 9), (10, 5)],
            "path_index": 1,
            "speed": 1,
            "direction_x": 1,
            "direction_y": 0,
            "facing_right": True,
            "stuck_frames": 0,
        },
        {
            "name": "guard2",
            "rect": pygame.Rect(draw_offset_x + 15 * TILE_SIZE + 4, draw_offset_y + 7 * TILE_SIZE + 4, TILE_SIZE - 8, TILE_SIZE - 8),
            "path": [(15, 7), (17, 7), (17, 10), (15, 10)],
            "path_index": 1,
            "speed": 1,
            "direction_x": 1,
            "direction_y": 0,
            "facing_right": True,
            "stuck_frames": 0,
        },
        {
            "name": "guard3",
            "rect": pygame.Rect(draw_offset_x + 5 * TILE_SIZE + 4, draw_offset_y + 8 * TILE_SIZE + 4, TILE_SIZE - 8, TILE_SIZE - 8),
            "path": [(5, 8), (8, 8), (8, 10), (5, 10)],
            "path_index": 1,
            "speed": 1,
            "direction_x": 1,
            "direction_y": 0,
            "facing_right": True,
            "stuck_frames": 0,
        }
    ]

    player_animation = {
        "last_direction_left": False,
        "velocity_x": 0,
        "velocity_y": 0
    }

    def move_player(rect, dx, dy):
        moved = False

        if dx != 0:
            next_rect = rect.move(dx, 0)
            if not any(next_rect.colliderect(w) for w in walls):
                rect.x += dx
                moved = True

        if dy != 0:
            next_rect = rect.move(0, dy)
            if not any(next_rect.colliderect(w) for w in walls):
                rect.y += dy
                moved = True

        return moved

    def update_player():
        keys = pygame.key.get_pressed()
        dx = dy = 0
        player_animation["velocity_x"] = 0
        player_animation["velocity_y"] = 0

        step = TILE_SIZE // 6

        if keys[pygame.K_a]:
            dx = -step
            player_animation["velocity_x"] = dx
            player_animation["last_direction_left"] = True
        if keys[pygame.K_d]:
            dx = step
            player_animation["velocity_x"] = dx
            player_animation["last_direction_left"] = False
        if keys[pygame.K_w]:
            dy = -step
            player_animation["velocity_y"] = dy
        if keys[pygame.K_s]:
            dy = step
            player_animation["velocity_y"] = dy

        move_player(player, dx, dy)

    def is_wall_blocking(cat_rect, player_rect, axis):
        start = cat_rect.center
        end = player_rect.center
        steps = int(max(abs(end[0] - start[0]), abs(end[1] - start[1])) // 4)

        if steps == 0:
            return False

        for i in range(steps + 1):
            t = i / steps
            x = int(start[0] + (end[0] - start[0]) * t)
            y = int(start[1] + (end[1] - start[1]) * t)
            point_rect = pygame.Rect(x, y, 4, 4)
            if any(point_rect.colliderect(w) for w in walls):
                return True

        return False

    def npc_vision_rect(cat):
        rect = cat["rect"]
        length = TILE_SIZE * 6
        width = TILE_SIZE

        dx = cat["direction_x"]
        dy = cat["direction_y"]

        if abs(dx) >= abs(dy):
            if dx >= 0:
                return pygame.Rect(rect.right, rect.centery - width // 2, length, width)
            else:
                return pygame.Rect(rect.left - length, rect.centery - width // 2, length, width)
        else:
            if dy >= 0:
                return pygame.Rect(rect.centerx - width // 2, rect.bottom, width, length)
            else:
                return pygame.Rect(rect.centerx - width // 2, rect.top - length, width, length)

    def move_guard_towards(cat, target_px, target_py):
        rect = cat["rect"]
        speed = cat["speed"]

        dx = target_px - rect.x
        dy = target_py - rect.y

        move_x = 0
        move_y = 0

        if abs(dx) > 2:
            move_x = speed if dx > 0 else -speed
        if abs(dy) > 2:
            move_y = speed if dy > 0 else -speed

        if move_x != 0:
            next_rect = rect.move(move_x, 0)
            if not any(next_rect.colliderect(w) for w in walls):
                rect.x = next_rect.x
                cat["direction_x"] = 1 if move_x > 0 else -1
                cat["direction_y"] = 0
                cat["facing_right"] = move_x > 0
                return True

        if move_y != 0:
            next_rect = rect.move(0, move_y)
            if not any(next_rect.colliderect(w) for w in walls):
                rect.y = next_rect.y
                cat["direction_x"] = 0
                cat["direction_y"] = 1 if move_y > 0 else -1
                return True

        return False

    def update_npcs():
        for cat in cats:
            target_tile = cat["path"][cat["path_index"]]
            target_px = draw_offset_x + target_tile[0] * TILE_SIZE + 4
            target_py = draw_offset_y + target_tile[1] * TILE_SIZE + 4

            moved = move_guard_towards(cat, target_px, target_py)

            if abs(cat["rect"].x - target_px) <= 4 and abs(cat["rect"].y - target_py) <= 4:
                cat["path_index"] = (cat["path_index"] + 1) % len(cat["path"])
                cat["stuck_frames"] = 0
            else:
                if not moved:
                    cat["stuck_frames"] += 1
                else:
                    cat["stuck_frames"] = 0

                if cat["stuck_frames"] > 20:
                    cat["path_index"] = (cat["path_index"] + 1) % len(cat["path"])
                    cat["stuck_frames"] = 0

            vis = npc_vision_rect(cat)
            axis = "x" if abs(cat["direction_x"]) >= abs(cat["direction_y"]) else "y"

            if vis.colliderect(player) and not is_wall_blocking(cat["rect"], player, axis):
                return "lose"

        return None

    def draw_player():
        pygame.draw.rect(screen, WHITE, player)

    def draw():
        screen.fill(BLACK)

        for y, row in enumerate(maze_data):
            for x, cell in enumerate(row):
                rect = pygame.Rect(
                    draw_offset_x + x * TILE_SIZE,
                    draw_offset_y + y * TILE_SIZE,
                    TILE_SIZE,
                    TILE_SIZE
                )

                if cell == "1":
                    pygame.draw.rect(screen, GREY, rect)
                else:
                    pygame.draw.rect(screen, FLOOR, rect)

        for exit_rect in exit_rects:
            pygame.draw.rect(screen, GREEN, exit_rect)

        draw_player()

        for cat in cats:
            pygame.draw.rect(screen, RED, cat["rect"])
            pygame.draw.rect(screen, MAGENTA, npc_vision_rect(cat), 2)

        if showing_dialogue:
            dialogue_box.update()
            dialogue_box.draw(screen)

        pygame.display.flip()

    showing_dialogue = False
    dialogue_box = None
    quest_result = None
    running = True

    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN and showing_dialogue:
                if dialogue_box.handle_input(event.key) == "CLOSE":
                    showing_dialogue = False
                    running = False

        if not showing_dialogue:
            update_player()
            npc_result = update_npcs()

            if npc_result == "lose":
                quest_result = "lose"
                font_path = "resources/Minecraft.ttf"
                dialogue_text = "Oops! You got caught. Press E to exit."
                dialogue_box = DialogueView(font_path, dialogue_text, mode="quest_fail")
                showing_dialogue = True

            if any(player.colliderect(exit_rect) for exit_rect in exit_rects):
                quest_result = "win"
                font_path = "resources/Minecraft.ttf"
                dialogue_text = "Congrats! You made it! Press E to exit."
                dialogue_box = DialogueView(font_path, dialogue_text, mode="quest_win")
                showing_dialogue = True

        draw()
        await asyncio.sleep(0)

    return quest_result


async def main():
    pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Third Quest Test")

    result = await play_third_quest(screen)
    print("Quest result:", result)

    pygame.quit()

asyncio.run(main())