#!/usr/bin/env python3

from extended_groups import Sprite, LayeredUpdates
from pygame.freetype import SysFont
import pygame.freetype
from pygame import Color, Surface, Rect
import pygame.draw as draw
import pygame.locals

from itertools import accumulate

import pygame.time

pygame.freetype.init()

class TextLine(Sprite):
    """
    Instane attributes:
        .full_rect      contains borders of text line
        .image_rect     borders of line's image; where to render it
        .render_rect    Rect(), returned by renderer
    """
    
    
    valuable_attributes = {'line', 'x', 'y'}
    
    invisible_image = Surface((0,0))
    
    def __init__(self, editor=None, prev_line=None, next_line=None, **kwargs):
        
        self.__dict__.update(kwargs)
        
        if editor is None:
            if prev_line is not None:
                editor = prev_line.editor
            elif prev_line is not None:
                editor = next_line.editor
            else:
                raise Exception('editor for new text line was not provided')
        
        if __debug__:
            test = []
            if editor is not None:
                test.append( editor )
            elif prev_line is not None:
                test.append( prev_line.editor )
            elif next_line is not None:
                test.append( next_line.editor )
            
            for i in range(len(test) - 1):
                if test[i] is not test[i+1]:
                    raise Exception('Inconsistent editors '
                                    'in TextLine() chain'  )
        
        self.editor = editor
        
        super().__init__()
        self.editor.add(self, layer=1)
        
        self.prev_line = prev_line
        self.next_line = next_line
        
        self.full_rect = Rect(0,0,0,self.font.get_sized_height())
        self.image_rect = Rect(0,0,0,self.font.get_sized_height())
        
        self.line = ''
        
        self.x_advances = [0]
        
        self.visible = 0
    
    @property
    def h(self):
        return self.full_rect.h
    
    height = h
    
    @property
    def bottom(self):
        return self.full_rect.bottom
    
    @property
    def top(self):
        return self.full_rect.top
    
    @property
    def y(self):
        return self.full_rect.y
    
    def _get_line(self):
        return self._line
    def _set_line(self, line):
        self._line = line
        self.real_image, self.render_rect = self.font.render(
            self._line,
            bgcolor=self.colorscheme['default']['bgcolor'],
            fgcolor=self.colorscheme['default']['fgcolor']
        )
        self.image_rect.w = self.render_rect.w
        self.image_rect.h = self.render_rect.h
        
        self.full_rect.w = self.render_rect.w
        self.image_rect.y =   self.full_rect.y \
                            + self.font.get_sized_ascender() \
                            - self.render_rect.y
        
        self.x_advances = [0]+list(accumulate(map(lambda m: m[4], self.font.get_metrics(line))))
        
    line = property(_get_line, _set_line)
    
    def _get_x(self):
        return self.full_rect.x
    def _set_x(self, x):
        self.full_rect.x = x
        self.image_rect.x = x
    x = property(_get_x, _set_x)
    
    def _get_y(self):
        return self.full_rect.y
    def _set_y(self, y):
        self.full_rect.y = y
        self.image_rect.y = y + self.font.get_sized_ascender() - self.render_rect.y
    
    y = property(_get_y, _set_y)
    
    def __getattr__(self, name):
        try:
            return super().__getattr__(name)
        except AttributeError:
            return getattr(self.editor, name)
    
    def insert_newline(self):
        new = type(self)(prev_line=self, next_line=self.next_line)
        
        if self.next_line is not None:
            self.next_line.prev_line = new
        self.next_line = new
        
        return new
    
    @property
    def rect(self):
        return self.image_rect
    
    @property
    def image(self):
        if self.visible:
            return self.real_image
        else:
            return self.invisible_image
    
    def __iter__(self):
        current_line = self
        while current_line is not None:
            yield current_line
            current_line = current_line.next_line
    
    def del_line(self):
        self.kill()
        if self.prev_line is not None:
            self.prev_line.next_line = self.next_line
        if self.next_line is not None:
            self.next_line.prev_line = self.prev_line
    
