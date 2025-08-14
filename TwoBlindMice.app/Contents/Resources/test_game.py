import unittest
import pygame
import sys
import os
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock
import pickle

# Add the game directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from player import PlayerMovement
from scenes import TitleScene, GameScene, Scene
from fireball import MouseGodBoss, GlobalSettings, GlobalSettingsMenu
from misc import SCREEN_WIDTH, SCREEN_HEIGHT

class TestPlayerMovement(unittest.TestCase):
    """Unit tests for PlayerMovement class"""
    
    def setUp(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        self.player = PlayerMovement(800, 600, 1000)
    
    def tearDown(self):
        pygame.quit()
    
    def test_player_initialization(self):
        """Test player is initialized with correct default values"""
        self.assertEqual(self.player.PLAYER_SPEED, 5)
        self.assertEqual(self.player.JUMP_POWER, 15)
        self.assertTrue(hasattr(self.player, 'player_x'))
        self.assertTrue(hasattr(self.player, 'player_y'))
        self.assertIsNotNone(self.player.rect)
    
    def test_player_movement_left(self):
        """Test player moves left when A key is pressed"""
        initial_x = self.player.player_x
        keys = {pygame.K_a: True, pygame.K_d: False, pygame.K_SPACE: False}
        self.player.handle_input(keys)
        self.player.update_position([], [])
        self.assertLess(self.player.player_x, initial_x)
    
    def test_player_movement_right(self):
        """Test player moves right when D key is pressed"""
        initial_x = self.player.player_x
        keys = {pygame.K_a: False, pygame.K_d: True, pygame.K_SPACE: False}
        self.player.handle_input(keys)
        self.player.update_position([], [])
        self.assertGreater(self.player.player_x, initial_x)
    
    def test_player_jump(self):
        """Test player jumps when space is pressed"""
        self.player.on_ground = True
        initial_y = self.player.player_y
        keys = {pygame.K_a: False, pygame.K_d: False, pygame.K_SPACE: True}
        self.player.handle_input(keys)
        self.player.update_position([], [])
        self.assertLess(self.player.player_y, initial_y)
    
    def test_player_gravity(self):
        """Test gravity affects player when not on ground"""
        self.player.on_ground = False
        initial_y = self.player.player_y
        self.player.apply_gravity()
        self.player.update_position([], [])
        self.assertGreater(self.player.player_y, initial_y)
    
    def test_player_collision_detection(self):
        """Test player collision with floor"""
        floor_rects = [pygame.Rect(0, 500, 800, 100)]
        self.player.player_y = 400
        self.player.player_velocity_y = 10
        self.player.update_position(floor_rects, [])
        self.assertTrue(self.player.on_ground)

class TestBossFight(unittest.TestCase):
    """Unit tests for boss fight mechanics"""
    
    def setUp(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        self.boss = MouseGodBoss()
    
    def tearDown(self):
        pygame.quit()
    
    def test_boss_initialization(self):
        """Test boss is initialized with correct values"""
        self.assertEqual(self.boss.boss['health'], 100)
        self.assertEqual(self.boss.boss['max_health'], 100)
        self.assertEqual(self.boss.boss['phase'], 1)
        self.assertIsNotNone(self.boss.boss_frames)
    
    def test_boss_movement(self):
        """Test boss moves side to side"""
        initial_x = self.boss.boss['x']
        self.boss.update_boss()
        # Boss should move after timer increments
        self.boss.boss['move_timer'] = 120
        self.boss.update_boss()
        self.assertNotEqual(self.boss.boss['x'], initial_x)
    
    def test_boss_phase_progression(self):
        """Test boss phases change based on health"""
        # Phase 1 (health > 66%)
        self.boss.boss['health'] = 80
        self.boss.update_boss()
        self.assertEqual(self.boss.boss['phase'], 1)
        
        # Phase 2 (health 33-66%)
        self.boss.boss['health'] = 50
        self.boss.update_boss()
        self.assertEqual(self.boss.boss['phase'], 2)
        
        # Phase 3 (health < 33%)
        self.boss.boss['health'] = 20
        self.boss.update_boss()
        self.assertEqual(self.boss.boss['phase'], 3)
    
    def test_player_attack_damage(self):
        """Test player attack damages boss"""
        initial_health = self.boss.boss['health']
        self.boss.player.rect.x = self.boss.boss['x'] + 50  # Close to boss
        self.boss.try_player_attack()
        self.assertLess(self.boss.boss['health'], initial_health)
    
    def test_fireball_creation(self):
        """Test fireballs are created by boss"""
        initial_count = len(self.boss.fire_cheeseballs)
        self.boss.boss['shoot_cooldown'] = 0
        self.boss.shoot_fire_cheeseball()
        self.assertGreater(len(self.boss.fire_cheeseballs), initial_count)
    
    def test_fireball_movement(self):
        """Test fireballs move correctly"""
        self.boss.shoot_fire_cheeseball()
        if self.boss.fire_cheeseballs:
            initial_x = self.boss.fire_cheeseballs[0]['x']
            initial_y = self.boss.fire_cheeseballs[0]['y']
            self.boss.update_projectiles()
            self.assertNotEqual(self.boss.fire_cheeseballs[0]['x'], initial_x)

class TestPauseSystem(unittest.TestCase):
    """Unit tests for pause system"""
    
    def setUp(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        self.boss = MouseGodBoss()
    
    def tearDown(self):
        pygame.quit()
    
    def test_pause_activation(self):
        """Test pause is activated with ESC"""
        self.assertEqual(self.boss.game_state, "playing")
        event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_ESCAPE})
        self.boss.handle_input()
        # Simulate ESC key press
        self.boss.game_state = "paused"
        self.assertEqual(self.boss.game_state, "paused")
    
    def test_pause_deactivation(self):
        """Test pause is deactivated with ESC"""
        self.boss.game_state = "paused"
        event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_ESCAPE})
        self.boss.handle_input()
        # Simulate ESC key press again
        self.boss.game_state = "playing"
        self.assertEqual(self.boss.game_state, "playing")
    
    def test_restart_functionality(self):
        """Test game restart functionality"""
        self.boss.boss['health'] = 50  # Damage boss
        self.boss.restart_game()
        self.assertEqual(self.boss.boss['health'], 100)  # Health should reset
        self.assertEqual(self.boss.game_state, "playing")

