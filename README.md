# Two Blind Mice 

## Proposed Level of Achievement:
Apollo 11

## Motivation 
<!-- The reason behind starting the project -->
Two students who want to further their interest in coding by making a game as a summer passion project. The game name is a play on the meme “the blind leading the blind”, a humorous jab at how we live. The inspiration for the game takes root from the short attention spans of this generation, prioritizing short cooperative puzzles and intuitive gameplay.

## Aim 
<!-- The intended purpose of the game\ desired eefect on players -->

## User stories 
1. As a player, I want to play a game with nostalgic gentle art and game style.
2. As a player, I want to play a game that offers me a sense of escape from the stressful reality.
3. As a player, I want to play a game that I can pick up intuitively without needing to use too much brain power.
4. As a player, I want to play a game with an interesting yet not too complicated storyline.

## Scope of Project 
<!-- Boundaries of the project -- what will and wn't be included --> 
Two Blind Mice is a single-player RPG desktop game ran using Python and Pygame. It is set in a post-apocalyptic world with a 2D 32-bit retro pixel art style, where players aim to complete quests to fulfill and explore its storyline. 

Players can navigate through the levels using a simple mini map. The storyline gradually unfolds as players progress. In each grid-based level, players interact with specific tiles to unlock and complete quests.

Players gain Golden Cheese(method of counting experience points) upon completing quests for the first time. By gaining Golden Cheese, players can get closer to revealing the truth behind the storyline. 

2 Blind Mice's features are outlined in the following sections, organised by the following tags:

**[Proposed]** - features for Minimum Viable Product (MVP) by MS 1\
**[Current Progress]** - elaboration on current progress of specific feature\
**[Additional Features]** - Add-on features to improve product after MVP is completed. 

## Features 
> RPG Point-and-Click adventure game system

**[Proposed]**

Our proposed RPG Point-and-Click adventure game system is inspired by Doodle Champion Island Games and Refind Self: The Personality Test Game.

In the main game setting, players freely explore a world and complete quests in mini-games to collect Golden Cheese and progress with world-building. To access these quests, players interact with tiles in the form of items or characters. 

In the quests, players play minigames, which take inspiration from classic video games such as Pac-man, Street-fighter, Pong and Endless Falling. Upon completing each quest for the first time, players will be awarded with 1 Golden Cheese. These minigames are replayable, so players can revisit them whenever they want. 

**[Current Progress]**

Our proof-of-concept is built using a basic **Interaction system** with the first minigame implemented in the game. Players can navigate the open world using WASD and press E near interactables to trigger a quest. Upon completing the minigame, players then press E again to exit the minigame. The player movement chart is shown below. For Milestone 1, the basic UI elements for displaying collected Golden Cheese count has yet to be implemented. 