class TextEditor(LayeredUpdates):
    
    font = SysFont('Liberation Mono', 15, bold=False)
    
    colorscheme = {'default':{'bgcolor':Color('#1e1e27'),
                              'fgcolor':Color('#cfbfad')},
                   'caret':  {'bgcolor':Color('#8b8bff')}
                  }
    
    caret_width = 1
    caret_ticks = 500
    
    def __init__(self, rect=None, text='', **kwargs):
        super().__init__()
        
        self.__dict__.update(kwargs)
        
        if rect is None:
            self.rect = pygame.display.get_surface().get_rect()
        else:
            self.rect = Rect(rect)
        
        # add background
        self.background = Sprite()
        self.background.rect = self.rect
        self.background.image = Surface((self.rect.w, self.rect.h))
        draw.rect(self.background.image,
                  self.colorscheme['default']['bgcolor'],
                  self.background.image.get_rect())
        self.add(self.background, layer=0)
        
        self.overwrite_text(text)
        self.caret = TextCaret(self, self.first_visible_line)
        
    def overwrite_text(self, text=''):
        lines = text.split('\n')
        
        self.first_visible_line = TextLine(self)
        self.first_visible_line.line = lines[0]
        
        last_line = self.first_visible_line
        for i in range(1, len(lines)):
            last_line = last_line.insert_newline()
            last_line.line = lines[i]
        
        self.reposition_lines()
    
    def reposition_lines(self):
        y = self.rect.y
        for line in self.first_visible_line:
            line.x = self.rect.x
            line.y = y
            line.visible = 1
            y += line.height
            
            if y >= self.rect.bottom:
                break
        self.last_visible_line = line
        
        next_line = self.last_visible_line.next_line
        while next_line is not None and next_line.visible:
            next_line.visible = 0
            next_line = next_line.next_line
        
        prev_line = self.first_visible_line.prev_line
        while prev_line is not None and prev_line.visible:
            prev_line.visible = 0
            prev_line = prev_line.prev_line
        
    def scroll(self, lines=1):
        
        moved = 0
        
        if lines > 0:
            first_visible_line = self.first_visible_line
            while lines > 0 and first_visible_line.next_line is not None:
                first_visible_line = first_visible_line.next_line
                lines -= 1
                moved += 1
            self.first_visible_line = first_visible_line
            self.reposition_lines()
        elif lines < 0:
            first_visible_line = self.first_visible_line
            while lines < 0 and first_visible_line.prev_line is not None:
                first_visible_line = first_visible_line.prev_line
                lines += 1
                moved -= 1
            self.first_visible_line = first_visible_line
            self.reposition_lines()
        
        return moved