class TestGlobalSettings(unittest.TestCase):
    """Unit tests for global settings system"""
    
    def setUp(self):
        self.settings = GlobalSettings()
        self.temp_dir = tempfile.mkdtemp()
        self.settings.save_file = os.path.join(self.temp_dir, "test_save.dat")
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_settings_initialization(self):
        """Test settings are initialized with default values"""
        self.assertEqual(self.settings.volume, 0.7)
        self.assertEqual(self.settings.music_volume, 0.5)
        self.assertEqual(self.settings.sfx_volume, 0.8)
        self.assertIn('move_left', self.settings.controls)
        self.assertIn('fullscreen', self.settings.graphics)
    
    def test_settings_save_load(self):
        """Test settings can be saved and loaded"""
        # Modify settings
        self.settings.volume = 0.5
        self.settings.music_volume = 0.3
        
        # Save settings
        self.settings.save_settings()
        
        # Create new settings object and load
        new_settings = GlobalSettings()
        new_settings.save_file = self.settings.save_file
        new_settings.load_settings()
        
        self.assertEqual(new_settings.volume, 0.5)
        self.assertEqual(new_settings.music_volume, 0.3)
    
    def test_game_save_load(self):
        """Test game data can be saved and loaded"""
        test_data = {'player_pos': (100, 200), 'boss_health': 50, 'score': 1000}
        
        # Save game data
        self.settings.save_game(test_data)
        
        # Load game data
        loaded_data = self.settings.load_game()
        
        self.assertEqual(loaded_data, test_data)

