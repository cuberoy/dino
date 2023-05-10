import pygame
import time
import random
import math

pygame.init()
pygame.mixer.init()
pygame.font.init()

WIDTH, HEIGHT = 600, 150
FONT = pygame.font.Font('assets\PressStart2P-Regular.ttf', 12)

# Define sprites
DINO_RUN_1 = pygame.image.load('assets\dino_run_1.png')
DINO_RUN_2 = pygame.image.load('assets\dino_run_2.png')
DINO_JUMP = pygame.image.load('assets\dino_jump.png')
DINO_DUCK_1 = pygame.image.load('assets\dino_duck_1.png')
DINO_DUCK_2 = pygame.image.load('assets\dino_duck_2.png')
DINO_DEAD = pygame.image.load('assets\dino_dead.png')
CACTUS_1 = pygame.image.load('assets\cactus_1.png')
CACTUS_2 = pygame.image.load('assets\cactus_2.png')
CACTUS_3 = pygame.image.load('assets\cactus_3.png')
CACTUS_4 = pygame.image.load('assets\cactus_4.png')
CACTUS_5 = pygame.image.load('assets\cactus_5.png')
CACTUS_6 = pygame.image.load('assets\cactus_6.png')
BIRD_1 = pygame.image.load('assets\\bird_1.png')
BIRD_2 = pygame.image.load('assets\\bird_2.png')
CLOUD = pygame.image.load('assets\cloud.png')

# Set up main window display
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dinosaur")
pygame.display.set_icon(DINO_JUMP)

WHITE = (255, 255, 255)
GREY = (83, 83, 83)

JUMP_SOUND = pygame.mixer.Sound('assets\jump_sound.mp3')
DEAD_SOUND = pygame.mixer.Sound('assets\dead_sound.mp3')
MILESTONE_SOUND = pygame.mixer.Sound('assets\milestone_sound.mp3')

GROUND = pygame.Rect(0, 130, WIDTH, 1)
DINO_RUN_FRAMES = [DINO_RUN_1, DINO_RUN_2]
DINO_DUCK_FRAMES = [DINO_DUCK_1, DINO_DUCK_2]
BIRD_FRAMES = [BIRD_1, BIRD_2]
BIRD_HEIGHTS = [50, 66, 98]
CACTUS_LIST = [CACTUS_1, CACTUS_2, CACTUS_3, CACTUS_4, CACTUS_5, CACTUS_6]
INITIAL_JUMP_VEL = 8
GRAVITY = 0.35
MAX_Y_POS = 0
DINO_X_POS = 30
INITIAL_MAP_VEL = 7
CLOUD_VEL = 2

FPS = 60

DINO_ANIMATION_COOLDOWN = 100

SCORE_BLINK_EVENT = pygame.USEREVENT + 1
SCORE_BLINK_TIMEOUT = 2000
SCORE_BLINK_COOLDOWN = 250

BIRD_FLAP_EVENT = pygame.USEREVENT + 2
BIRD_ANIMATION_COOLDOWN = 200

SCORE_INCREMENT_EVENT = pygame.USEREVENT + 3
SCORE_INCREMENT_COOLDOWN = 100

BACKGROUND_CHANGE_EVENT = pygame.USEREVENT + 4
BACKGROUND_CHANGE_TIMEOUT = 1530
BACKGROUND_CHANGE_COOLDOWN = 6

high_score = ''
background_color = WHITE

def draw(score, high_score, grains, clouds, dino_sprite, dino, cactus_sprites, cacti, bird_frame, birds):
    # Draw Background
    global background_color
    WIN.fill(background_color)

    # Draw Ground
    pygame.draw.rect(WIN, GREY, GROUND)

    # Draw score
    score_text = FONT.render(score, 1, GREY)
    WIN.blit(score_text, (525, 10))

    # Draw high score
    if high_score != '':
        high_score_text = FONT.render("HI " + high_score, 1, GREY)
        WIN.blit(high_score_text, (415, 10))

    # Draw Grains
    for grain in grains:
        pygame.draw.rect(WIN, GREY, grain)

    # Draw clouds
    for cloud in clouds:
        WIN.blit(CLOUD, (cloud.x, cloud.y))

    # Draw Cacti
    for i, cactus in enumerate(cacti):
        WIN.blit(cactus_sprites[i], (cactus.x, cactus.y))

    # Draw Birds
    for bird in birds:
        WIN.blit(BIRD_FRAMES[bird_frame], (bird.x, bird.y))

    # Draw Dino
    WIN.blit(dino_sprite, (dino.x, dino.y))

    # Update
    pygame.display.update()

