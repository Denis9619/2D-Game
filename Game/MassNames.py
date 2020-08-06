import configparser
from pygame.image import load
config = configparser.ConfigParser()

config.read('config_player.txt')
b = config.sections()
print(b)

        


#Stand = config['playerStand']
#print(Stand['images'])

#playerStand = [load(n) for n in Stand['images'].split('\n')]

#playerStand = load(Stand['images'])
#print(playerStand)

