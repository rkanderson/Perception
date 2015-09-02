
# (c) 2015-2016 Ryan Anderson All Rights Reserved

import pygame
from pygame.locals import *
import math
import sound
from random import randint

pygame.init()

# Some colors
BLACK=(0,0,0)
WHITE=(255,255,255)
PLATFORM_BLUE=(60, 60, 255)

GRAVITY=1

FPS=30
FPSCLOCK=pygame.time.Clock()
screen_dimensions = (700, 700)
DISPLAYSURF = pygame.display.set_mode(screen_dimensions)
pygame.display.set_caption("Perception")
my_icon = pygame.image.load("player.png")
pygame.display.set_icon(my_icon)
EVENTS = []

"""
        _           __                         _            __ __      
     __| |   ___   / _|    _ __ ___     __ _  (_)  _ __    / / \ \   _ 
    / _` |  / _ \ | |_    | '_ ` _ \   / _` | | | | '_ \  | |   | | (_)
   | (_| | |  __/ |  _|   | | | | | | | (_| | | | | | | | | |   | |  _ 
    \__,_|  \___| |_|     |_| |_| |_|  \__,_| |_| |_| |_| | |   | | (_)
                                                           \_\ /_/     
"""
def main():
    """Starts the game."""
    global game
    game = Game() # make a new Game object
    running = True
    while running: #<---Start of main game loop. 1 time around = 1 frame 
        EVENTS = pygame.event.get() # update EVENTS
        
        # See if there's any need to quit (red x button pressed)
        for event in EVENTS:
            if event.type==QUIT:
                running = False

        game.update(EVENTS) # update game state
        game.draw(DISPLAYSURF) # draw game

        FPSCLOCK.tick(FPS) # pause a few milliseconds (1/FPS seconds)

"""
#     ____                            
#    / ___|   __ _   _ __ ___     ___ 
#   | |  _   / _` | | '_ ` _ \   / _ \
#   | |_| | | (_| | | | | | | | |  __/
#    \____|  \__,_| |_| |_| |_|  \___|
#  
"""
class Game:
    """Top of class hierarchy; the godly class."""
    def __init__(self):
        """Initializes a new Game object."""
        self.room = MainMenu(self)

        #Start some music
        pygame.mixer.music.load('music.ogg')
        pygame.mixer.music.play(-1)

    def update(self, events):
        """Updates game state."""
        self.room.update(events)
    def draw(self, screen):
        screen.fill(BLACK)
        self.room.draw(screen)
        pygame.display.update()

"""
#    __  __           _           __  __                        
#   |  \/  |   __ _  (_)  _ __   |  \/  |   ___   _ __    _   _ 
#   | |\/| |  / _` | | | | '_ \  | |\/| |  / _ \ | '_ \  | | | |
#   | |  | | | (_| | | | | | | | | |  | | |  __/ | | | | | |_| |
#   |_|  |_|  \__,_| |_| |_| |_| |_|  |_|  \___| |_| |_|  \__,_|
#
"""
class MainMenu:
    title_img = pygame.image.load("title.png").convert()
    font = pygame.font.Font(None, 40)
    def __init__(self, game):
        self.game=game
        self.on_title = True
        # Initialize buttons, which will be represented as tuples (pygame.Rect, level_index). 
        # One row will consist of five buttons, each 100px wide and a space of 25px seperating them.
        # With a margin of 50 on either side, a row will span the entire 700.
        # A column will consist of 10 buttons, each 50px high and 10px seperating them. 
        # With a margin of 55px on either side, a column will span the full 700.
        self.buttons = []
        for level_index in range(50):
            row = level_index / 5
            if level_index <= 4:
                column = level_index
            else:
                column = level_index % 5
            self.buttons.append((pygame.Rect(50+125*column, 55+60*row, 100, 50),level_index))
            
    def update(self, events):
        for event in events:
            if self.on_title and event.type==KEYDOWN: self.on_title=False
            elif event.type==MOUSEBUTTONDOWN and not self.get_level_index_of_button_at_mouse_pos()==None:
                self.game.room = LevelGenerator.make_level(self.game, self.get_level_index_of_button_at_mouse_pos(), respawn_noise_at_start=True)

    def draw(self, screen):
        """Draws the main menu. If self.on_title == True, then draw our majestic title image.
        Otherwise, draw the level selecty stuff."""
        if self.on_title:
            screen.blit(MainMenu.title_img, (0,0))
        else:
            # Draw buttons
            for btn in self.buttons:
                if btn[0].collidepoint(pygame.mouse.get_pos()): pygame.draw.rect(screen, (PLATFORM_BLUE[0]+20, PLATFORM_BLUE[1]+20, PLATFORM_BLUE[2]), btn[0])
                else: pygame.draw.rect(screen, PLATFORM_BLUE, btn[0])
                level_num = btn[1]+1
                text = MainMenu.font.render(str(level_num), 0, (255,255,255))
                text_rect = text.get_rect()
                text_rect.centerx = btn[0].centerx
                text_rect.centery = btn[0].centery
                text_pos = (text_rect.left, text_rect.top)
                screen.blit(text, text_pos)
           
    def get_level_index_of_button_at_mouse_pos(self):
        """@return the level index of the button at the current mouse position"""
        if not self.on_title:
            for btn in self.buttons:
                if btn[0].collidepoint(pygame.mouse.get_pos()): return btn[1]

