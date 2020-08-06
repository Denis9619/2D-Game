import pygame
from pygame import draw
from pygame import Color

pygame.init()
win = pygame.display.set_mode((500 , 500))

pygame.display.set_caption("Cubes Game")

walkRight = [pygame.image.load('goblin_right_1.png'),pygame.image.load('goblin_right_2.png'),pygame.image.load('goblin_right_3.png'),
             pygame.image.load('goblin_right_4.png'),pygame.image.load('goblin_right_5.png'),pygame.image.load('goblin_right_6.png')]

walkLeft = [pygame.image.load('pygame_left_1.png'),pygame.image.load('pygame_left_2.png'),pygame.image.load('pygame_left_3.png'),
            pygame.image.load('pygame_left_4.png'),pygame.image.load('pygame_left_5.png'),pygame.image.load('pygame_left_6.png')]

bg = pygame.image.load('Nature.png')

playerStand = pygame.image.load('pygame_idle.png')

clock = pygame.time.Clock()

x = 50
y = 425

x1 = 200
y1 = 300

width = 60
height = 71
speed = 5

isJump = False
jumpCount = 10

left = False
right = False

animCount = 0

class fireBall():
    def __init__(self,x,y,radius,color,facing):
        self.x = x
        self.y = y

#def NPC():
 #   win.blit( npc1 , (x1,y1))
    

def drawWindow(x_end):
    global animCount
    win.blit(bg,(0,0))
    
    if animCount + 1 >= 30:
        animCount = 0

    if left:
        win.blit(walkLeft[animCount // 5], (x, y))
        animCount += 1
    elif right:
        win.blit(walkRight[animCount // 5], (x, y))
        animCount += 1
    else:
        win.blit(playerStand,(x,y))
    draw.line(win,(0,0,0,0),(40,50),(300,50),6)
    draw.line(win,(255,0,0,100),(40,50),(x_end,50),6)
    
    pygame.display.update()

x_end = 300

run= True
while run:
    clock.tick(30)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT] and x > 5:
        x -= speed
        left = True
        right = False
        if x_end > 40:
            x_end -=20

    elif keys[pygame.K_RIGHT] and x < 500 - width - 5:
        x += speed
        left = False
        right = True
        if x_end < 300:
            x_end +=20
        
    else:
        left = False
        right = False
        animCount = 0
        
    if keys[pygame.K_q]:
        if x_end > 40:
            x_end -=20
    elif keys[pygame.K_e]:
        if x_end < 300:
            x_end +=20

    if not (isJump):

        if keys[pygame.K_SPACE]:
            isJump = True

    else:
        if jumpCount >= -10:
            if jumpCount < 0:
                y += (jumpCount**2) / 2
            else :
                y -= (jumpCount**2) / 2
            jumpCount -= 1
        else:
            isJump = False
            jumpCount = 10

    drawWindow(x_end)
    

pygame.quit()

        
