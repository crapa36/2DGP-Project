from pico2d import (
    get_time,
    load_image,
    SDL_KEYDOWN,
    SDL_KEYUP,
    SDLK_SPACE,
    SDLK_LEFT,
    SDLK_RIGHT,
    delay,
    draw_rectangle,
    load_wav,
)
from ball import Ball
import game_world
import game_framework
import score

PIXEL_PER_METER = 10.0 / 0.3  # 10 pixel 30 cm
RUN_SPEED_KMPH = 10.0  # Km / Hour
RUN_SPEED_MPM = RUN_SPEED_KMPH * 1000.0 / 60.0
RUN_SPEED_MPS = RUN_SPEED_MPM / 60.0
RUN_SPEED_PPS = RUN_SPEED_MPS * PIXEL_PER_METER
TIME_PER_ACTION = 1
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = 20
not_served = True


def right_down(e):
    return e[0] == "INPUT" and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_RIGHT


def right_up(e):
    return e[0] == "INPUT" and e[1].type == SDL_KEYUP and e[1].key == SDLK_RIGHT


def left_down(e):
    return e[0] == "INPUT" and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_LEFT


def left_up(e):
    return e[0] == "INPUT" and e[1].type == SDL_KEYUP and e[1].key == SDLK_LEFT


def space_down(e):
    return e[0] == "INPUT" and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_SPACE


def time_out(e):
    return e[0] == "TIME_OUT"


def unserved(e):
    return e[0] == "UNSERVED"


