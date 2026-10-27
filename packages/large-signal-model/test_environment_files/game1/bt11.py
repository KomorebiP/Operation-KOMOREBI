from arcengine import ARCBaseGame, Camera, GameAction, Level, Sprite

sprites = {
    "bad": Sprite(pixels=[[8]], name="bad", visible=True, collidable=True),
    "good": Sprite(pixels=[[14]], name="good", visible=True, collidable=True),
}

levels = [
    Level(sprites=[], grid_size=(8, 8)),
    Level(sprites=[], grid_size=(16, 16)),
    Level(sprites=[], grid_size=(32, 32)),
    Level(sprites=[], grid_size=(40, 40)),
    Level(sprites=[], grid_size=(48, 48)),
]

BACKGROUND_COLOR = 5
PADDING_COLOR = 3


class Bt11(ARCBaseGame):
    _won: bool = True
    _depth: int = 0
    _position: int = 0

    def __init__(self) -> None:
        camera = Camera(background=BACKGROUND_COLOR, letter_box=PADDING_COLOR)
        super().__init__(game_id="bt11", levels=levels, camera=camera, available_actions=[3, 4])

    def step(self) -> None:
        if self.action.id == GameAction.ACTION3:
            if self._depth > 0:
                self._position -= 1
            sprite_name = "good" if self._won else "bad"
            self.current_level.add_sprite(sprites[sprite_name].clone().set_position(self._position, self._depth))
            self._depth += 1
        elif self.action.id == GameAction.ACTION4:
            self._position += 1
            self.current_level.add_sprite(sprites["bad"].clone().set_position(self._position, self._depth))
            self._won = False
            self._depth += 1

        if self._depth >= self.camera.width // 2:
            if self._won:
                self.next_level()
            else:
                self.lose()
        self.complete_action()

    def on_set_level(self, level: Level) -> None:
        self._won = True
        self._depth = 0
        self._position = self.camera.width // 2 - 1
