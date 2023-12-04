from pico2d import *
from grass import Grass
from player import Player
from enemy import Enemy
from ball import Ball
import game_world
import game_framework
import score

map_width, map_height = 350, 560

def handle_events():
    events = get_events()

    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()

        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()

        else:
            player.handle_event(event)
            enemy.handle_event(event)


def init():
    global grass
    global world
    global player
    global enemy
    world = []
    grass = Grass(175, 280)
    game_world.add_object(grass, 0)
    player = Player()
    enemy = Enemy()
    world.append(player)
    world.append(enemy)
    game_world.add_object(player, 1)
    game_world.add_object(enemy, 1)
    game_world.add_collision_pair('player:ball', player, None)
    game_world.add_collision_pair('enemy:ball', enemy, None)


def finish():
    game_world.clear()


def update():
    game_world.update()
    game_world.handle_collisions()


def draw():
    clear_canvas()
    game_world.render()
    update_canvas()
