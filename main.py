import pygame
import random
from creature import Zombie, Player
from screeninfo import get_monitors
import numpy as np
import math

monitors = get_monitors()

width, height = monitors[0].width, monitors[0].height

FPS = 15
GROUND_HEIGHT = 6
BLOCK_SIZE = 50
STEP_SIZE = 10
JUMP_SIZE = BLOCK_SIZE*2
CREATURE_SCALE = 100
DANGER_ZONE = width//3

sky_layer = pygame.transform.scale(
                           pygame.image.load('images/blocks/sky.png'),
                           (BLOCK_SIZE, BLOCK_SIZE))


ground_layers = [
    pygame.transform.scale(pygame.image.load('images/blocks/dirt.png'), (BLOCK_SIZE, BLOCK_SIZE)),
    pygame.transform.scale(pygame.image.load('images/blocks/grass.png'), (BLOCK_SIZE, BLOCK_SIZE))
]

state_layers = [
    pygame.transform.scale(pygame.image.load('images/icons/heart.png'), (BLOCK_SIZE*2, BLOCK_SIZE*2)),
]

default_y = height-GROUND_HEIGHT*BLOCK_SIZE-CREATURE_SCALE

weapons = {
    0 : {
        'name': 'hit_punch',
        'damage': 1.0,
        'range': 90,
        'resistance': float('inf'),
    },
    
    1 : {
        'name': 'iron_sword',
        'damage': 3.5,
        'range': 110,
        'resistance': 300.0
    }
}

player_mode_mapping = {
    'stand': 'images/player/stand.png',
    'walk': 'images/player/walk.png',
    'hit_punch': 'images/player/hit_punch.png',
    'iron_sword': 'images/tools/IronSword.png'
}

zombie_mode_mapping = {
    'stand': 'images/zombie/stand.png',
    'walk': 'images/zombie/stand.png',
    'hit': 'images/zombie/hit.png',
}

player = Player(width//2, default_y, 10.0, weapons=weapons,
                mode_mapping=player_mode_mapping, enemies=['Zombie'])

creatures = [player]

def fill_background():
    global screen
    
    for row in range(int(height//(sky_layer.get_height()))+1):
                for column in range(int(width // sky_layer.get_width())+1):
                    screen.blit(sky_layer, (column*sky_layer.get_width(), height-(row+1)*sky_layer.get_height()))

    for row in range(GROUND_HEIGHT-1):
        for column in range(int(width // ground_layers[0].get_width())+1):
            screen.blit(ground_layers[0], (column*ground_layers[0].get_width(), height-(row+1)*ground_layers[0].get_height()))
    
    for column in range(int(width // ground_layers[1].get_width())+1):
        screen.blit(ground_layers[1], (column*ground_layers[1].get_width(), height-(row+2)*ground_layers[1].get_height()))

    for col in range(int(math.ceil(player.hp))):
        screen.blit(state_layers[0], ((col*(state_layers[0].get_width()//3)), height*.00001))
    
def control_creatures():
    global screen
    
    for creature in creatures:
        if creature.hp < .001:
            creature.x = 9999
            creature.y = 9999
            
            del creature
            
            continue
        
        if isinstance(creature, Zombie):
            is_enemy_near = creature.is_enemy_near(creatures, DANGER_ZONE)
            if is_enemy_near:
                creature.go_to_closes_enemy([creature for creature in creatures if creature.__class__.__name__ != 'Zombie'], STEP_SIZE)
            
            creature.switch_mode('stand')
            
            if creature.is_reached_to_creature(player) and 'Player' in creature.enemies:
                creature.switch_mode('hit')
                creature.deal_damage_to_creature(player)
                creature.push_creature(player, creature.damage*100, creature.damage)
        
        if isinstance(creature, Player):
            if creature.mode == 'walk' and creature.reverse:
                creature.x -= STEP_SIZE
            elif creature.mode == 'walk' and not creature.reverse:
                creature.x += STEP_SIZE
            
            if creature.mode == 'hit_punch':
                near_creatures = [(creature.is_reached_to_creature(creat)) for creat in creatures]
                if any(near_creatures):
                    
                    for creat in np.array(creatures)[near_creatures]:
                        if not isinstance(creat, Player) and player.reverse == player.direction_with(creat):
                            creature.deal_damage_to_creature(creat)
                            creature.push_creature(creat, creature.weapon['damage']*10, creature.weapon['damage'])
                            break
            weapon_surface, cord = player.get_weapon_surface(CREATURE_SCALE*.8)
            
        if creature.y < default_y:
            creature.y += (default_y - creature.y)/2
        
        surface = creature.get_surface(CREATURE_SCALE)
        
        
        if weapon_surface != None and cord != None:
            cord = list(cord)
            if creature.y < default_y:
                cord[1] += (default_y - cord[1])/2
            screen.blit(weapon_surface, cord)
        
        screen.blit(surface, (creature.x, creature.y))
        
        player.switch_mode('stand')

def handle_events():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE or event.key == ord(' '):
                player.jump(JUMP_SIZE)
            
            if event.type == pygame.K_2 or event.key == ord('2'):
                player.switch_weapon('iron_sword')
                
            if event.type == pygame.K_1 or event.key == ord('1'):
                player.switch_weapon('hit_punch')
                
            if event.key == pygame.K_ESCAPE:
                pygame.event.post(pygame.event.Event(pygame.QUIT))
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            player.switch_mode('hit_punch')
        
    
    keys = pygame.key.get_pressed()
    
    if keys[pygame.K_a]:
        player.switch_mode('walk')
        player.reverse = True
    if keys[pygame.K_d]:
        player.switch_mode('walk')
        player.reverse = False

def when_player_died():
    for cret in creatures:
        cret.x = 9999
        cret.y = 9999
        
        del cret
    
    player.hp = 10
    player.x = width//2
    player.y = default_y
    # creatures.append(player)

def main():
    global screen
    
    pygame.init()
    pygame.display.set_caption('Minecraft 2D')
    pygame.mouse.set_visible(False)

    screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
    fps_controller = pygame.time.Clock()
    
    i = 0
    while True:
        if i % 15 ==0:
            creatures.append(Zombie(random.randint(0, width//3), default_y, hp=10.0, damage=0.25,
                attack_range=50, mode_mapping=zombie_mode_mapping, 
                enemies=['Player']))
            
        if player.hp <= 0:
            when_player_died()
            
        fill_background()
        
        handle_events()
        
        control_creatures()
        
        pygame.display.update()
        
        fps_controller.tick(FPS)
        
        i += 1

if __name__ == '__main__':
    main()