import pygame
import pygame.display
from extended_groups import LayeredUpdates, MetaLayeredUpdates
from menu import Menu, MenuEntry, QuestionMenu
from button import PreparedButton
from pygame import Surface, Rect, Color
import pygame.locals
import pygame.draw as draw
from pygame.font import Font
from pygame.sprite import GroupSingle
from gameboard.map import GameMap
from math import ceil
from extended_groups import Sprite

from pygame.image import load as load_image

from snippets import SnippetDialog, SnippetContainer, SnippetQuickbar

from stats import StatBarGroup

import os
import os.path
import json
from time import time
from datetime import datetime

START_MENU_LAYER = 10
PAUSE_BUTTON_LAYER = 9

LEVEL_LAYER = 2

class StartMenu(Menu):
    
    def __init__(self, game, screen_rect=None):
        
        self.game = game
        
        newgame_entry  = MenuEntry('New Game', on_click = self.game.new_game)
        loadgame_entry = MenuEntry('Load Game', \
                            on_click = lambda: self.game.open_load(False),
                            active = LoadMenu.is_anything_to_load())
        exit_entry = MenuEntry('Exit', on_click = self.on_exit_button)
        
        self.loadgame_entry = loadgame_entry
        
        super().__init__(
            newgame_entry,
            loadgame_entry,
            exit_entry,
            screen_rect = screen_rect,
            title = 'Main Menu'
            )
    def on_exit_button(self):
        
        self.game.add_menu(
            ExitConfirmationMenu(self.game,
                                 self.game.exit_game,
                                 self.game.start_menu
                                )
        )
    def on_added_to_LU(self, where):
        self.loadgame_entry.active = LoadMenu.is_anything_to_load()

class PauseMenu(Menu):
    
    def __init__(self, game, screen_rect=None):
        
        self.game = game
        
        continue_entry  = MenuEntry('Continue', on_click = self.game.continue_game)
        savegame_entry = MenuEntry('Save Game',on_click = self.game.open_save)
        loadgame_entry = MenuEntry('Load Game', \
                            on_click = lambda: self.game.open_load(True),
                            active = LoadMenu.is_anything_to_load())
        newgame_entry = MenuEntry('New Game', on_click = self.on_newgame_button)
        snippets_entry = MenuEntry('Snippets', on_click = self.on_snippets_button)
        exit_entry = MenuEntry('Exit', on_click = self.on_exit_button)
        
        self.loadgame_entry = loadgame_entry
        
        super().__init__(
            continue_entry,
            savegame_entry,
            loadgame_entry,
            newgame_entry,
            snippets_entry,
            exit_entry,
            screen_rect = screen_rect,
            title = 'Pause Menu'
            )
    def on_exit_button(self):
        self.game.add_menu(
            ExitConfirmationMenu(self.game,
                                 self.game.start_menu,
                                 self.game.pause_game,
                                 question = 'Are you sure you want to ' \
                                            'go to the Main Menu?'
                                )
        )
    def on_newgame_button(self):
        self.game.add_menu(
            ExitConfirmationMenu(self.game,
                                 self.game.new_game,
                                 self.game.pause_game
                                )
        )
    
    def on_snippets_button(self):
        
        def on_back():
            self.game.add_menu(self)
        
        self.game.add_menu(
            SnippetDialog(snippet_container = self.game.snippet_container,
                          on_back = on_back)
        )
        
    def on_added_to_LU(self, where):
        self.loadgame_entry.active = LoadMenu.is_anything_to_load()