"""
#    _                             _ 
#   | |       ___  __   __   ___  | |
#   | |      / _ \ \ \ / /  / _ \ | |
#   | |___  |  __/  \ V /  |  __/ | |
#   |_____|  \___|   \_/    \___| |_|
#  
"""
class Level(object):
    tip_font = pygame.font.Font(None, 24)
    misc_font = pygame.font.Font(None, 24)
    tip_color = (255,255,255)
    def __init__(self, game, start_pos, spawn_drop, finish_pos, allowed_shifts, index, bground_img_filename, make_respawn_cool_noise_at_start=False):
        """@param start_ps is a tuple containing the player's start x and y (x,y)
        @param spawn_drop is a boolean determining if the player will spawn a little bit above the
        ground (it looks cooler to spawn that way. It should be False if the player is spawning in a tight area.
        @param finish_pos is a tuple containg the x and y of the finish (x,y)
        @param allowed_shifts is the number of gravity shifts the players may make as they do the level.
        @param index is the index, or level number of this level (zero-based)
        @param bground_img_filename is a string of the filepath of this level's background image.
        @param make_respawn_cool_noise_at_start is a boolean that will determine if the respawn noise is made at
        the start. This is usually true if this level is the first one the player has clicked on."""
        self.game=game
        self.player_start_x = start_pos[0]
        self.player_start_y = start_pos[1]
        if spawn_drop:
            self.player = Player(self.game, (self.player_start_x, self.player_start_y - Player.spawn_dist_above_ground))
        else:
            self.player = Player(self.game, (self.player_start_x, self.player_start_y))
        self.end_x = finish_pos[0]
        self.end_y = finish_pos[1]
        self.finish = Finish(self.game, (self.end_x, self.end_y))
        self.allowed_shifts = allowed_shifts
        self.index = index
        self.is_completed = False
        self.button_pressed_at_least_once = False
        self.components = []
        self.tip_text_images = []
        self. tip_text_image_positions = []
        self.background_img = pygame.image.load(bground_img_filename).convert()
        self.paused=False
        self.just_started_flash_timer=3 #Will cause the screen to flash white for 3 frames upon starting
        if make_respawn_cool_noise_at_start: sound.play_sound("level_start")
       
    def update(self, events):
        """Updates the game state. Set self.is_completed to True if necessary."""
        
        for event in events: # Shall I pause?
            if event.type==KEYDOWN and event.key==K_p: self.paused= not self.paused

        if self.paused: return

        # HANDLE DA INPUTS (for Level)
        for event in events:
            if event.type==KEYDOWN:
                self.button_pressed_at_least_once=True
                if event.key==K_RIGHT: self.gravity_shift_right()
                elif event.key==K_UP: self.gravity_shift_up()
                elif event.key==K_LEFT: self.gravity_shift_left()
                elif event.key==K_r: 
                    self.game.room=LevelGenerator.make_level(self.game, self.index) #Restart
                    return
                elif event.key==K_m: 
                    self.game.room=MainMenu(self.game) #Return to MainMenu
                    return

        self.player.update(events) 

        # Check for win/death
        if self.player.is_dead: self.game.room=LevelGenerator.make_level(self.game, self.index, respawn_noise_at_start=True)
        elif self.player.won_game: self.game.room=LevelGenerator.make_level(self.game, self.index+1)
        

    def draw(self,screen):
        """Draws the entire level including the player, the finish, all tip texts, other text, and all components"""
        if not self.background_img == None:
            screen.blit(self.background_img, (0, 0))
        else:
            print ("(DEBUG) No background image")
        if not self.button_pressed_at_least_once:   # Only draw tip text if the user hasn't pressed any buttons yet.
                                                    # We can safely assume self.tti and self.ttis are the same size.
            for i in range(len(self.tip_text_images)):
                screen.blit(self.tip_text_images[i], self.tip_text_image_positions[i])

        for component in self.components:   # Draw all Platforms
            if isinstance(component, Platform): component.draw(screen)
        Lava.color = Lava.COLORS[randint(0, 2)]
        for component in self.components:   # Draw all Lavas
            if isinstance(component, Lava): component.draw(screen)
        self.player.draw(screen)
        self.finish.draw(screen)

        #Draw other text
        screen.blit(Level.misc_font.render("LEVEL-"+str(self.index+1), 0, (255,255,0)),(20,20))
        screen.blit(Level.misc_font.render("Shifts: "+str(self.allowed_shifts), 0, (255,255,0)),(screen_dimensions[0]-100,20))

        if self.just_started_flash_timer>0: 
            screen.fill(WHITE)
            self.just_started_flash_timer-=1
        # XXX_RYAN_XXX was here!
            
    def add_tip_text(self, text, pos):
        """Appends a rendered text image to self.tip_text_images using self.tip_font with the specified.
        @param text is the text that will be made into an image.
        @param pos is a tuple containing the x and y posions of the text image."""
        text_img = Level.tip_font.render(text, 0, Level.tip_color)
        self.tip_text_images.append(text_img)
        self.tip_text_image_positions.append(pos)
        
    def gravity_shift_up(self):
        """Changes the coordinates of self.player, self.finish, and self.components (heights too)
        to create the illusion of a gravity shift upwards"""
        if self.allowed_shifts > 0:
            self.allowed_shifts -= 1
            sound.play_sound("gravity_shift")
            
            self.player.y = screen_dimensions[1] - self.player.y - self.player.head_height
            #self.player.x = screen_dimensions[0] - self.player.x - self.player.head_width
            self.finish.rect.y = screen_dimensions[1] - self.finish.rect.y - self.finish.height
            #self.finish.rect.x = screen_dimensions[0] - self.finish.rect.x - self.finish.width

            self.player.xspeed = 0
            self.player.yspeed = 0
            self.player.prevx = self.player.x
            self.player.prevy = self.player.y

            for c in self.components:
                if isinstance(c, Platform) or isinstance(c, Lava):
                    c.rect.y = screen_dimensions[1] - c.rect.y - c.rect.height
                    #c.rect.x = screen_dimensions[1] - c.rect.x - c.rect.width
              
            self.background_img = pygame.transform.flip(self.background_img, False, True)   # Vertically flip self.background_img

    def gravity_shift_left(self):
        """Changes the coordinates of self.player, self.finish, and self.components (height/width too)
        to create the illusion of a gravity shift rightwards"""
        if self.allowed_shifts > 0:
            self.allowed_shifts -= 1
            sound.play_sound("gravity_shift")
            
            temp = self.player.y
            self.player.y = screen_dimensions[0] - (self.player.x + Player.head_width)
            self.player.x = temp

            temp = self.finish.rect.y
            self.finish.rect.y = screen_dimensions[0] - (self.finish.rect.x + Finish.width)
            self.finish.rect.x = temp

            self.player.xspeed = 0
            self.player.yspeed = 0
            self.player.prevx = self.player.x
            self.player.prevy = self.player.y


            for c in self.components:
                if isinstance(c, Platform) or isinstance(c, Lava):
                    temp = c.rect.y
                    c.rect.y = screen_dimensions[0] - (c.rect.x + c.rect.width)
                    c.rect.x = temp
                    # Swap heights and widths (height <--> width)
                    temp = c.rect.height
                    c.rect.height = c.rect.width
                    c.rect.width = temp
               
            self.background_img = pygame.transform.rotate(self.background_img, 90)   # Rotate self.background_img 90 degrees counter-clockwise

    def gravity_shift_right(self):
        """Changes the coordinates of self.player, self.finish, and self.components (height/width too)
        to create the illusion of a gravity shift leftwards"""
        if self.allowed_shifts > 0:
            self.allowed_shifts -= 1
            sound.play_sound("gravity_shift")
            
            temp = self.player.x
            self.player.x = screen_dimensions[1] - (self.player.y + Player.head_height)
            self.player.y = temp

            temp = self.finish.rect.x
            self.finish.rect.x = screen_dimensions[1] - (self.finish.rect.y + Finish.height)
            self.finish.rect.y = temp

            self.player.xspeed = 0
            self.player.yspeed = 0
            self.player.prevx = self.player.x
            self.player.prevy = self.player.y


            for c in self.components:
                if isinstance(c, Platform) or isinstance(c, Lava):
                    temp = c.rect.x
                    c.rect.x = screen_dimensions[1] - (c.rect.y + c.rect.height)
                    c.rect.y = temp
                    # Swap heights and widths (height <--> width)
                    temp = c.rect.height
                    c.rect.height = c.rect.width
                    c.rect.width = temp
               
            self.background_img = pygame.transform.rotate(self.background_img, -90)   # Rotate self.background_img 90 degrees clockwise