![image](https://github.com/user-attachments/assets/b70e762b-c6a1-4b61-ba41-a6c7a99c2c74)


**[Additional Features]**

1. Visibility progression as Golden Cheese are completed -- Visibility in terms of ability to identify objects further from them. Or could also be protrayed as the extent of explorability in the world, for eg. players are unable to enter certain places without completing a quest.
2. Animated cutscenes to set up and introduce the upcoming phase. Can be played between transitions in the game, eg. from the Start Menu to the Main game and from the Main game to the Minigame.

> Quest types

**[Proposed]**

For the MVP, 2 Blind Mice will have 1 minigame with simple win/loss conditions. Additional add-on minigames are also listed below. 

| Minigame | Description | 
| --- | :--- |
| Endless Freefall (MVP) | Players freefall down a certain distance and must reach the bottom without colliding into any obstacles |
| Avoid the Cat (Add-on) | Taking inspo from Pac-Man |
| Lengthy Snake (Add-on) | Taking inspo from the Snake Nokia phone game |
| Fight for the Cheese (Add-on) | Taking inspo from Street Fighters|

**[Current Progress]**

Currently, the minigame can be accessed by interacting with a specific tile in the world. However, the game graphics for the game have yet to be implemented, so the player and the objects are displayed as pixels.

**[Additional Features]**

## Timeline and Development Plan ## 
<!-- make table -->
## Milestone 1 – Technical Proof of Concept  
**Goal**: Build a minimal working system integrating core mechanics  
**Deadline**: 2 June

| Tasks                      | Description                                                                 | In-Charge | Date             |
|---------------------------|-----------------------------------------------------------------------------|-----------|------------------|
| Player Movement System    | WASD + arrow key controls, grid-based movement                             | Chloe     | 15 - 18 May      |
| Collision Detection       | Basic collision with world elements (walls, bins, etc.)                    | Chloe     | 18 - 20 May      |
| First Mini-game           | Implement first mini-game (e.g., cheese grab or trash sort)                | Jacelyn   | 20 - 26 May      |
| Integrate and Test        | Connect all systems together                                               | Chloe     | 26 May - 1 June  |

✅ **Milestone 1 Outcome (2 June):**  
- Navigable open world  
- Working movement + collisions  
- First mini-game with win/loss  

---

## Milestone 2 – Prototype  
**Goal**: Implement core gameplay features and flow, basic UI cheese count
**Deadline**: 30 June

| Tasks                          | Description                                                                       | In-Charge | Date             |
|-------------------------------|-----------------------------------------------------------------------------------|-----------|------------------|
| Add More Mini-games           | Avoid the Cat, Escape the Maze                                                    | Jacelyn   | 3 - 9 June       |
| UI cheese count               | Cheese counter at the top of the screen to track progress                         | Chloe     | 5 - 10 June      |
| Visibility Progression        | Implement light radius that increases with cheese                                 | Chloe     | 11 - 14 June     |
| Transition System             | Seamless movement between main world and mini-games                              | Chloe     | 15 - 19 June     |
| UI Improvements               | Pop-up prompts, cheese effects, game over/win screens                            | Jacelyn   | 20 - 25 June     |
| System Integration & Testing  | Playtesting, bug fixes, internal feedback                                         | Chloe + Jacelyn | 26 - 29 June |

✅ **Milestone 2 Outcome (30 June):**  
- Multiple working mini-games  
- Basic NPCs and door logic  
- Light grows as cheese is collected  
- Smooth transitions between zones and games  

---

## Milestone 3 – Extended System  
**Goal**: Expand with polish, replayability, and additional features  
**Deadline**: 28 July

| Tasks                             | Description                                                               | In-Charge | Date             |
|----------------------------------|---------------------------------------------------------------------------|-----------|------------------|
| Full Set of Mini-games           | Complete remaining games, allow replay                                    | Jacelyn   | 1 - 6 July       |
| Dynamic World Features           | Obstacles that move or unlock, hidden areas revealed by light             | Chloe     | 3 - 9 July       |
| SFX + Audio Integration          | Background music, sound cues for actions, mouse SFX                       | Jacelyn   | 10 - 13 July     |
| Polish and QA                    | Bug fixes, smoother transitions, UI polish                                | Chloe     | 14 - 20 July     |
| Final Integration & Balancing   | Connect all elements, balance difficulty                                  | Jacelyn + Chloe | 21 - 27 July |

✅ **Milestone 3 Outcome (28 July):**  
- All mini-games complete and replayable  
- Dynamic interactions in the world  
- Sound effects and music integrated  
- Polished and playable end-to-end build  

---

## Splashdown – Final Release  
**Goal**: MVP + Add-ons  
**Deadline**: 27 August

| Tasks                          | Description                                                             | In-Charge | Date             |
|--------------------------------|-------------------------------------------------------------------------|-----------|------------------|
| Advanced Enemy Behavior        | Smarter AI decision-making (if applicable)                              | Chloe     | 29 July - 5 Aug  |
| Mini-game & Character Expansions | Add new characters, cutscenes, game variations                          | Jacelyn   | 6 - 12 Aug       |
| Progression & Leveling System | Implement progression logic, pacing, difficulty scaling                 | Chloe     | 13 - 19 Aug      |
| Polish, Playtesting & UX      | Final playtests, user feedback, camera and UI polish                    | Jacelyn + Chloe | 20 - 26 Aug |

✅ **Splashdown (27 August):**  
- Full MVP with extra content  
- Final balancing and UX improvements  
- All core and additional features complete  


## Class Diagram ##
<!-- make picture diagrams -->


## Proof-of-Concept ##
<!-- make video -->
Github Repo:
https://github.com/kuwroo/TwoBlindMice.git
enter main.py, run the code. If it does not run, manually run it using "python3 [filelocation]/TwoBlindMice/main.py" depending on where you download it. For example "python3 /Users/chloe/Desktop/2blindmice/TwoBlindMice/main.py"

Video demonstration of gameplay:
https://youtu.be/U0KX2dnne00

## Work Log ##
<!-- spreadsheet to record how long we do work etc. -->
Refer to attached spreadsheet
https://docs.google.com/spreadsheets/d/1P33ckL-DrVosnxSF5SpMOJVcz_ajs3mXGDqgvIiaf3s/edit?usp=sharing



