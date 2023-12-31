from pico2d import load_image, draw_rectangle, load_wav
import game_world
import game_framework
import score

TIME_PER_ACTION = 1
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = 20


class Ball:
    image = None
    shadowImage = None
    deleted = True
    scored_sound = None

    def __init__(self, x=400, y=300, x_velocity=1, y_velocity=1):
        if Ball.image is None:
            Ball.image = load_image(".\\data\\ball.png")
        if Ball.shadowImage is None:
            Ball.shadowImage = load_image(".\\data\\ball_shadow.png")
        self.x, self.y, self.x_velocity, self.y_velocity = x, y, x_velocity, y_velocity
        self.frame, self.height, self.height_velocity = 0, 0.5, 0.25
        self.ground_hit_point = None
        self.deleted = False
        game_world.add_collision_pair("player:ball", None, self)
        game_world.add_collision_pair("enemy:ball", None, self)
        if not Ball.scored_sound:
            Ball.scored_sound = load_wav(".\\data\\scored.wav")
            Ball.scored_sound.set_volume(16)

    def draw(self):
        frame_width = 10
        frame_height = 10
        sheet_columns = 2
        sheet_rows = 2
        frame_index = int(self.frame) % (sheet_columns * sheet_rows)
        frame_x = (frame_index % sheet_columns) * frame_width
        frame_y = (sheet_rows - 1 - frame_index // sheet_columns) * frame_height

        self.image.clip_draw(
            frame_x, frame_y, frame_width, frame_height, self.x, self.y + self.height
        )
        self.shadowImage.draw(self.x, self.y)
        self.height += self.height_velocity
        self.height_velocity -= 0.001
        if self.height < -2:
            self.ground_hit_point = self.x
            self.height_velocity = 0.25
        # draw_rectangle(*self.get_bb())

    def get_bb(self):
        return (
            self.x - 5,
            self.y - 5 + self.height,
            self.x + 5,
            self.y + 5 + self.height,
        )

    def handle_collision(self, group, other):
        pass

    def __getstate__(self):
        state = {
            "x": self.x,
            "y": self.y,
            "height": self.height,
            "height_velocity": self.height_velocity,
            "ground_hit_point": self.ground_hit_point,
            "x_velocity": self.x_velocity,
            "x_velocity": self.x_velocity,
        }
        return state

    def __setstate__(self, state):
        self.__init__()
        self.__dict__.update(state)

    def update(self):
        self.x += self.x_velocity * game_framework.frame_time
        self.y += self.y_velocity * game_framework.frame_time
        self.frame = (
            self.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time
        )
        if self.y < 20 or self.y > 560 - 70:
            game_world.remove_object(self)
            self.deleted = True
            self.scored_sound.play()
            if self.y < 20:
                if self.ground_hit_point > 65 and self.ground_hit_point < 283:
                    score.score[0] += 1
                    score.player_turn = True
                else:
                    score.score[1] += 1
                    score.player_turn = False
            else:
                if self.ground_hit_point > 65 and self.ground_hit_point < 283:
                    score.score[1] += 1
                    score.player_turn = False
                else:
                    score.score[0] += 1
                    score.player_turn = True