"""
#    ____    _                               
#   |  _ \  | |   __ _   _   _    ___   _ __ 
#   | |_) | | |  / _` | | | | |  / _ \ | '__|
#   |  __/  | | | (_| | | |_| | |  __/ | |   
#   |_|     |_|  \__,_|  \__, |  \___| |_|   
#                        |___/               
"""
class Player(object):
    head_img = pygame.image.load("player.png").convert()
    head_width = head_img.get_rect().width
    head_height = head_img.get_rect().height

    w_pressed = False
    a_pressed = [False, False]   # The second boolean indicates whether this direction is on-queue
    s_pressed = False
    d_pressed = [False, False]   # The second boolean indicates whether this direction is on-queue

    jump_strength = 14   # With the current gravity and this jumps strength, the player can jump over a wall about 100 pixels high
    spawn_dist_above_ground = 50
    
    def __init__(self, game, pos):
        """@param pos is a tuple containing the x and y values of the upper left corner (x,y)"""
        self.game=game
        self.x = pos[0]
        self.y = pos[1]
        self.prevx = pos[0]
        self.prevy = pos[1]
        self.xspeed = 0
        self.yspeed = 0
        self.is_dead = False
        self.won_game = False
        self.on_ground = False
        self.rect = self.head_img.get_rect(x=self.x, y=self.y)
        Player.w_pressed = False
        Player.a_pressed = [False, False]
        Player.s_pressed = False
        Player.d_pressed = [False, False]
    def draw(self, screen):
        """Draws the player's head"""
        screen.blit(Player.head_img, (self.x, self.y))
    def update(self, events):
        """updates based on booleans properties/position based on booleans
        @param components is an array containing all the Level's components"""

        #Input detection for player
        for event in events:
            if event.type==KEYDOWN:
                if event.key==K_w: self.key_w_pressed()
                elif event.key==K_a: self.key_a_pressed()
                elif event.key==K_s: self.key_s_pressed()
                elif event.key==K_d: self.key_d_pressed()
            elif event.type==KEYUP:
                if event.key==K_w: self.key_w_released()
                elif event.key==K_a: self.key_a_released()
                elif event.key==K_s: self.key_s_released()
                elif event.key==K_d: self.key_d_released()

        # Updating position
        #x
        if Player.a_pressed[0]:
            self.xspeed = -5
        elif Player.d_pressed[0]:
            self.xspeed = 5
        else:
            self.xspeed = 0
            
        self.x += self.xspeed

        #y
        if Player.w_pressed and self.on_ground:   # jumping
            self.yspeed = -Player.jump_strength
            self.on_ground = False
        elif self.yspeed <= 10:
            self.yspeed += GRAVITY
        
        self.y += self.yspeed

        #update rect
        self.rect.x=self.x
        self.rect.y=self.y

        components=self.game.room.components
        
        # Collision logic; move player and set self.on_ground as necessary
        self.on_ground = False
        collided_with_something_from_sides = False
        collided_with_something_from_corner = False
        for c in components:
            if isinstance(c, Platform) and c.rect.colliderect(Player.head_img.get_rect(left=self.x, top=self.y)):   # Upon colliding with a platform
                #print ("(DEBUG) collison with platform.")
                if self.prevy + Player.head_height > c.rect.top and self.prevy < c.rect.bottom:   # hit from the side
                    if self.xspeed > 0: self.x = c.rect.left - Player.head_width
                    elif self.xspeed < 0: self.x = c.rect.right
                    collided_with_something_from_sides = True
                if self.prevx + Player.head_width > c.rect.left and self.prevx < c.rect.right:   # hit from top or bottom
                    if self.yspeed > 0:   # From top
                        self.y = c.rect.top - Player.head_height
                        self.on_ground = True
                    elif self.yspeed < 0:   # From bottom
                        self.y = c.rect.bottom
                        self.yspeed = self.yspeed/-2
                    collided_with_something_from_sides = True
                if not ((self.prevy + Player.head_height > c.rect.top and self.prevy < c.rect.bottom) or (self.prevx + Player.head_width > c.rect.left and self.prevx < c.rect.right)):
                    # Hit from corner
                    collided_with_something_from_corner = True
                    
        if not collided_with_something_from_sides and collided_with_something_from_corner:
            self.y+=1
        self.prevx = self.x
        self.prevy = self.y

        # Check for any lava collisions, setting self.is_dead as necessary
        for c in components:
            if isinstance(c, Lava) and c.rect.colliderect(Player.head_img.get_rect(left=self.x,top=self.y)):
                self.is_dead = True


        # Don't let player go too far up, left or right
        if self.y < 0:
            self.y = 0
            self.yspeed=self.yspeed/-2
        if self.x < 0: self.x = 0
        if self.x+Player.head_width > screen_dimensions[0]: self.x = screen_dimensions[0]-Player.head_width

        # Check if dead and set self.is_dead if player has gone off the screen appropiate
        if self.y > screen_dimensions[1] or self.y+Player.head_height < 0 or self.x + Player.head_width < 0 or self.x > screen_dimensions[0]:
            self.is_dead = True


        # Check for win
        if pygame.Rect.colliderect(self.rect, self.game.room.finish.rect): 
            self.won_game=True
            sound.play_sound("win")
        
    def key_w_pressed(self):
        if not Player.w_pressed and not Player.s_pressed:
            Player.w_pressed = True
    def key_a_pressed(self):
        Player.a_pressed[1] = True
        if not Player.d_pressed[1]: Player.a_pressed[0] = True
    def key_s_pressed(self):
        if not Player.s_pressed and not Player.w_pressed:
            Player.s_pressed = True
    def key_d_pressed(self):   
        Player.d_pressed[1] = True
        if not Player.a_pressed[1]: Player.d_pressed[0] = True
    def key_w_released(self):
        Player.w_pressed = False
    def key_a_released(self):
        Player.a_pressed[0] = False
        Player.a_pressed[1] = False
        if Player.d_pressed[1]: Player.d_pressed[0] = True
    def key_s_released(self):
        Player.s_pressed = False
    def key_d_released(self):
        Player.d_pressed[0] = False
        Player.d_pressed[1] = False
        if Player.a_pressed[1]: Player.a_pressed[0] = True

