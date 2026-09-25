import random
import pygame
from game.jewel.settings import CELL_SIZE, SCORE_PANEL_HEIGHT, SWAP_SPEED, FALL_SPEED

class Particle:
    def __init__(self, x, y, color):
        self.x, self.y = x, y
        self.color = color
        self.vx = random.uniform(-4, 4)
        self.vy = random.uniform(-6, 2)
        self.gravity = 0.25
        self.radius = random.randint(3, 6)
        self.alpha = 255

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.alpha = max(0, self.alpha - 8)
        return self.alpha > 0

    def draw(self, surface):
        if self.alpha <= 0: return
        p_surf = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        r, g, b = self.color
        pygame.draw.circle(p_surf, (r, g, b, self.alpha), (self.radius, self.radius), self.radius)
        surface.blit(p_surf, (self.x - self.radius, self.y - self.radius))

class Cell:
    def __init__(self, color, r, c):
        self.color, self.r, self.c = color, r, c
        self.x, self.target_x = c * CELL_SIZE, c * CELL_SIZE
        self.y = r * CELL_SIZE + SCORE_PANEL_HEIGHT
        self.target_y = self.y
        self.item_type = "NORMAL"
        self.alpha = 255
        self.is_destroying = False

    def update(self):
        if self.is_destroying:
            self.alpha = max(0, self.alpha - 25)
            return self.alpha > 0
        moved = False
        if self.x < self.target_x: self.x = min(self.x + SWAP_SPEED, self.target_x); moved = True
        elif self.x > self.target_x: self.x = max(self.x - SWAP_SPEED, self.target_x); moved = True
        if self.y < self.target_y: self.y = min(self.y + FALL_SPEED, self.target_y); moved = True
        elif self.y > self.target_y: self.y = max(self.y - FALL_SPEED, self.target_y); moved = True
        return moved

    def draw(self, s):
        surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        rect = pygame.Rect(3, 3, CELL_SIZE - 6, CELL_SIZE - 6)
        r, g, b = self.color
        pygame.draw.rect(surf, (r, g, b, self.alpha), rect, border_radius=6)
        if self.is_destroying:
            pygame.draw.rect(surf, (255, 255, 255, self.alpha), rect, 3, border_radius=6)
        if self.item_type == "H_MISSILE": pygame.draw.line(surf, (255,255,255, self.alpha), (8, CELL_SIZE//2), (CELL_SIZE-8, CELL_SIZE//2), 5)
        elif self.item_type == "V_MISSILE": pygame.draw.line(surf, (255,255,255, self.alpha), (CELL_SIZE//2, 8), (CELL_SIZE//2, CELL_SIZE-8), 5)
        elif self.item_type == "BOMB": pygame.draw.rect(surf, (0,0,0, self.alpha), (12, 12, CELL_SIZE-24, CELL_SIZE-24), 4)
        elif self.item_type == "PROPELLER": pygame.draw.circle(surf, (255,255,255, self.alpha), (CELL_SIZE//2, CELL_SIZE//2), 8)
        elif self.item_type == "RAINBOW": pygame.draw.circle(surf, (255,255,255, self.alpha), (CELL_SIZE//2, CELL_SIZE//2), 14, 3)
        s.blit(surf, (self.x, self.y))

def create_cell_by_type(item_type, color, r, c):
    cell_obj = Cell(color, r, c)
    cell_obj.item_type = item_type
    if item_type == "RAINBOW": cell_obj.color = (255, 255, 255)
    return cell_obj
