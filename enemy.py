from pico2d import (
    get_time,
    load_image,
    SDL_KEYDOWN,
    SDL_KEYUP,
    SDLK_SPACE,
    SDLK_LEFT,
    SDLK_RIGHT,
    delay,
    load_wav,
)
from ball import Ball
import play_mode
import game_world
import game_framework
from behavior_tree import BehaviorTree, Action, Sequence, Condition, Selector
import random
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


def start_run(e):
    return e[0] == "start_run"


def stop_now(e):
    return e[0] == "stop_now"


def serve_now(e):
    return e[0] == "serve_now"


def swing_now(e):
    return e[0] == "swing_now"


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
        frame_index = int(enemy.frame) % (sheet_columns * sheet_rows)
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
        # if right_down(e) or left_up(e):
        #     enemy.dir, enemy.face_dir = 1, 1
        # elif left_down(e) or right_up(e):
        #     enemy.dir, enemy.face_dir = -1, -1
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
        frame_width = 40
        frame_height = 40
        sheet_columns = 3
        sheet_rows = 4
        frame_index = int(enemy.frame) % (sheet_columns * sheet_rows)
        frame_x = (frame_index % sheet_columns) * frame_width
        frame_y = (sheet_rows - 1 - frame_index // sheet_columns) * frame_height
        if enemy.dir <= 0:
            enemy.runImage.clip_draw(
                frame_x, frame_y, frame_width, frame_height, enemy.x, enemy.y
            )
        else:
            enemy.runImage.clip_composite_draw(
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


class Serve:
    @staticmethod
    def enter(enemy, e):
        enemy.frame = 0
        enemy.face_dir = -(enemy.x - score.player.x) / (abs(enemy.x - score.player.x))

    @staticmethod
    def exit(enemy, e):
        score.player_turn = True
        enemy.hit_sound.play()

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
        sheet_rows = 4
        frame_index = int(enemy.frame) % (sheet_columns * sheet_rows)
        frame_x = (frame_index % sheet_columns) * frame_width
        frame_y = (sheet_rows - 1 - frame_index // sheet_columns) * frame_height
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
        enemy.frame = 0
        enemy.face_dir = -(enemy.x - score.player.x) / (abs(enemy.x - score.player.x))

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
        pass

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
        frame_width = 40
        frame_height = 40
        sheet_columns = 3
        sheet_rows = 3
        frame_index = int(enemy.frame) % (sheet_columns * sheet_rows)
        frame_x = (frame_index % sheet_columns) * frame_width
        frame_y = (sheet_rows - 1 - frame_index // sheet_columns) * frame_height
        if enemy.dir <= 0:
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
                start_run: Run,
                # left_down: Run,
                swing_now: Swing,
                serve_now: Serve,
            },
            Run: {
                stop_now: Stop,
                # left_down: Stop,
                # right_up: Stop,
                # left_up: Stop,
                swing_now: Swing,
                serve_now: Serve,
            },
            Stop: {
                # start_run: Run,
                # left_down: Run,
                # left_up: Run,
                serve_now: Serve,
                time_out: Idle,
                swing_now: Swing,
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
    hit_sound = None

    def __init__(self):
        self.x, self.y = 175, 440
        self.frame = 0
        self.not_served = True
        self.action = 3
        self.dir = 0
        self.face_dir = 1
        self.turn = False
        self.idleImage = load_image(".\\data\\enemy_idle.png")
        self.runImage = load_image(".\\data\\enemy_run.png")
        self.serveImage = load_image(".\\data\\enemy_serve.png")
        self.swingImage = load_image(".\\data\\enemy_swing.png")
        self.stopImage = load_image(".\\data\\enemy_stop.png")
        self.state_machine = StateMachine(self)
        self.state_machine.start()
        self.build_behavior_tree()
        if not self.hit_sound:
            self.hit_sound = load_wav(".\\data\\swing_hit.wav")
            self.hit_sound.set_volume(32)

    def update(self):
        self.state_machine.update()
        self.bt.run()

    def handle_event(self, event):
        self.state_machine.handle_event(("INPUT", event))

    def draw(self):
        self.state_machine.draw()

    def fire_ball(self):
        score.ball = Ball(self.x, self.y - 10, self.face_dir * 25, -200)
        game_world.add_object(score.ball, 0)

    def get_bb(self):
        return self.x - 10, self.y - 10, self.x + 10, self.y + 20

    def handle_collision(self, group, other):
        match group:
            case "enemy:ball":
                if self.state_machine.cur_state == Swing and other.y_velocity > 0:
                    if other.x_velocity * -self.face_dir > 0:
                        other.x_velocity = -other.x_velocity
                    other.x_velocity += (other.x - self.x) * 5
                    other.y_velocity = -other.y_velocity
                    other.height = 0.5
                    other.height_velocity = 0.25
                    self.hit_sound.play()

    def set_target_location(self, x=None, y=None):
        if not x or not y:
            raise ValueError("Location should be given")
        self.tx, self.ty = x, y
        return BehaviorTree.SUCCESS

    def distance_less_than(self, x1, x2, r):
        distance2 = abs(x1 - x2)
        return distance2 < (PIXEL_PER_METER * r)

    def ball_distance(self, x1, y1, x2, y2, r):
        distance2 = (x1 - x2) ** 2 + (y1 - y2) ** 2
        return distance2 < (PIXEL_PER_METER * r) ** 2

    def set_random_location(self):
        self.tx = 150
        # self.tx, self.ty = 1000, 100
        return BehaviorTree.SUCCESS

    def move_to_ball(self):
        if (
            score.ball.y > self.y
            or (self.dir > 0 and self.ball_find(self.y) <= self.x + 3)
            or (self.dir < 0 and self.ball_find(self.y) >= self.x - 3)
        ):
            if (
                self.y - 30 < score.ball.y
                and score.ball.ground_hit_point > 65
                and score.ball.ground_hit_point < 283
            ):
                self.dir = -(self.x - score.player.x) / (abs(self.x - score.player.x))
                self.state_machine.handle_event(("swing_now", 0))
                return BehaviorTree.SUCCESS
            if (
                not self.state_machine.cur_state == Idle
                and not self.state_machine.cur_state == Stop
            ):
                print(self.state_machine.cur_state)
                self.state_machine.cur_state = Idle
            return BehaviorTree.SUCCESS
        if self.state_machine.cur_state == Idle:
            self.dir = -(self.x - self.ball_find(self.y)) // abs(
                self.x - self.ball_find(self.y)
            )
            self.state_machine.handle_event(("start_run", 0))
            return BehaviorTree.RUNNING

    def ball_find(self, y):
        return score.ball.x + score.ball.x_velocity * (
            (y - score.ball.y) / score.ball.y_velocity
        )

    def serve(self):
        if self.x < 100:
            self.move_to(100)
        elif self.x > 200:
            self.move_to(200)
        else:
            self.state_machine.handle_event(("serve_now", 0))

        return BehaviorTree.RUNNING

    def move_to(self, tx):
        if (self.dir > 0 and tx < self.x) or (self.dir < 0 and tx > self.x):
            self.state_machine.handle_event(("stop_now", 0))
            return BehaviorTree.SUCCESS
        else:
            if not self.state_machine.cur_state == Run:
                self.state_machine.handle_event(("start_run", 0))
            self.dir = -(self.x - tx) / (abs(self.x - tx))
            return BehaviorTree.RUNNING

    def serve_cheak(self):
        if score.ball.deleted or score.ball.y_velocity < 0:
            return BehaviorTree.FAIL
        else:
            return BehaviorTree.SUCCESS

    def cheak_turn(self):
        if score.player_turn:
            if (
                not self.state_machine.cur_state == Idle
                and not self.state_machine.cur_state == Stop
            ):
                self.state_machine.handle_event(("stop_now", 0))

            return BehaviorTree.FAIL
        else:
            return BehaviorTree.SUCCESS

    def stay(self):
        if not self.state_machine.cur_state == Idle:
            self.state_machine.handle_event(("stop_now", 0))
        return BehaviorTree.SUCCESS

    def build_behavior_tree(self):
        a0 = Action("대기", self.stay)
        # a2 = Action("Move to", self.move_to)
        root = SEQ_move_than_stay = Sequence("이동 후 대기", a0, a0)
        a3 = Action("Set random location", self.set_random_location)
        root = SEQ_random_move = Sequence("위치 설정 후 이동", a3, SEQ_move_than_stay)

        a1 = Action("서브하기", self.serve)

        root = SEQ_serve_and_move = Sequence("서브 후 이동", a1, SEQ_random_move)

        c1 = Condition("turn_cheaking", self.cheak_turn)
        root = SEQ_turn_cheak = Sequence("턴 체크 후 서브", c1, SEQ_serve_and_move)

        root = SEQ_random_move_and_serve = Sequence(
            "이동 후 서브", SEQ_random_move, SEQ_turn_cheak
        )

        a4 = Action("공 추적", self.move_to_ball)
        c2 = Condition("공 존재 확인", self.serve_cheak)

        SEQ_ball_chase = Sequence("공 확인 후 추적", c2, a4)
        root = SEL_chase_or_move = Selector(
            "공추적 또는 랜덤이동", SEQ_ball_chase, SEQ_random_move_and_serve
        )

        self.bt = BehaviorTree(root)
