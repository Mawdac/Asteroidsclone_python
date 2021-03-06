###               RiceRocks v1.3 by Edward Reilly             ###
###                  Visit this link to play                  ###
###     http://www.codeskulptor.org/#user40_YIwgpdrElX_0.py   ###


# modules
import simplegui
import math
import random

# globals for user interface
WIDTH = 800
HEIGHT = 600
score = 0
lives = 3
lives_posx = 40
lives_posy = -5
time = 0.5
engine_temp = 0
engine_status = 'Green'
shoot_switch = 'space'

# global control variables
rate_of_acceleration = .3
friction = .03
rocks = 0
game_state = False

# class for easily accessing image info
class ImageInfo:
    def __init__(self, center, size, radius = 0, lifespan = None, animated = False):
        self.center = center
        self.size = size
        self.radius = radius
        if lifespan:
            self.lifespan = lifespan
        else:
            self.lifespan = float('inf')
        self.animated = animated

    def get_center(self):
        return self.center

    def get_size(self):
        return self.size

    def get_radius(self):
        return self.radius

    def get_lifespan(self):
        return self.lifespan

    def get_animated(self):
        return self.animated

    
# art assets created by Kim Lathrop, may be freely re-used in non-commercial projects
    
# debris images - debris1_brown.png, debris2_brown.png, debris3_brown.png, debris4_brown.png
#                 debris1_blue.png, debris2_blue.png, debris3_blue.png, debris4_blue.png, debris_blend.png
debris_info = ImageInfo([320, 240], [640, 480])
debris_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/debris1_brown.png")

# nebula images - nebula_brown.png, nebula_blue.png
nebula_info = ImageInfo([400, 300], [800, 600])
nebula_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/nebula_blue.png")

# splash image
splash_info = ImageInfo([200, 150], [400, 300])
splash_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/splash.png")

# ship image
ship_info = ImageInfo([45, 45], [90, 90], 35)
ship_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/double_ship.png")

# missile image - shot1.png, shot2.png, shot3.png
missile_info = ImageInfo([5,5], [10, 10], 3, 50)
missile_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/shot1.png")

# asteroid images - asteroid_blue.png, asteroid_brown.png, asteroid_blend.png
asteroid_info = ImageInfo([45, 45], [90, 90], 40)
asteroid_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/asteroid_brown.png")

# animated explosion - explosion_orange.png, explosion_blue.png, explosion_blue2.png, explosion_alpha.png
explosion_info = ImageInfo([64, 64], [128, 128], 17, 24, True)
explosion_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/explosion_alpha.png")

# sound assets purchased from sounddogs.com, please do not redistribute
soundtrack = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/soundtrack.mp3")
soundtrack.set_volume(.5)
missile_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/missile.mp3")
missile_sound.set_volume(.3)
ship_thrust_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/thrust.mp3")
ship_thrust_sound.set_volume(.5)
explosion_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/explosion.mp3")

# helper functions to handle transformations
def angle_to_vector(ang):
    return [math.cos(ang), math.sin(ang)]

def dist(p,q):
    return math.sqrt((p[0] - q[0]) ** 2+(p[1] - q[1]) ** 2)

# helper functions to handle colllisions
def process_sprite_group(group, canvas):
    collisions = set([])
    for sprite in group:
        sprite.draw(canvas)
        sprite.update()
        if sprite.update() == True:
            collisions.add(sprite)
    group.difference_update(collisions)

def group_collide(group, other_object):
    collisions = set([])
    collision = False
    for object in group:
        if object.collide(other_object) == True:
            collisions.add(object)
            collision = True
            explosion_group.add(Sprite(object.pos, object.vel, object.angle, object.angle_vel, explosion_image, explosion_info, explosion_sound))            
    group.difference_update(collisions)
    return collision       

def group_group_collide(group_1, group_2):
    global score
    group_a = group_1
    collision = False
    for sprite in group_a:
        if group_collide(group_2, sprite) == True:
            group_1.discard(sprite)
            collision = True
            score += 10
    return collision

