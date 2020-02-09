import pygame
from random import randint
from time import sleep
from math import floor,ceil
from os import system
from colorsys import hsv_to_rgb
from multiprocessing import Process,Queue,cpu_count

def hsv2rgb(h,s,v):
    return tuple(round(i * 255) for i in hsv_to_rgb(h,s,v))

class game_of_life():
    def __init__(self):
        self.grid_res = grid_res
        self.grid  = self.create_grid()
        self.c_sum = 0

    def create_grid(self):
        grid = []
        for x in range(self.grid_res + 1):
            grid.append([])
            grid[x] = [0] * (self.grid_res + 1)
        return grid

    def count_close(self,x,y):
        t = 0
        tx = self.grid[x-1:x+2]
        if len(tx) > 0:
            for l in range(0,3):
                t = t + sum(tx[l][y-1:y+2])
            if self.grid[x][y] == 1:
                t = t - 1
        return t

    def will_cell_live(self,x,y):
        c = self.count_close(x,y)
        if c == 3:
            return 1
        if c == 2 and self.grid[x][y] == 1:
            return 1
        return 0

    def worker_step(self,s,q):
        cols = s[1] - s[0] + 1
        while cols > self.grid_res:
            cols = cols - 1

        for t in range(0,cols):
            x = t + s[0]
            for y in range(self.grid_res):
                life = self.will_cell_live(x,y)
                self.grid2[x][y] = life
                self.draw_cell(x,y,colors[life])
                self.c_sum = self.c_sum + life
        q.put([s,self.grid2[s[0]:s[1]+1],self.c_sum])

    def step(self):
        refresh_title()
        # screen.fill(colors[0])
        self.c_sum = 0
        self.grid2 = self.create_grid()

        slices = []
        cores = cpu_count()-1

        s = ceil(self.grid_res/cores)
        for c in range(0,cores):
            min = c*s
            max = c*s+s-1
            while max > self.grid_res - 1:
                max = max - 1
            if c == cores - 1:
                while max < self.grid_res - 1:
                    max = max + 1
            slices.append((min,max))

        p = []
        q = Queue()
        for x in range(0,cores):
            proc = Process(target=self.worker_step, args=([slices[x],q]))
            proc.start()
            p.append(proc)

        for x in range(0,cores):
            p[x].join()
            qo = q.get()
            s  = qo[0]
            self.grid[s[0]:s[1]+1] = qo[1]
            self.c_sum = self.c_sum + qo[2]

    def reset_grid(self):
        for x in range(self.grid_res):
            for y in range(self.grid_res):
                if self.grid[x][y] == 1:
                    self.grid[x][y] = 0
                    self.draw_cell(x,y,colors[0])

    def print_step(self):
        system("clear")
        chars = ["- ","O "]
        for x in range(self.grid_res):
            for y in range(self.grid_res):
                print(chars[self.grid[y][x]],end="")
                # print(self.grid[y][x],end=",")
                if y == grid_res-1:
                    print("")
        print("")
        # for x in self.grid:
        #     print(x)

    def random_cells(self):
        l_count = 0
        self.reset_grid()
        for x in range(self.grid_res):
            for y in range(self.grid_res):
                if x > self.grid_res/3 and x < self.grid_res/3*2 and y > self.grid_res/3 and y < self.grid_res/3*2 :
                    if randint(0,100)  <= 50:
                        life = 1
                        l_count += 1
                    else:
                        life = 0
                    self.grid[x][y] = life
                    self.draw_cell(x,y,colors[life])
        refresh_title(l_count)

    def add_cell(self,pos):
        r = res / self.grid_res
        x = floor(pos[0]/r)
        y = floor(pos[1]/r)
        if self.grid[x][y] == 1:
            self.grid[x][y] = 0
            self.draw_cell(x,y,colors[0])
        else :
            self.grid[x][y] = 1
            self.draw_cell(x,y,colors[1])

    def info_cell(self, pos):
        r = res / self.grid_res
        x = floor(pos[0]/r)
        y = floor(pos[1]/r)
        print("Close cells :",self.count_close(x,y))
        print("Futur cell  :",self.will_cell_live(x,y))

    def draw_cell(self,x,y,color):
        r = res / self.grid_res
        x1 = floor(x * r)
        x2 = floor((x+1) * r)
        y1 = floor(y * r)
        y2 = floor((y+1) * r)
        r  = floor(r)
        x_corr = x2-x1-r
        y_corr = y2-y1-r
        if grid_res < 30:
            margin = 3
        elif grid_res < 70:
            margin = 2
        else:
            margin = 1
        pygame.draw.rect(screen,color,(x1,y1,r-margin+x_corr,r-margin+y_corr))

