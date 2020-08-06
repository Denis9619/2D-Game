#!/usr/bin/env python3

from extended_groups import Sprite, MetaLayeredUpdates
from pygame.font import Font
import pygame.font
import pygame.draw as draw
from pygame import Color, Rect, Surface
import pygame.locals
import pygame.mouse as mouse
import pygame.display

from button import PreparedButton, HeldButton

pygame.font.init()

# BUG: .on_...() callbacks are sent in strange way
class MenuEntry(PreparedButton):
    """
    Attributes:
        rect: where to draw a button relatively to screen
    """
    valuable_attributes = {'text', 'button_background_color', \
        'button_border_color', 'state', 'active'}
    
    @property
    def menu(self):
        for g in self.groups():
            if isinstance(g, Menu):
                return g
        
    def __init__(self, text, *groups, **kwargs):
        
        super().__init__(None, dict(), *groups, **kwargs)
        
        self.changed = True
        
        self.text = text
        
    def add(self, *groups):
        if self.menu is None:
            for g in groups:
                if isinstance(groups, Menu):
                    self.menu = g
                    break
        
        return super().add(*groups)
    
    def remove(self, *groups):
        if self.menu in groups:
            self.menu = None
    
    def min_size(self,
                 font = None,
                 button_h_inborders = None,
                 button_v_inborders = None):
        # some boilerplate code:
        if font is None:
            font = self.font            
        
        if button_h_inborders is None:
            button_h_inborders = self.button_h_inborders
        
        if button_v_inborders is None:
            button_v_inborders = self.button_v_inborders
        
        text_size = font.size(self.text)
        return (text_size[0] + 2*button_h_inborders, \
                text_size[1] + 2*button_v_inborders  \
               )
    
    def __setattr__(self, name, value):
        
        super().__setattr__(name, value)
        
        if name in self.valuable_attributes:
            super().__setattr__('changed', True)
            
        #if self.menu is not None:
            #if name in self.menu.valuable_entry_attributes:
                #self.menu.changed = True
    
    def __delattr__(self, name):
        del self.__dict__[name]
        if name in self.valuable_attributes:
            self.changed = True
    
    def __getattr__(self, name):
        try:
            return super().__getattr__(name)
        except AttributeError:
            if type(getattr(type(self), name, None)) is property:
                getattr(type(self), name).fget(self)
            else:
                return getattr(self.menu, name)
    
    def draw_image(self,
                   bg_color,
                   bg_border_color,):
        try:
            rect = Rect(self.rect)
        except TypeError:
            rect = Rect(0,0,0,0)
        rect.x = 0
        rect.y = 0
        border_rect = rect.inflate(*self.border_step)
        
        text = self.text
        
        image = Surface((rect.w, rect.h))
        
        draw.rect(image, bg_color, rect)
        draw.rect(image, bg_border_color, \
                  border_rect, self.border_width)
        
        if self.font.size(text)[0] > rect.w - 2*self.button_h_inborders:
            l = len(self.text) - 1
            text = self.text[:l] + '...'
            while l > 1 and \
                  self.font.size(text)[0] > rect.w - 2*self.button_h_inborders:
                l -= 1
                text = self.text[:l] + '...'
        
        text_image = self.font.render(text,
                                      True,
                                      self.fontcolor,
                                      bg_color)
        text_rect = text_image.get_rect()
        text_rect.center = image.get_rect().center
        
        image.blit(text_image, text_rect)
        
        return image
    
    def draw_images(self):
        images = dict()
        
        images['inactive'] = self.draw_image(
            bg_color = self.button_inactive_background_color,
            bg_border_color = self.button_inactive_border_color
        )
        images['normal'] = self.draw_image(
            bg_color = self.button_background_color,
            bg_border_color = self.button_border_color
        )
        images['pressed'] = self.draw_image(
            bg_color = self.button_pressed_background_color,
            bg_border_color = self.button_pressed_border_color
        )
        images['touched'] = self.draw_image(
            bg_color = self.button_touched_background_color,
            bg_border_color = self.button_touched_border_color
        )
        
        return images
    
    def update(self, *args, **kwargs):
        
        if self.images is None or self.changed:
            
            self.images.update(self.draw_images())
            
            self.changed = False
        
        super().update(*args, **kwargs)
    
