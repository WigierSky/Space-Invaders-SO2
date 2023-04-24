import time
import threading
import os
import random
import pygame

pygame.mixer.pre_init(44100, 16, 4, 4096) #frequency, size, channels, buffersize
pygame.init()
WIDTH, HEIGHT = 750, 750
PLAYGROUND = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SPACE INVADERS")

# spaceships assets
ENEMY_FIRST = pygame.image.load(os.path.join("assets", "enemy_1.png"))
ENEMY_SECOND = pygame.image.load(os.path.join("assets", "enemy_2.png"))
MAIN_SPACESHIP = pygame.image.load(os.path.join("assets", "ship_main.png"))

# laser assets
RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))

# background asset
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")), (WIDTH, HEIGHT))

# laser class
class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)
    
    def draw(self, window):
        window.blit(self.img, (self.x, self.y))
    
# ship class (parent to enemy and main player)
class Ship:
    COOLDOWN = 30
    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0
    
    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        # DRAWING LASER
        for laser in self.lasers:
            laser.draw(window)

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()
    
    def get_height(self):
        return self.ship_img.get_height()
    
# Player Ship class which inherits from Ship class
class Player(Ship):
    def __init__(self, x, y, health= 100):
        super().__init__(x, y, health)
        self.ship_img = MAIN_SPACESHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health
    
    def draw(self, window):
        super().draw(window)
        self.healthbar(PLAYGROUND)

    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y+self.get_height()+10, self.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y+self.get_height()+10, int(self.get_width()*(self.health/self.max_health)), 10))


def main():
    run = True
    lost = False
    level = 0
    lives = 1
    FPS = 60
    PLAYER_POS = 5
    LASER_POS = 5
    ENEMY_POS = 1
    enemies = []
    main_font = pygame.font.SysFont("comicsans", size=50)
    player = Player(300, 600)
    
    clock = pygame.time.Clock()
    
    # thread 1 - check if we lost
    def check_lost():
        if lives <= 0 or player.health <= 0:
            print(lost)
            lost = True
    
    # thread 2 - redraw all map
    def draw_window():
        PLAYGROUND.blit(BG, (0,0))
        
        level_label = main_font.render(f"Level: {level}", 1, (255,255,255))
        lives_label = main_font.render(f"Lives: {lives}", 1, (255,255,255))
        PLAYGROUND.blit(lives_label, (10, 10))
        PLAYGROUND.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))
        
        player.draw(PLAYGROUND)
        
        if lost:
            lost_label = main_font.render("YOU LOST!", 1, (255,255,255))
            PLAYGROUND.blit(lost_label, ((WIDTH-lost_label.get_width())//2, (HEIGHT-lost_label.get_height())//2))
        
        # updating display
        pygame.display.update()

    while run:
        clock.tick(FPS)
        
        draw_thr = threading.Thread(target=draw_window)
        draw_thr.start()
        
        lost_thr = threading.Thread(target=check_lost)
        lost_thr.start()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
        
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_a] or keys[pygame.K_LEFT]) and player.x - PLAYER_POS > 0: # left
            player.x -= PLAYER_POS
        if (keys[pygame.K_d] or keys[pygame.K_RIGHT]) and player.x + PLAYER_POS + player.get_width() < WIDTH: # right
            player.x += PLAYER_POS
        if (keys[pygame.K_w] or keys[pygame.K_UP]) and player.y - PLAYER_POS > 0: # up
            player.y -= PLAYER_POS
        if (keys[pygame.K_s] or keys[pygame.K_DOWN]) and player.y + PLAYER_POS + player.get_height() + 15 < HEIGHT: # down
            player.y += PLAYER_POS
        if keys[pygame.K_SPACE]:
            player.shoot()
    

    

def menu():
    title_font = pygame.font.SysFont("comicsans", size=70)
    run = True
    while run:
        title_label = title_font.render("Press the mouse", 1, (255,255,255))
        PLAYGROUND.blit(BG, (0,0))
        PLAYGROUND.blit(title_label, ((WIDTH-title_label.get_width())//2, (HEIGHT-title_label.get_height())//2))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()

if __name__ == "__main__":
    menu()