
from extended_groups import Sprite, LayeredUpdates
from pygame import Color, Rect, Surface

import pygame.draw as draw

from button import PreparedButton

from math import ceil

class ScrollBarButton(PreparedButton):
    
    border_width = 10
    
    """ abstract class; not intended for manual usage """
    def __init__(self, scroll_bar, **kwargs):
        
        self.__dict__.update(kwargs)
        
        rect = Rect(scroll_bar.rect)
        rect.h = rect.w
        
        images = \
            {'normal':  self.draw_image(rect,
                                        self.button_background_color,
                                        self.button_border_color,
                                        self.border_width), \
             'touched': self.draw_image(rect,
                                        self.button_touched_background_color,
                                        self.button_touched_border_color,
                                        self.border_width), \
             'pressed': self.draw_image(rect,
                                        self.button_pressed_background_color,
                                        self.button_pressed_border_color,
                                        self.border_width), \
             'inactive':self.draw_image(rect,
                                        self.button_inactive_background_color,
                                        self.button_inactive_border_color,
                                        self.border_width) \
            }
        
        super().__init__(rect, images)
        
        self.scroll_bar = scroll_bar
        self.scroll_bar.add(self, layer=2)
    
    @classmethod
    def draw_image(cls, rect, background_color, border_color, border_width):
        
        surface = Surface((rect.w,rect.h))
        
        draw.rect(surface, background_color, surface.get_rect())
        draw.rect(surface, border_color, surface.get_rect(), border_width)
        
        return surface
    
    @property
    def active(self):
        return self.scroll_bar.active()

class ScrollBarUpButton(ScrollBarButton):
    def on_press_start(self):
        self.scroll_bar.dec_position()

class ScrollBarDownButton(ScrollBarButton):
    def __init__(self, scroll_bar):
        super().__init__(scroll_bar)
        
        self.rect.y = self.scroll_bar.rect.bottom - self.rect.h
    
    def on_press_start(self):
        self.scroll_bar.inc_position()


class ScrollBarThumb(Sprite):
    
    background_color = Color('#694e33')
    border_color     = Color('#4a3724')
    
    inactive_background_color = Color('#564e46')
    inactive_border_color     = Color('#3d3731')
    
    border_width = 10
    
    def __init__(self, scroll_bar):
        super().__init__()
        
        self.scroll_bar = scroll_bar
        self.scroll_bar.add(self, layer = 1)
        
        self.visible_elements = None
        self.elements = None
        
    @property
    def rect(self):
        rect = self.scroll_bar.rect
        
        if self.scroll_bar.elements > 0:
            step = ceil((rect.h - 2*rect.w) / self.scroll_bar.elements)
        else:
            step = 0
        
        x = rect.x
        y = rect.y + rect.w + step * self.scroll_bar.position
        return Rect(x, y, 0, 0)
    
    def height(self):
        rect = self.scroll_bar.rect
        
        visible_elements = self.scroll_bar.visible_elements
        elements = self.scroll_bar.elements
        
        if visible_elements < elements:
            h = ceil(   (rect.h - 2 * rect.w) \
                      * (visible_elements / elements)
                    )
        else:
            h = (rect.h - 2 * rect.w)
        
        return h
    
    def draw_image(self, background_color, border_color):
        w = self.scroll_bar.rect.w
        h = self.height()
        
        surface = Surface((w,h))
        
        draw.rect(surface, background_color, surface.get_rect())
        draw.rect(surface, border_color,     surface.get_rect(),
                           self.border_width)
        
        return surface
    
    @property
    def image(self):
        if (self.visible_elements != self.scroll_bar.visible_elements) or \
           (self.elements != self.scroll_bar.elements):
                
                self.visible_elements = self.scroll_bar.visible_elements
                self.elements = self.scroll_bar.elements
                
                if self.scroll_bar.active():
                    self._image = self.draw_image(self.background_color,
                                                  self.border_color)
                else:
                    self._image = self.draw_image(self.inactive_background_color,
                                                  self.inactive_border_color)
        return self._image

class ScrollBar(LayeredUpdates):
    
    background_color = Color('#694e33')
    
    def __init__(self, rect, elements = 1, visible_elements = 1, **kwargs):
        
        super().__init__()
        self.__dict__.update(kwargs)
        
        self.rect = rect
        
        # background
        self.background = Sprite()
        self.add(self.background, layer=0)
        
        self.background.rect = self.rect
        self.background.image = Surface((self.background.rect.w, \
                                         self.background.rect.h  ))
        
        image_rect = Rect(self.rect)
        image_rect.x = 0
        image_rect.y = 0
        draw.rect(self.background.image,
                  self.background_color,
                  image_rect)
        
        if elements != 'dynamic':
            self.elements = elements
        if visible_elements != 'dynamic':
            self.visible_elements = visible_elements
        
        self.position = 0
        
        self.up_button = ScrollBarUpButton(self)
        self.down_button = ScrollBarDownButton(self)
        self.thumb = ScrollBarThumb(self)
    
    def set_position(self, position):
        position = min(position, self.elements - self.visible_elements)
        position = max(position, 0)
        self.position = position
        
        self.on_scroll()
    
    def inc_position(self):
        self.set_position(self.position + 1)
    
    def dec_position(self):
        self.set_position(self.position - 1)
    
    def on_scroll(self):
        pass
    
    def active(self):
        return self.visible_elements < self.elements
        
if __name__ == '__main__':
    
    import argparse as ap
    from pygame.time import Clock
    import pygame.event
    import pygame.locals
    
    parser = ap.ArgumentParser()
    
    parser.add_argument('-w', type=int, default=30)
    parser.add_argument('-rw', '--resolution-width', type=int, default=0)
    parser.add_argument('-rh', '--resolution-height', type=int, default=0)
    parser.add_argument('--no-loop', action='store_true')
    
    parser.add_argument('-v', '--visible-elements', type=int, default=1)
    parser.add_argument('-e', '--elements', type=int, default=5)
    
    args = parser.parse_args()
    
    pygame.init()
    pygame.mixer.quit()
    screen = pygame.display.set_mode((args.resolution_width, \
                                      args.resolution_height  ))
    pygame.display.set_caption('scrollbar_test')
    
    clock = Clock()
    
    scroll_rect = pygame.display.get_surface().get_rect()
    scroll_rect.x = scroll_rect.right - args.w
    scroll_rect.w = args.w
    scrollbar = ScrollBar(scroll_rect, args.elements, args.visible_elements)
    
    scrollbar.update()
    rect_list = scrollbar.draw(screen)
    pygame.display.flip()
    
    
    if not args.no_loop:
        run = True
        while run:
            clock.tick(30)
            
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.locals.QUIT:
                    run = False
            
            scrollbar.update()
            rect_list = scrollbar.draw(screen)
            pygame.display.update(rect_list)
