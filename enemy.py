from pico2d import get_time, load_image, SDL_KEYDOWN, SDL_KEYUP, SDLK_SPACE, SDLK_LEFT, SDLK_RIGHT, delay
from ball import Ball
import play_mode
import game_world
import game_framework
from behavior_tree import BehaviorTree, Action, Sequence, Condition, Selector
import random
import score

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
        enemy.frame = (enemy.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % 10

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
            enemy.idleImage.clip_draw(frame_x, frame_y, frame_width, frame_height, enemy.x, enemy.y)
        else:
            enemy.idleImage.clip_composite_draw(frame_x, frame_y, frame_width, frame_height, 0, "h", enemy.x, enemy.y, 40, 40)

class Run:
    @staticmethod
    def enter(enemy, e):
        if right_down(e) or left_up(e):
            enemy.dir, enemy.face_dir = 1, 1
        elif left_down(e) or right_up(e):
            enemy.dir, enemy.face_dir = -1, -1
        enemy.frame = 0

    @staticmethod
    def exit(enemy, e):
        pass

    @staticmethod
    def do(enemy):
        enemy.frame = (enemy.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % 10
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
        if enemy.face_dir <= 0:
            enemy.runImage.clip_draw(frame_x, frame_y, frame_width, frame_height, enemy.x, enemy.y)
        else:
            enemy.runImage.clip_composite_draw(frame_x, frame_y, frame_width, frame_height, 0, "h", enemy.x, enemy.y, 40, 40)

class Serve:
    @staticmethod
    def enter(enemy, e):
        enemy.frame = 0

    @staticmethod
    def exit(enemy, e):
        pass

    @staticmethod
    def do(enemy):
        enemy.frame = (enemy.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time)

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
            enemy.serveImage.clip_draw(frame_x, frame_y, frame_width, frame_height, enemy.x, enemy.y)
        else:
            enemy.serveImage.clip_composite_draw(frame_x, frame_y, frame_width, frame_height, 0, "h", enemy.x, enemy.y, 40, 40)
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
        enemy.frame = (enemy.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time)

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
            enemy.swingImage.clip_draw(frame_x, frame_y, frame_width, frame_height, enemy.x, enemy.y)
        else:
            enemy.swingImage.clip_composite_draw(frame_x, frame_y, frame_width, frame_height, 0, "h", enemy.x, enemy.y, 40, 40)
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
        enemy.frame = (enemy.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time)
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
        if enemy.face_dir <= 0:
            enemy.stopImage.clip_draw(frame_x, frame_y, frame_width, frame_height, enemy.x, enemy.y)
        else:
            enemy.stopImage.clip_composite_draw(frame_x, frame_y, frame_width, frame_height, 0, "h", enemy.x, enemy.y, 40, 40)
        if enemy.frame >= 7:
            enemy.state_machine.handle_event(("TIME_OUT", 0))

class StateMachine:
    def __init__(self, enemy):
        self.enemy = enemy
        self.cur_state = Idle
        self.transitions = {
            Idle: {
                # right_down: Run,
                # left_down: Run,
                # space_down: Swing,
            },
            Run: {
                # right_down: Stop,
                # left_down: Stop,
                # right_up: Stop,
                # left_up: Stop,
                # space_down: Swing,
            },
            Stop: {
                # right_down: Run,
                # left_down: Run,
                # left_up: Run,
                # right_up: Run,
                time_out: Idle,
                # space_down: Swing,
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
        self.turn=False
        self.idleImage = load_image("enemy_idle.png")
        self.runImage = load_image("enemy_run.png")
        self.serveImage = load_image("enemy_serve.png")
        self.swingImage = load_image("enemy_swing.png")
        self.stopImage = load_image("enemy_stop.png")
        self.state_machine = StateMachine(self)
        self.state_machine.start()
        
        self.build_behavior_tree()

    def update(self):
        self.state_machine.update()

    def handle_event(self, event):
        self.state_machine.handle_event(("INPUT", event))

    def draw(self):
        self.state_machine.draw()

    def fire_ball(self):
        score.ball = Ball(self.x, self.y - 10, -self.face_dir * 25, -200)
        game_world.add_object(score.ball, 0)
        
    def set_target_location(self, x=None, y=None):
        if not x or not y:
            raise ValueError('Location should be given')
        self.tx, self.ty = x, y
        return BehaviorTree.SUCCESS
    
    def set_random_location(self):
        self.tx = random.randint(100, 250)
        # self.tx, self.ty = 1000, 100
        return BehaviorTree.SUCCESS

    def move_to_ball(self, r=0.5):
        self.state = 'Run'
        self.move_slightly_to(play_mode.ball.x, play_mode.ball.y)
        if self.distance_less_than(play_mode.ball.x, play_mode.ball.y, self.x, self.y, r):
            return BehaviorTree.SUCCESS
        else:
            return BehaviorTree.RUNNING
        
    def distance_less_than(self, x1, y1, x2, y2, r):
        distance2 = (x1 - x2) ** 2 + (y1 - y2) ** 2
        return distance2 < (PIXEL_PER_METER * r) ** 2

    def move_slightly_to(self, tx):
        self.dir = (self.x-tx)/(abs(self.x-tx))
        self.speed = RUN_SPEED_PPS
        self.x += self.speed * self.dir * game_framework.frame_time

    def serve(self):
        self.state = 'Serve'
        return BehaviorTree.SUCCESS
        
    def move_to(self, r=0.5):
        self.state = 'Walk'
        self.move_slightly_to(self.tx, self.ty)
        if self.distance_less_than(self.tx, self.ty, self.x, self.y, r):
            return BehaviorTree.SUCCESS
        else:
            return BehaviorTree.RUNNING
        
    def serve_cheak():
        if not_served:
            return BehaviorTree.SUCCESS
        else:
            return BehaviorTree.FAIL
        
        
    def build_behavior_tree(self):
        a1= Action('서브하기', self.serve)
        c1 = Condition('turn_cheak', self.cheak_turn)
        root = SEQ_turn_cheak = Sequence('턴 체크 후 서브', c1, a2)     
        
        a2 = Action('Move to', self.move_to)
        a3 = Action('Set random location', self.set_random_location)
        root = SEQ_random_move = Sequence('위치 설정 후 이동', a3, a2)
        
        root = SEQ_random_move_and_serve = Sequence('이동 후 서브', SEQ_random_move, SEQ_turn_cheak)
        
        a4 = Action('공 추적', self.move_to_ball)
        c2 = Condition('공 존재 확인', self.serve_cheak())
        
        SEQ_ball_chase = Sequence('공 확인 후 추적', c2, a4)
        root = SEL_chase_or_move = Selector('공추적 또는 랜덤이동', SEQ_ball_chase, SEQ_random_move_and_serve)

        self.bt = BehaviorTree(root)


def ball_cheak_served(e):
    global not_served
    not_served = e
    
