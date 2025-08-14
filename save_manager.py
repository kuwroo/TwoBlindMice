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
            "cheese_count": 0,
            "scene_states": {}  # Add scene states storage
        }

    def save_game(self, game_state: Dict[str, Any], quest_completions: Dict[str, bool], cheese_count: int, scene_states: Dict[str, Any] = None) -> bool:
        """Save the current game progress to a file."""
        try:
            self.current_state = {
                "game_state": game_state,
                "quest_completions": quest_completions,
                "cheese_count": cheese_count,
                "scene_states": scene_states or {}
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

    def save_scene_state(self, scene_name: str, scene_state: Dict[str, Any]) -> bool:
        """Save a specific scene's state"""
        try:
            self.current_state["scene_states"][scene_name] = scene_state
            return self.save_game(
                self.current_state["game_state"],
                self.current_state["quest_completions"],
                self.current_state["cheese_count"],
                self.current_state["scene_states"]
            )
        except Exception as e:
            print(f"Error saving scene state: {e}")
            return False

    def load_scene_state(self, scene_name: str) -> Dict[str, Any]:
        """Load a specific scene's state"""
        try:
            return self.current_state.get("scene_states", {}).get(scene_name, {})
        except Exception as e:
            print(f"Error loading scene state: {e}")
            return {}