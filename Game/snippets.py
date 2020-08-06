
from menu import FixedWidthMenu, MenuEntry, HeldMenuEntry, HorizButtonsAlignWidth
from extended_groups import MetaLayeredUpdates, Sprite
from scrollbar import ScrollBar

import pygame.display
from pygame import Rect, Color, Surface

import pygame.draw as draw

import re
from itertools import cycle

import pygame.freetype
from pygame.freetype import SysFont as FtSysFont
pygame.freetype.init()

class SnippetScrollBar(ScrollBar):
    def __init__(self, rect, dialog, **kwargs):
        
        self.dialog = dialog
        
        super().__init__(rect,
                         elements = 'dynamic',
                         visible_elements = self.dialog.entry_height,
                         **kwargs)
    
    @property
    def elements(self):
        return len(self.dialog.snippet_container)
    
    def on_scroll(self):
        for e in self.dialog.entries:
            e.update_text()

class SnippetEntry(HeldMenuEntry):
    def __init__(self, dialog, count):
        self.dialog = dialog
        self.count = count
        
        text = self.current_text()
        
        super().__init__(text)
        
    def global_count(self):
        try:
            position = self.dialog.scrollbar.position
        except AttributeError:
            position = 0
        return self.count + position
    def current_text(self):
        try:
            return self.dialog.snippet_description(self.global_count())
        except IndexError:
            return ''
    
    def update_text(self):
        self.text = self.current_text()
    
    @property
    def active(self):
        try:
            position = self.dialog.scrollbar.position
        except AttributeError:
            position = 0
        return len(self.dialog.snippet_container) > (position + self.count)
    
    @property
    def held(self):
        try:
            self.dialog.held_num
        except AttributeError:
            return False
        
        if self.dialog.held_num is None:
            return False
        elif self.dialog.held_num == self.global_count():
            return True
        else:
            return False
    
    def on_click(self):
        if self.dialog.held_num == self.global_count():
            self.dialog.held_num = None
        elif self.active:
            self.dialog.held_num = self.global_count()

class Snippet:
    def __init__(self, name, text='', icon=''):
        self.name = name
        self.text = text
        self.icon = icon
    def __str__(self):
        return self.icon + ' ' + self.name

class SnippetContainer:
    def __init__(self, snippets=(), \
                 icons='aqertyuiopasdfghjklzxcvbnm',
                 defname_prefix='New snippet'):
        self.snippets = list(snippets)
        
        self.defname_prefix = defname_prefix
        
        pref_re = re.escape(self.defname_prefix) + ' ([0-9]+)'
        i = 0
        for s in self.snippets:
            match = re.fullmatch(pref_re, s.name)
            if match is not None:
                i = max(i, int(match.group(1)))
        self.last_defname_num = i
        
        self.icons = icons
        self.icon_iter = cycle(self.icons)
        
        self.quick_access = [None]*9
        
        self.quick_access_subscriptions = dict()
        
    def next_defname(self):
        self.last_defname_num += 1
        
        return self.defname_prefix + ' ' + str(self.last_defname_num)
    
    def new_snippet(self, name=None, text=None, icon=None):
        
        if name is None: name = self.next_defname()
        if text is None: text = ''
        if icon is None: icon = next(self.icon_iter)
        sn = Snippet(name, text, icon)
        self.snippets.append(sn)
        return sn
    
    def snippet_description(self, i):
        return str(self.snippets[i])
    
    def call_quick_access_subscriptions(self):
        for subscribe in self.quick_access_subscriptions.values():
            subscribe()
    
    def set_quick_access(self, what, where):
        try:
            self.quick_access[where] = self.snippets[what]
        except IndexError:
            return
        
        self.call_quick_access_subscriptions()
    
    def remove_quick_access(self, what):
        try:
            quick_access[what] = None
        except IndexError:
            pass
        
        self.call_quick_access_subscriptions()
    
    def quick_access_subscribe(self, func, identity):
        self.quick_access_subscriptions[identity] = func
    
    def quick_access_unsubscribe(self, identity):
        del self.quick_access_subscriptions[identity]
    
    def __len__(self):
        return len(self.snippets)

class SnippetDialogBackButton(MenuEntry):
    def __init__(self, dialog, *groups, **kwargs):
        super().__init__('Back', *groups, **kwargs)
        
        self.dialog = dialog
        self.on_click = self.dialog.on_back
    
class SnippetDialogEditButton(MenuEntry):
    def __init__(self, dialog, *groups, **kwargs):
        super().__init__('Edit', *groups, **kwargs)
        
        self.dialog = dialog
        self.on_click = self.dialog.on_edit
    
    @property
    def active(self):
        return self.dialog.held_num is not None

class SnippetDialogCreateButton(MenuEntry):
    def __init__(self, dialog, *groups, **kwargs):
        super().__init__('Create', *groups, **kwargs)
        
        self.dialog = dialog
        self.on_click = self.dialog.on_create