class SaveSlot(MenuEntry):
    save_dir = './save'
    
    def __init__(self, number, *groups, **kwargs):
        
        self.number = number
        self.filename = os.path.join(self.save_dir,
                                     str(self.number)+'.json')
        
        active = True
        
        text, corrupted = self.get_description()
        
        super().__init__(text, *groups, active = not corrupted, **kwargs)
    
    def ensure_savepath(self):
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
        else:
            if not os.path.isdir(self.save_dir):
                mv_name = self.save_dir
                while os.path.exists(mv_name):
                    mv_name = mv_name + '.old'
                
                os.rename(self.save_dir, mv_name)
                
                self.ensure_savepath()
    
    def get_description(self):
        
        corrupted = False
        
        if os.path.isfile(self.filename):
            try:
                text = datetime.fromtimestamp( self.load()['timestamp'] ) \
                               .strftime('%d %b %Y %H:%M')
            except Exception as e:
                print(e)
                text = '<corrupted save>'
                corrupted = True
        else:
            text = '[empty]'
        
        return text, corrupted
    
    def save(self):
        self.ensure_savepath()
        with open(self.filename, mode='wt') as f:
            json.dump({'timestamp':time()}, f)
        
        self.text, corrupted = self.get_description()
        self.active = not corrupted
        # this is supposed to br done automatically, but...
        self.menu.changed=True
        self.menu.update()
        
    def load(self):
        with open(self.filename, mode='rt') as f:
            return_value = json.load(f)
        return return_value
    
    def on_click(self):
        if os.path.isfile(self.filename):
            # This part is tricky.
            # Teoretically, buttons of SaveMenu still can receive
            # keystrokes even when they are invisible.
            #
            # But, they do not receive .update() calls while they
            # are removed from the Game group. So, all is fine.
            
            def on_yes():
                self.save()
                self.menu.game.add_menu(self.success_question())
            
            def on_no():
                self.menu.game.add_menu(self)
            
            yes = MenuEntry('yes')
            yes.on_click = on_yes
            
            no  = MenuEntry('no')
            no.on_click  = on_no
            
            self.menu.game.add_menu(
                QuestionMenu('Are you sure you want to use this Save slot? It will remove a previous saving.',
                             yes,
                             no
                            )
            ) 
        else:
            self.save()
            self.menu.game.add_menu(self.success_question())
    
    def success_question(self):
        
        def on_ok():
            self.menu.game.add_menu(self)
        
        ok = MenuEntry('ok')
        ok.on_click = on_ok
        
        return QuestionMenu('The game was successfully saved.', ok)

class LoadSlot(SaveSlot):
    
    def __init__(self, number, *groups, **kwargs):
        super().__init__(number, *groups, **kwargs)
        
        self.active = os.path.isfile(self.filename)
    
    def on_click(self):
        
        if self.menu.confirmation:
            
            def on_yes():
                self.menu.game.new_game()
            
            def on_no():
                self.menu.game.add_menu(self)
                        
            yes = MenuEntry('yes')
            yes.on_click = on_yes
            
            no  = MenuEntry('no')
            no.on_click  = on_no
            
            self.menu.game.add_menu(
                QuestionMenu('Do you want to continue?',
                             yes,
                             no
                            )
            )
        else:
            self.menu.game.new_game()

class SaveSlotMenu(Menu):
    
    def __init__(self, game, return_to, slot_entry_class, title, screen_rect=None):
        
        self.game = game
        self.return_to = return_to
        
        firstSlot_entry  = slot_entry_class(1)
        secondSlot_entry = slot_entry_class(2)
        thirdSlot_entry  = slot_entry_class(3)
        
        def on_back():
            self.game.add_menu(self.return_to)
        
        back_entry = MenuEntry('back', on_click = on_back)
        
        super().__init__(
            firstSlot_entry,
            secondSlot_entry ,
            thirdSlot_entry,
            bottom_entries = [back_entry],
            screen_rect = screen_rect,
            title = title
            )
                                

class SaveMenu(SaveSlotMenu):
    def __init__(self, game, return_to, screen_rect=None):
        super().__init__(game, return_to, SaveSlot, 'Save Menu', screen_rect)

class LoadMenu(SaveSlotMenu):
    def __init__(self, game, return_to, confirmation=False, screen_rect=None):
        self.confirmation = confirmation
        super().__init__(game, return_to, LoadSlot, 'Load Menu', screen_rect)

    @staticmethod
    def is_anything_to_load(save_dir = SaveSlot.save_dir):
        for i in range(1,4):
            filename = os.path.join(save_dir, str(i)+'.json')
            if os.path.isfile(filename):
                return True
        return False

