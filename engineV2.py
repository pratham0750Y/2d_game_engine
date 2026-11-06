import pygame as py
from functools import lru_cache

class _default:
    pass

class World_parameters:

    directions={'left':0,'right':1,'top':2,'bottom':3}
    reverse_directions={0:1,1:0,2:3,3:2}

    entities=[]
    blocks=[]

    screen=None
    halfscreen=None
    screen_size=None
    chunk_size=None
    freezex=False
    freezey=False
    fps=60
    gravity=None

    camera_pos=py.Vector2(0,0)
    camera_follow=None
    camera_offset=py.Vector2(0,0)
    current_chunk=py.Vector2(0,0)

    background=None
    background_speed=1
    background_relative_pos=py.Vector2()
    background_size=None

    infinitex=False
    infinitey=False

    clock=None
    time=0
    frame=0

    colors = {
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "white": (255, 255, 255),
    "black": (0, 0, 0),
    "yellow": (255, 255, 0),
    "cyan": (0, 255, 255),
    "magenta": (255, 0, 255),
    "orange": (255, 165, 0),
    "purple": (128, 0, 128),
    "pink": (255, 192, 203),
    "brown": (139, 69, 19),
    "gray": (128, 128, 128),
    "light_gray": (211, 211, 211),
    "dark_gray": (64, 64, 64),
    "lime": (0, 255, 0),
    "navy": (0, 0, 128),
    "gold": (255, 215, 0),
    "coral": (255, 127, 80),
    "turquoise": (64, 224, 208)
    }

def init(screensize,world_size,freezex=False,freezey=False,fps=60,gravity=None,chunks_size=100):
    py.init()
    py.font.init()

    World_parameters.screen_size=py.Vector2(screensize)
    World_parameters.halfscreen=py.Vector2(screensize[0]/(2*chunks_size),screensize[1]/(2*chunks_size))

    entities=World_parameters.entities
    blocks=World_parameters.blocks

    for x in range(0,world_size[0]):
        entities.append([])
        blocks.append([])
        for y in range(0,world_size[1]):
            entities[x].append([])
            blocks[x].append([])

    World_parameters.freezex=freezex
    World_parameters.freezey=freezey
    
    World_parameters.chunk_size=chunks_size
    World_parameters.screen=py.display.set_mode(screensize)

    World_parameters.fps=fps
    World_parameters.gravity=gravity

    World_parameters.clock=py.time.Clock()

    World_parameters.background=py.surface.Surface(World_parameters.screen_size)
    World_parameters.background_size=py.Vector2(World_parameters.screen_size)
    return World_parameters.screen

#@lru_cache(maxsize=128)
def image_load(path,alpha=True,size=None,fit_screen=False):
    
    if '.' not in path:
        if type(path)!=tuple:
            path=World_parameters.colors[path]
        img=py.surface.Surface(size)
        img.fill(path)
    else:
        if alpha:
            img=py.image.load(path).convert_alpha()
        else:
            img=py.image.load(path).convert()
   
    if fit_screen:
        img=py.transform.smoothscale(img,World_parameters.screen_size)
    elif size is not None:
        img=py.transform.smoothscale(img,size)
    else:
        img=py.transform.smoothscale(img,World_parameters.screen_size)

    return img

def camera_update():
    if World_parameters.camera_follow is not None:
        World_parameters.camera_pos=py.Vector2(World_parameters.camera_follow.rec.x if not World_parameters.freezex else 0, World_parameters.camera_follow.rec.y if not World_parameters.freezey else 0)+World_parameters.camera_offset
        World_parameters.background_relative_pos=py.Vector2(World_parameters.camera_follow.rec.x if not World_parameters.freezex else 0, World_parameters.camera_follow.rec.y if not World_parameters.freezey else 0)*World_parameters.background_speed

