import pygame
import time
import random
import sys

WINDOW_WIDTH = 1291
WINDOW_HEIGHT = 696
SHIP_HEIGHT = 610
REFRESH_RATE = 60
clock = pygame.time.Clock()
AUTO = False

pygame.init()
pygame.font.init()
pygame.mixer.init()
pygame.mixer.set_num_channels(4)
PewSFX = pygame.mixer.Sound('venv/pew.wav')
pews = pygame.mixer.Channel(0)
pews.set_volume(0.05)
BoomSFX = pygame.mixer.Sound('venv/explosion.wav')
booms = pygame.mixer.Channel(1)
booms.set_volume(0.05)
clicks = pygame.mixer.Channel(2)
PlaySFX = pygame.mixer.Sound('venv/play_button.wav')
FailSFX = pygame.mixer.Sound('venv/fail.wav')
music = pygame.mixer.Channel(3)
MusicSound = pygame.mixer.Sound('venv/game_music.wav')
music.set_volume(0.65)
scorefont = pygame.font.Font("venv/font.TTF",36)
titlefont = pygame.font.Font("venv/font.TTF",60)
subtitlefont = pygame.font.Font("venv/font.TTF",44)
spaceinvadersfont = pygame.font.Font("venv/font.TTF",140)
size = (WINDOW_WIDTH, WINDOW_HEIGHT)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("venv/Space Invaders")
background = pygame.image.load("venv/space_background.jpg")
# screen.blit(background,[0,0])
scorefile = open("venv/Scores.txt")
maxsc = 0
for line in scorefile:
    if int(line) > maxsc:
        maxsc = int(line)
scorefile.close()
enemy_1 = pygame.image.load('venv/enemy_1.png').convert()
enemy_1.set_colorkey((64,0,0))
enemy_2 = pygame.image.load('venv/enemy_2.png').convert()
enemy_2.set_colorkey((192,192,192))
enemy = [enemy_1,enemy_2]
# screen.blit(enemy,[WINDOW_WIDTH//2,WINDOW_HEIGHT//2])
ship = pygame.image.load('venv/ship.png').convert()
ship.set_colorkey((255,201,14))
# screen.blit(ship,[WINDOW_WIDTH//2,610])
laser = pygame.image.load('venv/laser.png').convert()
laser.set_colorkey((112,146,190))
# screen.blit(laser,[200,200])
# loadscreen = pygame.image.load('loading_screen.png')
# screen.blit(loadscreen,[WINDOW_WIDTH//2-250, WINDOW_HEIGHT//2-170])
# gameover = pygame.image.load('game_over.png').convert()
# gameover.set_colorkey((136,0,21))
explosion = pygame.image.load('venv/explosion.png').convert()
explosion.set_colorkey((255,255,255))
# screen.blit(gameover,[WINDOW_WIDTH//2-300, WINDOW_HEIGHT//2-100])
# pygame.display.flip()
# time.sleep(2)

Sound_On = True

