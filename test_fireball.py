import pygame
import sys
from player import PlayerMovement
from fireball import FireballQuest
from tilemap import TileMap
import pytmx


def test_fireball_quest():
    # Initialize Pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    
    # Create instances
    player = PlayerMovement(800, 600, 1600)
    quest = FireballQuest(player)
    tilemap = TileMap("resources/sewermap.tmx")
    
    floor_rects = []
    floor_layer = tilemap.tmx_data.get_layer_by_name('floor')
    if isinstance(floor_layer, pytmx.TiledTileLayer):
        for x, y, gid in floor_layer:
            if gid:  # If there's a tile here
                floor_rect = pygame.Rect(
                    x * tilemap.tmx_data.tilewidth,
                    y * tilemap.tmx_data.tileheight,
                    tilemap.tmx_data.tilewidth,
                    tilemap.tmx_data.tileheight
                )
                floor_rects.append(floor_rect)
     
    
    

    # Game loop
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Get keyboard input
        keys = pygame.key.get_pressed()
        
        # Update game state
        player.handle_input(keys)
        player.apply_gravity()
        player.update_position(floor_rects, [])  # Empty lists for floor/ladder rects
        player.update_animation(keys)
        quest.update()
        
        # Draw
        screen.fill((0, 0, 0))  # Black background
        tilemap.draw(screen, pygame.Vector2(0, 0))  # Draw tilemap first
        quest.draw(screen)
        player.draw(screen, keys, pygame.Vector2(0, 0))
        pygame.draw.rect(screen, (255, 0, 0), quest.boss.rect, 2)
        # Draw active fireballs hitboxes
        for fireball in quest.active_fireballs:
            pygame.draw.rect(screen, (255, 255, 0), fireball.rect, 2)
        
        
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    test_fireball_quest()