class Entity:
    def __init__(self,pos,size,status=None,direction='right',image=None,colour=(255,0,0),velocity=(0,0),acceleration=(0,0),gravity=World_parameters.gravity,max_velocity=None,tag=None,collision=True):
        World_parameters.entities[pos[0]//World_parameters.chunk_size][pos[1]//World_parameters.chunk_size].append(self)

        self.rec=py.Rect(pos[0],pos[1],size[0],size[1])
        self.prevpos=py.Vector2(pos)
        self.image=[{},{},{},{}]
        if type(colour)==str:
            colour=World_parameters.colors[colour]
        
        self.load_image(image if image is not None else colour,status,direction)

        self.vel=py.Vector2(velocity)
        self.acc=py.Vector2((0,gravity) if gravity is not None else acceleration)

        self.current_status=status

        self.l=py.Rect(self.rec.x-1,self.rec.y,1,self.rec.height)
        self.r=py.Rect(self.rec.x+self.rec.width,self.rec.y,1,self.rec.height)
        self.t=py.Rect(self.rec.x,self.rec.y-1,self.rec.width,1)
        self.b=py.Rect(self.rec.x,self.rec.y+self.rec.height,self.rec.width,1)

        self.max_vel=py.Vector2(max_velocity) if max_velocity is not None else None
        self.tag=tag
        self.collision=collision
        self.load_radius=py.Vector2(size[0]//World_parameters.chunk_size+1,size[1]//World_parameters.chunk_size+1)
        self.facing_direction=direction

    @property
    def left(self):
            self.l.x=self.rec.x-1
            self.l.y=self.rec.y
            return self.l

    @property
    def right(self):
        self.r.x=self.rec.right
        self.r.y=self.rec.y
        return self.r

    @property
    def top(self):
        self.t.x=self.rec.x
        self.t.y=self.rec.y-1
        return self.t

    @property
    def bottom(self):
        self.b.x = self.rec.x
        self.b.y = self.rec.bottom
        return self.b

    def entity_entity_collision(self,entity):
        pass

    def entity_block_collision(self,block,direction):
        pass

    def update(self):
        pass

    def late_update(self):
        pass

    def load_image(self,path,status,direction):
        direction=World_parameters.directions[direction]
        rev_direction=World_parameters.reverse_directions[direction]

        if status in self.image[direction]:
            self.image[direction][status].append(image_load(path,size=self.rec.size))
            self.image[rev_direction][status].append(py.transform.flip(image_load(path,size=self.rec.size),True if direction==1 or direction==0 else False,True if direction==2 or direction==3 else False))

        else:
            self.image[direction][status]=[image_load(path,size=self.rec.size)]
            self.image[rev_direction][status]=[py.transform.flip(image_load(path,size=self.rec.size),True if direction==1 or direction==0 else False,True if direction==2 or direction==3 else False)]

    def moveTo(self,x,y):
            chunk_size=World_parameters.chunk_size
            if self.rec.x//chunk_size!=x//chunk_size or self.rec.y//chunk_size!=y//chunk_size:    
                if x//chunk_size>=len(World_parameters.entities) or y//chunk_size>=len(World_parameters.entities[0]) or x<0 or y<0:
                    raise IndexError("Entity cannot be moved outside the world boundaries.")
                World_parameters.entities[self.rec.x//chunk_size][self.rec.y//chunk_size].remove(self)
                World_parameters.entities[int(x//chunk_size)][int(y//chunk_size)].append(self)
    
            self.rec.x=x
            self.rec.y=y

    def focus(self,offset=(0,0)):
        World_parameters.camera_follow=self
        World_parameters.camera_offset=py.Vector2(offset)


class Block:
    def __init__(self,pos,size,status=None,direction='right',image=None,colour=(0,255,0),tag=None,current_status=None):

        World_parameters.blocks[pos[0]//World_parameters.chunk_size][pos[1]//World_parameters.chunk_size].append(self)

        self.rec=py.Rect(pos[0],pos[1],size[0],size[1])
        self.image={}
        self.load_image(image if image is not None else colour,status,direction)
        self.current_status=current_status
        
        self.l=py.Rect(self.rec.x-1,self.rec.y,1,self.rec.height)
        self.r=py.Rect(self.rec.x+self.rec.width,self.rec.y,1,self.rec.height)
        self.t=py.Rect(self.rec.x,self.rec.y-1,self.rec.width,1)
        self.b=py.Rect(self.rec.x,self.rec.y+self.rec.height,self.rec.width,1)

    @property
    def left(self):
            self.l.x=self.rec.x-1
            self.l.y=self.rec.y
            return self.l

    @property
    def right(self):
        self.r.x=self.rec.right
        self.r.y=self.rec.y
        return self.r

    @property
    def top(self):
        self.t.x=self.rec.x
        self.t.y=self.rec.y-1
        return self.t

    @property
    def bottom(self):
        self.b.x = self.rec.x
        self.b.y = self.rec.bottom
        return self.b

    def load_image(self,path,status,direction):
        direction=World_parameters.directions[direction]

        if status in self.image:
            self.image[status].append(image_load(path,size=self.rec.size))
        else:
            self.image[status]=[image_load(path,size=self.rec.size)]
            
    def update(self):
        pass

    def late_update(self):
        pass

    def moveTo(self,x,y):
            chunk_size=World_parameters.chunk_size
            if self.rec.x//chunk_size!=x//chunk_size or self.rec.y//chunk_size!=y//chunk_size:    
                if x//chunk_size>=len(World_parameters.blocks) or y//chunk_size>=len(World_parameters.blocks[0]) or x<0 or y<0:
                    raise IndexError("Block cannot be moved outside the world boundaries.")
                World_parameters.blocks[self.rec.x//chunk_size][self.rec.y//chunk_size].remove(self)
                World_parameters.blocks[x//chunk_size][y//chunk_size].append(self)
            self.rec.x=x
            self.rec.y=y

class Image:
    
    def __init__(self,path):
        self.current=0
        self.image=None
        self.tempx=0
        self.image_size=py.Vector2(0,0)
        self.raw_image=[[]]
        self.add(path)
        self.inserted=[]

    def add(self,image,size=World_parameters.screen_size):
        img=image_load(image,alpha=False,size=size)
        self.raw_image[self.current].append(img)
        self.tempx+=img.size[0]

    load=image_load  

    def next(self):
        self.current+=1
        self.raw_image.append([])
        self.image_size.y+=self.raw_image[self.current-1][0].size[1]
        self.image_size.x=max(self.tempx,self.image_size.x)
        self.tempx=0

    def pad(self,x,y):
        self.raw_image[self.current].append(py.surface.Surface((x,y)))
        self.tempx+=x

    def insert(self,image,pos,size=World_parameters.screen_size):
        self.inserted.append((image_load(image,alpha=False,size=size),pos))
        
    def compile(self):
        self.image_size.x=max(self.tempx,self.image_size.x)
        image=py.surface.Surface(self.image_size)
        pos=py.Vector2(0,0)
        layer=0
        for y in self.raw_image:
            for x in y:
                image.blit(x,pos)
                pos.x+=x.size[0]
            pos.x=0
            pos.y+=self.raw_image[layer][0].size[1]
            layer+=1
        image.blits(self.inserted)
        self.image=image
        del self.raw_image,self.current,self.image_size,self.inserted
        return image
            
def set_background(image,speed=1,infinitex=False,infinitey=False,start=(0,0)):

    World_parameters.background=image
    World_parameters.background_speed=speed
    World_parameters.infinitex=infinitex
    World_parameters.infinitey=infinitey
    World_parameters.background_relative_pos.update(start)
    World_parameters.background_size=py.Vector2(image.get_size())


def objupdate():

    World_parameters.clock.tick(World_parameters.fps)

    entities=World_parameters.entities
    blocks=World_parameters.blocks
    current_chunk=World_parameters.current_chunk
    startx=int(max(0,current_chunk.x-1-World_parameters.camera_offset.x//World_parameters.chunk_size))
    starty=int(max(0,current_chunk.y-1-World_parameters.camera_offset.y//World_parameters.chunk_size))
    endx=int(min(len(World_parameters.blocks),current_chunk.x+World_parameters.screen_size.x+1))
    endy=int(min(len(World_parameters.blocks[0]),current_chunk.y+World_parameters.screen_size.y+1))
    World_parameters.time+=1

    if World_parameters.time%15==0:
        World_parameters.frame+=1

    for x in range(startx,endx):
        for y in range(starty,endy):
            for entity in entities[x][y]:

                entity.prevpos.update(entity.rec.x,entity.rec.y)
               
                entity.vel+=entity.acc

                if entity.max_vel is not None:
                    entity.vel.x=max(min(entity.vel.x,entity.max_vel.x),-entity.max_vel.x)
                    entity.vel.y=max(min(entity.vel.y,entity.max_vel.y),-entity.max_vel.y)

                entity.moveTo(entity.rec.x+entity.vel.x,entity.rec.y+entity.vel.y)
                entity.update()

            for block in blocks[x][y]:
                block.update()

    for x in range(startx,endx):
        for y in range(starty,endy):
            for entity in entities[x][y]:
                for r in range(-1,int(entity.load_radius.x)+1):
                    for c in range(-1,int(entity.load_radius.y)+1):
                        for entity2 in entities[x+r][y+c]:
                                if entity!=entity2 and entity.rec.colliderect(entity2.rec):
                                    entity.entity_entity_collision(entity2)
                        if entity.collision:
                            for block in blocks[x+r][y+c]:
                                if entity.rec.colliderect(block.left) and entity.vel.x>0:
                                    entity.rec.x=block.left.x-entity.rec.width+1
                                    if entity.prevpos.x==entity.rec.x:
                                        entity.vel.x=0
                                    entity.entity_block_collision(block,'left')
                                elif entity.rec.colliderect(block.right) and entity.vel.x<0:
                                    entity.rec.x=block.right.x
                                    if entity.prevpos.x==entity.rec.x:
                                        entity.vel.x=0
                                    entity.entity_block_collision(block,'right')
                                if entity.rec.colliderect(block.top) and entity.vel.y>=0:
                                    entity.rec.y=block.top.y-entity.rec.height+1
                                    if entity.prevpos.y==entity.rec.y:
                                        entity.vel.y=0
                                    entity.entity_block_collision(block,'top')
                                elif entity.rec.colliderect(block.bottom) and entity.vel.y<0:
                                    entity.rec.y=block.bottom.y
                                    if entity.prevpos.y==entity.rec.y:
                                        entity.vel.y=0
                                    entity.entity_block_collision(block,'bottom')

    for x in range(startx,endx):
        for y in range(starty,endy):
            for entity in entities[x][y]:
                entity.late_update()

            for block in blocks[x][y]:
                block.late_update()

    camera_update()

def drawall():
    
    entities=World_parameters.entities
    blocks=World_parameters.blocks
    current_chunk=World_parameters.current_chunk
    startx=int(max(0,current_chunk.x-1-World_parameters.camera_offset.x//World_parameters.chunk_size))
    starty=int(max(0,current_chunk.y-1-World_parameters.camera_offset.y//World_parameters.chunk_size))
    endx=int(min(len(World_parameters.blocks),current_chunk.x+World_parameters.screen_size.x+1))
    endy=int(min(len(World_parameters.blocks[0]),current_chunk.y+World_parameters.screen_size.y+1))

    frame=World_parameters.frame

    offsetx=-World_parameters.camera_offset.x-World_parameters.camera_pos.x
    offsety=-World_parameters.camera_pos.y+World_parameters.camera_offset.y
    background_size=World_parameters.background_size
    relative_pos=World_parameters.background_relative_pos

    if not (World_parameters.infinitex or World_parameters.infinitey):
        World_parameters.screen.blit(World_parameters.background,(0,0),(World_parameters.background_relative_pos.x,World_parameters.background_relative_pos.y,World_parameters.screen_size.x,World_parameters.screen_size.y))
    elif World_parameters.infinitex and not World_parameters.infinitey:
        diff=0
        World_parameters.background_relative_pos.x=World_parameters.background_relative_pos.x%background_size.x

        if relative_pos.x>=background_size[0]-World_parameters.screen_size[0]:
            diff=background_size[0]-relative_pos[0]
            World_parameters.screen.blit(World_parameters.background,(0,0),(relative_pos.x,relative_pos.y,diff,World_parameters.screen_size.y))
            World_parameters.screen.blit(World_parameters.background,(diff,0),(0,World_parameters.background_relative_pos.y,World_parameters.screen_size.x-diff,World_parameters.screen_size.y))
        else:
            World_parameters.screen.blit(World_parameters.background,(0,0),(relative_pos.x,relative_pos.y,World_parameters.screen_size.x,World_parameters.screen_size.y))
    elif not World_parameters.infinitex and World_parameters.infinitey:
        diff=0
        World_parameters.background_relative_pos.y=World_parameters.background_relative_pos.y%background_size[1]
   
        if relative_pos.y>=background_size[1]-World_parameters.screen_size[1]:
            diff=background_size[1]-relative_pos[1]
            World_parameters.screen.blit(World_parameters.background,(0,0),(relative_pos.x,relative_pos.y,World_parameters.screen_size.x,diff))
            World_parameters.screen.blit(World_parameters.background,(0,diff),(World_parameters.background_relative_pos.x,0,World_parameters.screen_size.x,World_parameters.screen_size.y-diff))
        else:
            World_parameters.screen.blit(World_parameters.background,(0,0),(relative_pos.x,relative_pos.y,World_parameters.screen_size.x,World_parameters.screen_size.y))     

    else:
        diffx=0
        diffy=0

        World_parameters.background_relative_pos.x=World_parameters.background_relative_pos.x%background_size.x
        World_parameters.background_relative_pos.y=World_parameters.background_relative_pos.y%background_size.y
        World_parameters.screen.blit(World_parameters.background,(0,0),(relative_pos.x,relative_pos.y,World_parameters.screen_size.x,World_parameters.screen_size.y))     
       
        if relative_pos.x>=background_size[0]-World_parameters.screen_size[0]:
            diffx=background_size[0]-relative_pos[0]
            World_parameters.screen.blit(World_parameters.background,(diffx,0),(0,World_parameters.background_relative_pos.y,World_parameters.screen_size.x-diffx,World_parameters.screen_size.y))
    
        if relative_pos.y>=background_size[1]-World_parameters.screen_size[1]:
            diffy=background_size[1]-relative_pos[1]
            World_parameters.screen.blit(World_parameters.background,(0,diffy),(World_parameters.background_relative_pos.x,0,World_parameters.screen_size.x,World_parameters.screen_size.y-diffy))
       
        if relative_pos.x>=background_size[0]-World_parameters.screen_size[0] and relative_pos.y>=background_size[1]-World_parameters.screen_size[1]:
            World_parameters.screen.blit(World_parameters.background,(diffx,diffy),(0,0,World_parameters.screen_size.x-diffx,World_parameters.screen_size.y-diffy))

    for x in range(startx,endx):
        for y in range(starty,endy):
            for block in blocks[x][y]:
                World_parameters.screen.blit(block.image[block.current_status][frame%len(block.image[block.current_status])],(block.rec.x+offsetx,block.rec.y+offsety))
            for entity in entities[x][y]:
                World_parameters.screen.blit(entity.image[World_parameters.directions[entity.facing_direction]][entity.current_status][frame%len(entity.image[World_parameters.directions[entity.facing_direction]][entity.current_status])],(entity.rec.x+offsetx,entity.rec.y+offsety))





"""

stuff to do 

1)add colour id dict like {"red:(255,0,0)} all of them - done but test

2)add prevpos and set vel to 0 if pos is same for 2 continous frame during collision - done but test





"""





















































































