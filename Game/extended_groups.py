
from pygame.sprite import LayeredUpdates as _LayeredUpdates
from pygame.sprite import Sprite as _Sprite

class LayeredUpdates(_LayeredUpdates):
    def update(self, *args, **kwargs):
        for s in self.sprites():
            s.update(*args, **kwargs)

class Sprite(_Sprite):
    def update(self, *args, **kwargs):
        pass

class MetaLayeredUpdates(LayeredUpdates):
    def addLU(self, other, start_layer):
        
        for layer in other.layers():
            self.add(*other.get_sprites_from_layer(layer),
                     layer = start_layer + layer           )
        try:
            other.on_added_to_LU
        except AttributeError:
            return
        other.on_added_to_LU(self)
    
    addLA = addLU
    
    def removeLU(self, other):
        self.remove( other.sprites() )
    
    def on_added_to_LU(self, where):
        pass
