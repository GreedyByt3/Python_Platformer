import os
import random as rand
import math
import pygame
from os import listdir
#os.path.join --> joins one or more path components intelligently.
#This method concatenates various path components with exactly one directory separator (‘/’)
#following each non-empty part except the last path component.
#If the last path component to be joined is empty 
#then a directory separator (‘/’) is put at the end.
from os.path import isfile, join

pygame.init()

pygame.display.set_caption("Platformer")

#                                           R  ,  G,   B    
BG_COLOR = (255, 255, 255)
WIDTH, HEIGHT = 1000, 800
FPS = 60
PLAYER_VEL = 5 

window = pygame.display.set_mode((WIDTH, HEIGHT))

def flip(sprites):
    #pygame.transform.flip --> can flip a Surface either vertically, horizontally, or both.
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]

#laod all of the different sheets for the character
def load_sprite_sheets(dir1, dir2, width, height, direction = False):
    path = join("assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))]

    all_sprites = {}

    for img in images:
        sprite_sheet = pygame.image.load(join(path, img)).convert_alpha()

        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height),pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            #scale2x --> mi scala il character
            sprites.append(pygame.transform.scale2x(surface))
        if direction:
            all_sprites[img.replace(".png", "") + "_right"] = sprites
            all_sprites[img.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[img.replace(".png", "")] = sprites
    
    return all_sprites


def get_block(size):
    path = join("assets", "Terrain", "Terrain.png")
    img = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(96, 0, size, size)
    surface.blit(img, (0, 0), rect)
    #it double the size
    return pygame.transform.scale2x(surface)


#player code________________________________________________
class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0)
    GRAVITY = 1
    SPRITES = load_sprite_sheets("MainCharacters", "MaskDude", 32, 32, True)
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0

    def jump(self):
        self.y_vel = -self.GRAVITY * 8
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0


    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy
    
    def make_hit(self):
        self.hit = True
        

    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0


    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0
    
    #moving our character
    def loop(self, fps):
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)

        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps * 2:
            self.hit = False
            self.hit_count = 0

        #Increment the gravity for every loop
        self.fall_count += 1
        self.update_sprite()

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def hit_head(self):
        self.count = 0
        self.y_vel *= -1

    #per caricare le animazioni negli assets
    def update_sprite(self):
        sprite_sheet = "idle"
        if self.hit:
            sprite_sheet = "hit"
        elif self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
        elif self.y_vel > self.GRAVITY * 2:
            sprite_sheet = "fall"
        elif self.x_vel != 0:
            sprite_sheet = "run"


        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()


    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    #function that handle the draw on the screen
    def draw(self, win, offset_x):
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))

#Collision code_______________________________________________________
class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.img = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, win, offset_x):
        win.blit(self.img, (self.rect.x - offset_x, self.rect.y))

class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block(size)
        self.img.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.img)


#Fire_Class______________________________________________________________
#Fire class inherites from Object, thats why i can use the super().__init__(...... name added)
class Fire(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height,"fire")
        self.fire = load_sprite_sheets("Traps", "Fire", width, height)
        self.img = self.fire["off"][0]
        self.mask = pygame.mask.from_surface(self.img)
        self.animation_count = 0
        self.animation_name = "off"

    def on(self):
        self.animation_name = "on"

    def off(self):
        self.animation_name = "off"

    def loop(self): 
        sprites = self.fire[self.animation_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.img = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.img.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.img)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0


#Player Code___________________________________________________________________
#Generate the background
def get_background(name):
    image = pygame.image.load(join("Assets","Background", name))
    _, _, width, height = image.get_rect()
    tiles = []

    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            #made it directly a tuple so that we dont need it to convert it on line 37
            pos = (i * width, j * height)
            tiles.append(pos)

    return tiles, image

def draw(window, background, bg_image, player, objects, offset_x):
    for tile in background:
        window.blit(bg_image, tile)

    for obj in objects:
        obj.draw(window, offset_x)

    player.draw(window, offset_x)
    #for every single frame we clear the screen
    pygame.display.update()

#Collision_Handler____________________________________

def handle_vertical_collision(player, objects, dy):
    collided_objs = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if dy > 0:
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom 
                player.hit_head()
        
            collided_objs.append(obj)
    
    return collided_objs

def collide(player, objects, dx):
    player.move(dx, 0)
    player.update()
    collided_obj = None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collided_obj = obj
            break
    
    player.move(-dx, 0)
    player.update()
    return collided_obj

#End_Collision_Handler____________________________________________

def handle_Move(player, objects):
    keys = pygame.key.get_pressed()
    #set player velocity to 0
    player.x_vel = 0
    collide_left = collide(player, objects, -PLAYER_VEL * 2)
    collide_right = collide(player, objects, PLAYER_VEL * 2)

    if keys[pygame.K_LEFT] and not collide_left:
        player.move_left(PLAYER_VEL)
    
    if keys[pygame.K_RIGHT] and not collide_right:
        player.move_right(PLAYER_VEL)
    
    vertical_collision = handle_vertical_collision(player, objects, player.y_vel)
    to_check = [collide_left, collide_right, *vertical_collision]

    for obj in to_check:
        if obj and obj.name == "fire":
            player.make_hit()
    

#EVENT loop --> move character ecc...
def main(window):
    clock = pygame.time.Clock()
    background, bg_image = get_background("Blue.png")\
    
    block_size = 96

    player = Player(100, 100, 50, 50)
    fire = Fire(100, HEIGHT - block_size - 64, 16, 32)
    fire.on()
    floor = [Block(i * block_size, HEIGHT - block_size, block_size) 
        for i in range(-WIDTH // block_size, (WIDTH * 2) // block_size)]

    objects = [*floor, Block(0, HEIGHT - block_size * 2, block_size), 
                                    Block(block_size * 3, HEIGHT - block_size * 4, block_size), fire]

    offset_x = 0
    scroll_area_width = 200

    run = True
    while run:
        #Utile per adattare i framerate in base al dispositivo 
        #su qui viene visualizzato il gioco
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.jump_count < 2:
                    player.jump()
        
        player.loop(FPS)
        fire.loop()
        handle_Move(player, objects)
        draw(window, background, bg_image, player, objects,offset_x)

        #                                                         (this says if the char is moving)
        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or (
                (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
            offset_x += player.x_vel


    pygame.quit()
    quit()

#Only call main function only if we run this file directly
if __name__ == "__main__":
    main(window)