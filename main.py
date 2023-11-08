from pico2d import open_canvas, delay, close_canvas
import game_framework

import play_mode as start_mode

map_width, map_height = 350, 560
open_canvas(map_width, map_height, sync=True)
game_framework.run(start_mode)
close_canvas()
