# 🐭 2 Blind Mice

**2 Blind Mice** is a 2D pixel RPG game built with Python and Pygame.

You play as a mouse who wakes up in a dark world. Your mission is to explore, complete quests, and find pieces of cheese to slowly bring light back into the world.

Playable by running `python main.py` in a terminal.

---

## 🎮 Gameplay Goals

- 🧀 Find cheese to light up the world
- 🗣️ Talk to NPCs and complete quests to get cheese or tools
- 🌌 Navigate through darkness with limited vision
- 🔍 Discover hidden areas and secrets

---

## 🛠️ How to Run

1. **Install Python** (version 3.9 or above).
2. **Install Pygame** by running:
   ```bash
   pip install pygame

git clone https://github.com/kuwroo/TwoBlindMice.git
cd 2-blind-mice

python main.py

📁 Folder Structure
/project-root
│
├── main.py                 # Game runner
├── scenes.py               # Scene controller
├── player.py               # Player movement + light radius
├── npc.py                  # Interactions
├── quest.py                # Handles quests/cheese collection
├── dialogue.py             # Dialogue system (text box + cutscene handling)
├── misc.py                 # Misc helpers
├── assets/                 # Sprites, audio, etc.
│   ├── sprites/
│   ├── fonts/
│   └── sfx/

📌 Possible Improvements
Converting into a web game: Currently, this is a desktop game, but you could explore converting it into a web game in the future.

Release as a downloadable PC game: Consider releasing it on platforms like Itch.io or Steam.