import pygame
import threading
from random import randint
from time import sleep
from math import floor,ceil
from os import system
import tkinter
from colorsys import hsv_to_rgb
from multiprocessing import Process,Queue,cpu_count
import itertools
from pprint import pprint
system("clear")
birth = [3]
stay  = [2,3]

def hsv2rgb(h,s,v):
    return tuple(round(i * 255) for i in hsv_to_rgb(h,s,v))

def daemonizer(fName):
    try:
        daemon = threading.Thread(target=fName)
        daemon.daemon = True
        daemon.start()
    except Exception as e:
        print(e)

offbt = "grey79"
onbt  = "lime green"
bgmain = 'grey60'

class tk_window():
    def __init__(self):
        self.tk = tkinter.Tk()
        self.tk.title("Rules")
        self.tk.geometry('240x120')
        self.tk.configure(background=bgmain)

        self.buttons = {'b':[],'s':[]}

        self.sep1 = tkinter.Label(self.tk, text=" ", background=bgmain).grid(column=0,row=3)

        self.buttons['b'] = self.create_buttons(self.bfunc,'b')
        self.bl   = tkinter.Label(self.tk, text="Birth", background=bgmain).grid(column=2,row=0)

        self.sep2 = tkinter.Label(self.tk, text=" ", background=bgmain).grid(column=5,row=3)

        self.buttons['s'] = self.create_buttons(self.bfunc,'s',6)
        self.sl   = tkinter.Label(self.tk, text="Stay", background=bgmain).grid(column=8,row=0)
        self.press_buttons()
        self.init_window()


    def init_window(self):
        self.tk.mainloop()

    def create_buttons(self, command, type, py=0, px=0):
        btnsb = 9*[0]
        i = 0
        for x, y in itertools.product(range(3),range(3)):
            btnsb[i] = tkinter.Button(self.tk, relief="raised", text=str(i), command = lambda num=i+1, t=type, : command(num,t))
            btnsb[i].grid(column=y+1+py,row=x+1+px)
            i+=1
        return btnsb

    def press_buttons(self):
        for b in self.buttons['b']:
            if b['text'] == "3":
                self.buttons['b'][int(b['text'])]['relief'] = 'sunken'
        for s in self.buttons['s']:
            if s['text'] in ["2","3"]:
                self.buttons['s'][int(s['text'])]['relief'] = 'sunken'

    def bfunc(self,v,t):
        global birth, stay, death, game_on
        game_on = False
        sleep(0.1)

        if self.buttons[t][v-1]['relief'] == 'sunken':
            self.buttons[t][v-1]['relief'] = 'raised'
        else :
            self.buttons[t][v-1]['relief'] = 'sunken'

        self.apply_rules()
        game_on = True

    def is_int(self,s):
        try:
            int(s)
            return True
        except ValueError:
            return False

    def apply_rules(self):
        global birth, stay, death
        birth = []
        stay  = []
        for b in self.buttons['b']:
            if b['relief'] == 'sunken':
                birth.append(int(b['text']))
        for s in self.buttons['s']:
            if s['relief'] == 'sunken':
                stay.append(int(s['text']))



daemonizer(tk_window)

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
        if self.grid[x][y] == 0 and c in birth:
            return 1
        if self.grid[x][y] == 1 and c in stay:
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
        divider = 12
        halfgrid = floor(self.grid_res/2)
        proportion = floor(self.grid_res/divider)
        self.reset_grid()
        for x in range(self.grid_res):
            for y in range(self.grid_res):
                if  self.grid_res/2+1 > x > halfgrid - proportion and self.grid_res/2+1 > y > halfgrid - proportion :
                    if randint(0,100)  <= 25:
                        life = 1
                        l_count += 1
                    else:
                        life = 0
                    self.grid[x][y] = life
                    self.draw_cell(x,y,colors[life])

                    mirrorX = halfgrid + (halfgrid - x)
                    self.grid[mirrorX][y] = life
                    self.draw_cell(mirrorX,y,colors[life])

                    mirrorY = halfgrid + (halfgrid - y)
                    self.grid[x][mirrorY] = life
                    self.draw_cell(x,mirrorY,colors[life])

                    self.grid[mirrorX][mirrorY] = life
                    self.draw_cell(mirrorX,mirrorY,colors[life])

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
    if grid_res < 140:
        screen.fill(colors[0])
        grid_res = grid_res + 10
        gol.reset_grid()
        gol = game_of_life()
        gol.random_cells()

def grid_minus():
    global grid_res,gol
    if grid_res > 10:
        screen.fill(colors[0])
        grid_res = grid_res - 10
        gol.reset_grid()
        gol = game_of_life()
        gol.random_cells()

def speed_plus():
    global fps,gol
    if fps == 2: fps = 5
    elif fps < 60 : fps = fps + 5

def speed_minus():
    global fps,gol
    if fps > 5: fps = fps - 5
    else : fps = 2

def refresh_title(count=0):
    if count == 0: count = gol.c_sum
    title = "Game of life / Cells : "+str(count)+" / Grid_res : "+str(grid_res)+" / FPS : "+str(fps)
    pygame.display.set_caption(title)

def clear_output():
    system("clear")

pygame.init()

res = 980
size = [res, res]
grid_res = 80

screen = pygame.display.set_mode(size)
pygame.display.set_caption("Game of life")
clock = pygame.time.Clock()

fps  = 30

color_c = randint(0,1000)
c_c = hsv2rgb(color_c/1000,0.85,0.85)
colors = [(0,0,0),c_c]

gol = game_of_life()

game_on = False

def pause_unpause():
    global game_on
    game_on = (not game_on)

def run_game():
    global game_on
    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if event.button == 1:
                    gol.add_cell(pos)
                    # gol.print_step()
                    # gol.info_cell(pos)
                elif event.button == 3:
                    pause_unpause()
                if event.button == 2:
                    gol.random_cells()
                elif event.button == 4:
                    grid_plus()
                elif event.button == 5:
                    grid_minus()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game_on = False
                    done = True
                elif event.key == pygame.K_r or event.key == pygame.K_RETURN :
                    gol.reset_grid()
                    screen.fill(colors[0])
                elif event.key == pygame.K_f:
                    gol.print_step()
                elif event.key == pygame.K_d:
                    gol.random_cells()
                elif event.key == pygame.K_SPACE:
                    pause_unpause()
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