def colorcycle():
    global color_c,colors
    if color_c < 1000:
        color_c = color_c +1
    else :
        color_c = 0
    WHITE = hsv2rgb(color_c/1000,0.85,0.85)
    BLACK = (0,0,0)
    colors = [BLACK,WHITE]

def grid_plus():
    global grid_res,gol
    if grid_res < 160:
        screen.fill(colors[0])
        grid_res = grid_res + 10
        print(grid_res,grid_res*grid_res)
        gol.reset_grid()
        gol = game_of_life()
        gol.random_cells()

def grid_minus():
    global grid_res,gol
    if grid_res > 10:
        screen.fill(colors[0])
        grid_res = grid_res - 10
        print(grid_res,grid_res*grid_res)
        gol.reset_grid()
        gol = game_of_life()
        gol.random_cells()

def speed_plus():
    global fps,gol
    if fps == 2: fps = 5
    elif fps < 60 : fps = fps + 5
    system("clear")
    print(fps)

def speed_minus():
    global fps,gol
    if fps > 5: fps = fps - 5
    else : fps = 2
    system("clear")
    print(fps)

def refresh_title(count=0):
    if count == 0: count = gol.c_sum
    title = "Game of life / Cells : "+str(count)+" / Grid_res : "+str(grid_res)+" / FPS : "+str(fps)
    pygame.display.set_caption(title)

def clear_output():
    system("clear")

pygame.init()
system("clear")

res = 800
size = [res, res]
grid_res = 80

screen = pygame.display.set_mode(size)
pygame.display.set_caption("Game of life")
clock = pygame.time.Clock()

fps  = 20

color_c = randint(0,1000)
c_c = hsv2rgb(color_c/1000,0.85,0.85)
colors = [(0,0,0),c_c]

gol = game_of_life()

def run_game():
    done = False
    game_on = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if event.button == 1:
                    gol.add_cell(pos)
                    # gol.print_step()
                    # gol.info_cell(pos)
                elif event.button == 3:
                    if game_on == True:
                        game_on = False
                    else:
                        game_on = True
                if event.button == 2:
                    gol.random_cells()

                elif event.button == 4:
                    grid_plus()
                elif event.button == 5:
                    grid_minus()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    done=True
                elif event.key == pygame.K_r or event.key == pygame.K_RETURN :
                    gol.reset_grid()
                    screen.fill(colors[0])
                elif event.key == pygame.K_f:
                    gol.print_step()
                elif event.key == pygame.K_d:
                    gol.random_cells()
                elif event.key == pygame.K_SPACE:
                    if game_on == True:
                        game_on = False
                    else:
                        game_on = True
                elif event.key == pygame.K_g:
                    game_on = False
                    gol.step()
                    gol.print_step()
                elif event.key == pygame.K_c:
                    clear_output()
                elif event.key == pygame.K_s:
                    game_on = False
                    gol.step()
                elif event.key == pygame.K_KP_PLUS:
                    speed_plus()
                elif event.key == pygame.K_KP_MINUS:
                    speed_minus()

        if game_on == True:
            gol.step()
            colorcycle()
            if gol.c_sum == 0:
                game_on = False

        pygame.display.update()
        clock.tick(fps)

if __name__ == '__main__':
    run_game()