class PauseButton(PreparedButton):
    
    border_step = (-15, -15)
    border_width = 5
    
    button_h_inborders = 20
    button_v_inborders = 15
    
    font = Font(None, 45)
    
    def __init__(self, text, game, screen_rect=None, **kwargs):
        
        self.__dict__.update(kwargs)
        self.text = text
        self.game = game
        
        if screen_rect is None:
            self.screen_rect = pygame.display.get_surface().get_rect()
        else:
            self.screen_rect = Rect(screen_rect)
        
        text_w, text_h = self.font.size(text)
        
        self.rect = Rect(0, \
                         0, \
                         text_w * ceil(2**0.5) + 2*self.button_h_inborders, \
                         text_h * ceil(2**0.5) + 2*self.button_v_inborders  )
        self.rect.top   = self.screen_rect.top
        self.rect.right = self.screen_rect.right
        
        normal_img = self.draw_button(self.button_background_color,
                                      self.button_border_color      )
        
        touched_img = self.draw_button(self.button_touched_background_color,
                                       self.button_touched_border_color      )
        
        pressed_img = self.draw_button(self.button_pressed_background_color,
                                       self.button_pressed_border_color      )
        
        inactive_img = self.draw_button(self.button_inactive_background_color,
                                       self.button_inactive_border_color      )
        images = {'normal': normal_img,     \
                  'touched': touched_img,   \
                  'pressed': pressed_img,   \
                  'inactive': inactive_img  }
        
        super().__init__(self.rect, images)
        
    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
    
    def draw_button(self, bg_color, border_color):
        
        
        w = self.rect.w
        h = self.rect.h
        
        image = Surface((w, h), flags = pygame.locals.SRCALPHA)
        
        bg_rect = Rect(0, -h, 2*w, 2*h)
        draw.ellipse(image, bg_color, bg_rect)
        
        border_rect = bg_rect.inflate(*self.border_step)
        draw.ellipse(image, border_color, border_rect, self.border_width)
        
        text_img = self.font.render(self.text, True, (0,0,0), bg_color)
        text_rect = text_img.get_rect()
        text_w, text_h = text_rect.w, text_rect.h
        text_rect = Rect(0, 0, text_w, text_h)
        text_rect.right = w - self.button_h_inborders
        text_rect.top   = self.button_v_inborders
        
        image.blit(text_img, text_rect)
        
        return image
    def on_click(self):
        game.pause_game()

class SnippetButton(PauseButton):
    def __init__(self, text, game, screen_rect=None, **kwargs):
        super().__init__(text, game, screen_rect, **kwargs)
        self.rect.bottom = self.screen_rect.bottom
    
    def draw_button(self, bg_color, border_color):
        
        w = self.rect.w
        h = self.rect.h
        
        image = Surface((w, h), flags = pygame.locals.SRCALPHA)
        
        bg_rect = Rect(0, 0, 2*w, 2*h)
        draw.ellipse(image, bg_color, bg_rect)
        
        border_rect = bg_rect.inflate(*self.border_step)
        draw.ellipse(image, border_color, border_rect, self.border_width)
        
        text_img = self.font.render(self.text, True, (0,0,0), bg_color)
        text_rect = text_img.get_rect()
        text_w, text_h = text_rect.w, text_rect.h
        text_rect = Rect(0, 0, text_w, text_h)
        text_rect.right = w - self.button_h_inborders
        text_rect.bottom   = h - self.button_v_inborders
        
        image.blit(text_img, text_rect)
        
        return image
    
    def on_click(self):
        pass

class ExitConfirmationMenu(QuestionMenu):
    def __init__(self, game, on_yes, on_no,
                 question = 'Are you sure you want to leave the game?'):
        
        yes_entry = MenuEntry('Yes', on_click = on_yes)
        no_entry  = MenuEntry('No',  on_click = on_no)
        
        super().__init__(question, yes_entry, no_entry)
        self.game = game

