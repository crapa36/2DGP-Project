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


# state event check

# ( state event type, event value )


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


# time_out = lambda e : e[0] == 'TIME_OUT'


class Idle:
    @staticmethod
    def enter(player, e):
        player.dir = 0

    @staticmethod
    def exit(player, e):
        pass

    @staticmethod
    def do(player):
        player.frame = (player.frame + 1) % 10

    @staticmethod
    def draw(player):
        frame_width = 40

        frame_height = 40

        sheet_columns = 4

        sheet_rows = 3

        # 현재 프레임의 인덱스 계산

        frame_index = player.frame % (sheet_columns * sheet_rows)

        # 현재 프레임의 x, y 좌표 계산

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
        if right_down(e) or left_up(e):  # 오른쪽으로 RUN
            player.dir, player.face_dir = 1, 1

        elif left_down(e) or right_up(e):  # 왼쪽으로 RUN
            (
                player.dir,
                player.face_dir,
            ) = (
                -1,
                -1,
            )

        player.frame = 0

    @staticmethod
    def exit(player, e):
        pass

    @staticmethod
    def do(player):
        player.frame = (player.frame + 1) % 7

        moveSpeed = 5

        player.x += player.dir * moveSpeed

    @staticmethod
    def draw(player):
        # 각 프레임의 크기와 스프라이트 시트의 가로 및 세로 줄 수

        frame_width = 40

        frame_height = 40

        sheet_columns = 4

        sheet_rows = 2

        # 현재 프레임의 인덱스 계산

        frame_index = player.frame % (sheet_columns * sheet_rows)

        # 현재 프레임의 x, y 좌표 계산

        frame_x = (frame_index % sheet_columns) * frame_width

        frame_y = (sheet_rows - 1 - frame_index // sheet_columns) * frame_height

        # player.x와 player.y에 현재 프레임의 이미지를 출력

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
        player.fire_ball()

    @staticmethod
    def do(player):
        player.frame = player.frame + 1

    @staticmethod
    def draw(player):
        # 각 프레임의 크기와 스프라이트 시트의 가로 및 세로 줄 수

        frame_width = 40

        frame_height = 60

        sheet_columns = 4

        sheet_rows = 3

        # 현재 프레임의 인덱스 계산

        frame_index = player.frame % (sheet_columns * sheet_rows)

        # 현재 프레임의 x, y 좌표 계산

        frame_x = (frame_index % sheet_columns) * frame_width

        frame_y = (sheet_rows - 1 - frame_index // sheet_columns) * frame_height

        # player.x와 player.y에 현재 프레임의 이미지를 출력

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
        player.frame = player.frame + 1

        moveSpeed = 0.3

        player.x += player.dir * moveSpeed

    @staticmethod
    def draw(player):
        # 각 프레임의 크기와 스프라이트 시트의 가로 및 세로 줄 수

        frame_width = 40

        frame_height = 40

        sheet_columns = 3

        sheet_rows = 4

        # 현재 프레임의 인덱스 계산

        frame_index = player.frame % (sheet_columns * sheet_rows)

        # 현재 프레임의 x, y 좌표 계산

        frame_x = (frame_index % sheet_columns) * frame_width

        frame_y = (sheet_rows - 1 - frame_index // sheet_columns) * frame_height

        # player.x와 player.y에 현재 프레임의 이미지를 출력

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


# class Sleep:

#     @staticmethod

#     def enter(player, e):

#         player.frame = 0

#         pass


#     @staticmethod

#     def exit(player, e):

#         pass


#     @staticmethod

#     def do(player):

#         player.frame = (player.frame + 1) % 8


#     @staticmethod

#     def draw(player):

#         if player.face_dir == -1:

#             player.image.clip_composite_draw(

#                 player.frame * 100,

#                 200,

#                 100,

#                 100,

#                 -3.141592 / 2,

#                 "",

#                 player.x + 25,

#                 player.y - 25,

#                 100,

#                 100,

#             )

#         else:

#             player.image.clip_composite_draw(

#                 player.frame * 100,

#                 300,

#                 100,

#                 100,

#                 3.141592 / 2,

#                 "",

#                 player.x - 25,

#                 player.y - 25,

#                 100,

#                 100,

#             )


class StateMachine:
    def __init__(self, player):
        self.player = player

        self.cur_state = Idle

        self.transitions = {
            Idle: {
                right_down: Run,
                left_down: Run,
                left_up: Run,
                right_up: Run,
                space_down: Serve,
            },
            Run: {
                right_down: Stop,
                left_down: Stop,
                right_up: Stop,
                left_up: Stop,
                space_down: Serve,
            },
            Stop: {
                right_down: Run,
                left_down: Run,
                left_up: Run,
                right_up: Run,
                time_out: Idle,
                space_down: Serve,
            },
            Serve: {time_out: Idle},
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
    def __init__(self):
        self.x, self.y = 175, 120

        self.frame = 0

        self.action = 3

        self.dir = 0

        self.face_dir = 1

        self.idleImage = load_image("player_idle.png")

        self.runImage = load_image("player_run.png")

        self.serveImage = load_image("player_serve.png")

        self.swingImage = load_image("player_swing.png")

        self.stopImage = load_image("player_stop.png")

        self.state_machine = StateMachine(self)

        self.state_machine.start()

    def update(self):
        self.state_machine.update()

    def handle_event(self, event):
        self.state_machine.handle_event(("INPUT", event))

    def draw(self):
        self.state_machine.draw()

    def fire_ball(self):
        ball = Ball(self.x, self.y + 10, self.face_dir, 5)

        game_world.add_object(ball, 0)