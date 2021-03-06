import pygame as pg
import time as tm
import random as rd
import sys

class Player():
    def __init__(self, x, y):
        self.x = x
        self.y = y

        self.sprite = pg.image.load("sprites/player.png").convert()
        self.sprite.set_colorkey((255, 255, 255))

    def move(self, grid, direction):
        # On doit verifier les possibles collisions avant de bouger
        if direction == "north":
            if grid[self.y - 1][self.x] == "c" or grid[self.y - 1][self.x] == "v":
                self.y -= 1
        elif direction == "west":
            if grid[self.y][self.x - 1] == "c" or grid[self.y][self.x - 1] == "v":
                self.x -= 1
        elif direction == "south":
            if grid[self.y + 1][self.x] == "c" or grid[self.y + 1][self.x] == "v":
                self.y += 1
        elif direction == "east":
            if grid[self.y][self.x + 1] == "c" or grid[self.y][self.x + 1] == "v":
                self.x += 1

    def update(self, grid):
        # Cette fonction permet de recuperer les touches enfoncees
        pressed_keys = pg.key.get_pressed()

        # On fait bouger notre joueur avec les fleches
        if pressed_keys[pg.K_UP]:
            self.move(grid, "north")
        if pressed_keys[pg.K_LEFT]:
            self.move(grid, "west")
        if pressed_keys[pg.K_DOWN]:
            self.move(grid, "south")
        if pressed_keys[pg.K_RIGHT]:
            self.move(grid, "east")

    def draw(self, screen):
        screen.blit(self.sprite, (self.x * 32, self.y * 32))

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

class Ennemy():
    def __init__(self, sprite, x, y):
        self.x = x
        self.y = y
        self.direction = "north"

        self.sprite = pg.image.load(f"sprites/{sprite}").convert()
        self.sprite.set_colorkey((255, 255, 255))

    def move(self, grid, direction):
        # Pareil que pour le joueur, il faut verifier les collisions avant de bouger
        if direction == "north":
            if grid[self.y - 1][self.x] != "w":
                self.y -= 1
        elif direction == "west":
            if grid[self.y][self.x - 1] != "w":
                self.x -= 1
        elif direction == "south":
            if grid[self.y + 1][self.x] != "w":
                self.y += 1
        elif direction == "east":
            if grid[self.y][self.x + 1] != "w":
                self.x += 1

    def update(self, grid):
        # Une chance sur 8 de ne rien faire
        if rd.randint(0, 7) != 0:
            # On récupère une liste de toute les directions disponibles
            available_directions = []
            if grid[self.y - 1][self.x] != "w":
                available_directions.append("north")
            if grid[self.y][self.x - 1] != "w":
                available_directions.append("west")
            if grid[self.y + 1][self.x] != "w":
                available_directions.append("south")
            if grid[self.y][self.x + 1] != "w":
                available_directions.append("east")

            # Une chance sur 2 de changer de direction si plus de 2 sont disponibles
            if len(available_directions) > 2:
                possible_directions = available_directions
                if self.direction == "north" and available_directions.count("south") >= 1:
                    possible_directions.remove("south")
                elif self.direction == "west" and available_directions.count("east") >= 1:
                    possible_directions.remove("east")
                elif self.direction == "south" and available_directions.count("north") >= 1:
                    possible_directions.remove("north")
                elif self.direction == "east" and available_directions.count("west") >= 1:
                    possible_directions.remove("west")

                if rd.randint(0, 1) == 0:
                    self.direction = possible_directions[rd.randint(0, len(possible_directions) - 1)]

            # Une chance sur 16 de faire demi-tour si les seules 2 directions dispo sont opposées
            elif (self.direction == "north" or self.direction == "south") and (available_directions.count("north") >= 1 and available_directions.count("south") >= 1):
                if rd.randint(0, 15) == 0:
                    self.direction = "south" if self.direction == "north" else "north"
            elif (self.direction == "west" or self.direction == "east") and (available_directions.count("west") >= 1 and available_directions.count("east") >= 1):
                if rd.randint(0, 15) == 0:
                    self.direction = "east" if self.direction == "west" else "west"

            # On change de direction si seulement 2 sont disponibles
            elif len(available_directions) == 2:
                self.direction = available_directions[rd.randint(0, 1)]

            # On va vers la seule direction disponible si il n'y en a qu'une
            elif len(available_directions) == 1:
                self.direction = available_directions[0]

            self.move(grid, self.direction)

    def draw(self, screen):
        screen.blit(self.sprite, (self.x * 32, self.y * 32))

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

