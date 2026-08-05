from pygame import *
from random import randint
#add
import sounddevice as sd
import numpy as np

sr = 16000
block = 256
mic_level = 0.0

def audio_cd(indata, frames, time, status):
    global mic_level
    if status:
        return
    rms = float(np.sqrt(np.mean(indata**2)))
    mic_level = 0.85 * mic_level + 0.15 * rms
#add

init()
window_size = 1200, 800
window = display.set_mode(window_size)
clock = time.Clock()

#add
player_img = transform.scale(image.load('WED_19/flappy_bird/image-removebg-preview.png'), (100,100))
pipe_img = transform.scale(image.load('WED_19/flappy_bird/image-removebg-preview (1).png'), (140, 500))

player_rect = player_img.get_rect()
player_rect.x = 150
player_rect.y = 300
#add
def generate_pipes(count, pipe_width=140, gap=280, min_height=50, max_height=440, distance=650):
    pipes = []
    start_x = window_size[0]
    for i in range(count):
        height = randint(min_height, max_height)
        top_pipe = Rect(start_x, 0, pipe_width, height)
        bottom_pipe = Rect(start_x, height + gap, pipe_width, window_size[1] - (height + gap))
        #correected 
        pipes.append(("top", top_pipe)) 
        pipes.append(("bottom", bottom_pipe))
        #correected 
        start_x += distance
    return pipes

pipes = generate_pipes(150)
main_font = font.Font(None, 100)
score = 0
lose = False
wait = 40 #add
y_vel = 0.0 # correct
#add
gravity = 0.6
THRESH = 0.001
IMPULSE = -8.0

with sd.InputStream(samplerate=sr, channels=1, blocksize=block, callback=audio_cd):
    while True:
        for e in event.get():
            if e.type == QUIT:
                quit()
        if mic_level > THRESH:
            y_vel = IMPULSE
        y_vel += gravity
        player_rect.y += int(y_vel)
        window.fill("skyblue")
        window.blit(player_img, player_rect)
        for pipe_type, pipe in pipes[:]:
            if not lose:
                pipe.x -= 10
            if pipe_type == "top":
                flipped = transform.flip(pipe_img, False, True)
                window.blit(flipped, (pipe.x, pipe.bottom - 500))
            else:
                window.blit(pipe_img, (pipe.x, pipe.y))
            if pipe.x <= -100:
                pipes.remove((pipe_type, pipe))
                score += 0.5
            if player_rect.colliderect(pipe):
                lose = True
        if len(pipes) < 8:
            pipes += generate_pipes(150)
        score_text = main_font.render(f"Score: {int(score)}", True, "black")
        window.blit(score_text, (600 - score_text.get_width() // 2, 40))
        display.update()
        clock.tick(60)
        keys = key.get_pressed()
        if keys[K_r] and lose:
            lose = False
            score = 0
            pipes = generate_pipes(150)
            player_rect.y = 300
            y_vel = 0.0
        if player_rect.bottom > window_size[1]:
            player_rect.bottom = window_size[1]
            y_vel = 0.0
        if player_rect.top < 0:
            player_rect.top = 0
            if y_vel < 0:
                y_vel = 0.0
        if lose and wait > 1:
            for i, pipe in pipes:
                pipe.x += 8
            wait -= 1
        else:
            lose = False
            wait = 40
#add