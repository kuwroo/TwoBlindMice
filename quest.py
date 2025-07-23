import pygame
import random
from misc import SCREEN_WIDTH as WIDTH, SCREEN_HEIGHT as HEIGHT, TILE_SIZE
import sys
from collections import deque
from tilemap import TileMap
from spritesheet_loader import SpriteSheet
from colours import *
from spritesheet_loader import *

def play_first_quest():
    pygame.init()
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Rabbit-hole!")
    FPS = 60

    # Load TMX map
    tmx = TileMap("resources/quest1map.tmx")

    # Setup variables
    obstacles = []
    floor_tiles = []
    player = None  # Default to None in case spawn isn't found

    # Find spawn point from object layer
    for obj in tmx.interactables:
        obj_type = obj["type"].lower()
        rect = obj["rect"]
        if obj_type == "spawn":
            PLAYER_SIZE = 32
            player = pygame.Rect(rect.x, rect.y, PLAYER_SIZE, PLAYER_SIZE)

    if player is None:
        raise ValueError("No 'spawn' object found in TMX map. Cannot start quest.")

    # === LOAD FLOOR AND OBSTACLE TILES FROM LAYERS ===
    tilewidth = tmx.tmx_data.tilewidth
    tileheight = tmx.tmx_data.tileheight

    # Get floor tiles (pick the lowest one for landing logic)
    # Get floor tiles (now store all of them)
    floor_layer = tmx.tmx_data.get_layer_by_name("floor")
    for x, y, gid in floor_layer:
        if gid:
            rect = pygame.Rect(x * tilewidth, y * tileheight, tilewidth, tileheight)
            floor_tiles.append(rect)

    # Get obstacle tiles (touch = lose)
    obs_layer = tmx.tmx_data.get_layer_by_name("obs")
    for x, y, gid in obs_layer:
        if gid:
            rect = pygame.Rect(x * tilewidth, y * tileheight, tilewidth, tileheight)
            obstacles.append(rect)

    # Game loop vars
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

        # Movement logic — no walking through floor tile (not used currently but kept for consistency)
        def can_move(new_rect):
            for tile in floor_tiles:
                tile_shifted = tile.copy()
                tile_shifted.y -= camera_offset
                if new_rect.colliderect(tile_shifted):
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

        # Begin falling
        if not falling:
            # Check if no floor is under the player
            feet_rect = player.copy()
            feet_rect.y += 1  # One pixel below player
            on_platform = any(feet_rect.colliderect(tile) for tile in floor_tiles)
            if not on_platform:
                falling = True



        # Simulate falling by scrolling upward
        if falling and not on_floor:
            # Check collision with any floor tile
            player_feet = player.copy()
            player_feet.y += 1
            for tile in floor_tiles:
                if player_feet.colliderect(tile.move(0, -camera_offset)):
                    on_floor = True
                    print("You landed on the floor! Press E to win.")
                    break
            else:
                camera_offset += scroll_speed


        # --- DRAW EVERYTHING ---
        tmx.draw(win, pygame.Vector2(0, camera_offset))
        tmx.draw_texts(win, pygame.Vector2(0, camera_offset))

        win.blit(font.render("press SPACE to start", True, WHITE), (50, 50))

        # Check collision with obstacles
        for obs in obstacles:
            obs_screen = obs.copy()
            obs_screen.y -= camera_offset
            if player.colliderect(obs_screen):
                print("You hit an obstacle. Game over!")
                quest_result = "lose"
                run = False

        # Draw player
        pygame.draw.rect(win, PLAYER_COLOR, player)

        # Win condition
        if on_floor and keys[pygame.K_e]:
            print("You completed the quest!")
            quest_result = "win"
            run = False

        pygame.display.update()

    return quest_result


