# Helper functions like fog, collision checks, and managing game state transitions.
import pygame

def update_fog(fog, player):
    # Here, we can use a simple circle to simulate the player's "vision"
    fog.fill((0, 0, 0, 180))  # Dark overlay (semi-transparent)
    pygame.draw.circle(fog, (0, 0, 0, 0), (player.x, player.y), 100)  # Clear area around the player

def draw_fog(screen, fog):
    screen.blit(fog, (0, 0))  # Draw the fog overlay on top of the screen

class GameState:
    def __init__(self):
        self.fog = pygame.Surface((800, 600), pygame.SRCALPHA)  # Transparent surface for fog
        self.completed_quests = 0

class QuestManager:
    def __init__(self):
        self.quests = [
            {"quest_id": 1, "completed": False, "description": "Find cheese from the snake!"}
        ]
    
    def update(self):
        for quest in self.quests:
            if quest["completed"]:
                print(f"Quest {quest['quest_id']} completed!")
            else:
                print(f"Quest {quest['quest_id']} active: {quest['description']}")
    
    def complete_quest(self, quest_id):
        for quest in self.quests:
            if quest["quest_id"] == quest_id:
                quest["completed"] = True
                break
