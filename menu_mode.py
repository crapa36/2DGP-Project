from pico2d import *
import game_framework
import play_mode
import score
import ball
import game_world
import player
import enemy
import grass

def init():
    global image
    image = load_image('.\\data\\menu_image.png')
    
def finish():
    global image
    del image

def draw():
    global image
    image.draw(175, 280)
    update_canvas()

def update():
    pass
    
def handle_events():
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN:
            match event.key:
                case pico2d.SDLK_ESCAPE:
                    game_framework.pop_mode()
                case pico2d.SDLK_r:
                    score.score[0], score.score[1] = 0,0
                    score.player.x=175
                    score.enemy.x=175
                    score.player_turn = True
                    if score.ball.deleted==False:
                        game_world.remove_object(score.ball)
                        score.ball.deleted=True
                    game_framework.pop_mode()
                
