#!/usr/bin/env python3

import pygame
import pygame.locals
from math import ceil
from itertools import accumulate

"""
Note:   In pygame it is supposed, that in pair of coordinates (x, y)
        the first is a horizontal coordinate, and the second
        is vertical.
"""

class TileCollection:
    """
    Base class to contain tile collection.
    """
    def __init__(self, tile_table):
        """
        tile_table: list of lists with Surface instances
        
        WARNING: It is expected, that tile_table contains
                 list of "columns".
        """
        
        if not (len(tile_table) > 0):
            raise Exception('empty tile_table')
        
        if max(len(column) for column in tile_table) != \
           min(len(column) for column in tile_table)    :
            raise Exception('noneven columns in tile_table')
        
        self.tile_table = tile_table
        self.tile_width, self.tile_height = tile_table[0][0].get_size()
        
        for row in tile_table:
            for s in row:
                if s.get_size() != (self.tile_width, self.tile_height):
                    raise Exception('noneven sizes of Surfaces in tile_table')
    
    def blit(self, tile, dest, pos, area = None, special_flags = 0):
        """
            tile:   tuple with tile's (column, row)
                    in this TileCollection
            dest:   Surface to draw onto
            pos:    (x, y) tuple of coordinates in \dest\ Surface
                    to draw the tile onto.
                    It can also be a Rect object; in that case its
                    width and height will be ignored.
            
            area:           passed to the Surface.blit() method as is;
                            means part of the tile to draw
                            (I don't know if this will ever be needed.
                             Added for consistency.)
            special_flags:  passed to the Surface.blit() method as is.
        """
        
        return dest.blit(self.tile_table[tile[0]][tile[1]],
                         pos,
                         area = area,
                         special_flags = special_flags)
    
    def blits(self, dest, blit_sequence):
        """
        dest:   Surface to draw onto
        blit_sequence:  iterable of tuples of descriptions for what
                        and where to draw:
                        ((tile, pos, area = None, special_flags = 0) ... )
        """
        
        def bs_convert(args):
            tile = args[0]
            pos  = args[1]
            try:
                area = args[2]
            except IndexError:
                area = None
            try:
                special_flags = args[3]
            except IndexError:
                special_flags = 0
            
            return (self.tile_table[tile[0]][tile[1]],
                    pos,
                    area,
                    special_flags)
        
        dest.blits(list(map(bs_convert, blit_sequence)))
        
    def blit_tile_map(self, surface, x=0, y=0, x_step=8, y_step=8):
        """
        blit (paint) wole tile collection onto surface;
        intended for demo
        
        surface: where to blit
        x, y:    position to start
        x_step, y_step: indentation between columns and rows
        """
        
        # TODO: rewrite this legacy
        
        column_widths = [ max(s.get_size()[0] for s in column) + x_step \
                       for column in self.tile_table          ]
        
        row_heights = \
            [ max(self.tile_table[i][j].get_size()[1] + y_step \
                    for i in range(len(self.tile_table)) \
                 ) \
              for j in range(len(self.tile_table[0])) \
            ]
        
        row_starts = [0] + list(accumulate(row_heights))
        column_starts = [0] + list(accumulate(column_widths))
        
        for i, column in enumerate(self.tile_table):
            for j, tile in enumerate(column):
                surface.blit(tile, (x+column_starts[i], y+row_starts[j]))
        
    
class TileCollectionFromFile(TileCollection):
    """
    Intended to load tile collection from image file.
    """
    def __init__(self, filename, tile_width, tile_height):
        """
        filename:                path to image
        tile_width, tile_height: self-explanatory
        """
        
        image = pygame.image.load(filename).convert()
        image_width, image_height = image.get_size()
        tile_table = []
        for tile_x in range(0, ceil(image_width/tile_width)):
            line = []
            tile_table.append(line)
            for tile_y in range(0, ceil(image_height/tile_height)):
                rect = (tile_x*tile_width, tile_y*tile_height, \
                        tile_width, tile_height)
                line.append(image.subsurface(rect))
        
        self.full_image = image
        super().__init__(tile_table)
    
    @classmethod
    def from_descriotion(cls, section):
        """
            section: a dict-like object, which describes 
                     tile collection as in 'TileCollecton' section
                     of map description.
        """
        
        return cls(section['tile_image'],
                   int(section['tile_width']),
                   int(section['tile_height'])
                  )
        

if __name__ == '__main__':
    
    import argparse as ap
    
    parser = ap.ArgumentParser()
    parser.add_argument('file_name')
    parser.add_argument('-W', '--tile-width', type=int, default=24)
    parser.add_argument('-H', '--tile-height', type=int, default=16)
    parser.add_argument('-sx', '--x-step', type=int, default=8)
    parser.add_argument('-sy', '--y-step', type=int, default=8)
    parser.add_argument('-x', type=int, default=0)
    parser.add_argument('-y', type=int, default=0)
    parser.add_argument('-rw', '--resolution-width', type=int, default=0)
    parser.add_argument('-rh', '--resolution-height', type=int, default=0)
    parser.add_argument('--no-loop', action='store_true')
    
    args = parser.parse_args()
    
    pygame.display.init()
    
    screen = pygame.display.set_mode((args.resolution_width, \
                                      args.resolution_height  ))
    pygame.display.set_caption('tilecollection_test')
    
    tile_table = TileCollectionFromFile(args.file_name,
                                        args.tile_width,
                                        args.tile_height)
    
    tile_table.blit_tile_map(screen, args.x,
                                     args.y,
                                     args.x_step,
                                     args.y_step )
    
    pygame.display.flip()
    
    if not args.no_loop:
        while pygame.event.wait().type != pygame.locals.QUIT:
            pass
    
