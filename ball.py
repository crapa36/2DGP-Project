from pico2d import load_image
import game_world


class Ball:
    image = None
    shadowImage = None

    def __init__(self, x=400, y=300, velocity=1):
        if Ball.image is None:
            Ball.image = load_image("ball.png")
        if Ball.shadowImage is None:
            Ball.shadowImage = load_image("ballshadow.png")
        self.x, self.y, self.velocity = x, y, velocity
        self.frame, self.height = 0, 3

    def draw(self):
        frame_width = 5
        frame_height = 5
        sheet_columns = 2
        sheet_rows = 2
        # 현재 프레임의 인덱스 계산
        frame_index = self.frame % (sheet_columns * sheet_rows)

        # 현재 프레임의 x, y 좌표 계산
        frame_x = (frame_index % sheet_columns) * frame_width
        frame_y = (sheet_rows - 1 - frame_index // sheet_columns) * frame_height

        self.image.clip_draw(
            frame_x, frame_y, frame_width, frame_height, self.x, self.y
        )
        self.shadowImage.draw(self.x, self.y - self.height)

    def update(self):
        self.y += self.velocity
        self.frame = (self.frame + 1) % 4
        if self.y < 25 or self.y > 800 - 25:
            game_world.remove_object(self)