# helper function to restart game
def reset_game(game):
    global game_state, score, lives, rocks, rock_group, missile_group
    game_state = False
    score, rocks, lives = 0, 0, 3
    rock_group = set([])
    missile_group = set([])
    timer.stop()
    soundtrack.rewind()
    
# Ship class
class Ship:
    def __init__(self, pos, vel, angle, image, info):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.thrust = False
        self.angle = angle
        self.angle_vel = 0
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        
    def draw(self,canvas):
        if self.thrust == False:
            canvas.draw_image(self.image, self.image_center, self.image_size, self.pos, self.image_size, self.angle)
        elif self.thrust == True:
            canvas.draw_image(self.image, [135,45], self.image_size, self.pos, self.image_size, self.angle)
            
    def update(self):
        if self.thrust == True:
            self.vel[0] += angle_to_vector(self.angle)[0] * rate_of_acceleration
            self.vel[1] += angle_to_vector(self.angle)[1] * rate_of_acceleration
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        self.vel[0] *= (1 - friction)
        self.vel[1] *= (1 - friction)
        self.angle += self.angle_vel
        self.pos[0] %= WIDTH
        self.pos[1] %= HEIGHT
    
    def get_position(self):
        return self.pos
    
    def get_radius(self):   
        return self.radius  

    def thrust_switch(self, switch):
        if switch == True:
            self.thrust = True
            ship_thrust_sound.play()
        elif switch == False:
            self.thrust = False
            ship_thrust_sound.rewind()
 
    def shoot(self):
        global engine_temp
        missile_sound.play()
        missile_group.add(Sprite([(self.pos[0] + (self.radius) * angle_to_vector(self.angle)[0]), (self.pos[1] + (self.radius) * angle_to_vector(self.angle)[1])], [(angle_to_vector(self.angle)[0] * 10), (angle_to_vector(self.angle)[1] * 10)], self.angle, 0, missile_image, missile_info, missile_sound))
        engine_temp += 15
        
        
# Sprite class
class Sprite:
    def __init__(self, pos, vel, ang, ang_vel, image, info, sound = None):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.angle = ang
        self.angle_vel = ang_vel
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        self.lifespan = info.get_lifespan()
        self.animated = info.get_animated()
        self.age = 0
        if sound:
            sound.rewind()
            sound.play()
   
    def draw(self, canvas):
        if self.animated == True:
            canvas.draw_image(self.image, (self.image_center[0] + (self.image_size[0] * self.age), self.image_center[1]), self.image_size, self.pos, self.image_size, self.angle)
        else:
            canvas.draw_image(self.image, self.image_center, self.image_size, self.pos, self.image_size, self.angle)
     
    def update(self):
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        self.angle += self.angle_vel
        self.pos[0] %= WIDTH
        self.pos[1] %= HEIGHT
        self.age += 1
        if self.age > self.lifespan:
            return True
        else:
            return False
    
    def get_position(self):
        return self.pos
    
    def get_radius(self):    
        return self.radius
    
    def collide(self, other_object):
        if dist(self.get_position(), other_object.get_position()) < (self.get_radius()+ other_object.get_radius()):
            return True
        return False
        
    def safe_distance(self, other_object):
        if dist(self.get_position(), other_object.get_position()) < 1.5 * (self.get_radius() + other_object.get_radius()):
            return False
        return True    
        