def check_collision(dino_image, dino_rect, obstacle_images, obstacle_rects):

    for i, obstacle_rect in enumerate(obstacle_rects):
        dino_sprite = pygame.sprite.Sprite()
        dino_sprite.image = dino_image
        dino_sprite.rect = dino_rect

        obstacle_sprite = pygame.sprite.Sprite()
        obstacle_sprite.image = obstacle_images[i]
        obstacle_sprite.rect = obstacle_rect
        dino_mask = pygame.mask.from_surface(dino_sprite.image)
        obstacle_mask = pygame.mask.from_surface(obstacle_sprite.image)

        if pygame.sprite.collide_mask(dino_sprite, obstacle_sprite):
            return True

    return False


def get_sprite_ground_y_pos(sprite):
    return 140 - sprite.get_height()

def get_dino_rect(dino_sprite, dino_y_pos):
    return pygame.Rect(DINO_X_POS, dino_y_pos, dino_sprite.get_width(), dino_sprite.get_height())

def start_game():
    wait_for_input = True

    # Draw Background
    WIN.fill(WHITE)

    # Draw Ground
    pygame.draw.rect(WIN, GREY, GROUND)

    # Draw Dino
    dino = get_dino_rect(DINO_JUMP, get_sprite_ground_y_pos(DINO_JUMP))
    WIN.blit(DINO_JUMP, (dino.x, dino.y))

    # Update
    pygame.display.update()

    while wait_for_input:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        # Get list of keys pressed
        keys = pygame.key.get_pressed()
        # Restart the game
        if keys[pygame.K_SPACE] or keys[pygame.K_UP]:
            return

