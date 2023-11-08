# 이것은 각 상태들을 객체로 구현한 것임.


from pico2d import (
    get_time,
    load_image,
    SDL_KEYDOWN,
    SDL_KEYUP,
    SDLK_SPACE,
    SDLK_LEFT,
    SDLK_RIGHT,
    delay,
)
from ball import Ball
import game_world
import game_framework

PIXEL_PER_METER = 10.0 / 0.3  # 10 pixel 30 cm
RUN_SPEED_KMPH = 20.0  # Km / Hour
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
    def enter(enemy, e):
        enemy.dir = 0

    @staticmethod
    def exit(enemy, e):
        pass

    @staticmethod
    def do(enemy):
        enemy.frame = (
            enemy.frame
            + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time
        ) % 10

    @staticmethod
    def draw(enemy):
        frame_width = 40

        frame_height = 40

        sheet_columns = 3

        sheet_rows = 4

        # 현재 프레임의 인덱스 계산

        frame_index = int(enemy.frame) % (sheet_columns * sheet_rows)

        # 현재 프레임의 x, y 좌표 계산

        frame_x = (frame_index % sheet_columns) * frame_width

        frame_y = (sheet_rows - 1 - frame_index // sheet_columns) * frame_height

        if enemy.face_dir <= 0:
            enemy.idleImage.clip_draw(
                frame_x, frame_y, frame_width, frame_height, enemy.x, enemy.y
            )

        else:
            enemy.idleImage.clip_composite_draw(
                frame_x,
                frame_y,
                frame_width,
                frame_height,
                0,
                "h",
                enemy.x,
                enemy.y,
                40,
                40,
            )


class Run:
    @staticmethod
    def enter(enemy, e):
        if right_down(e) or left_up(e):  # 오른쪽으로 RUN
            enemy.dir, enemy.face_dir = 1, 1

        elif left_down(e) or right_up(e):  # 왼쪽으로 RUN
            (
                enemy.dir,
                enemy.face_dir,
            ) = (
                -1,
                -1,
            )

        enemy.frame = 0

    @staticmethod
    def exit(enemy, e):
        pass

    @staticmethod
    def do(enemy):
        enemy.frame = (
            enemy.frame
            + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time
        ) % 10

        enemy.x += enemy.dir * RUN_SPEED_PPS * game_framework.frame_time
        if enemy.x < 25:
            enemy.x = 25
        elif enemy.x > 350 - 25:
            enemy.x = 350 - 25

    @staticmethod
    def draw(enemy):
        # 각 프레임의 크기와 스프라이트 시트의 가로 및 세로 줄 수

        frame_width = 40

        frame_height = 40

        sheet_columns = 3

        sheet_rows = 4

        # 현재 프레임의 인덱스 계산

        frame_index = int(enemy.frame) % (sheet_columns * sheet_rows)

        # 현재 프레임의 x, y 좌표 계산

        frame_x = (frame_index % sheet_columns) * frame_width

        frame_y = (sheet_rows - 1 - frame_index // sheet_columns) * frame_height

        # enemy.x와 enemy.y에 현재 프레임의 이미지를 출력

        if enemy.face_dir <= 0:
            enemy.runImage.clip_draw(
                int(frame_x), int(frame_y), frame_width, frame_height, enemy.x, enemy.y
            )

        else:
            enemy.runImage.clip_composite_draw(
                int(frame_x),
                int(frame_y),
                frame_width,
                frame_height,
                0,
                "h",
                enemy.x,
                enemy.y,
                40,
                40,
            )


class Serve:
    @staticmethod
    def enter(enemy, e):
        enemy.frame = 0

    @staticmethod
    def exit(enemy, e):
        global not_served
        not_served = False

    @staticmethod
    def do(enemy):
        enemy.frame = (
            enemy.frame
            + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time
        )

    @staticmethod
    def draw(enemy):
        # 각 프레임의 크기와 스프라이트 시트의 가로 및 세로 줄 수

        frame_width = 40

        frame_height = 40

        sheet_columns = 3

        sheet_rows = 4

        # 현재 프레임의 인덱스 계산

        frame_index = int(enemy.frame) % (sheet_columns * sheet_rows)

        # 현재 프레임의 x, y 좌표 계산

        frame_x = (frame_index % sheet_columns) * frame_width

        frame_y = (sheet_rows - 1 - frame_index // sheet_columns) * frame_height

        # enemy.x와 enemy.y에 현재 프레임의 이미지를 출력

        if enemy.face_dir <= 0:
            enemy.serveImage.clip_draw(
                frame_x, frame_y, frame_width, frame_height, enemy.x, enemy.y
            )

        else:
            enemy.serveImage.clip_composite_draw(
                frame_x,
                frame_y,
                frame_width,
                frame_height,
                0,
                "h",
                enemy.x,
                enemy.y,
                40,
                40,
            )

        if enemy.frame >= 11:
            enemy.fire_ball()

            enemy.state_machine.handle_event(("TIME_OUT", 0))


class Swing:
    @staticmethod
    def enter(enemy, e):
        global not_served
        if not_served:
            enemy.state_machine.handle_event(("UNSERVED", 0))
        enemy.frame = 0

    @staticmethod
    def exit(enemy, e):
        pass

    @staticmethod
    def do(enemy):
        enemy.frame = (
            enemy.frame
            + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time
        )

    @staticmethod
    def draw(enemy):
        frame_width = 40
        frame_height = 40
        sheet_columns = 3
        sheet_rows = 3
        frame_index = int(enemy.frame) % (sheet_columns * sheet_rows)
        frame_x = (frame_index % sheet_columns) * frame_width
        frame_y = (sheet_rows - 1 - frame_index // sheet_columns) * frame_height

        if enemy.face_dir <= 0:
            enemy.swingImage.clip_draw(
                frame_x, frame_y, frame_width, frame_height, enemy.x, enemy.y
            )

        else:
            enemy.swingImage.clip_composite_draw(
                frame_x,
                frame_y,
                frame_width,
                frame_height,
                0,
                "h",
                enemy.x,
                enemy.y,
                40,
                40,
            )

        if enemy.frame >= 6:
            enemy.state_machine.handle_event(("TIME_OUT", 0))


class Stop:
    @staticmethod
    def enter(enemy, e):
        enemy.frame = 0

    @staticmethod
    def exit(enemy, e):
        pass

    @staticmethod
    def do(enemy):
        enemy.frame = (
            enemy.frame
            + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time
        )

        enemy.x += (enemy.dir * RUN_SPEED_PPS * game_framework.frame_time) / 10

    @staticmethod
    def draw(enemy):
        # 각 프레임의 크기와 스프라이트 시트의 가로 및 세로 줄 수

        frame_width = 40

        frame_height = 40

        sheet_columns = 3

        sheet_rows = 3

        # 현재 프레임의 인덱스 계산

        frame_index = int(enemy.frame) % (sheet_columns * sheet_rows)

        # 현재 프레임의 x, y 좌표 계산

        frame_x = (frame_index % sheet_columns) * frame_width

        frame_y = (sheet_rows - 1 - frame_index // sheet_columns) * frame_height

        # enemy.x와 enemy.y에 현재 프레임의 이미지를 출력

        if enemy.face_dir <= 0:
            enemy.stopImage.clip_draw(
                frame_x, frame_y, frame_width, frame_height, enemy.x, enemy.y
            )

        else:
            enemy.stopImage.clip_composite_draw(
                frame_x,
                frame_y,
                frame_width,
                frame_height,
                0,
                "h",
                enemy.x,
                enemy.y,
                40,
                40,
            )

        if enemy.frame >= 7:
            enemy.state_machine.handle_event(("TIME_OUT", 0))


class StateMachine:
    def __init__(self, enemy):
        self.enemy = enemy

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
        self.cur_state.enter(self.enemy, ("NONE", 0))

    def update(self):
        self.cur_state.do(self.enemy)

    def handle_event(self, e):
        for check_event, next_state in self.transitions[self.cur_state].items():
            if check_event(e):
                self.cur_state.exit(self.enemy, e)

                self.cur_state = next_state

                self.cur_state.enter(self.enemy, e)

                return True

        return False

    def draw(self):
        self.cur_state.draw(self.enemy)


class Enemy:
    def __init__(self):
        self.x, self.y = 175, 440

        self.frame = 0
        self.not_served = True
        self.action = 3

        self.dir = 0

        self.face_dir = 1

        self.idleImage = load_image("enemy_idle.png")

        self.runImage = load_image("enemy_run.png")

        self.serveImage = load_image("enemy_serve.png")

        self.swingImage = load_image("enemy_swing.png")

        self.stopImage = load_image("enemy_stop.png")

        self.state_machine = StateMachine(self)

        self.state_machine.start()

    def update(self):
        self.state_machine.update()

    def handle_event(self, event):
        self.state_machine.handle_event(("INPUT", event))

    def draw(self):
        self.state_machine.draw()

    def fire_ball(self):
        ball = Ball(self.x, self.y - 10, -self.face_dir * 25, -200)

        game_world.add_object(ball, 0)
        
def ball_cheak_served(e):
    global not_served
    not_served = e

