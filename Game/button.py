
from extended_groups import Sprite
import pygame.mouse as mouse
from pygame import Color

class AbstractButton(Sprite):
    
    active = True
    
    def __init__(self, *groups, **kwargs):
        super().__init__(*groups)
        
        self.__dict__.update(kwargs)
        self.state = 'normal'
    
    def update(self, *args, **kwargs):
        try:
            self.rect
        except AttributeError:
            return
        
        if not self.active:
            state = 'inactive'
        else:
            mouse_pos = mouse.get_pos()
            if not self.rect.collidepoint(mouse_pos):
                state = 'normal'
            else:
                if mouse.get_pressed()[0]:
                    state = 'pressed'
                else:
                    state = 'touched'
            
        if self.state != state:
            
            if state == 'pressed':
                self.on_press()
            if self.state == 'pressed' and state == 'touched':
                self.on_click()
            
            if self.state == 'touched' and state == 'pressed':
                self.on_press_start()
            
            self.state = state
            
    
    def on_press(self):
        pass
    
    def on_click(self):
        pass
    
    def on_press_start(self):
        pass
    
class PreparedButton(AbstractButton):
    
    button_background_color = Color('#694e33')
    button_border_color     = Color('#4a3724')
    
    button_touched_background_color = Color('#8b5d31')
    button_touched_border_color     = Color('#6c4926')
    
    button_pressed_background_color = Color('#55391e')
    button_pressed_border_color     = Color('#422d17')
    
    button_inactive_background_color = Color('#564e46')
    button_inactive_border_color     = Color('#3d3731')
    
    def __init__(self, rect, images, *groups, **kwargs):
        super().__init__(*groups, **kwargs)
        
        self.images = images
        
        self.rect = rect
        try:
            self.image = images['normal']
        except (KeyError, TypeError):
            self.image = None
        
        self.changed = False
    
    def __setattr__(self, name, value):
        if name == 'state':
            if 'state' not in self.__dict__ or \
               self.__dict__['state'] != value :
                self.changed = True
        super().__setattr__(name, value)
    
    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        
        self.image = self.images[self.state]

class HeldButton(PreparedButton):
    
    button_held_background_color = Color('#5b4026')
    button_held_border_color = Color('#493520')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        try:
            self.held = False
        except AttributeError:
            pass
        
    def update(self, *args, **kwargs):
        AbstractButton.update(self, *args, **kwargs)
        
        if self.state == 'normal':
            if self.held:
                self.image = self.images['held']
            else:
                self.image = self.images['normal']
        else:
            self.image = self.images[self.state]
    