"""
#    _____   _           _         _     
#   |  ___| (_)  _ __   (_)  ___  | |__  
#   | |_    | | | '_ \  | | / __| | '_ \ 
#   |  _|   | | | | | | | | \__ \ | | | |
#   |_|     |_| |_| |_| |_| |___/ |_| |_|
#
"""
class Finish(object):
    img = pygame.image.load("finish_circle.png").convert()
    height = 40
    width = 40
    def __init__(self, game, pos):
         """@param pos is a tuple containing the x and y values of the upper right corner (x,y)"""
         self.game = game
         self.img.set_colorkey((0,0,0))
         self.rect = self.img.get_rect(x=pos[0], y=pos[1])
    def draw(self, screen):
        screen.blit(Finish.img, (self.rect.x, self.rect.y))
    
        
"""
#    ____    _           _      __                            
#   |  _ \  | |   __ _  | |_   / _|   ___    _ __   _ __ ___  
#   | |_) | | |  / _` | | __| | |_   / _ \  | '__| | '_ ` _ \ 
#   |  __/  | | | (_| | | |_  |  _| | (_) | | |    | | | | | |
#   |_|     |_|  \__,_|  \__| |_|    \___/  |_|    |_| |_| |_|
#                                                             
"""
class Platform(object):
    COLOR = (60, 60, 255)
    def __init__(self, game, rect):
        """@param rect is a pygame.Rect representing the bounds of the platform"""
        self.game=game
        self.rect = rect
    def draw(self, screen):
        pygame.draw.rect(screen, Platform.COLOR, self.rect)