# draw handler           
def draw(canvas):
    global time, score, lives, rocks, engine_temp, engine_status, shoot_switch

    # animiate background
    time += 1
    wtime = (time / 4) % WIDTH
    center = debris_info.get_center()
    size = debris_info.get_size()
    canvas.draw_image(nebula_image, nebula_info.get_center(), nebula_info.get_size(), [WIDTH / 2, HEIGHT / 2], [WIDTH, HEIGHT])
    canvas.draw_image(debris_image, center, size, (wtime - WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))
    canvas.draw_image(debris_image, center, size, (wtime + WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))

    # draw ship and sprites
    process_sprite_group(rock_group, canvas)
    process_sprite_group(missile_group, canvas)
    process_sprite_group(explosion_group, canvas)
    my_ship.draw(canvas)
    
    # update ship and sprites
    my_ship.update()
    
    # user interface
    if game_state == True:
        canvas.draw_text("Score: " + str(score), [60,75], 20, 'White', 'sans-serif')
        # lives display
        canvas.draw_image(ship_image, ship_info.center, ship_info.size, [620+lives_posx, 75+lives_posy], [40,40],-1.57)
        if lives >= 2:
            canvas.draw_image(ship_image, ship_info.center, ship_info.size, [660+lives_posx, 75+lives_posy], [40,40],-1.57)
        if lives >= 3:
            canvas.draw_image(ship_image, ship_info.center, ship_info.size, [700+lives_posx, 75+lives_posy], [40,40],-1.57)
        canvas.draw_polygon([[200,55],[engine_temp * 4 + 200,55],[engine_temp * 4 + 200,80],[200,80]], 1, engine_status, engine_status)
        canvas.draw_polyline([[200,55],[600,55],[600,80],[200,80],[200,55]],3, 'White')
        # engine overheat control
        if engine_temp <= 1:
            shoot_switch = 'space'
        elif engine_temp >= 100:
            shoot_switch = '1'
            engine_temp -= .4
        elif engine_temp > 0:
            engine_temp -= .4
        # engine status color control
        if engine_temp >= 80:
            engine_status = 'Red'
        elif engine_temp >= 60:
            engine_status = 'Orange'
        elif engine_temp >= 30:
            engine_status = 'Yellow'
        elif engine_temp >= 0:
            engine_status = 'Green'
    elif game_state == False:
        canvas.draw_image(splash_image, splash_info.center, splash_info.size, [(WIDTH/2), (HEIGHT/2)], splash_info.size)    
    
    if group_collide(rock_group, my_ship) == True:
        lives -= 1
        rocks -= 1

    if group_group_collide(missile_group, rock_group) == True:
        rocks -= 1
    
    if lives == 0:
        reset_game(False)
            
# key handlers
def keydown(key):
    if key == simplegui.KEY_MAP['left']:
        my_ship.angle_vel += -.06
    elif key == simplegui.KEY_MAP['right']:
        my_ship.angle_vel -= -.06
    elif key == simplegui.KEY_MAP['up']:
        my_ship.thrust_switch(True)
    elif key == simplegui.KEY_MAP[shoot_switch]:
        my_ship.shoot()
        
def keyup(key):
    if key == simplegui.KEY_MAP['left']:
        my_ship.angle_vel -= -.06
    elif key == simplegui.KEY_MAP['right']:
        my_ship.angle_vel += -.06
    elif key == simplegui.KEY_MAP['up']:
        my_ship.thrust_switch(False)

# mouse handler
def mouse_handler(position):
    global game_state
    if game_state == False:
        game_state = True
        timer.start()
        soundtrack.play()
        
# timer handler that spawns a rock    
def rock_spawner():
    global rock_group, rocks
    if rocks < 12:
        new_rock = (Sprite([random.randrange(0, WIDTH), random.randrange(0, HEIGHT)], [(random.random()) - .5, (random.random()) - .5], (random.randrange(0, 10)/10), float(random.randrange(-60, 60))/1000, asteroid_image, asteroid_info))
        if new_rock.safe_distance(my_ship) == True:
            rock_group.add(new_rock)
            rocks += 1

# initialize frame
frame = simplegui.create_frame("Asteroids", WIDTH, HEIGHT)

# initialize ship and two sprites
my_ship = Ship([WIDTH / 2, HEIGHT / 2], [0, 0], -1.57, ship_image, ship_info)
rock_group = set([])
missile_group = set([])
explosion_group = set([])

# register handlers
frame.set_draw_handler(draw)
frame.set_keydown_handler(keydown)
frame.set_keyup_handler(keyup)
frame.set_mouseclick_handler(mouse_handler)

timer = simplegui.create_timer(1000.0, rock_spawner)

# get things rolling
frame.start()