class Game(MetaLayeredUpdates):
    
    def __init__(self, config, surface = None):
        super().__init__()
        
        self.config = config
        if surface is None:
            self.surface = pygame.display.get_surface()
        else:
            self.surface = surface
        
        self.pause_button = None
        self.game_map = None
        self.menu = None

        
        self.snippet_container = None
        
    def inc_frame(self):
        if self.game_map is None:
            return
        else:
            self.game_map.inc_frame()
            
    
    def add_menu(self, menu):
        
        if self.menu is not None:
            self.remove_menu()
        
        self.menu = menu

        self.addLU(menu, START_MENU_LAYER)
    
    def remove_menu(self):
        try:
            self.menu.sprites
        except AttributeError:
            return
        
        self.removeLU(self.menu)
        
        # TODO: maybe there is a better way to clean?
        try:
            draw.rect(self.surface, (0,0,0), self.menu.background.rect)
        except AttributeError:
            pass

        
        self.menu = None
    #######Denis######################
    def open_save(self):
        self.add_menu(SaveMenu(self, self.menu))
    
    def open_load(self, confirmation = False):
        self.add_menu(LoadMenu(self, self.menu, \
                               confirmation = confirmation))

    #def back_save(self):
        #self.add_menu(PauseMenu(self))
    ###################################
    
    def new_game(self):
        
        self.remove_menu()
        
        self.snippet_container = SnippetContainer()\
        
        self.open_level('level0')
    
    def open_level(self, level_name):
        self.close_level()
        
        self.pause_button = PauseButton('Pause', self)
        #self.snippet_button = SnippetButton('Snippets', self)
        self.snippet_button = None
        self.add(self.pause_button, layer = PAUSE_BUTTON_LAYER)
        #self.add(self.snippet_button, layer = PAUSE_BUTTON_LAYER)
        
        self.snippet_quickbar = SnippetQuickbar(self.snippet_container)
        self.statbar = StatBarGroup()
        
        help_image = Sprite()
        help_image.image = load_image('instructions.png')
        help_image.rect  = help_image.image.get_rect()
        help_image.rect.right = self.surface.get_rect().right
        help_image.rect.bottom = self.surface.get_rect().bottom
        
        self.add(help_image, layer = PAUSE_BUTTON_LAYER)
        
        self.game_ui_buttons = [self.pause_button, help_image]
        self.game_ui_groups  = [self.snippet_quickbar, self.statbar]
        for group in self.game_ui_groups:
            self.addLU(group, start_layer = PAUSE_BUTTON_LAYER)
        
        def on_sprite_add(sprite):
            # Simply adding sprite does not work. Why??!!!
            #self.add(sprite, level = 500)
            self.addLA(self.game_map, LEVEL_LAYER)
        
        self.game_map =  GameMap.from_file(self.config[level_name]['config'],
                                           on_sprite_add = on_sprite_add)
        if self.game_map.player is not None:
            self.statbar.subscribe_on_unit(self.game_map.player)
        self.addLA(self.game_map, LEVEL_LAYER)
        
    def close_level(self):
        try:
            self.game_map.sprites
        except AttributeError:
            return
        
        self.remove( self.game_map.sprites() )
        # TODO: maybe there is a better way to clean?
        try:
            draw.rect(self.surface, (0,0,0), self.game_map.background.rect)
        except AttributeError:
            pass
        self.game_map = None
        
        assert self.pause_button is not None
        
        self.remove( *self.game_ui_buttons )
        for group in self.game_ui_groups:
            self.removeLU(group)
        # TODO: maybe there is a better way to clean?
        try:
            for b in self.game_ui_buttons:
                draw.rect(self.surface, (0,0,0), b.rect)
        except AttributeError:
            pass
        
        for group in self.game_ui_groups:
            for s in group.sprites():
                try:
                    rect = s.image.get_rect()
                    rect.x = s.rect.x
                    rect.y = s.rect.y
                    draw.rect(self.surface, (0,0,0), rect)
                except AttributeError:
                    pass
        
        self.remove( self.pause_button )
        self.pause_button = None
        self.snippet_button = None
        self.statbar = None
        self.game_ui_buttons = []
        self.game_ui_groups = []
    
    def pause_game(self):
        
        self.game_map.pause_event = True
        
        for b in self.game_ui_buttons:
            b.active = False
        
        self.add_menu(PauseMenu(self))
        
    
    def continue_game(self):
        
        self.game_map.pause_event = False
        
        for b in self.game_ui_buttons:
            b.active = True
        
        self.remove_menu()
        
    
    def exit_game(self):
        
        global run
        
        run = False
    
    def start_menu(self):
        self.close_level()
        self.snippet_container = None
        self.add_menu(StartMenu(self))
    
if __name__ == '__main__':
    
    import argparse as ap
    import configparser
    
    from pygame.time import Clock
    
    parser = ap.ArgumentParser()
    parser.add_argument('--config',
                        default='game.config',
                        help="game's config filename")
    parser.add_argument('--no-loop', action='store_true')
    parser.add_argument('--windowed', action='store_true')
    args = parser.parse_args()
    
    game_config = configparser.ConfigParser()
    game_config.read( args.config )
    
    pygame.init()

    pygame.mixer.quit()
    pygame.key.set_repeat(200, 200)
    
    screen = pygame.display.set_mode(
        tuple(int(d) for d \
                     in game_config.get('display',
                                        'dimensions',
                                        fallback = '-1x-1').split('x')
        ),
        flags = 0 if args.windowed else pygame.FULLSCREEN
    )
    
    game = Game(game_config)
    start_menu = StartMenu(game)
    game.add_menu(start_menu)
    
    clock = Clock()
    run = True
    while run:
        clock.tick(30)
        
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.locals.QUIT:
                run = False
        keydown_events = list(filter(lambda e: e.type == pygame.KEYDOWN, events))

        game.update(keydown_events = keydown_events)
        rect_list = game.draw(screen)
        pygame.display.update(rect_list)
        
        
    pygame.quit()
