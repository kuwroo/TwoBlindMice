class SceneManager:
    def __init__(self):
        self.current_scene = None
        
    def switch_to(self, scene):
        self.current_scene = scene
        
    def update(self):
        if self.current_scene:
            return self.current_scene.update()
        return None
            
    def draw(self, screen):
        if self.current_scene:
            self.current_scene.draw(screen)
            
    def handle_event(self, event):
        if self.current_scene:
            return self.current_scene.handle_event(event)
        return None