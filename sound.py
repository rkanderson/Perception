
"""Deals with all things sound"""

import pygame
pygame.init()

sounds = {}
sounds["win"]=pygame.mixer.Sound("win.ogg")
sounds["level_start"]=pygame.mixer.Sound("level_start.ogg")
sounds["gravity_shift"]=pygame.mixer.Sound("gravity_shift.ogg")

def play_sound(sound_name):
	sounds[sound_name].play()