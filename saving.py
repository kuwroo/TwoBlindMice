from scenes import *
import shelve

def save_game(self, filename="savefile"):
    with shelve.open(filename) as save:
        save["player_pos"] = self.player.rect.topleft
        save["cheese_count"] = self.cheese_count
        save["quest1_completed"] = self.quest1_completed
        save["quest2_completed"] = self.quest2_completed
        save["quest3_completed"] = self.quest3_completed
    print("Game saved.")