class Idle:
    @staticmethod
    def enter(player, e):
        player.dir = 0

    @staticmethod
    def exit(player, e):
        pass

    @staticmethod
    def do(player):
        player.frame = (
            player.frame
            + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time
        ) % 10

    @staticmethod
    def draw(player):
        frame_width = 40
        frame_height = 40
        sheet_columns = 4
        sheet_rows = 3
        frame_index = int(player.frame) % (sheet_columns * sheet_rows)
        frame_x = (frame_index % sheet_columns) * frame_width
        frame_y = (sheet_rows - 1 - frame_index // sheet_columns) * frame_height
        if player.face_dir <= 0:
            player.idleImage.clip_draw(
                frame_x, frame_y, frame_width, frame_height, player.x, player.y
            )
        else:
            player.idleImage.clip_composite_draw(
                frame_x,
                frame_y,
                frame_width,
                frame_height,
                0,
                "h",
                player.x,
                player.y,
                40,
                40,
            )


class Run:
    @staticmethod
    def enter(player, e):
        if right_down(e) or left_up(e):
            player.dir, player.face_dir = 1, 1
        elif left_down(e) or right_up(e):
            player.dir, player.face_dir = -1, -1
        player.frame = 0

    @staticmethod
    def exit(player, e):
        pass

    @staticmethod
    def do(player):
        player.frame = (
            player.frame
            + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time
        ) % 7
        player.x += player.dir * RUN_SPEED_PPS * game_framework.frame_time
        if player.x < 25:
            player.x = 25
        elif player.x > 350 - 25:
            player.x = 350 - 25

    @staticmethod
    def draw(player):
        frame_width = 40
        frame_height = 40
        sheet_columns = 4
        sheet_rows = 2
        frame_index = int(player.frame) % (sheet_columns * sheet_rows)
        frame_x = (frame_index % sheet_columns) * frame_width
        frame_y = (sheet_rows - 1 - frame_index // sheet_columns) * frame_height
        if player.face_dir <= 0:
            player.runImage.clip_draw(
                frame_x, frame_y, frame_width, frame_height, player.x, player.y
            )
        else:
            player.runImage.clip_composite_draw(
                frame_x,
                frame_y,
                frame_width,
                frame_height,
                0,
                "h",
                player.x,
                player.y,
                40,
                40,
            )


class Serve:
    @staticmethod
    def enter(player, e):
        player.frame = 0

    @staticmethod
    def exit(player, e):
        player.hit_sound.play()

    @staticmethod
    def do(player):
        player.frame = (
            player.frame
            + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time
        )

    @staticmethod
    def draw(player):
        frame_width = 40
        frame_height = 60
        sheet_columns = 4
        sheet_rows = 3
        frame_index = int(player.frame) % (sheet_columns * sheet_rows)
        frame_x = (frame_index % sheet_columns) * frame_width
        frame_y = (sheet_rows - 1 - frame_index // sheet_columns) * frame_height
        if player.face_dir <= 0:
            player.serveImage.clip_draw(
                frame_x, frame_y, frame_width, frame_height, player.x, player.y
            )
        else:
            player.serveImage.clip_composite_draw(
                frame_x,
                frame_y,
                frame_width,
                frame_height,
                0,
                "h",
                player.x,
                player.y,
                40,
                60,
            )
        if player.frame >= 11:
            player.fire_ball(player.face_dir * 25, 200)
            player.state_machine.handle_event(("TIME_OUT", 0))


class Swing:
    @staticmethod
    def enter(player, e):
        if score.ball.deleted and score.player_turn:
            player.state_machine.handle_event(("UNSERVED", 0))

        player.frame = 0

    @staticmethod
    def exit(player, e):
        pass

    @staticmethod
    def do(player):
        player.frame = (
            player.frame
            + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time
        )

    @staticmethod
    def draw(player):
        frame_width = 40
        frame_height = 40
        sheet_columns = 4
        sheet_rows = 2
        frame_index = int(player.frame) % (sheet_columns * sheet_rows)
        frame_x = (frame_index % sheet_columns) * frame_width
        frame_y = (sheet_rows - 1 - frame_index // sheet_columns) * frame_height
        if player.face_dir <= 0:
            player.swingImage.clip_draw(
                frame_x, frame_y, frame_width, frame_height, player.x, player.y
            )
        else:
            player.swingImage.clip_composite_draw(
                frame_x,
                frame_y,
                frame_width,
                frame_height,
                0,
                "h",
                player.x,
                player.y,
                40,
                40,
            )
        if player.frame >= 5:
            player.state_machine.handle_event(("TIME_OUT", 0))


class Stop:
    @staticmethod
    def enter(player, e):
        player.frame = 0

    @staticmethod
    def exit(player, e):
        pass

    @staticmethod
    def do(player):
        player.frame = (
            player.frame
            + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time
        )
        player.x += (player.dir * RUN_SPEED_PPS * game_framework.frame_time) / 10

    @staticmethod
    def draw(player):
        frame_width = 40
        frame_height = 40
        sheet_columns = 3
        sheet_rows = 4
        frame_index = int(player.frame) % (sheet_columns * sheet_rows)
        frame_x = (frame_index % sheet_columns) * frame_width
        frame_y = (sheet_rows - 1 - frame_index // sheet_columns) * frame_height
        if player.face_dir <= 0:
            player.stopImage.clip_draw(
                frame_x, frame_y, frame_width, frame_height, player.x, player.y
            )
        else:
            player.stopImage.clip_composite_draw(
                frame_x,
                frame_y,
                frame_width,
                frame_height,
                0,
                "h",
                player.x,
                player.y,
                40,
                40,
            )
        if player.frame >= 10:
            player.state_machine.handle_event(("TIME_OUT", 0))


class StateMachine:
    def __init__(self, player):
        self.player = player
        self.cur_state = Idle
        self.transitions = {
            Idle: {
                right_down: Run,
                left_down: Run,
                space_down: Swing,
            },
            Run: {
                right_down: Stop,
                left_down: Stop,
                right_up: Stop,
                left_up: Stop,
                space_down: Swing,
            },
            Stop: {
                right_down: Run,
                left_down: Run,
                left_up: Run,
                right_up: Run,
                time_out: Idle,
                space_down: Swing,
            },
            Serve: {time_out: Idle},
            Swing: {
                time_out: Idle,
                unserved: Serve,
            },
        }

    def start(self):
        self.cur_state.enter(self.player, ("NONE", 0))

    def update(self):
        self.cur_state.do(self.player)

    def handle_event(self, e):
        for check_event, next_state in self.transitions[self.cur_state].items():
            if check_event(e):
                self.cur_state.exit(self.player, e)
                self.cur_state = next_state
                self.cur_state.enter(self.player, e)
                return True
        return False

    def draw(self):
        self.cur_state.draw(self.player)


class Player:
    hit_sound = None

    def __init__(self):
        self.x, self.y = 175, 120
        self.frame = 0
        self.dir = 0
        self.face_dir = 1
        self.idleImage = load_image(".\data\player_idle.png")
        self.runImage = load_image(".\data\player_run.png")
        self.serveImage = load_image(".\data\player_serve.png")
        self.swingImage = load_image(".\data\player_swing.png")
        self.stopImage = load_image(".\data\player_stop.png")
        self.state_machine = StateMachine(self)
        self.state_machine.start()
        if not self.hit_sound:
            self.hit_sound = load_wav(".\\data\\swing_hit.wav")
            self.hit_sound.set_volume(32)

    def update(self):
        self.state_machine.update()

    def handle_event(self, event):
        self.state_machine.handle_event(("INPUT", event))

    def draw(self):
        self.state_machine.draw()
        # draw_rectangle(*self.get_bb())

    def fire_ball(self, x_velocity, y_velocity):
        score.ball = Ball(self.x, self.y + 10, x_velocity, y_velocity)
        game_world.add_object(score.ball, 0)

    def get_bb(self):
        return self.x - 10, self.y - 15, self.x + 10, self.y + 10

    def handle_collision(self, group, other):
        match group:
            case "player:ball":
                if self.state_machine.cur_state == Swing and other.y_velocity < 0:
                    if other.x_velocity * self.face_dir < 0:
                        other.x_velocity = -other.x_velocity
                    other.x_velocity += (other.x - self.x) * 5
                    other.y_velocity = -other.y_velocity
                    other.height = 0.5
                    other.height_velocity = 0.25
                    self.hit_sound.play()
                    self.hit_sound.set_volume(32)