def main():
    run = True
    clock = pygame.time.Clock()
    last_update_duck = pygame.time.get_ticks()
    last_update_run = pygame.time.get_ticks()
    last_update_blink_score = pygame.time.get_ticks()
    last_cactus_time = pygame.time.get_ticks()

    start_time = time.time()
    elasped_time = 0

    score = 0
    score_text = ''
    score_incrementer = 1
    score_visible = True
    score_blinking = False
    score_target = 1
    map_vel = INITIAL_MAP_VEL

    grain_add_increment = 0
    grain_ms_count = 0
    grains = []

    cloud_add_increment = 500
    cloud_ms_count = 0
    clouds = []

    cactus_add_increment = random.randint(500, 1200)
    cactus_ms_count = 0
    cacti = []
    cactus_sprites = []

    bird_add_increment = random.randint(2500, 3000)
    bird_ms_count = 0
    birds = []
    bird_sprites = []

    obstacle_rects = []
    obstacle_sprites = []

    duck_frame = 0
    run_frame = 0
    bird_frame = 0
    duck = False
    jump = False
    hit = False

    dino_sprite = DINO_JUMP
    dino = get_dino_rect(dino_sprite, get_sprite_ground_y_pos(dino_sprite))

    pygame.time.set_timer(BIRD_FLAP_EVENT, BIRD_ANIMATION_COOLDOWN)
    pygame.time.set_timer(SCORE_INCREMENT_EVENT, SCORE_INCREMENT_COOLDOWN)

    global high_score
    global background_color
    background_color = WHITE
    rgb = 255
    background_700_target = 1
    background_900_target = 1
    white_to_black = True
    
    wait_for_input = False

    while run:
        ticker = clock.tick(FPS)
        grain_ms_count += ticker
        cloud_ms_count += ticker
        cactus_ms_count += ticker
        bird_ms_count += ticker

        elasped_time = time.time() - start_time
        current_time = pygame.time.get_ticks()

        dino = get_dino_rect(dino_sprite, dino.y)

        # Change map velocity
        map_vel = round(INITIAL_MAP_VEL + elasped_time / 25, 2)

        # Event handler
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

            # Event handle score blinking
            if event.type == SCORE_BLINK_EVENT:
                score_visible = not score_visible
                if current_time - last_update_blink_score >= SCORE_BLINK_TIMEOUT:
                    last_update_blink_score = current_time
                    score_blinking = False
                    pygame.time.set_timer(SCORE_BLINK_EVENT, 0)

            # Event handle the frame of the bird
            if event.type == BIRD_FLAP_EVENT:
                bird_frame += 1
                if bird_frame == len(BIRD_FRAMES):
                    bird_frame = 0

            # Event handle update score
            if event.type == SCORE_INCREMENT_EVENT:
                score_incrementer = min(2.0, 1 + score / 700)
                score += score_incrementer

            # Event handle background color
            if event.type == BACKGROUND_CHANGE_EVENT:
                if white_to_black:
                    rgb -= 1
                    if rgb < 0:
                        pygame.time.set_timer(BACKGROUND_CHANGE_EVENT, 0)
                    else:
                        background_color = (rgb, rgb, rgb)
                else:
                    rgb += 1
                    if rgb > 255:
                        pygame.time.set_timer(BACKGROUND_CHANGE_EVENT, 0)
                    else:
                        background_color = (rgb, rgb, rgb)

        score_text = '{:05d}'.format(math.floor(score))

        # Every 700 points
        if int(score) >= 700 * background_700_target:
            pygame.time.set_timer(BACKGROUND_CHANGE_EVENT, BACKGROUND_CHANGE_COOLDOWN)
            white_to_black = True
            background_700_target += 1

        # Every 240 points more than 700 points
        if int(score) >= 700 * background_900_target + 240:
            pygame.time.set_timer(BACKGROUND_CHANGE_EVENT, BACKGROUND_CHANGE_COOLDOWN)
            white_to_black = False
            background_900_target += 1

        # Every 100 points
        if int(score) >= 100 * score_target:
            MILESTONE_SOUND.play()
            pygame.time.set_timer(SCORE_BLINK_EVENT, SCORE_BLINK_COOLDOWN)
            last_update_blink_score = current_time
            score_blinking = True
            score_target += 1

        if not score_visible:
            score_text = ""
        else:
            if score_blinking:
                score_text = '{:05d}'.format(math.floor(score / 100) * 100)

        if dino.y == get_sprite_ground_y_pos(dino_sprite):
            duck = False

        # Get list of keys pressed
        keys = pygame.key.get_pressed()

        if keys[pygame.K_DOWN]:
            # Update dino ducking animation
            if current_time - last_update_duck >= DINO_ANIMATION_COOLDOWN:
                duck_frame += 1
                last_update_duck = current_time
                if duck_frame == len(DINO_DUCK_FRAMES):
                    duck_frame = 0
            dino_sprite = DINO_DUCK_FRAMES[duck_frame]
            duck = True

        elif (keys[pygame.K_SPACE] or keys[pygame.K_UP]) and dino.y - 1 == get_sprite_ground_y_pos(dino_sprite):
            # Update dino jumping animation
            JUMP_SOUND.play()
            jump_vel = INITIAL_JUMP_VEL
            max_height = False
            jump = True

        else:
            # Update dino running animation
            if current_time - last_update_run >= DINO_ANIMATION_COOLDOWN:
                run_frame += 1
                last_update_run = current_time
                if run_frame == len(DINO_RUN_FRAMES):
                    run_frame = 0
            dino_sprite = DINO_RUN_FRAMES[run_frame]

        # Update dino y position for jump
        if jump == True:
            dino_sprite = DINO_JUMP
            # Going up
            if max_height == False and duck == False:
                if dino.y - jump_vel >= MAX_Y_POS:
                    dino.y -= jump_vel
                    jump_vel -= GRAVITY
                else:
                    max_height = True
            # Going down
            else:
                dino.y += jump_vel
                jump_vel += GRAVITY + duck
                if dino.y > get_sprite_ground_y_pos(dino_sprite):
                    dino.y = get_sprite_ground_y_pos(dino_sprite)
                    jump = False

        # Add grains on the ground
        if grain_ms_count > grain_add_increment:
            grain_y = random.randint(133, 145)
            grain_width = random.randint(2, 5)
            grain = pygame.Rect(WIDTH, grain_y, grain_width, 1.5)
            grains.append(grain)
            grain_add_increment = random.randint(30, 60)
            grain_ms_count = 0

        # Add clouds
        if cloud_ms_count > cloud_add_increment:
            cloud_sprite = CLOUD
            cloud_y = random.randint(30, 50)
            cloud = pygame.Rect(WIDTH, cloud_y, cloud_sprite.get_width(), cloud_sprite.get_height())
            clouds.append(cloud)
            cloud_add_increment = random.randint(1000, 4000)
            cloud_ms_count = 0

        # Add bird
        if score >= 200 and (bird_ms_count > bird_add_increment - 800) and (current_time - last_cactus_time > 800):
            bird_sprite = BIRD_FRAMES[bird_frame]
            bird = pygame.Rect(WIDTH, random.choice(BIRD_HEIGHTS), bird_sprite.get_width(), bird_sprite.get_height())
            bird_sprites.append(bird_sprite)
            birds.append(bird)
            bird_add_increment = random.randint(2500, 3000)
            cactus_add_increment = random.randint(500, 1100)
            bird_ms_count = 0
            cactus_ms_count = 0

        # Add cactus
        if cactus_ms_count > cactus_add_increment:
            cactus_sprite = CACTUS_LIST[random.randint(0, len(CACTUS_LIST) - 1)]
            cactus = pygame.Rect(WIDTH, get_sprite_ground_y_pos(cactus_sprite), cactus_sprite.get_width(), cactus_sprite.get_height())
            cactus_sprites.append(cactus_sprite)
            cacti.append(cactus)
            cactus_add_increment = random.randint(500, 1100)
            cactus_ms_count = 0
            last_cactus_time = current_time

        # Move the grains
        for grain in grains[:]:
            grain.x -= map_vel
            if grain.x + grain.width < 0:
                grains.remove(grain)

        # Move the cloud
        for cloud in clouds[:]:
            cloud.x -= CLOUD_VEL
            if cloud.x + cloud.width < 0:
                clouds.remove(cloud)

        # Move the cacti
        for i, cactus in enumerate(cacti[:]):
            cactus.x -= map_vel
            if cactus.x + cactus.width < 0:
                cacti.remove(cactus)
                cactus_sprites.pop(i)

        # Move the bird
        for bird in birds[:]:
            bird.x -= map_vel
            if bird.x + bird.width < 0:
                birds.remove(bird)

        # Check collision
        obstacle_sprites.extend(cactus_sprites)
        obstacle_sprites.extend(bird_sprites)
        obstacle_rects.extend(cacti)
        obstacle_rects.extend(birds)

        if check_collision(dino_sprite, dino, obstacle_sprites, obstacle_rects):
            DEAD_SOUND.play()
            dino_sprite = DINO_DEAD
            pygame.time.set_timer(SCORE_BLINK_EVENT, 0)
            pygame.time.set_timer(BACKGROUND_CHANGE_EVENT, 0)
            score_text = '{:05d}'.format(math.floor(score))
            hit = True
        else:
            obstacle_sprites.clear()
            obstacle_rects.clear()

        # Update display
        draw(score_text, high_score, grains, clouds, dino_sprite, dino, cactus_sprites, cacti, bird_frame, birds)

        if hit:
            wait_for_input = True

            # Draw score
            gameover_text = FONT.render("G A M E  O V E R", 1, GREY)
            WIN.blit(gameover_text, ((WIDTH - gameover_text.get_width()) / 2, (HEIGHT - gameover_text.get_height()) / 2))
            pygame.display.update()

            # Check high score
            if high_score == '':
                high_score = score_text
            else:
                if int(score_text) > int(high_score):
                    high_score = score_text
            pygame.time.delay(500)
            break

    while wait_for_input:
        # Event handler
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

        # Get list of keys pressed
        keys = pygame.key.get_pressed()
        # Restart the game
        if keys[pygame.K_SPACE] or keys[pygame.K_UP]:
            main()

if __name__ == '__main__':
    start_game()
    main()