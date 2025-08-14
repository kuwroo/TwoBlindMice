import pickle
import os
from typing import Dict, Any

class SaveManager:
    def __init__(self, save_file_path: str = "game_save.pkl"):
        """Initialize the save manager with a default save file path."""
        self.save_file_path = save_file_path
        self.current_state = {
            "game_state": {},
            "quest_completions": {},
            "cheese_count": 0
        }

    def save_game(self, game_state: Dict[str, Any], quest_completions: Dict[str, bool], cheese_count: int) -> bool:
        """Save the current game progress to a file."""
        try:
            self.current_state = {
                "game_state": game_state,
                "quest_completions": quest_completions,
                "cheese_count": cheese_count
            }
            
            with open(self.save_file_path, 'wb') as save_file:
                pickle.dump(self.current_state, save_file)
            return True
        except Exception as e:
            print(f"Error saving game: {e}")
            return False

    def load_game(self) -> Dict[str, Any]:
        """Load the saved game progress from file."""
        try:
            if os.path.exists(self.save_file_path):
                with open(self.save_file_path, 'rb') as save_file:
                    self.current_state = pickle.load(save_file)
            return self.current_state
        except Exception as e:
            print(f"Error loading game: {e}")
            return self.current_state

    def delete_save(self) -> bool:
        """Delete the save file."""
        try:
            if os.path.exists(self.save_file_path):
                os.remove(self.save_file_path)
            return True
        except Exception as e:
            print(f"Error deleting save file: {e}")
            return False

    def has_save_file(self) -> bool:
        """Check if a save file exists."""
        return os.path.exists(self.save_file_path)