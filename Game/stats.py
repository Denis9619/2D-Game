import pygame
from extended_groups import Sprite, MetaLayeredUpdates
from pygame.time import delay
from math import ceil, floor
import random
import pygame.draw as draw
from pygame import Rect, Surface, Color

from pygame.freetype import SysFont as FtSysFont
pygame.freetype.init()

class Stat:
    def __init__(self, val=100, max_val=200):
        self._val = val
        self._max_val = max_val
        
        self.change_subscribers = dict()
    
    
    def call_change_subscribers(self):
        for sub in self.change_subscribers.values():
            sub(self.val, self.max_val)
    
    @property
    def val(self):
        return self._val
    @val.setter
    def val(self,val):
        self._val = val
        self.call_change_subscribers()
    
    @property
    def max_val(self):
        return self._max_val
    @max_val.setter
    def max_val(self,max_val):
        self._max_val = max_val
        self.call_change_subscribers()
    
    def subscribe(self, func, identity):
        self.change_subscribers[identity] = func
        func(self.val, self.max_val)
    
    def unsubscribe(self, identity):
        try:
            del self.change_subscribers[identity]
        except KeyError:
            pass
        
# (width / self.stat._max_val)*self.val    
class StatBar(Sprite):
    
    border_color = Color('#4a3724')
    border_width = 5
    
    def __init__(self, rect,
                 color = (200, 0, 0),
                 bg_color = (255,255,255)):
        super().__init__()
        self.rect = Rect(rect)
        self.color = color
        self.bg_color = bg_color
        
        self.image = Surface((self.rect.w, self.rect.h))
        
        self.on_stat_change(0, 100)

    def on_stat_change(self, stat_val, max_stat_val):
        self.image.fill(self.bg_color)
        
        rect = self.image.get_rect()
        rect.w = round((self.rect.w / max_stat_val)*stat_val) 
        draw.rect(self.image,self.color,rect)
        draw.rect(self.image,
                  self.border_color,
                  self.image.get_rect(),
                  self.border_width)
    

        # ~ draw.rect(self.image, (255,255,255), self.image.get_rect())
        
        #draw.rect(self.image, (255,0,0),border_rect, self.border_width)
        
    
    
class StatBarGroup(MetaLayeredUpdates):
    
    font = FtSysFont('Liberation Mono', 20, bold=False)
    font_color = Color(255, 255, 255)
    
    hp_y = 40
    mp_y = 20
    stats_x = 30
    
    statbar_width  = 100
    statbar_height = 20
    
    hp_color    = Color(200, 0, 0)
    hp_bg_color = Color(255, 255, 255)
    
    mp_color    = Color(0, 0, 200)
    mp_bg_color = Color(255, 255, 255)
    
    def __init__(self, screen_rect=None):
        super().__init__()
        if screen_rect is None:
            self.screen_rect = pygame.display.get_surface().get_rect()
        else:
            self.screen_rect = Rect(screen_rect)
        
        
        
        self.hp_text = Sprite(self)
        self.hp_text.image, self.hp_text.rect = self.font.render('hp',
                                                                 self.font_color)
        self.hp_text.rect.y = self.screen_rect.bottom \
                              - self.hp_y - self.hp_text.rect.y \
                              + self.font.get_sized_ascender()
        
        self.mp_text = Sprite(self)
        self.mp_text.image, self.mp_text.rect = self.font.render('mp',
                                                                 self.font_color)
        self.mp_text.rect.y = self.screen_rect.bottom \
                              - self.mp_y - self.mp_text.rect.y \
                              + self.font.get_sized_ascender()
        
        self.hp_bar = StatBar(Rect(self.stats_x,
                                   self.screen_rect.bottom - self.hp_y,
                                   self.statbar_width,
                                   self.statbar_height),
                              self.hp_color,
                              self.hp_bg_color)
        self.mp_bar = StatBar(Rect(self.stats_x,
                                   self.screen_rect.bottom - self.mp_y,
                                   self.statbar_width,
                                   self.statbar_height),
                              self.mp_color,
                              self.mp_bg_color)
        
        self.add(self.hp_bar, self.mp_bar)
        
    def subscribe_on_unit(self, unit):
        unit.hp.subscribe(self.hp_bar.on_stat_change, id(self.hp_bar))
        unit.mp.subscribe(self.mp_bar.on_stat_change, id(self.mp_bar))

if __name__ == '__main__':
    import pygame
    from pygame.sprite import GroupSingle
    import pygame.display
    import argparse as ap
    from extended_groups import LayeredUpdates
    
    pygame.init()

    parser = ap.ArgumentParser()
    parser.add_argument('-rw', '--resolution-width', type=int, default=0)
    parser.add_argument('-rh', '--resolution-height', type=int, default=0)
    args = parser.parse_args()

    pygame.display.init()
    screen = pygame.display.set_mode((args.resolution_width, \
                                      args.resolution_height  ))
        
    pygame.display.set_caption('map_test')
    
    stat = Stat()
    br = StatBar(stat, 0,0)
    group = LayeredUpdates()
    group.add(br)
    
    
    clock = pygame.time.Clock()
    run = True
    while run:
        clock.tick(30)

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                run = False

        group.update()
        ###########################################
        
        #gm.update(keydown_events = keydown_events)
        group.draw(screen)
        #pers_group.draw(win)
        pygame.display.flip()
        
    pygame.quit()
        
        

