
from snippets import SnippetQuickbar, SnippetContainer, Snippet

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
    pygame.display.set_caption('SnippetQuickbar_test')
    
    clock = Clock()
    
    container = SnippetContainer()
    for name in args.entries:
        container.new_snippet(name = name)
    for i in range(9):
        container.set_quick_access(i, i)
    
    quickbar = SnippetQuickbar(container)
    
    rect_list = quickbar.draw(screen)
    pygame.display.flip()
    
    
    if not args.no_loop:
        run = True
        while run:
            clock.tick(30)
            
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.locals.QUIT:
                    run = False
            
            quickbar.update()
            rect_list = quickbar.draw(screen)
            pygame.display.update(rect_list)
