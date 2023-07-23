from abc import abstractclassmethod, ABCMeta
import pygame

class Creature(metaclass=ABCMeta):
    
    def __init__(self, x, y, hp) -> None:
        self.x = x
        self.y = y
        self.hp = hp
        
    def move(self, move_x, move_y):
        self.x += move_x
        self.y += move_y
    
    @abstractclassmethod
    def get_surface(self):
        pass
    
    def jump(self, amount):
        self.y -= amount
    
    def direction_with(self, creature):
        if self.x <= creature.x:
            return False
        return True

class Player(Creature):
    def __init__(self, x, y, hp, weapons, mode_mapping, enemies) -> None:
        super().__init__(x, y, hp)
        assert type(mode_mapping) == dict
        
        self.weapons = weapons
        self.mode_mapping = mode_mapping
        
        self.mode = tuple(mode_mapping.keys())[0]
        self.weapon = weapons[0]
        self.enemies = enemies
        
        self.reverse = False
    
    def get_surface(self, scale):
        img_path = self.mode_mapping.get(self.mode)
        
        surface = pygame.image.load(img_path)
        
        surface = pygame.transform.scale(surface, (scale, scale))
        
        if self.reverse:
            surface = pygame.transform.flip(surface, True, False)

        return surface

    def get_weapon_surface(self, scale):
        if not self.weapon['name'] == 'hit_punch':
            img_path = self.mode_mapping.get(self.weapon['name'])
        else:
            img_path = 'images\\tools\empty.png'
        
        surface = pygame.image.load(img_path)
        
        surface = pygame.transform.scale(surface, (scale, scale))
        if self.reverse:
            surface = pygame.transform.flip(surface, True, False)
            
        if self.mode in ('stand' or 'walk'):
            if self.reverse:
                return(pygame.transform.rotate(surface, 45), (self.x-25, self.y))
            else:
                return(pygame.transform.rotate(surface, -45), (self.x+10, self.y))
        if self.mode == 'hit_punch':
            if self.reverse: 
                return(surface, (self.x-40, self.y-10))
            else:
                return(surface, (self.x+60, self.y-10))
        
        if self.reverse:
            return pygame.transform.rotate(surface, 45), (self.x-25, self.y)
        else:
            return(pygame.transform.rotate(surface, -45), (self.x+10, self.y))

    def is_enemy_near(self, creatures, zone):
        return any([abs(self.x - creature.x) < zone for creature in creatures])
    
    def switch_mode(self, mode):
        self.mode = mode
        
    def is_reached_to_creature(self, creature):
        if (self.x-self.weapon['range'] <= creature.x) and (self.x+self.weapon['range'] >= creature.x):
            return True
        return False
    
    def push_creature(self, creature, step_x, step_y):
        creature.y -= step_y
        if self.direction_with(creature):
            creature.x -= step_x
        else:
            creature.x += step_x
    
    def deal_damage_to_creature(self, creature):
        creature.hp -= self.weapon['damage']
    
    def switch_weapon(self, weapon):
        assert any([weapon == weapon_object['name'] for weapon_object in self.weapons.values()])
        
        for k, v in self.weapons.items():
            if v['name'] == weapon:
                self.weapon = self.weapons[k]
                return None
        
class Zombie(Creature):
    
    def __init__(self, x, y, hp, damage, attack_range, mode_mapping, enemies) -> None:
        super().__init__(x, y, hp)

        self.mode_mapping = mode_mapping
        self.enemies = enemies
        
        self.range = attack_range
        self.damage = damage
        
        self.mode = tuple(mode_mapping.keys())[0]
        self.reverse = False
        
    def get_surface(self, scale):
        img_path = self.mode_mapping.get(self.mode)
        
        surface = pygame.image.load(img_path)
        
        surface = pygame.transform.scale(surface, (scale, scale))
        
        if self.reverse:
            surface = pygame.transform.flip(surface, True, False)

        return surface
    
    def go_to_closes_enemy(self, creatures, step):
        
        sorted_creatures = sorted(creatures, key=lambda z: z.x, reverse=True)
        
        for i in range(len(sorted_creatures)):
            
            if creatures[i].__class__.__name__ in self.enemies:
                
                if self.x+self.range <= creatures[i].x:
                    self.x += step
                    self.reverse = False
                elif self.x-self.range >= creatures[i].x:
                    self.x -= step
                    self.reverse = True
    
    def is_reached_to_creature(self, creature):
        if (self.x-self.range <= creature.x) and (self.x+self.range >= creature.x):
            return True
        return False
    
    def push_creature(self, creature, step_x, step_y):
        creature.y -= step_y
        if self.direction_with(creature):
            creature.x -= step_x
        else:
            creature.x += step_x
        
    def deal_damage_to_creature(self, creature):
        creature.hp -= self.damage

    def switch_mode(self, mode):
        self.mode = mode
    
    def is_enemy_near(self, creatures, zone):
        return any([(abs(self.x - creature.x) < zone) and not isinstance(creature, Zombie) for creature in creatures])