score = [0]
enemies = []
explosions = [] #explosion objects are of the type ([x,y],time)
lasers = []
pos = [WINDOW_WIDTH//2,SHIP_HEIGHT]

def tick_lasers():
    for i in lasers:
        if i[1]<10:
            lasers.remove(i)
        else:
            i[1]-=10

#tick_enemies returns 1 if enemy has reached the end of the screen, 0 otherwise
def tick_enemies(delta):
    for i in enemies:
        if i[1]>=WINDOW_HEIGHT-delta:
            return True
        else:
            i[1]+=delta
    return False

def check_collisions():
    for i in enemies:
        for j in lasers:
            if -65<=i[0]-j[0]<=10 and -10<=i[1]-j[1]<=10:
                explosions.append([i,1])
                score[0]+=1
                if Sound_On:
                    booms.play(BoomSFX)
                enemies.remove(i)
                lasers.remove(j)


def render_highscore():
    text = "Highscore- "+str(maxsc if maxsc>score[0] else score[0])
    surface = scorefont.render(text,False,(255,255,255))
    screen.blit(surface,[50,100])

def render_score():
    text = "Score- "+str(score[0])
    surface = scorefont.render(text,False,(255,255,255))
    screen.blit(surface,[50,50])


def create_title(inverse):
    colors = [None,None]
    if inverse:
        colors[0] = (255,255,255)
        colors[1] = (153,217,234)
    else:
        colors[0] = (136,0,21)
        colors[1] = (255,255,255)
    screen.blit(background,[0,0])
    screen.blit(spaceinvadersfont.render("Space Invaders",False,colors[0]),[WINDOW_WIDTH//2-400,25])
    screen.blit(subtitlefont.render("Press arrows to move",False,colors[1]),[WINDOW_WIDTH//2-350,250])
    screen.blit(subtitlefont.render("Press Left Click To Shoot", False, colors[1]), [WINDOW_WIDTH // 2 - 350, 290])
    screen.blit(subtitlefont.render("Press Q for Autoplay", False, colors[1]), [WINDOW_WIDTH // 2 - 350, 330])
    screen.blit(subtitlefont.render("Press M to toggle sound", False, colors[1]),
                [WINDOW_WIDTH // 2 - 350, 370])
    screen.blit(subtitlefont.render("Dont let the enemies get to the bottom!", False, colors[1]),
                [WINDOW_WIDTH // 2 - 350, 450])
    pygame.draw.rect(screen,colors[0],(WINDOW_WIDTH//2 - 370 ,490,150,45))
    pygame.draw.rect(screen,colors[0],(WINDOW_WIDTH//2 - 20 ,490,150,45))
    screen.blit(titlefont.render("Play",False,colors[1]),[WINDOW_WIDTH//2-360, 495])
    screen.blit(titlefont.render("Quit",False,colors[1]),[WINDOW_WIDTH//2-10,495])
    pygame.display.flip()

def render_pressed_button(posx,posy,text):
    pygame.draw.rect(screen,(255,201,14),(posx,posy,150,45))
    screen.blit(titlefont.render(text, False, (0,0,0)), [posx+10, posy])
    pygame.display.flip()
    if Sound_On:
        clicks.play(PlaySFX if text=="Play" else FailSFX)
    time.sleep(0.5)



finish = False
end_game = False

while not end_game:
    finish = False
    go_to_game = False
    inverse = False
    sec = 0
    freeze_time = 0
    ticks = 0
    scorefile = open("venv/Scores.txt")
    maxsc = 0
    for line in scorefile:
        if int(line) > maxsc:
            maxsc = int(line)
    scorefile.close()
    while not go_to_game:
        click = []
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                end_game = True
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_LEFT:
                click = pygame.mouse.get_pos()
                if WINDOW_WIDTH//2-370<=click[0]<=WINDOW_WIDTH//2-220 and 490<=click[1]<=535:
                    render_pressed_button(WINDOW_WIDTH//2-370,490,"Play")
                    freeze_time = pygame.time.get_ticks()
                    go_to_game = True
                    break
                elif WINDOW_WIDTH//2-20<=click[0]<=WINDOW_WIDTH//2+130 and 490<=click[1]<=535:
                    render_pressed_button(WINDOW_WIDTH // 2 - 20,490, "Quit")
                    end_game = True
                    sys.exit()
        if go_to_game:
            break
        create_title(inverse)
        t_ticks = ticks
        ticks = pygame.time.get_ticks()
        if ticks//500 > t_ticks//500:
            inverse = not inverse
    enemies = []
    score = [0]
    lasers = []
    generation_rate = 1000
    ticks = 0
    finish = False
    while not finish:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                end_game = True
                finish = True
                break
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_LEFT:
                if Sound_On:
                    pews.play(PewSFX)
                lasers.append([pos[0]+45,pos[1]])
            elif event.type == pygame.MOUSEMOTION:
                pos[0] = pygame.mouse.get_pos()[0]-45
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    pos[0]-= (50 if pos[0]>50 else 0)
                elif event.key == pygame.K_RIGHT:
                    pos[0]+= (50 if pos[0]<WINDOW_WIDTH-50 else 0)
                elif event.key == pygame.K_q:
                    AUTO = not AUTO
                elif event.key == pygame.K_m:
                    Sound_On = not Sound_On
        if finish:
            break
        t_ticks = ticks
        ticks = pygame.time.get_ticks()-freeze_time
        if AUTO:
            if len(enemies) !=0:
                pos = [enemies[0][0],SHIP_HEIGHT]
                if ticks//generation_rate > t_ticks//generation_rate:
                    lasers.append([pos[0]+45,pos[1]])
        screen.blit(background,[0,0])
        if ticks//generation_rate> t_ticks//generation_rate:
            enemies.append([random.randint(0,WINDOW_WIDTH-50),-10])
            if ticks//27000 > t_ticks//27000 and Sound_On:
                music.play(MusicSound)
        delta = (((ticks+10000)//20000)+1) * 0.2
        tick_lasers()
        finish = tick_enemies(delta)
        if finish:
            gameover = spaceinvadersfont.render("Game Over",False,(255,201,14))
            screen.blit(gameover, [WINDOW_WIDTH//2-300, WINDOW_HEIGHT // 2])
            pygame.display.flip()
            if Sound_On:
                music.play(FailSFX)
                time.sleep(0.5)
                music.play(FailSFX)
                time.sleep(2)
            else:
                time.sleep(2.5)
            continue
        check_collisions()
        for i in enemies:
            screen.blit(enemy[ticks//500 % 2],i)
        for i in lasers:
            screen.blit(laser,i)
        for i in explosions:
            if i[1]==0:
                explosions.remove(i)
            else:
                screen.blit(explosion,i[0])
            i[1]+=1
            i[1]%=31
        screen.blit(ship,pos)
        render_score()
        render_highscore()
        pygame.display.flip()
        if ticks//20000> t_ticks//20000:
            generation_rate/=1.1
            generation_rate = int(generation_rate)
            # if generation_rate<250:
            #     generation_rate = 250
    scorefile = open("venv/Scores.txt",'a')
    scorefile.write(str(score[0])+"\n")
    scorefile.close()










