import pygame
import json

# variables
size = 20
mult = 50
gW = size * mult
gH = size * mult
bgC = (0, 0, 0)
fgC = (255, 255, 0)
running = False
generation = 0
tick = 10
alldead = False


# objects
class Brick(pygame.sprite.Sprite):
    def __init__(self, xp, yp, c, x, y, a):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([size, size])

        self.rect = self.image.get_rect()
        self.rect.center = [xp, yp]
        self.w, self.h, self.x, self.y = size, size, x, y
        self.alive = a
        if self.alive:
            self.c = fgC
        else:
            self.c = bgC
        self.image.fill(self.c)
        self.will_die = False
        self.will_be_born = False

    def updateC(self):
        if self.alive:
            self.alive = False
            self.c = bgC
        else:
            self.alive = True
            self.c = fgC
        pygame.mixer.music.play(1, 0)
        self.image.fill(self.c)

    def born(self):
        if not self.alive:
            self.alive = True
            self.c = fgC
            self.image.fill(self.c)
            self.will_be_born = False

    def kill(self):
        if self.alive:
            self.alive = False
            self.c = bgC
            self.image.fill(self.c)
            self.will_die = False

    def check_neighbours(self):
        alive_neighbours = 0
        for y in range(self.y - 1, self.y + 2):
            for x in range(self.x - 1, self.x + 2):
                if x == self.x and y == self.y:
                    continue
                try:
                    if cellarr[str(x) + "," + str(y)].alive:
                        alive_neighbours += 1
                except:
                    pass
                if alive_neighbours >= 4:
                    break
        if (alive_neighbours < 2 or alive_neighbours > 3) and self.alive:
            self.will_die = True
        elif alive_neighbours == 3 and not self.alive:
            self.will_be_born = True

    def draw_rect(self):
        offset = (size / 2) - 1
        pygame.draw.rect(screen, (20,20,20), (self.rect.center[0]-offset, self.rect.center[1]-offset, size, size), 1)


# build game
pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((gW, gH))
pygame.display.set_caption('Conways Game Of Life - By Aya')
ico = pygame.image.load('res/icon.png')
pygame.display.set_icon(ico)
myfont = pygame.font.SysFont('Arial', 30)
pygame.mixer.music.load("res/pop.flac")

# cells loop
cells = pygame.sprite.Group()
cellarr = {}

def buildGame():
    xpos = (size / 2) - 1
    ypos = (size / 2) - 1
    for y in range(int(gH / size)):
        for x in range(int(gW / size)):
            cell = Brick(xpos, ypos, bgC, x, y, False)
            cells.add(cell)
            cellarr[str(x) + "," + str(y)] = cell
            xpos += size
        ypos += size
        xpos = (size / 2) - 1

def saveGame():
    output = {}
    for c in cellarr:
        cell = cellarr[c]
        output[c] = cell.alive
    with open("save.aya", "r") as f:
        json.dump(output, f, indent=4)



buildGame()
# main loop
paint_mode = False
while True:
    p = pygame.mouse.get_pressed()
    e = pygame.event.poll()
    if not running:
        clock.tick(140)
    else:
        clock.tick(tick)
    if e.type == pygame.QUIT:
        break
    elif pygame.mouse.get_pressed()[0] and not running and not pygame.key.get_mods() & pygame.KMOD_LCTRL:
        ex, ey = pygame.mouse.get_pos()
        for c in cellarr:
            cell = cellarr[c]
            if not cell.alive:
                if cell.rect.collidepoint(ex, ey):
                    cell.updateC()
    elif pygame.mouse.get_pressed()[0] and not running and pygame.key.get_mods() & pygame.KMOD_LCTRL:
        ex, ey = pygame.mouse.get_pos()
        for c in cellarr:
            cell = cellarr[c]
            if cell.alive:
                if cell.rect.collidepoint(ex, ey):
                    cell.updateC()
    if e.type == pygame.KEYDOWN:
        key_name = pygame.key.name(e.key)
        if key_name == "space":
            if running:
                running = False
            else:
                running = True
        elif key_name == "left":
            tick -= 1
        elif key_name == "right":
            tick += 1
        elif key_name == "r":
            cells = pygame.sprite.Group()
            cellarr = {}
            buildGame()
            generation = 0
            running = False
        elif key_name == "up":
            mult += 1
            gW, gH = size * mult, size * mult
            pygame.display.set_mode((gW, gH))
            buildGame()
        elif key_name == "down":
            mult -= 1
            gW, gH = size * mult, size * mult
            pygame.display.set_mode((gW, gH))
            buildGame()
        elif key_name == "q":
            print(cellarr)
    if running:
        alive = 0
        for c in cellarr:
            cell = cellarr[c]
            if cell.alive:
                alive += 1
            cell.check_neighbours()
        for c in cellarr:
            cell = cellarr[c]
            if cell.will_be_born:
                cell.born()
            elif cell.will_die:
                cell.kill()
        if alive < 1:
            running = False
            generation -= 1
        generation += 1


    cells.draw(screen)
    if not running:
        for c in cellarr:
            cell = cellarr[c]
            cell.draw_rect()
    gentext = myfont.render("Generation: " + str(generation), True,
                            (255, 255, 255))
    screen.blit(gentext, (10, 10))
    speedtext = myfont.render("Speed: " + str(tick), True,
                              (255, 255, 255))
    screen.blit(speedtext, (10, 40))
    if not running:
        pausetext = myfont.render("Paused", True,
                                  (255, 255, 255))
        screen.blit(pausetext, (10, 70))
        inst_line_1 = myfont.render("Click the screen to place starting nodes", True,
                                  (255, 255, 255))
        screen.blit(inst_line_1, (20, gH-130))
        inst_line_2 = myfont.render("Hold control to remove clicked nodes",
                                    True,
                                    (255, 255, 255))
        screen.blit(inst_line_2, (20, gH-100))
        inst_line_3 = myfont.render("Hit space to start/pause the game",
                                    True,
                                    (255, 255, 255))
        screen.blit(inst_line_3, (20, gH-70))
        inst_line_4 = myfont.render("Hit R to reset the game",
                                    True,
                                    (255, 255, 255))
        screen.blit(inst_line_4, (20, gH - 40))
    pygame.display.flip()
