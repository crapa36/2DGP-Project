from pico2d import *
from grass import Grass
from player import Player
from enemy import Enemy
from ball import Ball
import game_world
import game_framework
import score
import menu_mode

map_width, map_height = 350, 560


def handle_events():
    events = get_events()

    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()

        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.push_mode(menu_mode)
        else:
            score.player.handle_event(event)
            score.enemy.handle_event(event)


def init():
    global grass
    global world
    world = []
    grass = Grass(175, 280)
    game_world.add_object(grass, 0)
    score.player = Player()
    score.enemy = Enemy()
    world.append(score.player)
    world.append(score.enemy)
    game_world.add_object(score.player, 1)
    game_world.add_object(score.enemy, 1)
    game_world.add_collision_pair("player:ball", score.player, None)
    game_world.add_collision_pair("enemy:ball", score.enemy, None)
    score.ball = Ball
    score.ball.deleted = True
    draw()
    game_framework.push_mode(menu_mode)


def finish():
    game_world.clear()


def update():
    game_world.update()
    game_world.handle_collisions()


def draw():
    clear_canvas()
    game_world.render()
    update_canvas()


def pause():
    pass


def resume():
    pass
