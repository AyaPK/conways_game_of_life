import pygame
import json
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
import hashlib

root = tk.Tk()
root.withdraw()

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
showins = True


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
        pygame.draw.rect(screen, (20, 20, 20), (
            self.rect.center[0] - offset, self.rect.center[1] - offset, size,
            size),
                         1)

class Cursor(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([1, 1])
        self.image.fill((255,0,0))
        self.rect = self.image.get_rect()
        self.rect.center = pygame.mouse.get_pos()
    def move(self):
        pos = pygame.mouse.get_pos()
        self.rect.center = pos

# build game
pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((gW, gH))
pygame.display.set_caption('Conways Game Of Life - By Aya')
ico = pygame.image.load('res/icon.png')
pygame.display.set_icon(ico)
myfont = pygame.font.SysFont('Arial', 30)
pygame.mixer.music.load("res/pop.flac")
cursor = Cursor()

# cells loop
cells = pygame.sprite.Group()
cellarr = {}


def buildGame():
    global cells
    global cellarr
    cells = pygame.sprite.Group()
    cellarr = {}
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
    try:
        tosave = Path(filedialog.asksaveasfilename(defaultextension=".aya",
                                                   filetypes=(
                                                       ("Aya file", "*.aya"),
                                                       ("All Files", "*.*"))))
        tosave.touch(exist_ok=True)
        inst_line_1 = myfont.render(
            "Saving, please wait...", True,
            (255, 255, 255))
        screen.blit(inst_line_1, (500, 100))
        with open(tosave, "r") as f:
            output = {}
            output["con"] = {
                "tick": tick,
                "mult": mult
            }
            for c in cellarr:
                cell = cellarr[c]
                output[c] = cell.alive
            with open(tosave, "w") as w:
                json.dump(output, w, indent=4)
    except PermissionError:
        pass


def loadGame():
    global tick
    global mult
    global running
    global gW
    global gH
    global cells
    global cellarr
    try:
        with open(filedialog.askopenfilename(defaultextension=".aya",
                                             filetypes=(("Aya file", "*.aya"),
                                                        ("All Files", "*.*"))),
                  "r") as f:
            data = json.load(f)
            tick = data["con"]["tick"]
            mult = data["con"]["mult"]
            gW, gH = size * mult, size * mult
            pygame.display.set_mode((gW, gH))
            buildGame()
            cells = pygame.sprite.Group()
            cellarr = {}
            xpos = (size / 2) - 1
            ypos = (size / 2) - 1
            for y in range(int(gH / size)):
                for x in range(int(gW / size)):
                    cell = Brick(xpos, ypos, bgC, x, y,
                                 data[str(x) + "," + str(y)])
                    cells.add(cell)
                    cellarr[str(x) + "," + str(y)] = cell
                    xpos += size
                ypos += size
                xpos = (size / 2) - 1
            running = False
    except FileNotFoundError:
        pass

c = pygame.sprite.Group()
c.add(cursor)
buildGame()
# main loop
paint_mode = False
while True:

    # The main loop first checks the status of the mouse/keyboard and then sets the FPS as appropriate
    p = pygame.mouse.get_pressed()
    e = pygame.event.poll()
    cursor.move()
    if not running:
        clock.tick(60)
    else:
        clock.tick(tick)
    if e.type == pygame.QUIT:
        break

    # Places a node when clicked
    elif pygame.mouse.get_pressed()[
        0] and not running and not pygame.key.get_mods() & pygame.KMOD_LCTRL:
        if pygame.sprite.spritecollideany(cursor, cells, False):
            cell = pygame.sprite.spritecollideany(cursor, cells, False)
            if not cell.alive:
                cell.updateC()


    # Removes a node when ctrl+clicked
    elif pygame.mouse.get_pressed()[
        0] and not running and pygame.key.get_mods() & pygame.KMOD_LCTRL:
        if pygame.sprite.spritecollideany(cursor, cells, False):
            cell = pygame.sprite.spritecollideany(cursor, cells, False)
            if cell.alive:
                cell.updateC()

    # Performs an action if a key is pressed
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
        elif key_name == "s":
            if not running:
                saveGame()
        elif key_name == "l":
            if not running:
                loadGame()
        elif key_name == "i":
            showins = not showins

    # If the game is running, checks every cell to see if it should live or die on the next generation
    # Game gets paused if no cells will be alive on the next generation
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

    # Draws a grid and displays the paused text if the game is no running
    if not running:
        for c in cellarr:
            cell = cellarr[c]
            cell.draw_rect()
        pausetext = myfont.render("Paused", True,
                                  (255, 255, 255))
        screen.blit(pausetext, (10, 70))
    gentext = myfont.render("Generation: " + str(generation), True,
                            (255, 255, 255))
    screen.blit(gentext, (10, 10))
    speedtext = myfont.render("Speed: " + str(tick), True,
                              (255, 255, 255))
    screen.blit(speedtext, (10, 40))


    # Shows instructions if they are toggled on
    if not running and showins:
        pausetext = myfont.render("Paused", True,
                                  (255, 255, 255))
        screen.blit(pausetext, (10, 70))
        ins = ["I: show/hide instructions", "Click: Place node",
               "Ctrl+Click: Delete Node", "Space: Start/Pause game",
               "R: Reset game", "Up/Down: Resize game",
               "Left/Right: Change speed",
               "S: Save board", "L: Load board"]
        start = gH - 400
        for i in ins:
            inst_line_1 = myfont.render(
                i, True,
                (255, 255, 255))
            screen.blit(inst_line_1, (20, start))
            start += 30
    pygame.display.flip()
