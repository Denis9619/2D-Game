import pygame
from extended_groups import Sprite
import configparser
from pygame.image import load
import gameboard.map
from pygame.transform import scale
from pygame.time import delay
from math import ceil, floor
import random
from stats import Stat,StatBarGroup


pygame.init()

class Unit(Sprite):
    def __init__(self,walkRight,walkLeft,stand,speed_h,speed_v,game_map,x,y,hp,mp,clock_rate = 30):
        
        super().__init__()
        self.speed_h = speed_h
        self.speed_v = speed_v
        self.stand = stand
        self.walkRight = walkRight
        self.walkLeft = walkLeft
        self.game_map = game_map
        self.move_to = 0
        self.x = x
        self.y = y
        self.frame = 0
        self.maxframe = 15
        self.stephor = self.maxframe / 6
        self.stepver = self.maxframe / 4
        self.image = self.stand
        self.direction = None
        self.rect = self.image.get_rect()
        self._layer = self.rect.bottom
        self.next_move = None
        self.rect.x = self.game_map.background.rect.left + \
            self.game_map.tile_collection.tile_width * self.x 
        self.rect.y = self.game_map.background.rect.y + \
            self.game_map.tile_collection.tile_height * self.y
        self.current_move = None
        self.clock_rate = clock_rate
        self.animCount = 0
        self.hp = hp
        self.mp = mp
        
        

    @classmethod
    def from_file(cls,pers_filename,game_map,x,y,hp,mp,clock_rate = 30):
        
        config = configparser.ConfigParser()
        config.read(pers_filename)

        w = game_map.tile_collection.tile_width
        h = game_map.tile_collection.tile_height
        
        Left = config['walkLeft']
        walkLeft = [scale(load(n),(w,h)) for n in Left['images'].split('\n')]
        
        Right = config['walkRight']
        walkRight = [scale(load(n),(w,h)) for n in Right['images'].split('\n')]

        Stand = config['stand']
        stand = scale(load(Stand['image']),(w,h))
        
        speed_v = h
        speed_h = w

        
        return cls(walkRight,walkLeft,stand,speed_h,speed_v, game_map, x,y,hp,mp,clock_rate)
    
    @classmethod
    def from_config_section(cls, section, game_map):
        player_config = section.get('config', fallback = None)
        
        try:
            x = int(section.get('x', fallback = 0))
        except ValueError:
            x = 0
        try:
            y = int(section.get('y', fallback = 0))
        except ValueError:
            y = 0
        
        try:
            hp_val     = int(section.get('hp',     fallback = 100))
            hp_max_val = int(section.get('hp_max', fallback = 100))
        except ValueError:
            hp_val = 0
            hp_max_val = 100
        hp = Stat(hp_val, hp_max_val)
        
        try:
            mp_val     = int(section.get('mp',     fallback = 100))
            mp_max_val = int(section.get('mp_max', fallback = 100))
        except ValueError:
            mp_val = 0
            mp_max_val = 100
        mp = Stat(mp_val, mp_max_val)
        
        return cls.from_file(player_config,
                             game_map = game_map,
                             x = x,
                             y = y,
                             hp = hp,
                             mp = mp)
    def inc_frame(self):
        self.frame = (self.frame + 1) % self.maxframe
        #print("pl_frame - ",self.frame)
        
    def x_location(self):
        location_x = self.game_map.background.rect.x + self.x * self.game_map.tile_collection.tile_width
        return location_x
        
    def x_location_change(self):
        location_change = self.game_map.tile_collection.tile_width //6 *round(((self.frame + 1) // self.stephor))
        return location_change 
    
    def y_location(self):
        location_y = self.game_map.background.rect.y + self.y * self.game_map.tile_collection.tile_height
        return location_y
    
    def y_location_change(self):
        location_change_y = self.game_map.tile_collection.tile_height // 4 *round(((self.frame + 1) // self.stepver))
        return location_change_y
    
        
    def move_and_chek(self,current_move,next_move):
            #print("c_move - ",self.current_move)
            if self.current_move == 'left':                
                self.x -= 1
                self.game_map.turn_queue.release(self)
                print("----------")
                
            elif self.current_move == 'right':
                self.x += 1
                self.game_map.turn_queue.release(self)
                print("----------")

            elif self.current_move == 'up':
                self.y -= 1
                self.game_map.turn_queue.release(self)
                print("----------")

            elif self.current_move == 'down':
                self.y += 1
                self.game_map.turn_queue.release(self)
                print("----------")
                
            elif self.current_move == 'space':
                print('space')
                self.game_map.turn_queue.release(self)
                

            if self.next_move is not None:
                if self.next_move == 'left':
                    if self.game_map.background.rect.left + self.x *self.game_map.tile_collection.tile_width > \
                               self.game_map.background.rect.left and self.game_map.is_wall(self.x - 1,self.y) == False:
                        self.current_move = self.next_move
                        self.next_move = None
                    else:
                        self.next_move = None
                        self.current_move = None

                elif self.next_move == 'right':
                    if self.game_map.background.rect.left + self.x *self.game_map.tile_collection.tile_width < \
                               self.game_map.background.rect.left + self.game_map.background.rect.width - \
                               self.game_map.tile_collection.tile_width and self.game_map.is_wall(self.x + 1,self.y) == False:
                        self.current_move = self.next_move
                        self.next_move = None
                    else:
                        self.next_move = None
                        self.current_move = None
                        

                elif self.next_move == 'up':
                    if self.game_map.background.rect.top + self.y  * self.game_map.tile_collection.tile_height > self.game_map.background.rect.top \
                         and self.game_map.is_wall(self.x,self.y - 1) == False:
                        self.current_move = self.next_move
                        self.next_move = None
                    else:
                        self.next_move = None
                        self.current_move = None

                elif self.next_move == 'down':
                    if self.game_map.background.rect.top + self.y * self.game_map.tile_collection.tile_height < self.game_map.background.rect.top \
                                 + self.game_map.background.rect.height - self.game_map.tile_collection.tile_height and self.game_map.is_wall(self.x,self.y + 1) == False:
                        self.current_move = self.next_move
                        self.next_move = None
                    else:
                        self.next_move = None
                        self.current_move = None
                elif self.next_move == 'space':
                    self.current_move = self.next_move
                    self.next_move = None
                    
                else:
                    self.current_move = None
                    self.next_move = None
            else:
                self.current_move = None
    
    def x_location(self):
        location_x = self.game_map.background.rect.x + self.x * self.game_map.tile_collection.tile_width
        return location_x
        
    def x_location_change(self):
        location_change = self.game_map.tile_collection.tile_width //6 *round(((self.frame + 1) // self.stephor))
        return location_change 
    
    def y_location(self):
        location_y = self.game_map.background.rect.y + self.y * self.game_map.tile_collection.tile_height
        return location_y
    
    def y_location_change(self):
        location_change_y = self.game_map.tile_collection.tile_height // 4 *round(((self.frame + 1) // self.stepver))
        return location_change_y
        
    def move_sprites(self,current_move):
        
        if self.current_move == 'left' :
            self.rect.x = self.x_location() - self.x_location_change()
            self.image = self.walkLeft[round(self.frame // self.stephor)]
            self.inc_frame()
                
        elif self.current_move == 'right':
            self.rect.x = self.x_location() + self.x_location_change()
            self.image = self.walkRight[round(self.frame  // self.stephor)]
            self.inc_frame()
            
        elif self.current_move == 'up':
            self.rect.y = self.y_location() - self.y_location_change()
            self.image = self.stand
            self.inc_frame()
           
        elif self.current_move == 'down':
            self.rect.y = self.y_location() + self.y_location_change()
            self.image = self.stand          
            self.inc_frame()
        else:
            self.image = self.stand
        

    def command_move(self, direction):
        #gm = self.game_map
        if self.game_map.pause_event is False :
            if self.next_move == None:
                self.next_move = direction
    
    
    def from_event_to_command(self,event):
                        
        if event.key == pygame.K_LEFT:
            self.command_move('left')
                    
        elif event.key == pygame.K_RIGHT:
            self.command_move('right')
                    
        elif event.key == pygame.K_UP:
            self.command_move('up')

        elif event.key == pygame.K_DOWN :
            self.command_move('down')
        
        elif event.key == pygame.K_SPACE:
            self.command_move('space')
            
            

    def get_position(self):
        pixel_x = self.rect.x - self.game_board.background.rect.x
        pixel_y = self.rect.y - self.game_board.background.rect.y
        
        if self.move_to == 'left':
            x = ceil (pixel_x / self.game_board.tile_collection.tile_width)
        else:
            x = floor(pixel_x / self.game_board.tile_collection.tile_width)
        
        if self.move_to == 'up':
            y = ceil (pixel_y / self.game_board.tile_collection.tile_height)
        else:
            y = floor(pixel_y / self.game_board.tile_collection.tile_height)

    def hp_line(self):
        draw.rect
        
class Player (Unit):
            
    def update(self, *args, **kwargs):
        for event in kwargs['keydown_events']:        
            if event.key == pygame.K_1:
                self.game_map.ghost_birth()
                self.game_map.turn_queue.release(self)
            elif event.key == pygame.K_2:
                 self.game_map.ghost_birth()
                 self.game_map.turn_queue.release(self)
            elif event.key == pygame.K_3:
                 self.game_map.ghost_birth()
                 self.game_map.turn_queue.release(self)
            elif event.key == pygame.K_4:
                 self.game_map.ghost_birth()
                 self.game_map.turn_queue.release(self)
            elif event.key == pygame.K_5:
                 self.game_map.ghost_birth()
                 self.game_map.turn_queue.release(self)
            elif event.key == pygame.K_6:
                 self.game_map.ghost_birth()
                 self.game_map.turn_queue.release(self)
            elif event.key == pygame.K_7:
                 self.game_map.ghost_birth()
                 self.game_map.turn_queue.release(self)
            elif event.key == pygame.K_8:
                 self.game_map.ghost_birth()
                 self.game_map.turn_queue.release(self)
            elif event.key == pygame.K_9:
                 self.game_map.ghost_birth()
                 self.game_map.turn_queue.release(self)
                
        if self.game_map.turn_queue.current() is self:
            if self.frame == 0:
                self.move_and_chek(self.current_move,self.next_move)

                    
            for event in kwargs['keydown_events']:        
                self.from_event_to_command(event)
            print("cur_move - ",self.next_move)
            self.move_sprites(self.current_move)

        
class Mob (Unit):
    
    def from_move_to_command(self,move):
        if move == 'left':
            self.command_move('left')
                    
        elif move == 'right':                
            self.command_move('right')
                                  
        elif move == 'up':
            self.command_move('up')
                                   
        elif move == 'down' :
            self.command_move('down')
        
    def update(self, *args, **kwargs):
        
        if self.game_map.turn_queue.current() == self:

            moves_list = ['left','right','up','down']
            move = random.choice(moves_list)

            if self.frame == 0:
                self.move_and_chek(self.current_move,self.next_move)
               
            self.from_move_to_command(move)
            self.move_sprites(self.current_move)

class Ghost(Mob):
    
    @classmethod
    def from_config_section(cls, section, game_map):
        player_config = section.get('config', fallback = None)
        
        x = game_map.player.x
        y = game_map.player.y
        
        try:
            hp_val     = int(section.get('hp',     fallback = 100))
            hp_max_val = int(section.get('hp_max', fallback = 100))
        except ValueError:
            hp_val = 0
            hp_max_val = 100
        hp = Stat(hp_val, hp_max_val)
        
        try:
            mp_val     = int(section.get('mp',     fallback = 100))
            mp_max_val = int(section.get('mp_max', fallback = 100))
        except ValueError:
            mp_val = 0
            mp_max_val = 100
        mp = Stat(mp_val, mp_max_val)
        
        return cls.from_file(player_config,
                             game_map = game_map,
                             x = x,
                             y = y,
                             hp = hp,
                             mp = mp)
        
    def update(self, *args, **kwargs):
            
        if self.game_map.turn_queue.current() == self:

            moves_list = ['left','right','up','down']
            move = random.choice(moves_list)

            if self.frame == 0:
                self.move_and_chek(self.current_move,self.next_move)
               
            self.from_move_to_command(move)
            self.move_sprites(self.current_move)
    
    
        
if __name__ == '__main__':
    import pygame
    from pygame.sprite import GroupSingle
    import pygame.display
    import argparse as ap
    from extended_groups import LayeredUpdates

    from gameboard.map import GameMap
    
    pygame.init()
    win = pygame.display.set_mode((500 , 500))
    pygame.display.set_caption("Cubes Game")
    clock = pygame.time.Clock()

    parser = ap.ArgumentParser()
    parser.add_argument('-rw', '--resolution-width', type=int, default=0)
    parser.add_argument('-rh', '--resolution-height', type=int, default=0)
    parser.add_argument('--no-loop', action='store_true')
    args = parser.parse_args()

    pygame.display.init()
    screen = pygame.display.set_mode((args.resolution_width, \
                                      args.resolution_height  ))
        
    pygame.display.set_caption('map_test')

    gm = GameMap.from_file('gameboard/map_demo.map')
    #pers = Unit.from_file('player_config.txt',gm,0,0)

    #pers_group = GroupSingle(pers)
    #g = LayeredUpdates()
    #g.add(gm.background,layer = 0)
    #g.add(pers, layer = 1)
    #units = gm.units_list()
    #turn = Turn(units)
    
    #gm.turn_queue.restart_queue()
    run = True
    while run:
        
        clock.tick(30)

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                run = False

        keydown_events = list(filter(lambda e: e.type == pygame.KEYDOWN, events))
        gm.update(keydown_events = keydown_events)

        gm.draw(screen)
        pygame.display.flip()
        pygame.sprite.LayeredUpdates()
        
    pygame.quit()

        