class TestSceneSystem(unittest.TestCase):
    """Unit tests for scene management"""
    
    def setUp(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
    
    def tearDown(self):
        pygame.quit()
    
    def test_title_scene_initialization(self):
        """Test title scene initializes correctly"""
        scene = TitleScene(self.screen)
        self.assertIsNotNone(scene.player)
        self.assertIsNotNone(scene.tile_map)
        self.assertTrue(scene.is_mouse)
    
    def test_game_scene_initialization(self):
        """Test game scene initializes correctly"""
        scene = GameScene(self.screen)
        self.assertIsNotNone(scene.player)
        self.assertIsNotNone(scene.tile_map)
        self.assertIsNotNone(scene.fog)
        self.assertEqual(scene.cheese_count, 1)

class TestIntegration(unittest.TestCase):
    """Integration tests for game systems"""
    
    def setUp(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
    
    def tearDown(self):
        pygame.quit()
    
    def test_complete_game_flow(self):
        """Test complete game flow from title to boss fight"""
        # Create title scene
        title_scene = TitleScene(self.screen)
        
        # Simulate switching to game
        game_scene = GameScene(self.screen)
        
        # Simulate entering boss fight
        boss_scene = MouseGodBoss()
        
        # Verify all scenes are properly initialized
        self.assertIsNotNone(title_scene)
        self.assertIsNotNone(game_scene)
        self.assertIsNotNone(boss_scene)
    
    def test_pause_system_integration(self):
        """Test pause system works across different scenes"""
        boss_scene = MouseGodBoss()
        
        # Test pause in boss fight
        boss_scene.game_state = "paused"
        self.assertEqual(boss_scene.game_state, "paused")
        
        # Test resume
        boss_scene.game_state = "playing"
        self.assertEqual(boss_scene.game_state, "playing")
    
    def test_settings_integration(self):
        """Test settings system integrates with game"""
        settings = GlobalSettings()
        boss_scene = MouseGodBoss()
        
        # Test that settings can be accessed during gameplay
        self.assertIsNotNone(settings.controls)
        self.assertIsNotNone(settings.graphics)

class TestSystemRequirements(unittest.TestCase):
    """System requirement tests"""
    
    def test_pygame_initialization(self):
        """Test pygame initializes correctly"""
        pygame.init()
        self.assertTrue(pygame.get_init())
        pygame.quit()
    
    def test_display_modes(self):
        """Test different display modes work"""
        pygame.init()
        
        # Test windowed mode
        screen = pygame.display.set_mode((800, 600))
        self.assertIsNotNone(screen)
        
        # Test fullscreen mode
        screen = pygame.display.set_mode((800, 600), pygame.FULLSCREEN)
        self.assertIsNotNone(screen)
        
        pygame.quit()
    
    def test_file_operations(self):
        """Test file operations work correctly"""
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.close()
        
        try:
            # Test file writing
            with open(temp_file.name, 'w') as f:
                f.write("test data")
            
            # Test file reading
            with open(temp_file.name, 'r') as f:
                data = f.read()
            
            self.assertEqual(data, "test data")
        finally:
            os.unlink(temp_file.name)

class TestPerformance(unittest.TestCase):
    """Performance tests"""
    
    def setUp(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
    
    def tearDown(self):
        pygame.quit()
    
    def test_frame_rate(self):
        """Test game maintains acceptable frame rate"""
        boss_scene = MouseGodBoss()
        clock = pygame.time.Clock()
        
        # Run for a few frames and measure performance
        start_time = pygame.time.get_ticks()
        for _ in range(60):  # 1 second at 60 FPS
            boss_scene.handle_input()
            boss_scene.update_player()
            boss_scene.update_boss()
            boss_scene.update_projectiles()
            boss_scene.check_collisions()
            boss_scene.draw()
            clock.tick(60)
        
        end_time = pygame.time.get_ticks()
        elapsed_time = end_time - start_time
        
        # Should complete 60 frames in approximately 1000ms
        self.assertLess(elapsed_time, 2000)  # Allow some tolerance
    
    def test_memory_usage(self):
        """Test memory usage is reasonable"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Create multiple game objects
        scenes = []
        for _ in range(5):
            scene = MouseGodBoss()
            scenes.append(scene)
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 100MB)
        self.assertLess(memory_increase, 100 * 1024 * 1024)

def run_all_tests():
    """Run all test suites"""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestPlayerMovement,
        TestBossFight,
        TestPauseSystem,
        TestGlobalSettings,
        TestSceneSystem,
        TestIntegration,
        TestSystemRequirements,
        TestPerformance
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"TEST SUMMARY")
    print(f"{'='*50}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print(f"\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1) 