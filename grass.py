from pico2d import load_image, load_music
import score


class Grass:
    def __init__(self, x=560, y=350):
        self.image = load_image(".\\data\\map.png")
        self.numbers_image = load_image(".\\data\\numbers.png")
        self.x = x
        self.y = y
        self.bgm = load_music(".\\data\\BGM.mp3")
        self.bgm.set_volume(32)
        self.bgm.repeat_play()

    def draw(self):
        self.image.draw(self.x, self.y)
        self.numbers_image.clip_draw(
            score.score[0] * 170, 0, 170, 200, 130, 560 - 28, 34, 40
        )

    def update(self):
        pass