class TextCaret(Sprite):
    
    invisible_image = Surface((0,0))
    
    def __init__(self, editor, text_line, position=0, **kwargs):
        
        self.__dict__.update(kwargs)
        
        self.editor = editor
        
        
        self.text_line = text_line
        self.position = position
        
        self.master_surface = None
        
        super().__init__()
        self.editor.add(self, layer=2)
    
    @property
    def real_image(self):
        
        w = self.caret_width
        h = self.text_line.height
        
        if self.master_surface is None:
            self.master_surface = Surface((w,h))
            draw.rect(self.master_surface,
                      self.colorscheme['caret']['bgcolor'],
                      self.master_surface.get_rect()
                     )
        
        master_rect = self.master_surface.get_rect()
        if master_rect.w < w or master_rect.h < h:
            mw = max(w, master_rect.w)
            mh = max(h, master_rect.h)
            
            self.master_surface = Surface(mw,mh)
            
            draw.rect(self.master_surface,
                      self.colorscheme['caret']['bgcolor'],
                      self.master_surface.get_rect()
                     )
        rect = self.rect
        
        rect.w = w
        rect.h = h
        rect = rect.clip(self.editor.rect)
        rect.x = 0
        rect.y = 0
        
        return self.master_surface.subsurface(rect)
    
    @property
    def image(self):
        if self.visible:
            return self.real_image
        else:
            return self.invisible_image
    
    @property
    def rect(self):
        position = max(min(self.position, len(self.text_line.line)), 0)
        x =   self.editor.rect.x \
            + self.text_line.x_advances[position]
        y = self.text_line.full_rect.y
        return Rect(x, y, 100, 100)
    
    @property
    def visible(self):
        return (  pygame.time.get_ticks() % (self.caret_ticks * 2) \
                - self.caret_ticks
               ) > 0 \
               and self.text_line.visible
    
    def __getattr__(self, name):
        try:
            return super().__getattr__(name)
        except AttributeError:
            
            if type(getattr(type(self), name, None)) is property:
                getattr(type(self), name).fget(self)
            
            return getattr(self.editor, name)
    
    def move_right(self):
        self.position = min(self.position + 1, len(self.text_line.line))
        
    def move_left (self):
        self.position = max(0, min(self.position - 1, len(self.text_line.line)-1))
    
    def move_up   (self):
        up = self.text_line.prev_line
        if up is not None:
            self.text_line = up
    
    def move_down (self):
        down = self.text_line.next_line
        if down is not None:
            self.text_line = down
    
    def enter_key(self):
        position = self.position
        
        self.text_line.insert_newline()
        assert self.text_line.next_line is not None
        
        line = self.text_line.line
        self.text_line.line = line[0:position]
        self.text_line.next_line.line = line[position:]
        
        self.position = 0
        self.text_line = self.text_line.next_line
        
        self.editor.reposition_lines()
    
    def write(self, string):
        
        if None in self.text_line.font.get_metrics(string):
            return
        
        self.text_line.line =   self.text_line.line[0:self.position] \
                              + string \
                              + self.text_line.line[self.position:]
        self.position += len(string)
    
    def backspace(self):
        
        if self.position <= 0:
            
            if self.text_line.prev_line is None:
                return
            
            line = self.text_line.line
            current_text_line = self.text_line
            
            self.text_line = current_text_line.prev_line
            
            current_text_line.del_line()
            
            self.position = len(self.text_line.line)
            self.text_line.line =   self.text_line.line \
                                  + current_text_line.line
            
            if current_text_line is self.editor.first_visible_line:
                self.editor.first_visible_line = self.text_line
            
            self.editor.reposition_lines()
            
            
        else:
            self.text_line.line =   self.text_line.line[0:self.position-1] \
                                  + self.text_line.line[self.position:]
            self.move_left()
    
    def del_key(self):
        
        if self.position >= len(self.text_line.line):
            
            if self.text_line.next_line is None:
                return
            
            self.text_line.line += self.text_line.next_line.line
            
            self.text_line.next_line.del_line()
            
            self.editor.reposition_lines()
            
            
        else:
            self.text_line.line =   self.text_line.line[0:self.position] \
                                  + self.text_line.line[self.position+1:]
    
    
    
    def end_key(self):
        self.position = len(self.text_line.line)
    
    def home_key(self):
        self.position = 0
    
    def update(self, *args, **kwargs):
        if 'keydown_events' not in kwargs:
            return
        
        for e in kwargs['keydown_events']:
            if e.key == pygame.locals.K_RIGHT:
                self.move_right()
            elif e.key == pygame.locals.K_LEFT:
                self.move_left()
            elif e.key == pygame.locals.K_UP:
                self.move_up()
            elif e.key == pygame.locals.K_DOWN:
                self.move_down()
            elif e.key == pygame.locals.K_RETURN:
                self.enter_key()
            elif e.key == pygame.locals.K_BACKSPACE:
                self.backspace()
            elif e.key == pygame.locals.K_DELETE:
                self.del_key()
            elif e.key == pygame.locals.K_END:
                self.end_key()
            elif e.key == pygame.locals.K_HOME:
                self.home_key()
            elif 'unicode' in e.__dict__ and len(e.unicode) > 0:
                print(e)
                self.write(e.unicode)
            else:
                print(e)
    
if __name__ == '__main__':
    
    import argparse as ap
    from pygame.time import Clock
    import pygame.event
    
    parser = ap.ArgumentParser()
    
    parser.add_argument('lines', nargs='*', default=['Test'])
    parser.add_argument('-rw', '--resolution-width', type=int, default=0)
    parser.add_argument('-rh', '--resolution-height', type=int, default=0)
    parser.add_argument('--no-loop', action='store_true')
    
    args = parser.parse_args()
    
    pygame.init()
    pygame.mixer.quit()
    screen = pygame.display.set_mode((args.resolution_width, \
                                      args.resolution_height  ))
    pygame.display.set_caption('text_editor test')
    
    clock = Clock()
    
    editor = TextEditor(text='\n'.join(args.lines))
    
    rect_list = editor.draw(screen)
    pygame.display.flip()
    
    if not args.no_loop:
        run = True
        while run:
            clock.tick(30)
            
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.locals.QUIT:
                    run = False
            
            keydown_events = list(filter(lambda e: e.type == pygame.locals.KEYDOWN,
                                         events))
            editor.update(keydown_events = keydown_events)
            rect_list = editor.draw(screen)
            pygame.display.update(rect_list)
