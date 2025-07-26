import pygame
import asyncio
from scenes import *
from scene_manager import SceneManager
from misc import SCREEN_WIDTH, SCREEN_HEIGHT



async def main():
    pygame.init()
    screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT], pygame.SRCALPHA, 32)
    pygame.display.set_caption("2 Blind Mice")
    clock = pygame.time.Clock()
    
    # Create scene manager and start with title scene
    scene_manager = SceneManager()
    # from title 
    # entry_scene = Entry(screen)
    # #title_scene = TitleScene(screen)
    # scene_manager.switch_to(entry_scene)
    # from game
    game_scene = GameScene(screen) # Assuming GameScene is your main game scene
    scene_manager.switch_to(game_scene)

    
    running = True

    while running:
        # Handle all events first
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
                
            # Let current scene handle its specific events
            if scene_manager.current_scene:
                result = scene_manager.current_scene.handle_event(event)
                if result == "SWITCH_TO_GAME":
                    game_scene = GameScene(screen)
                    scene_manager.switch_to(game_scene)
        
        # Update current scene
        if scene_manager.current_scene:
            result = scene_manager.current_scene.update()
            if result == "SWITCH_TO_GAME":
                game_scene = GameScene(screen)
                scene_manager.switch_to(game_scene)
        
        # Draw current scene
        screen.fill((0, 0, 0))  # Clear screen each frame
        if scene_manager.current_scene:
            scene_manager.current_scene.draw(screen)
        
        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)
    
    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main())