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

    def move(self, laser_velo):
        self.y += laser_velo
    
    def off_screen(self, height):
        return self.y > height or self.y < 0 
    
    def collision(self, obj):
        return collide(self, obj)
    
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
    
    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

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
        self.enemies_killed = 1

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(-vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        self.enemies_killed += 1
                        if laser in self.lasers:
                            self.lasers.remove(laser)
    
    def draw(self, window):
        super().draw(window)
        self.healthbar(PLAYGROUND)

    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y+self.get_height()+10, self.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y+self.get_height()+10, int(self.get_width()*(self.health/self.max_health)), 10))

# Enemy ship class which inherits from ship class
class Enemy(Ship):

    COLOR_MAP = {
        "red": (ENEMY_FIRST, RED_LASER),
        "blue": (ENEMY_SECOND, BLUE_LASER),
    }

    def __init__(self, x, y, color, health= 100):
        super().__init__(x, y, health)
        self.ship_img = self.COLOR_MAP[color][0]
        self.laser_img = self.COLOR_MAP[color][1]
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health
    
    def move(self, vel): # To move down the enemy ship
        self.y += vel

    def shoot(self): # To offset the laser position
        if self.cool_down_counter == 0:
            laser = Laser(self.x-20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

def sound_check(obj: Laser): # To see if the laser is out of bound or not
    if obj.y < 0 or obj.y > 750:
        return False
    else:
        return True

def main():
    run = True
    lost = False
    level = 0
    lives = 2
    FPS = 60
    PLAYER_POS = 5
    LASER_POS = 5
    ENEMY_POS = 1
    enemies = []
    wave_length = 0
    main_font = pygame.font.SysFont("comicsans", size=50)
    player = Player(300, 600)

    # semaphore to handle making and moving enemies
    semaphore_enemies = threading.Semaphore(1)
    
    clock = pygame.time.Clock()
    
    # thread 1 - check if we lost
    def check_lost():
        nonlocal run, lost
        if lives <= 0 or player.health <= 0:
            run = False
    
    # thread 2 - redraw all map
    def draw_window():
        PLAYGROUND.blit(BG, (0,0))
        
        level_label = main_font.render(f"Level: {level}", 1, (255,255,255))
        lives_label = main_font.render(f"Lives: {lives}", 1, (255,255,255))
        PLAYGROUND.blit(lives_label, (10, 10))
        PLAYGROUND.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))
        
        for enemy in enemies:
            enemy.draw(PLAYGROUND)

        player.draw(PLAYGROUND)
        
        pygame.display.update()

    # thread 3 - checking if all enemies are killed and making new
    def check_enemies():
        nonlocal level, wave_length
        semaphore_enemies.acquire()
        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for _ in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500 *(1+level//4), -100), random.choice(["red", "blue"]))
                enemies.append(enemy)
        semaphore_enemies.release()

    #thread 4 - moving enemies and their shots
    def move_enemies():
        semaphore_enemies.acquire()
        for enemy in enemies[:]:
            enemy.move(ENEMY_POS)
            enemy.move_lasers(LASER_POS, player)
            if random.randrange(0, 2*FPS) == 1: # Or shoot every 2 second with randomness
                enemy.shoot()
            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
                player.enemies_killed += 1
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)
        semaphore_enemies.release()

    while run:
        clock.tick(FPS)
        
        draw_thr = threading.Thread(target=draw_window)
        draw_thr.start()
        
        lost_thr = threading.Thread(target=check_lost)
        lost_thr.start()

        enemy_thr = threading.Thread(target=check_enemies)
        enemy_thr.start()

        enemy_mov_thread = threading.Thread(target=move_enemies)
        enemy_mov_thread.start()
        
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

        player.move_lasers(LASER_POS, enemies)    
    return True, player.enemies_killed

    
def menu():
    global enemies_count
    enemies_count = 0
    title_font = pygame.font.SysFont("comicsans", size=70)
    run = True
    lost = False
    while run:
        label_counter = "You killed " + str(enemies_count - 1) + " enemies"
        title_label = title_font.render("Press the mouse", 1, (255,255,255))
        lost_label = title_font.render("YOU LOST!", 1, (255,255,255))
        lost_label2 = title_font.render(label_counter, 1, (255,255,255))
        PLAYGROUND.blit(BG, (0,0))
        if lost:
            PLAYGROUND.blit(lost_label, ((WIDTH-lost_label.get_width())//2, (HEIGHT-lost_label.get_height())//2 - 60))
            PLAYGROUND.blit(lost_label2, ((WIDTH-lost_label2.get_width())//2, (HEIGHT-lost_label.get_height())//2 + 60))
        else:
            PLAYGROUND.blit(title_label, ((WIDTH-title_label.get_width())//2, (HEIGHT-title_label.get_height())//2))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                res=main()
                lost=res[0]
                enemies_count=res[1]

    pygame.quit()

if __name__ == "__main__":
    menu()