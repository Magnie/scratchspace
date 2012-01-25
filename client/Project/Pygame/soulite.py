#/usr/bin/env python
'''
Soulite is a module for Pygame to keep the Scratch feel
of programming. It tries to keep the Project, Stage,
Sprites and commands in Pygame.

Soulite is made by Magnie (http://www.scratch.mit.edu/users/Magnie)
Scratch is a program made by MIT (http://www.scratch.mit.edu)

This is version of Soulite is version 1.0
'''
import sys
import os

import pygame
from pygame.locals import *

pygame.init()


class Project(object):
    
    def __init__(self):
        self.sprites = {} # 'name' : Sprite()
        self.stage = Stage(background_color=0xFFFFFF)
    
        self.clock = pygame.time.Clock()
    
    def tick(self, ticker):
        "This controls the FPS of the project."
        self.clock.tick(ticker)
    
    def update_all(self):
        "This updates all the sprites of the project."
        for event in pygame.event.get(): 
            if event.type == pygame.QUIT: 
                sys.exit(0) 
        self.stage.screen.blit(self.stage.background, (0, 0))
        for sprite in self.sprites:
            self.sprites[sprite]._update()
        pygame.display.flip()
    
    def new_sprite(self, sprite):
        "Adds a new sprite to the dictionary so it can be updated."
        self.sprites[sprite.name] = sprite


class Stage(object):
    
    def __init__(self, width=512, height=512, caption='Soulite', background_color=0x000000):
        self.width = width
        self.height = height
        self.background_color = background_color
        self.window = pygame.display.set_mode((self.width, self.height))
        self.screen = pygame.display.get_surface()
        
        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill(self.background_color)
        
        self.backgrounds = {} # 'costume name' : costume
    
    def set_background(self, costume_name):
        "Set the background image."
        self.background = self.backgrounds[costume_name]
    
    def add_background(self, background_file, path='', background_name=''):
        "Add a background image."
        if not background_name:
            background_name = background_file
        
        background_location = os.path.join(path, background_file)
        try:
            background = pygame.image.load(background_location)
            background = background.convert()
        except pygame.error:
            return 'Failed to load image.'
        
        self.backgrounds[costume_name] = background


class Sprite(pygame.sprite.Sprite):
    
    def __init__(self, project, xpos=0, ypos=0, angle=360, name='sprite'):
        pygame.sprite.Sprite.__init__(self)
        self.xpos = xpos
        self.ypos = ypos
        self.angle = angle
        
        self.name = name
        
        self.costumes = {} # 'costume name' : image
        self.current_rect = None
        self.current_costume = ''
        
        self.show_sprite = False
        
        self.key_presses = {} # 'key' : True or False
    
        self.screen = project.stage.screen
        self.project = project
        self.project.new_sprite(self)
    
    # Soulite Functions
    
    def _update(self):
        "This updates the sprites location and display."
        self.current_rect.midtop = (self.xpos, self.ypos)
        try:
            self.update()
        except AttributeError, e:
            print self.name, e
        if self.show_sprite:
            image = self.costumes[self.current_costume]
            image = self.rotate(image, self.angle)
            self.screen.blit(image, (self.xpos, self.ypos))
    
    # Motion Functions
    
    def go_to(self, x, y):
        "This tell the sprite to go to an x and y location on the screen."
        self.xpos = x
        self.ypos = y
    
    def set_x_pos(self, x):
        "This sets the x (left and right axis) position of the sprite."
        self.xpos = x
    
    def set_y_pos(self, y):
        "This sets the y (up and down axis) position of the sprite."
        self.ypos = y
    
    def set_direction(self, angle):
        "This changes the direction the sprite is facing in."
        self.angle = angle
    
    # Looks Functions
    
    def show(self):
        "This allows the sprite to be displayed."
        self.show_sprite = True
    
    def hide(self):
        "Keeps the sprite from being displayed."
        self.show_sprite = False
    
    def set_costume(self, costume_name):
        "This changes the current costume."
        self.current_costume = costume_name
        self.current_rect = self.costumes[costume_name].get_rect()
    
    def add_costume(self, costume_file, path='', costume_name='', colorkey=0xFFFFFF):
        "This loads an image and saves it to the costume dictionary."
        if not costume_name:
            costume_name = costume_file
        
        costume_location = os.path.join(path, costume_file)
        try:
            costume = pygame.image.load(costume_location)
            costume = costume.convert()
            costume.set_colorkey(colorkey, RLEACCEL)
        except pygame.error:
            return 'Failed to load image.'
        self.costumes[costume_name] = costume
    
    def del_costume(self, image_name):
        "This deletes a costume from the costum dictionary."
        if image_name in self.costumes:
            del self.costumes[image_name]
    
    def rotate(self, image, angle): # http://stackoverflow.com/questions/4183208/pygame-rotating-an-image-around-its-center
        """rotate an image while keeping its center and size"""
        orig_rect = image.get_rect()
        rot_image = pygame.transform.rotate(image, angle)
        rot_rect = orig_rect.copy()
        rot_rect.center = rot_image.get_rect().center
        rot_image = rot_image.subsurface(rot_rect).copy()
        return rot_image
    
    # Sensors Functions
    
    def key_pressed(self, bool_key):
        "This command checks if a key is being pressed."
        key = pygame.key.get_pressed()
        temp = False
        exec('''
if key['''+bool_key+''']:
    temp = True''')
        if temp == True:
            return True
        return False
    
    def touching(self, sprite_name):
        "This command checks if the current sprite is touching another sprite."
        hitbox = self.current_rect
        target = self.project.sprites[sprite_name].current_rect
        return hitbox.colliderect(target)
    
    # Pen Functions
    
    def stamp(self):
        image = self.costumes[self.current_costume]
        image = self.rotate(image, self.angle)
        self.screen.blit(image, (self.xpos, self.ypos))