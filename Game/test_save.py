from menu import MenuEntry, Menu, QuestionMenu, FixedWidthMenu


    def on_exit_button(self):
        
        self.game.add_menu(
            ExitConfirmationMenu(self.game,
                                 self.game.exit_game,
                                 self.game.start_menu
                                )
        )

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
    
    args = parser.parse_args()
    
    pygame.init()
    pygame.mixer.quit()
    screen = pygame.display.set_mode((args.resolution_width, \
                                      args.resolution_height  ))
    pygame.display.set_caption('menu_test')
    
    clock = Clock()
    
    if args.width == 0:
        menu = Menu(*args.entries)
    else:
        menu = FixedWidthMenu(args.width, *args.entries)
    
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
    pygame.quit()