class HeldMenuEntry(MenuEntry, HeldButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def draw_images(self):
        
        images = super().draw_images()
        
        images['held'] = self.draw_image(
            bg_color = self.button_held_background_color,
            bg_border_color = self.button_held_border_color
        )
        
        return images
    
    #~ def on_click(self):
        #~ self.held = not self.held
        
        #~ if self.held and self.menu is not None:
            #~ for e in self.menu.entries:
                #~ if isinstance(e, HeldMenuEntry) and e is not self:
                    #~ e.held = False
        
        #~ super().on_click()

class HorizButtonsAlignRight:
    @classmethod
    def align(cls, buttons_rect, buttons, button_hspacing, min_button_size):
        button_hstep = min_button_size[0] + button_hspacing
        
        for i, entry in enumerate(reversed(buttons)):
            entry.rect = Rect(buttons_rect.right + button_hspacing - button_hstep*(i+1),
                              buttons_rect.y,
                              min_button_size[0],
                              min_button_size[1])

class HorizButtonsAlignWidth(HorizButtonsAlignRight):
    @classmethod
    def align(cls, buttons_rect, buttons, button_hspacing, min_button_size):
        button_hspacing = (buttons_rect.width \
                           - min_button_size[0] * len(buttons)) \
                          / (len(buttons) - 1)
        super().align(buttons_rect, buttons, button_hspacing, min_button_size)

class Menu(MetaLayeredUpdates):
    
    # it's not working for now
    valuable_entry_attributes = ['text']
    
    button_h_inborders = 20
    button_v_inborders = 15
    
    button_vspacing = 20
    button_hspacing = 20
    
    button_background_color = Color('#694e33')
    button_border_color     = Color('#4a3724')
    
    button_touched_background_color = Color('#8b5d31')
    button_touched_border_color     = Color('#6c4926')
    
    button_pressed_background_color = Color('#55391e')
    button_pressed_border_color     = Color('#422d17')
    
    button_inactive_background_color = Color('#564e46')
    button_inactive_border_color     = Color('#3d3731')
    
    h_inborders = 40
    v_inborders = 40
    
    border_step = (-15, -15)
    border_width = 5
    
    background_color = Color('#764f28')
    border_color     = Color('#492e13')
    
    fontsize = 45
    font = Font(None, fontsize)
    fontcolor = (0,0,0)
    
    text = '[WIP]'
    
    bottom_button_align = HorizButtonsAlignRight
    
    def __init__(self,
                 *entries,
                 screen_rect = None,
                 top_space = 0,
                 bottom_space = 0,
                 right_space = 0,
                 bottom_entries = [],
                 title = None,
                 **kwargs):
        
        self.__dict__.update(kwargs)
        self.top_space = top_space
        self.bottom_space = bottom_space
        self.right_space = right_space
        self.title = title
        
        entries = list(entries)
        print(entries)
        for i in range(len(entries)):
            if not isinstance(entries[i], MenuEntry):
                entries[i] = MenuEntry(entries[i])
        
        
        bottom_entries = list(bottom_entries)
        for i in range(len(bottom_entries)):
            if not isinstance(bottom_entries[i], MenuEntry):
                bottom_entries[i] = MenuEntry(bottom_entries[i])
        print('bottom_entries', bottom_entries)
        
        super().__init__()
        super().add(*(entries + bottom_entries), layer = 1)
        self.entries = entries
        self.bottom_entries = bottom_entries
        
        #self.entry_num = [ e: i for i, e in enumerate(self.entries) ]
        
        if screen_rect is None:
            self.screen_rect = pygame.display.get_surface().get_rect()
        else:
            self.screen_rect = Rect(screen_rect)
        
        self.changed = True
        
        self.background = Sprite()
        self.add(self.background, layer = 0)
        
        self.update()
    
    def calculate_min_button_size(self):
        min_size = [5,10]
        for w, h in map(lambda e: e.min_size(), self.entries):
            if w > min_size[0]: min_size[0] = w
            if h > min_size[1]: min_size[1] = h
        
        return min_size
    
    def calculate_min_bottom_button_size(self):
        min_size = [5,10]
        for w, h in map(lambda e: e.min_size(), self.bottom_entries):
            if w > min_size[0]: min_size[0] = w
            if h > min_size[1]: min_size[1] = h
        
        return min_size
    
    def render_background(self, w, h):
        bg_surf = Surface((w, h))
        bg_rect = bg_surf.get_rect()
        
        bg_border_rect = bg_rect.inflate(*self.border_step)
        
        draw.rect(bg_surf, self.background_color, bg_rect)
        draw.rect(bg_surf, self.border_color, \
                  bg_border_rect, self.border_width)
        
        if self.title is not None:
            text_img = self.font.render(self.title,
                                        True,
                                        self.fontcolor,
                                        self.background_color)
            text_rect = text_img.get_rect()
            text_rect.y       = bg_rect.y + self.h_inborders // 2
            text_rect.centerx = bg_rect.centerx
            bg_surf.blit(text_img, text_rect)
        
        return bg_surf
    
    def update(self, *args, **kwargs):
        """
        Please, take note, that if Menu's surfaces are updated from
        different group, this method MUST be called manually when it
        is needed.
        It is called once at the end of Menu.__init__() execution.
        """
        
        if self.changed:
            
            for e in self.entries + self.bottom_entries:
                e.changed = True
            
            if self.title is not None:
                title_size = list(self.font.size(self.title))
                title_size[1] = self.font.get_height()
            else:
                title_size = (0,0)
            
            self.min_button_size = self.calculate_min_button_size()
            self.min_bottom_button_size = self.calculate_min_bottom_button_size()
            
            if len(self.bottom_entries) == 0:
                bottom_buttons_spacing = 0
            else:
                bottom_buttons_spacing = self.min_bottom_button_size[1] \
                                         + self.button_vspacing
            
            button_vstep = self.min_button_size[1] + self.button_vspacing
            button_hstep = self.min_bottom_button_size[0] + self.button_hspacing
            
            buttons_rect = Rect(
                0,
                0,
                max(self.min_button_size[0],
                    button_hstep * len(self.bottom_entries) - self.button_hspacing,
                    title_size[0]),
                button_vstep * len(self.entries) - self.button_vspacing
            )
            
            buttons_rect.center = self.screen_rect.center
            
            
            bg_rect = buttons_rect.inflate(self.h_inborders \
                                           + self.right_space,
                                           self.v_inborders \
                                           + self.top_space \
                                           + self.bottom_space \
                                           + bottom_buttons_spacing\
                                           + title_size[1])
            buttons_rect.x = bg_rect.x + self.h_inborders // 2
            buttons_rect.y = bg_rect.y \
                             + self.v_inborders // 2 \
                             + self.top_space \
                             + title_size[1]
            
            bottom_buttons_rect = Rect(bg_rect.x + self.h_inborders // 2,
                                       buttons_rect.bottom \
                                       + self.button_vspacing,
                                       bg_rect.w - self.h_inborders,
                                       self.min_bottom_button_size[1]
                                      )
            
            for i, entry in enumerate(self.entries):
                entry.rect = Rect(buttons_rect.x,
                                  buttons_rect.y + i*button_vstep,
                                  self.min_button_size[0],
                                  self.min_button_size[1])
                entry.rect.centerx = buttons_rect.centerx
            
            self.bottom_button_align.align(bottom_buttons_rect,
                                           self.bottom_entries,
                                           self.button_hspacing,
                                           self.min_bottom_button_size)
            
            self.background.image = \
                self.render_background(bg_rect.w, bg_rect.h)
            self.background.rect = bg_rect
            
            self.buttons_rect = buttons_rect
            
            self.changed = False
        
        super().update(*args, **kwargs)
    
    # TODO: write proper .add() and .remove()

class QuestionMenu(Menu):
    
    def __init__(self,
                 question,
                 *entries,
                 screen_rect = None,
                 **kwargs):
        
        self.question = question
        super().__init__(*entries, screen_rect = screen_rect, **kwargs)
    
    def __setattr__(self, name, value):
        
        super().__setattr__(name, value)
        
        if name == 'question':
            super().__setattr__('changed', True)
    
    def update(self, *args, **kwargs):
        if self.changed:
            
            self.min_button_size = self.calculate_min_button_size()
            
            text_img = self.font.render(self.question,
                                        True,
                                        self.fontcolor, 
                                        self.background_color)
            text_rect = text_img.get_rect()
            
            inside_rect = Rect(
                0,
                0,
                max(text_rect.w,\
                    len(self.entries) * (self.min_button_size[0] \
                    + self.button_hspacing) - self.button_hspacing),
                text_rect.h + self.button_vspacing + self.min_button_size[1])
            inside_rect.center = self.screen_rect.center
            
            
            rect = inside_rect.inflate(self.h_inborders, self.v_inborders)
            image = self.render_background(rect.w, rect.h)
            
            text_rect.centerx = image.get_rect().centerx
            text_rect.y = inside_rect.y - rect.y
            image.blit(text_img, text_rect)
            
            self.background.rect  = rect
            self.background.image = image
            
            button_hstep = self.min_button_size[0] + self.button_hspacing
            
            text_rect.centerx = inside_rect.centerx
            text_rect.y       = inside_rect.y
            
            button_rect = \
                Rect(inside_rect.x,
                     text_rect.bottom + self.button_vspacing,
                     inside_rect.width,
                     self.min_button_size[1])
            
            button_rect_center = button_rect.center
            button_rect.width = button_hstep * len(self.entries) - self.button_hspacing
            button_rect.center = button_rect_center
            
            for i, entry in enumerate(self.entries):
                entry.rect = Rect(button_rect.x + i*button_hstep,
                                  button_rect.y,
                                  *self.min_button_size)
            self.changed = False
        
        super(Menu, self).update(*args, **kwargs)
            

# TODO: fix behaviour with too long titles
class FixedWidthMenu(Menu):
    
    valuable_entry_attributes = []
    
    def __init__(self, width, *entries,
                 screen_rect = None, **kwargs  ):
        
        self.width = width
        
        super().__init__(*entries,
                         screen_rect = screen_rect,
                         **kwargs)
        
    
    def calculate_min_button_size(self):
        sizes = super().calculate_min_button_size()
        sizes[0] = max(self.width \
                       - self.h_inborders \
                       - self.right_space, self.h_inborders)
        return sizes
    
    def calculate_min_bottom_button_size(self):
        sizes = super().calculate_min_bottom_button_size()
        
        if len(self.bottom_entries) == 0:
            return sizes
        
        max_button_width = (self.width - self.h_inborders \
                            - self.button_hspacing \
                              * (len(self.bottom_entries) - 1)) / len(self.bottom_entries)
        sizes[0] = min(sizes[0], max_button_width)
        return sizes

if __name__ == '__main__':
    
    import argparse as ap
    from pygame.time import Clock
    import pygame.event
    
    parser = ap.ArgumentParser()
    
    parser.add_argument('entries', nargs='*', default=['Test'])
    parser.add_argument('-rw', '--resolution-width', type=int, default=0)
    parser.add_argument('-rh', '--resolution-height', type=int, default=0)
    parser.add_argument('--no-loop', action='store_true')
    
    parser.add_argument('-w', '--width', type=int, default=0)
    parser.add_argument('-t', '--top-space', type=int, default=0)
    parser.add_argument('-b', '--bottom-space', type=int, default=0)
    
    parser.add_argument('-B', '--bottom-entries', nargs='*', help='bottom buttons', default = [])
    
    args = parser.parse_args()
    
    pygame.init()
    pygame.mixer.quit()
    screen = pygame.display.set_mode((args.resolution_width, \
                                      args.resolution_height  ))
    pygame.display.set_caption('menu_test')
    
    clock = Clock()
    
    if args.width == 0:
        menu = Menu(*args.entries, top_space = args.top_space,
                    bottom_space = args.bottom_space,
                    bottom_entries = args.bottom_entries)
    else:
        menu = FixedWidthMenu(args.width, *args.entries,
                              top_space = args.top_space,
                              bottom_space = args.bottom_space,
                              bottom_entries = args.bottom_entries)
    
    rect_list = menu.draw(screen)
    pygame.display.flip()
    
    
    if not args.no_loop:
        run = True
        while run:
            clock.tick(30)
            
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.locals.QUIT:
                    run = False
            
            menu.update()
            rect_list = menu.draw(screen)
            pygame.display.update(rect_list)
    
    