class Level():
    # Charge l'image de fond du niveau, la "grille" qui correspond a tous les elements
    # presents dans le niveau (murs, pieces, etc...), et les ennemis en fonction du nombre
    # d'ennemis demandes
    def __init__(self, image, grid, ennemy_count):
        self.image = pg.image.load(image).convert()

        self.grid = []
        for line in open(grid).read().split("\n"):
            self.grid.append(line.split(","))

        # On cherche dans la grille toutes les positions d'apparitions possibles pour les
        # ennemis
        possible_positions = []
        for i in range(0, len(self.grid)):
            for j in range(0, len(self.grid[i])):
                if self.grid[i][j] == "s":
                    possible_positions.append((i, j))

        # On cree les ennemis avec un sprite aleatoire sur une des positions disponibles
        self.ennemies = []
        for i in range(0, ennemy_count):
            sprite = ["ennemy_blue.png", "ennemy_green.png", "ennemy_red.png"][rd.randint(0, 2)]
            position = possible_positions[rd.randint(0, len(possible_positions) - 1)]

            self.ennemies.append(Ennemy(sprite, position[0], position[1]))

    def replace_point(self, x, y, value):
        self.grid[y][x] = value

    def draw(self, screen):
        screen.blit(self.image, (0, 0))

    def get_ennemies(self):
        return self.ennemies

    def get_grid(self):
        return self.grid

# Cette class permet de controler tous le jeu (le chargement des niveaux, les mises a jour
# du joueur, des ennemis, du niveau...)
class Game():
    def __init__(self):
        pg.init()
        pg.mixer.music.set_volume(0.1)

        self.screen = pg.display.set_mode((512, 512))
        pg.display.set_caption("Pacman")

        self.level_number = 1
        self.state = "playing"
        self.load_playing_state()

    def load_playing_state(self):
        self.level = Level("maps/map.png", "maps/map.csv", self.level_number)

        self.player = Player(8, 12)

        self.collectible_sprite = pg.image.load("sprites/collectible.png").convert()
        self.collectible_sprite.set_colorkey((255, 255, 255))

        self.score = 0
        self.max_score = 0

        for line in self.level.get_grid():
            self.max_score += line.count("c")

        pg.mixer.set_num_channels(2)

        self.music_channel = pg.mixer.Channel(0)
        self.music_channel.set_volume(0.4)
        self.music = pg.mixer.Sound("sounds/music.ogg")

        self.effect_channel = pg.mixer.Channel(1)
        self.pickup_sound = pg.mixer.Sound("sounds/pickup.ogg")
        self.death_sound = pg.mixer.Sound("sounds/death.ogg")

        self.tick = 0

        font = pg.font.Font("font.ttf", 24)
        self.level_text = font.render(f"Level {self.level_number}", True, (255, 255, 255))

    def update_playing_state(self):
        if not self.music_channel.get_busy():
            self.music_channel.play(self.music)

        self.level.draw(self.screen)
        grid = self.level.get_grid()

        for i in range(0, len(grid)):
            for j in range(0, len(grid[0])):
                if grid[j][i] == "c":
                    self.screen.blit(self.collectible_sprite, (i * 32, j * 32))

        self.player.update(grid)
        self.player.draw(self.screen)

        # Permet d'afficher l'annonce de changement de niveau en haut a gauche de l'ecran,
        # pendant 3 seocndes, avec les 1.5 dernieres secondes en clignotant
        if self.tick <= 12:
            if self.tick <= 6:
                pg.draw.rect(self.screen, (0, 0, 0), pg.Rect(0, 0, 100, 28))
                self.screen.blit(self.level_text, (0, 0))
            elif self.tick % 2 == 0:
                pg.draw.rect(self.screen, (0, 0, 0), pg.Rect(0, 0, 100, 28))
                self.screen.blit(self.level_text, (0, 0))

        # Permet au joueur de collecter les pieces, et gere le changement de niveau et la
        # possible victoire
        if grid[self.player.get_y()][self.player.get_x()] == "c":
            self.level.replace_point(self.player.get_x(), self.player.get_y(), "v")
            self.score += 1
            self.effect_channel.play(self.pickup_sound)

            if self.score == self.max_score:
                if self.level_number == 4:
                    self.state = "won"
                    self.load_end_state(True, self.score)
                else:
                    self.level_number += 1
                    self.load_playing_state()

        # Gere l'interaction entre les ennemis et le joueur, et la possible defaite
        for i in range(0, len(self.level.get_ennemies())):
            self.level.get_ennemies()[i].update(grid)
            self.level.get_ennemies()[i].draw(self.screen)
            
            if self.level.get_ennemies()[i].get_x() == self.player.get_x() and self.level.get_ennemies()[i].get_y() == self.player.get_y():
                self.music_channel.stop()
                self.effect_channel.play(self.death_sound)
                self.state = "end"
                self.load_end_state(False, self.score)
        
        self.tick += 1

    def load_end_state(self, won, score):
        font = pg.font.Font("font.ttf", 24)

        text = ""
        if won == True:
            text = f"You won! Score: {score}"
        else:
            text = f"You lost :( Score: {score}"

        self.end_text = font.render(text, True, (255, 255, 255))

    def update_end_state(self):
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.end_text, (128, 128))

    # On utilise un systeme de limitation de mises a jour (ticks) par secondes, de facon a
    # ce que le jeu ne soit pas plus ou moins rapide en fonction de l'ordinateur sur
    # lequel on y joue.
    def run(self):
        should_run = True
        last_tick = 0

        while should_run:
            tick = tm.time()
            elapsed_time = tick - last_tick

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    should_run = False

            if elapsed_time >= 0.25:
                if self.state == "playing":
                    self.update_playing_state()
                elif self.state == "end":
                    self.update_end_state()

                pg.display.update()
                last_tick = tick

        pg.quit()

game = Game()
game.run()

sys.exit()
