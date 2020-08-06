#!/usr/bin/env python3

from configparser import ConfigParser
from gameboard.tilecollection import TileCollectionFromFile

import pygame
import pygame.display
from extended_groups import Sprite, LayeredUpdates
from pygame import Rect
from unit import Unit, Mob, Player,Ghost
import re

class Turn():
    def __init__(self, game_map):
        
        self.game_map = game_map
        
        self.restart_queue()
    
    def current(self):
        if self.is_empty():
            return None
        else:
            return self.units[self.current_num]
    
    def release (self, unit):
        if self.current() is unit:
            self.current_num += 1
        
        if self.is_empty():
            self.restart_queue()
    
    def is_empty(self):
        if self.current_num >= len(self.units):
            return True
    
    def restart_queue(self):
        
        self.units = [self.game_map.player]
        self.units.extend(self.game_map.ghosts)
        self.units.extend(self.game_map.mobs)
        
        self.current_num = 0
    

class GameMap(LayeredUpdates):
    """
    Attributes:
    
    .map:   Contains array of **rows** of tile-describing characters.
    .key:   A dict() containing pairs of tile's describing characters
            and their full descriptions.
    
    .width  Width of map in tiles.
    .height Height of map in tiles.
    
    .pixel_width    Width of map in pixels.
    .pixel_height   Height of map in pixels.
    """
    def __init__(self, parser, screen_rect = None, on_sprite_add = None):
        """
            parser: a valid ConfigParser-like object;
            screen_rect: rect of screen, on which this background sprite
            will be rendered
        """
        
        super().__init__()
        
        if on_sprite_add is not None:
            self.on_sprite_add = on_sprite_add
        
        self.key = {}
        
        self.tile_collection = TileCollectionFromFile.from_descriotion(
                                 parser['TileCollecton'])
                               
        self.map = parser.get("level", "map").split("\n")
        
        for section in parser.sections():
            if len(section) == 1:
                desc = dict(parser.items(section))
                self.key[section] = desc
        
        self.width = len(self.map[0])
        self.height = len(self.map)
        
        self.pixel_width  = self.width  * self.tile_collection.tile_width
        self.pixel_height = self.height * self.tile_collection.tile_height

        

        self.pause_event = False
        
        
        if screen_rect is None:
            self.screen_rect = pygame.display.get_surface().get_rect()
        else:
            self.screen_rect = screen_rect
        
        self.background = Sprite()
        self.background.image = self.render()
        self.background.rect = self.background.image.get_rect()
        self.background.rect.center = self.screen_rect.center
        self.add(self.background, layer = 0)
        
        self.player = None
        try:
            player_section = parser['player']
        except KeyError:
            player_section = None

        if player_section is not None:

            self.player = Player.from_config_section(player_section, self)
            self.add(self.player, layer = 1)
        
        self.mobs = []
        
        
        
        for name, section in parser.items():
            if re.fullmatch('Mob_.*', name):
                self.mobs.append( Mob.from_config_section(section, self) )
                self.add(self.mobs[-1], layer = 1)
        
        self.ghosts = []
        self.ghost_limb = None
        try:
            ghost_limb_section = parser['ghost']
        except KeyError:
            ghost_limb_section = None

        self.ghost_limb_section = ghost_limb_section

        #self.ghosts_in_limbo = []
        #for name, section in parser.items():
         #   if re.fullmatch('Ghost_.*', name):
          #      self.ghosts_in_limbo.append(Ghost.from_config_section(section, self))
                #self.add(self.ghosts[-1], layer = 1)
                
        self.turn_queue = Turn(self)
    
    def on_sprite_add(self, sprite):
        pass
    
    def ghost_birth(self):
        self.ghosts.append(Ghost.from_config_section(self.ghost_limb_section, self))
        self.add(self.ghosts[-1], layer = 1)
        self.on_sprite_add(self.ghosts[-1])

    @property
    def hp(self):
        return self.player.hp
    
    @property
    def mp(self):
        return self.player.mp
    
    @classmethod
    def from_file(cls, map_filename, **kwargs):
        parser = ConfigParser()
        parser.read(map_filename)
           
        return cls(parser, **kwargs)
    
    def get_tile(self, x, y):
        try:
            char = self.map[y][x]
        except IndexError:
            return {}
        try:
            return self.key[char]
        except KeyError:
            return {}
    
    def get_tile_id(self, x, y):
        return tuple(map(int, self.get_tile(x, y) ['tile'] .split(',')))
        
    def get_bool(self, x, y, name):
        """Tell if the specified flag is set for position on the map."""

        value = self.get_tile(x, y).get(name)
        return value in (True, 1, 'true', 'yes', 'True', \
                         'Yes', '1', 'on', 'On')
    def is_wall(self, x, y):
        """Is there a wall?"""

        return self.get_bool(x, y, 'wall')

    def is_blocking(self, x, y):
        """Is this place blocking movement?"""

        if not 0 <= x < self.width or not 0 <= y < self.height:
            return True
        return self.get_bool(x, y, 'block')
    
    def render(self, image = None):
        
        tile_width  = self.tile_collection.tile_width
        tile_height = self.tile_collection.tile_height
        
        if image is None:
            image = pygame.Surface((self.pixel_width, self.pixel_height))
        
        blit_sequence = list()
        for x in range(self.width):
            for y in range(self.height):
                blit_sequence.append((self.get_tile_id(x, y),
                                      (x*tile_width, y*tile_height)
                                     )
                                    )
        
        self.tile_collection.blits(image, blit_sequence)
        
        return image
        
        

if __name__ == '__main__':
    
    import argparse as ap
    
    parser = ap.ArgumentParser()
    parser.add_argument('file_name', help='filename if .map file')
    #parser.add_argument('-x', type=int, default=0)
    #parser.add_argument('-y', type=int, default=0)
    parser.add_argument('-rw', '--resolution-width', type=int, default=0)
    parser.add_argument('-rh', '--resolution-height', type=int, default=0)
    parser.add_argument('--no-loop', action='store_true')
    
    args = parser.parse_args()
    
    pygame.display.init()
    screen = pygame.display.set_mode((args.resolution_width, \
                                      args.resolution_height  ))
    pygame.display.set_caption('map_test')
    
    gm = GameMap.from_file(args.file_name)
    gm.render(screen)
    pygame.display.flip()
    
    if not args.no_loop:
        while pygame.event.wait().type != pygame.locals.QUIT:
            pass
