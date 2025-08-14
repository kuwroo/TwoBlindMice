class SceneManager:
    def __init__(self):
        self.scene_stack = []  # Stack of scenes

    @property
    def current_scene(self):
        return self.scene_stack[-1] if self.scene_stack else None

    def switch_to(self, scene):
        """Replace current scene with a new one (clears stack)."""
        self.scene_stack = [scene]

    def push(self, scene):
        """Push a new scene on top of the stack."""
        self.scene_stack.append(scene)

    def pop(self):
        """Remove the top scene from the stack."""
        if self.scene_stack:
            self.scene_stack.pop()

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
