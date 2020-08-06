
from menu import QuestionMenu

import argparse as ap
from pygame.time import Clock
import pygame.event

parser = ap.ArgumentParser()

parser.add_argument('entries', nargs='*', default=['Test'])
parser.add_argument('--question', '-q', default='Hello, world.')
parser.add_argument('-rw', '--resolution-width', type=int, default=0)
parser.add_argument('-rh', '--resolution-height', type=int, default=0)
parser.add_argument('--no-loop', action='store_true')

args = parser.parse_args()

pygame.init()
screen = pygame.display.set_mode((args.resolution_width, \
                                  args.resolution_height  ))
pygame.display.set_caption('entries')

clock = Clock()

print(args.entries)
menu = QuestionMenu(args.question, *args.entries)

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
