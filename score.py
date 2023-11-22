import player
import enemy

player_turn = True

def ball_deleted():
    player.ball_cheak_served(True)
    enemy.ball_cheak_served(True)
    
def ball_created():
    player.ball_cheak_served(False)
    enemy.ball_cheak_served(False)
    
    