"""
#    _                             
#   | |       __ _  __   __   __ _ 
#   | |      / _` | \ \ / /  / _` |
#   | |___  | (_| |  \ V /  | (_| |
#   |_____|  \__,_|   \_/    \__,_|
#                                  
"""
class Lava(object):
    COLORS = [(220, 130, 0), (235, 140, 0), (210, 160, 0)]
    color = COLORS[0]
    def __init__(self, game, rect, direction):
        """@param rect is a pygame.Rect representing the bounds of the lava block
        @param direction is an int value indicating the initial direction of the Lava block:
        0 = right
        1 = up
        2 = left
        3 = down"""
        self.game=game
        self.rect = rect
        self.org_x = rect.x
        self.org_y = rect.y
        # Move the lava block 1px in the idrection it is facing
        if direction == 0:
            self.rect.width += 1
        elif direction == 1:
            self.rect.y -= 1
            self.rect.height += 1
        elif direction == 2:
            self.rect.x -= 1
            self.rect.width += 1
        elif direction == 3:
            self.rect.height += 1
        self.direction = direction
    def draw(self, screen):
        pygame.draw.rect(screen, Lava.color, self.rect)
   

"""
#    _                             _    ____                                        _                  
#   | |       ___  __   __   ___  | |  / ___|   ___   _ __     ___   _ __    __ _  | |_    ___    _ __ 
#   | |      / _ \ \ \ / /  / _ \ | | | |  _   / _ \ | '_ \   / _ \ | '__|  / _` | | __|  / _ \  | '__|
#   | |___  |  __/  \ V /  |  __/ | | | |_| | |  __/ | | | | |  __/ | |    | (_| | | |_  | (_) | | |   
#   |_____|  \___|   \_/    \___| |_|  \____|  \___| |_| |_|  \___| |_|     \__,_|  \__|  \___/  |_|   
#      
"""
class LevelGenerator:
    @staticmethod
    def make_level(game, level_index, respawn_noise_at_start=False):
        """Constructs and return a new Level based on the given level_index"""

        """
        The standard ascii picture for showing the layout of a level.
        A good way to make the layout is by importing this into this
        into asciiflow.com.
        
               100 200 300 400 500 600 700
        (0,0)   |   |   |   |   |   |   | 
            +---+---+---+---+---+---+---+ 
            |                           | 
        100-+                           | 
            |                           | 
        200-+                           | 
            |                           | 
        300-+                           | 
            |                           | 
        400-+                           | 
            |                           | 
        500-+                           | 
            |                           | 
        600-+                           | 
            |                           | 
        700-+---------------------------+
        X = Platform
        S = Start
        F = Finish

        """
        if level_index == 0:
            """
                   100 200 300 400 500 600 700
            (0,0)   +   +   +   +   +   +   + 
                +---+---+---+---+---+---+---+ 
                |                           | 
            100++                           | 
                |                           | 
            200++                           | 
                |                           | 
            300++                           | 
                |                           | 
            400++                           | 
                |                           | 
            500++                           | 
                |    S                 F    | 
            600++   XXXXXXXXXXXXXXXXXXXXX   | 
                |                           | 
            700++---------------------------+ 
            X = Platform                      
            S = Start                         
            F = Finish                        

            """
            lvl = Level(game, (150, 460), True, (550,460), 0, 0, "clock-ascii.png", respawn_noise_at_start)
            lvl.components.append(Platform(game, pygame.Rect(100, 500, 500, 50)))
            lvl.add_tip_text("Use WASD to Move.", (200,250))
            lvl.add_tip_text("Finish the Level by moving to the white circle.", (200, 280))
            return lvl
        elif level_index == 1:
            lvl = Level(game, (125, 600 - Player.head_height), True, (600 - Finish.width, 150), 1, 1, "clock-ascii.png", respawn_noise_at_start)
            lvl.components.append(Platform(game, pygame.Rect(100, 600, 200, 50)))
            lvl.components.append(Platform(game, pygame.Rect(600, 150, 50, 500)))
            lvl.add_tip_text("Distort the universe! Use the arrow keys to shift gravity.", (100, 400))
            return lvl
        elif level_index == 2:
            lvl = Level(game, start_pos=(150, 550 - Player.head_height), spawn_drop = True, finish_pos=(250, 250), allowed_shifts=2, index=2, bground_img_filename="clock-ascii.png", make_respawn_cool_noise_at_start=respawn_noise_at_start)
            # Components
            lvl.components.append(Platform(game, pygame.Rect(100, 550, 400, 50)))
            lvl.components.append(Platform(game, pygame.Rect(500, 150, 50, 450)))
            lvl.components.append(Platform(game, pygame.Rect(100, 100, 450, 50)))
            lvl.components.append(Platform(game, pygame.Rect(100, 150, 50, 250)))
            lvl.components.append(Platform(game, pygame.Rect(100, 400, 300, 50)))
            lvl.components.append(Platform(game, pygame.Rect(350, 250, 50, 150)))
            lvl.components.append(Platform(game, pygame.Rect(200, 200, 200, 50)))
            lvl.components.append(Platform(game, pygame.Rect(200, 250, 50, 100)))
            # Tip text
            lvl.add_tip_text("You only get a few shifts per level.",(100,460))
            lvl.add_tip_text("Use them wisely.",(100,485))
            return lvl
        elif level_index == 3:
            lvl = Level(game, start_pos=(130,560), spawn_drop=True, finish_pos=(505,355), allowed_shifts=1, index=3, bground_img_filename="clock-ascii.png", make_respawn_cool_noise_at_start=respawn_noise_at_start)
            # Components
            lvl.components.append(Platform(game, pygame.Rect(50, 150, 250, 50)))
            lvl.components.append(Platform(game, pygame.Rect(50, 200, 50, 400)))
            lvl.components.append(Platform(game, pygame.Rect(50, 600, 200, 50)))
            lvl.components.append(Platform(game, pygame.Rect(200, 350, 50, 250)))
            lvl.components.append(Platform(game, pygame.Rect(200, 300, 100, 50)))
            lvl.components.append(Platform(game, pygame.Rect(400, 150, 250, 50)))
            lvl.components.append(Platform(game, pygame.Rect(400, 300, 50, 150)))
            lvl.components.append(Platform(game, pygame.Rect(450, 400, 150, 50)))
            lvl.components.append(Platform(game, pygame.Rect(600, 300, 50, 150)))
            # Tip text
            lvl.add_tip_text("Try different approaches.",(350,550))
            return lvl
        elif level_index == 4:
            lvl = Level(game, start_pos=(205, 555), spawn_drop=False, finish_pos=(305, 55), allowed_shifts=2, index=4, bground_img_filename="clock-ascii.png", make_respawn_cool_noise_at_start=respawn_noise_at_start)
            # Components
            lvl.components.append(Platform(game, pygame.Rect(300, 100, 50, 100)))
            lvl.components.append(Platform(game, pygame.Rect(350, 50, 50, 100)))
            lvl.components.append(Platform(game, pygame.Rect(150, 350, 350, 50)))
            lvl.components.append(Platform(game, pygame.Rect(500, 350, 50, 200)))
            lvl.components.append(Platform(game, pygame.Rect(150, 400, 50, 100)))
            lvl.components.append(Platform(game, pygame.Rect(100, 500, 150, 50)))
            lvl.components.append(Platform(game, pygame.Rect(250, 500, 50, 150)))
            lvl.components.append(Platform(game, pygame.Rect(200, 600, 50, 50)))
            # Tip text
            lvl.add_tip_text("Sometimes, you must shift in mid-air.",(150, 275))
            return lvl
        elif level_index == 5:
            lvl = Level(game, start_pos=(105, 505), spawn_drop = True, finish_pos=(605, 105), allowed_shifts=3, index=5, bground_img_filename="train-ascii.png", make_respawn_cool_noise_at_start=respawn_noise_at_start)
            # Components
            lvl.components.append(Platform(game, pygame.Rect(150, 0, 50, 100)))
            lvl.components.append(Platform(game, pygame.Rect(150, 100, 200, 50)))
            lvl.components.append(Platform(game, pygame.Rect(300, 150, 50, 300)))
            lvl.components.append(Platform(game, pygame.Rect(150, 400, 50, 150)))
            lvl.components.append(Platform(game, pygame.Rect(50, 550, 150, 50)))
            lvl.components.append(Platform(game, pygame.Rect(400, 200, 300, 50)))
            return lvl
        elif level_index == 6:
            lvl = Level(game, start_pos=(155, 505), spawn_drop = True, finish_pos=(605, 105), allowed_shifts=1, index=6, bground_img_filename="train-ascii.png", make_respawn_cool_noise_at_start=respawn_noise_at_start)
            lvl.components.append(Lava(game, pygame.Rect(250, 550, 100, 25), 1))
            # Components
            lvl.components.append(Lava(game, pygame.Rect(400, 550, 50, 25), 1))
            lvl.components.append(Lava(game, pygame.Rect(500, 550, 200, 25), 1))
            lvl.components.append(Platform(game, pygame.Rect(550, 50, 150, 50)))
            lvl.components.append(Platform(game, pygame.Rect(550, 100, 50, 200)))
            lvl.components.append(Platform(game, pygame.Rect(650, 100, 50, 200)))
            lvl.components.append(Platform(game, pygame.Rect(100, 550, 250, 50)))
            lvl.components.append(Platform(game, pygame.Rect(400, 550, 50, 50)))
            lvl.components.append(Platform(game, pygame.Rect(500, 550, 200, 50)))
            lvl.components.append(Platform(game, pygame.Rect(350, 500, 50, 100)))
            lvl.components.append(Platform(game, pygame.Rect(450, 400, 50, 200)))
            # Tip text
            lvl.add_tip_text("Lava is bad. Don't touch it.", (50, 300))
            return lvl
        elif level_index == 7:
            lvl = Level(game, start_pos=(355, 55), spawn_drop = True, finish_pos=(505, 55), allowed_shifts=3, index=7, bground_img_filename="train-ascii.png", make_respawn_cool_noise_at_start=respawn_noise_at_start)
            # Components
            lvl.components.append(Lava(game, pygame.Rect(250, 150, 25, 240), 2))
            lvl.components.append(Lava(game, pygame.Rect(400, 400, 25, 290), 2))
            lvl.components.append(Lava(game, pygame.Rect(500, 150, 25, 390), 2))
            lvl.components.append(Lava(game, pygame.Rect(400, 125, 125, 25), 3))
            lvl.components.append(Platform(game, pygame.Rect(450, 0, 50, 100)))
            lvl.components.append(Platform(game, pygame.Rect(250, 100, 300, 50)))
            lvl.components.append(Platform(game, pygame.Rect(250, 150, 50, 250)))
            lvl.components.append(Platform(game, pygame.Rect(400, 250, 50, 450)))
            lvl.components.append(Platform(game, pygame.Rect(500, 150, 50, 400)))
            return lvl
        elif level_index == 8:
            lvl = Level(game, start_pos=(130, 450), spawn_drop = True, finish_pos=(305, 65), allowed_shifts=2, index=8, bground_img_filename="train-ascii.png", make_respawn_cool_noise_at_start=respawn_noise_at_start)
            # Components
            lvl.components.append(Lava(game, pygame.Rect(0, 550, 100, 25), 1))
            lvl.components.append(Lava(game, pygame.Rect(200, 600, 500, 25), 1))
            lvl.components.append(Lava(game, pygame.Rect(0, 375, 400, 25), 3))
            lvl.components.append(Lava(game, pygame.Rect(405, 475, 90, 25), 3))
            lvl.components.append(Platform(game, pygame.Rect(0, 550, 100, 50)))
            lvl.components.append(Platform(game, pygame.Rect(100, 500, 100, 150)))
            lvl.components.append(Platform(game, pygame.Rect(200, 600, 500, 50)))
            lvl.components.append(Platform(game, pygame.Rect(0, 350, 400, 50)))
            lvl.components.append(Platform(game, pygame.Rect(400, 350, 100, 150)))
            return lvl
        elif level_index == 9:
            lvl = Level(game, start_pos=(605, 455), spawn_drop = True, finish_pos=(205, 555), allowed_shifts=2, index=9, bground_img_filename="train-ascii.png", make_respawn_cool_noise_at_start=respawn_noise_at_start)
            # Components
            lvl.components.append(Platform(game, pygame.Rect(550, 250, 150, 50)))
            lvl.components.append(Platform(game, pygame.Rect(550, 500, 150, 50)))
            lvl.components.append(Platform(game, pygame.Rect(350, 300, 200, 50)))
            lvl.components.append(Platform(game, pygame.Rect(300, 450, 250, 50)))
            lvl.components.append(Platform(game, pygame.Rect(300, 100, 50, 50)))
            lvl.components.append(Platform(game, pygame.Rect(250, 100, 50, 500)))
            lvl.components.append(Platform(game, pygame.Rect(100, 600, 200, 50)))
            lvl.components.append(Platform(game, pygame.Rect(100, 350, 50, 250)))
            lvl.components.append(Platform(game, pygame.Rect(125, 100, 50, 250)))
            lvl.components.append(Platform(game, pygame.Rect(150, 550, 50, 50)))
            lvl.components.append(Lava(game, pygame.Rect(350, 325, 200, 25), 3))
            lvl.components.append(Lava(game, pygame.Rect(300, 450, 250, 25), 1))
            lvl.components.append(Lava(game, pygame.Rect(250, 100, 25, 500), 2))
            lvl.components.append(Lava(game, pygame.Rect(325, 100, 25, 50), 0))
            lvl.components.append(Lava(game, pygame.Rect(150, 100, 25, 250), 0))
            lvl.components.append(Lava(game, pygame.Rect(125, 350, 25, 200), 0))
            return lvl
    ##    elif level_index == 10:
    ##        lvl = Level(start_pos=(0, 0), spawn_drop = True, finish_pos=(0, 0), allowed_shifts=0, index=10, bground_img_filename="train-ascii.png", make_respawn_cool_noise_at_start=respawn_noise_at_start)
    ##        # Components:
    ##        lvl.components.append(Platform(game, pygame.Rect(0, 0, 0, 0)))
    ##        return lvl
    ##    elif level_index == 11:
    ##        lvl = Level(start_pos=(0, 0), spawn_drop = True, finish_pos=(0, 0), allowed_shifts=0, index=11, bground_img_filename="train-ascii.png", make_respawn_cool_noise_at_start=respawn_noise_at_start)
    ##        # Components:
    ##        lvl.components.append(Platform(game, pygame.Rect(0, 0, 0, 0)))
    ##        return lvl
    ##    elif level_index == 12:
    ##        lvl = Level(start_pos=(0, 0), spawn_drop = True, finish_pos=(0, 0), allowed_shifts=0, index=12, bground_img_filename="train-ascii.png", make_respawn_cool_noise_at_start=respawn_noise_at_start)
    ##        # Components:
    ##        lvl.components.append(Platform(game, pygame.Rect(0, 0, 0, 0)))
    ##        return lvl
    ##    elif level_index == 13:
    ##        lvl = Level(start_pos=(0, 0), spawn_drop = True, finish_pos=(0, 0), allowed_shifts=0, index=13, bground_img_filename="train-ascii.png", make_respawn_cool_noise_at_start=respawn_noise_at_start)
    ##        # Components:
    ##        lvl.components.append(Platform(game, pygame.Rect(0, 0, 0, 0)))
    ##        return lvl
    ##    elif level_index == 14:
    ##        lvl = Level(start_pos=(0, 0), spawn_drop = True, finish_pos=(0, 0), allowed_shifts=0, index=14, bground_img_filename="train-ascii.png", make_respawn_cool_noise_at_start=respawn_noise_at_start)
    ##        # Components:
    ##        lvl.components.append(Platform(game, pygame.Rect(0, 0, 0, 0)))
    ##        return lvl
   
        else:
            print ("The requested level don't exist!")
            lvl = Level(game, start_pos=(300, 300), spawn_drop = False, finish_pos=(800, 800), allowed_shifts=100, index=50, bground_img_filename="clock-ascii.png")
            lvl.components.append(Platform(game, pygame.Rect(200, 310, 300, 50)))
            lvl.add_tip_text("Thankyou for beta testing!", (200, 200))
            return lvl

# Start game only if this is the module being run.
if __name__=="__main__":
    main()