class SnippetDialog(FixedWidthMenu):
    
    scrollbar_width = 20
    button_vspacing = 5
    # BUG: with width 400 it produces too small buttons
    width = 500
    
    def __init__(self, snippet_container=None,
                       entry_height = 5,
                       game = None,
                       screen_rect = None,
                       on_back = None,
                       **kwargs             ):
        
        if snippet_container is None:
            self.snippet_container = SnippetContainer()
        else:
            self.snippet_container = snippet_container
        
        if on_back is not None:
            self.on_back = on_back
        
        self.held_num = None
        
        entries = [SnippetEntry(self, i) for i in range(entry_height)]
        self.entry_height = entry_height
        
        super().__init__(self.width,
                         *entries,
                         screen_rect = screen_rect,
                         right_space = 50,
                         bottom_entries = [SnippetDialogBackButton(self),
                                           SnippetDialogEditButton(self),
                                           SnippetDialogCreateButton(self)],
                         title = 'Code Snippets',
                         bottom_button_align = HorizButtonsAlignWidth,
                         **kwargs)
        
        #sx = self.background.rect.right \
             #- self.button_h_inborders // 2 \
             #- self.scrollbar_width
        sx = self.buttons_rect.right
        sy = self.buttons_rect.y
        sw = self.scrollbar_width
        sh = self.buttons_rect.h
        
        scrollbar_rect = Rect(sx, sy, sw, sh)
        self.scrollbar = SnippetScrollBar(scrollbar_rect, self)
        self.add(self.scrollbar, layer=2)
    
    def snippet_description(self, i):
        return self.snippet_container.snippet_description(i)
    
    def on_back(self):
        pass
    
    def on_edit(self):
        pass
    
    def on_create(self):
        self.snippet_container.new_snippet()
        # maybe there is a better way to do this?
        for e in self.entries:
            e.update_text()
        

class SnippetQuickbarItem(Sprite):
    def __init__(self, quickbar, i):
        self.quickbar = quickbar
        super().__init__(quickbar)
        
        self.i = i
        
        self.rect = Rect(self.quickbar.rect.x \
                         + self.quickbar.quickbar_item_height * self.i,
                         self.quickbar.rect.y,
                         self.quickbar.quickbar_item_height,
                         self.quickbar.quickbar_item_height)
        
        self.update_image()
        
        self.quickbar \
            .container \
            .quick_access_subscribe(self.update_image, id(self))
            
    
    def draw_image(self):
        image = Surface((self.rect.w, self.rect.h))
        image_rect = image.get_rect()
        
        image.fill(self.quickbar.background_color)
        draw.rect(image,
                  self.quickbar.border_color,
                  image_rect,
                  self.quickbar.border_width)
        
        num_image, num_rect = self.quickbar \
                                  .number_font \
                                  .render(str(self.i+1),
                                          self.quickbar.number_font_color)
        num_rect.y     = image_rect.y     + self.quickbar.border_width
        num_rect.right = image_rect.right - self.quickbar.border_width
        
        image.blit(num_image, num_rect)
        
        if self.quickbar.container.quick_access[self.i] is not None:
            snippet = self.quickbar.container.quick_access[self.i]
            
            icon, icon_rect = self.quickbar \
                                  .font \
                                  .render(snippet.icon,
                                          self.quickbar.font_color)
            icon_rect.center = image_rect.center
            image.blit(icon, icon_rect)
        
        return image
    
    def update_image(self):
        self.image = self.draw_image()
        

class SnippetQuickbar(MetaLayeredUpdates):
    
    quickbar_item_height = 30
    border_width = 5
    
    background_color = Color('#694e33')
    border_color     = Color('#4a3724')
    
    number_font = FtSysFont('Liberation Mono', 15, bold=False)
    number_font_color = Color(30,30,30)
    
    font = FtSysFont('Liberation Mono', 20, bold=False)
    font_color = Color(0,0,0)
    
    def __init__(self, container, screen_rect = None,**kwargs):
        
        self.__dict__.update(kwargs)
        super().__init__()
        
        if screen_rect is None:
            self.screen_rect = pygame.display.get_surface().get_rect()
        else:
            self.screen_rect = Rect(screen_rect)
        
        self.container = container
        self.rect = Rect(0,0,
                         self.quickbar_item_height*9,
                         self.quickbar_item_height)
        self.rect.bottom = self.screen_rect.bottom
        self.rect.centerx = self.screen_rect.centerx
        
        self.items = [SnippetQuickbarItem(self, i) for i in range(9)]
    
if __name__ == '__main__':
    
    import argparse as ap
    from pygame.time import Clock
    import pygame.event
    
    parser = ap.ArgumentParser()
    
    parser.add_argument('entries', nargs='*', default=['Test'])
    parser.add_argument('-rw', '--resolution-width', type=int, default=0)
    parser.add_argument('-rh', '--resolution-height', type=int, default=0)
    parser.add_argument('--no-loop', action='store_true')
    
    args = parser.parse_args()
    
    pygame.init()
    pygame.mixer.quit()
    screen = pygame.display.set_mode((args.resolution_width, \
                                      args.resolution_height  ))
    pygame.display.set_caption('menu_test')
    
    clock = Clock()
    
    container = SnippetContainer([Snippet(name) for name in args.entries])
    menu = SnippetDialog(container)
    
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