def play_second_quest():
    pygame.init()
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pac-Mouse!")

    WALL_COLOR = (0, 0, 255)
    DOT_COLOR = (255, 255, 255)
    PLAYER_COLOR = (255, 255, 0)
    GHOST1_COLOR = (255, 0, 0)
    GHOST2_COLOR = (255, 105, 180)

    maze = [
        "WWWWWWWWWWWWWWWWWWWWW",
        "W.......W....   .   W",
        "W.WWW .W. . WWW.    W",
        "W.W    W W    W.  . W",
        "W.W WW  G   WW W   WW",
        "W....    .   .....  W",
        "W. W  WWWWW WW   WW W",
        "W. W  W  W   W      W",
        "W.WW WWWWWW WW   WW W",
        "W..    ...   G....  W",
        "W.WW WWW WWW W W WW W",
        "W.W        W        W",
        "W.WWWWWWWWWW  WWWWW W",
        "W....        .....  W",
        "W    .........      W",
        "W    WWWW           W",
        "W      ........     W",
        "WWWWWWWWWWWWWWWWWWWWW"
    ]

    ROWS = len(maze)
    COLS = len(maze[0])
    maze_width = COLS * TILE_SIZE
    maze_height = ROWS * TILE_SIZE

    draw_offset_x = (WIDTH - maze_width) // 2  # 64
    draw_offset_y = (HEIGHT - maze_height) // 2  # 64

    walls = []
    points = []
    ghosts = []

    for y, row in enumerate(maze):
        for x, char in enumerate(row):
            px = draw_offset_x + x * TILE_SIZE
            py = draw_offset_y + y * TILE_SIZE

            if char == 'W':
                walls.append(pygame.Rect(px, py, TILE_SIZE, TILE_SIZE))
            elif char == '.':
                points.append(pygame.Rect(px + TILE_SIZE // 4, py + TILE_SIZE // 4, TILE_SIZE // 2, TILE_SIZE // 2))
            elif char == 'G':
                ghosts.append(pygame.Rect(px, py, TILE_SIZE, TILE_SIZE))

    player = pygame.Rect(draw_offset_x + TILE_SIZE, draw_offset_y + TILE_SIZE, TILE_SIZE, TILE_SIZE)

    ghost = ghosts[0] if len(ghosts) > 0 else pygame.Rect(draw_offset_x + (COLS - 2) * TILE_SIZE, draw_offset_y + (ROWS - 2) * TILE_SIZE, TILE_SIZE, TILE_SIZE)
    ghost2 = ghosts[1] if len(ghosts) > 1 else pygame.Rect(draw_offset_x + TILE_SIZE * (COLS - 3), draw_offset_y + TILE_SIZE, TILE_SIZE, TILE_SIZE)

    clock = pygame.time.Clock()
    run = True
    quest_result = None
    game_started = False
    ghost_move_timer = 0
    ghost_move_interval = 2

    def can_move(rect, ignore_ghost=None):
        # Check walls and screen bounds as before
        if rect.left < draw_offset_x or rect.right > draw_offset_x + maze_width:
            return False
        if rect.top < draw_offset_y or rect.bottom > draw_offset_y + maze_height:
            return False
        if any(rect.colliderect(w) for w in walls):
            return False
        # Prevent collision with the other ghost
        if ignore_ghost != ghost and rect.colliderect(ghost):
            return False
        if ignore_ghost != ghost2 and rect.colliderect(ghost2):
            return False
        return True

    def move(rect, dx, dy, ignore_ghost=None):
        new_rect = rect.move(dx * TILE_SIZE, dy * TILE_SIZE)
        if can_move(new_rect, ignore_ghost):
            rect.x = new_rect.x
            rect.y = new_rect.y


    def ghost_chase(ghost_rect, ignore_ghost=None):
        start = ((ghost_rect.x - draw_offset_x) // TILE_SIZE, (ghost_rect.y - draw_offset_y) // TILE_SIZE)
        goal = ((player.x - draw_offset_x) // TILE_SIZE, (player.y - draw_offset_y) // TILE_SIZE)
        queue = deque([(start, [])])
        visited = set()

        while queue:
            (x, y), path = queue.popleft()
            if (x, y) == goal:
                if path:
                    dx, dy = path[0]
                    move(ghost_rect, dx, dy, ignore_ghost)
                return
            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                nx, ny = x+dx, y+dy
                if 0 <= nx < COLS and 0 <= ny < ROWS and maze[ny][nx] != 'W' and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append(((nx, ny), path+[(dx, dy)]))


            while queue:
                (x, y), path = queue.popleft()
                if (x, y) == goal:
                    if path:
                        dx, dy = path[0]
                        move(ghost_rect, dx, dy)
                    return
                for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                    nx, ny = x+dx, y+dy
                    if 0 <= nx < COLS and 0 <= ny < ROWS and maze[ny][nx] != 'W' and (nx, ny) not in visited:
                        visited.add((nx, ny))
                        queue.append(((nx, ny), path+[(dx, dy)]))

            # If no path found, ghost does not move this turn (safe fallback)

    while run:
        clock.tick(8)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                quest_result = "quit"

        keys = pygame.key.get_pressed()
        if not game_started and keys[pygame.K_SPACE]:
            game_started = True

        if game_started:
            if keys[pygame.K_a]:
                move(player, -1, 0)
            if keys[pygame.K_d]:
                move(player, 1, 0)
            if keys[pygame.K_w]:
                move(player, 0, -1)
            if keys[pygame.K_s]:
                move(player, 0, 1)

            ghost_move_timer += 1
            if ghost_move_timer >= ghost_move_interval:
                ghost_chase(ghost, ignore_ghost=ghost)
                ghost_chase(ghost2, ignore_ghost=ghost2)

                ghost_move_timer = 0

            points = [p for p in points if not player.colliderect(p)]

            if not points:
                print("You Win!")
                quest_result = "win"
                run = False

            if player.colliderect(ghost):
                print("Caught by Ghost! You Lose.")
                quest_result = "lose"
                run = False

            if player.colliderect(ghost2):
                print("Caught by Second Ghost! You Lose.")
                quest_result = "lose"
                run = False

        win.fill((0, 0, 0))

        for wall in walls:
            pygame.draw.rect(win, WALL_COLOR, wall)
        for p in points:
            pygame.draw.rect(win, DOT_COLOR, p)

        pygame.draw.rect(win, PLAYER_COLOR, player)
        pygame.draw.rect(win, GHOST1_COLOR, ghost)
        pygame.draw.rect(win, GHOST2_COLOR, ghost2)

        pygame.display.update()

    return quest_result

def play_third_quest():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    pygame.display.set_caption("Stealth Heist")
    FPS = 60

    tmx = TileMap("resources/mazemap.tmx")

    player = None
    exit_rects = []
    walls = []
    npcs = []

    for obj in tmx.interactables:
        if obj["type"].lower() == "wall":
            walls.append(obj["rect"])
        elif obj["type"].lower() == "spawn":
            PLAYER_SIZE = 32  # or any value you want
            player = pygame.Rect(obj["rect"].x, obj["rect"].y, PLAYER_SIZE, PLAYER_SIZE)
        elif obj["type"].lower() == "exit":
            exit_rects.append(obj["rect"])
        elif obj["type"].lower() == "npc":
            print("Raw NPC object:", obj)  # <-- Add this line
            props = obj.get("properties", {})
            patrol_tiles = int(props.get("patrol_length", props.get("patrol length", 1)))
            direction = props.get("direction", "horizontal").lower()
            start_dir = props.get("start_direction", "right").lower()

            print(f"NPC {obj.get('name', f'npc{len(npcs)+1}')}: direction={direction}, patrol_range={patrol_tiles}, start_direction={start_dir}")

            npc = {
                "name": obj.get("name", f"npc{len(npcs)+1}"),
                "rect": pygame.Rect(obj["rect"].x, obj["rect"].y, TILE_SIZE, TILE_SIZE),
                "origin": (obj["rect"].x, obj["rect"].y),
                "axis": direction,
                "direction": 1 if start_dir in ("right", "down") else -1,
                "patrol_range": patrol_tiles * TILE_SIZE,
                "speed": 1,
                "start_direction": start_dir
            }
            npcs.append(npc)

    print("Walls loaded:", walls)
    print("Player spawn:", player)
    print("Exits loaded:", exit_rects)
    print("NPCs loaded:", npcs)

    for i, npc in enumerate(npcs):
        print(f"{npc['name']}: pos={npc['rect'].topleft}, axis={npc['axis']}, patrol_range={npc['patrol_range']}, direction={npc['direction']}")

    def move_player(rect, dx, dy):
        next_rect = rect.move(dx, dy)
        if not any(next_rect.colliderect(w) for w in walls):
            rect.x += dx
            rect.y += dy

    def update_player():
        keys = pygame.key.get_pressed()
        dx = dy = 0
        if keys[pygame.K_a]: dx = -TILE_SIZE // 6
        if keys[pygame.K_d]: dx = TILE_SIZE // 6
        if keys[pygame.K_w]: dy = -TILE_SIZE // 6
        if keys[pygame.K_s]: dy = TILE_SIZE // 6
        if dx or dy:
            move_player(player, dx, dy)

    def is_wall_blocking(npc_rect, player_rect, axis):
        # Use center points for raycast
        start = npc_rect.center
        end = player_rect.center

        # Number of steps for the ray (higher = more accurate)
        steps = int(max(abs(end[0] - start[0]), abs(end[1] - start[1])) // 4)
        if steps == 0:
            return False  # Same position

        for i in range(steps + 1):
            t = i / steps
            x = int(start[0] + (end[0] - start[0]) * t)
            y = int(start[1] + (end[1] - start[1]) * t)
            point_rect = pygame.Rect(x, y, 4, 4)  # Small box for collision
            if any(point_rect.colliderect(w) for w in walls):
                return True  # Wall blocks vision
        return False  # No wall blocks vision

    def npc_vision_rect(npc):
        rect = npc["rect"]
        direction = npc["direction"]
        length = TILE_SIZE * 5  # Vision length (how far the NPC can see)
        width = TILE_SIZE       # Vision width (same as NPC width)
        if npc["axis"] == "horizontal":
            x = rect.right if direction > 0 else rect.left - length
            return pygame.Rect(x, rect.centery - width // 2, length, width)
        else:
            y = rect.bottom if direction > 0 else rect.top - length
            return pygame.Rect(rect.centerx - width // 2, y, width, length)

    def update_npcs():
        for npc in npcs:
            rect = npc["rect"]
            axis = npc["axis"]
            speed = npc["speed"]
            dir = npc["direction"]
            ox, oy = npc["origin"]

            if axis == "horizontal":
                rect.x += dir * speed
                if abs(rect.x - ox) >= npc["patrol_range"]:
                    npc["direction"] *= -1
            else:
                rect.y += dir * speed
                if abs(rect.y - oy) >= npc["patrol_range"]:
                    npc["direction"] *= -1

            vis = npc_vision_rect(npc)
            if vis.colliderect(player) and not is_wall_blocking(rect, player, "x" if axis == "horizontal" else "y"):
                print(f"{npc['rect']} spotted the player!")
                return "lose"
        return None

    def draw():
        screen.fill(BLACK)
        # Draw all tile layers from the map
        tmx.draw(screen, pygame.Vector2(0, 0))

        # Draw player
        pygame.draw.rect(screen, WHITE, player)

        # Draw NPCs and their vision
        for npc in npcs:
            pygame.draw.rect(screen, RED, npc["rect"])
            pygame.draw.rect(screen, MAGENTA, npc_vision_rect(npc), 2)

        # Draw any map texts
        tmx.draw_texts(screen, pygame.Vector2(0, 0))
        pygame.display.flip()

    # Game loop
    result = None
    running = True
    while running:
        dt = clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        update_player()
        npc_result = update_npcs()
        if npc_result == "lose":
            result = "lose"
            break
        if any(player.colliderect(exit_rect) for exit_rect in exit_rects):
            result = "win"
            break
        draw()

    pygame.quit()
    return result

