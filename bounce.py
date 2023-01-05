import curses

Y = 0
X = 1
PLAYERLOOKUP = {"One player mode": 1, "Two player mode": 2, "Three player mode": 3, "Four player mode": 4, "Adventure": 1 }
MODELOOKUP = {"One player mode": 0, "Two player mode": 0, "Three player mode": 0, "Four player mode": 0, "Options": 0, "Adventure": 1 }
BACKGROUND = curses.COLOR_BLACK
curses.initscr()
curses.start_color()
WHITE = curses.color_pair(0)
curses.init_pair(1, curses.COLOR_GREEN, BACKGROUND)
GREEN = curses.color_pair(1)
curses.init_pair(2, curses.COLOR_RED, BACKGROUND)
RED = curses.color_pair(2)
ORANGE = curses.color_pair(2)
curses.init_pair(3, curses.COLOR_BLUE, BACKGROUND)
BLUE = curses.color_pair(3)
curses.init_pair(4, curses.COLOR_YELLOW, BACKGROUND)
YELLOW = curses.color_pair(4)
CIRCLE = {
    0.0 :   [(0,0)], 
    0.5 :   [(-0.5,-0.5),(-0.5,0.5),(0.5,-0.5),(0.5,0.5)], 
    1.0 :   [(1,0),(0,-1),(-1,0),(0,1)], 
    1.0 :   [(1,1),(1,0),(1,-1),(0,-1),(-1,-1),(-1,0),(-1,1),(0,1)], 
    1.5 :   [(1.5,0.5),(0.5,1.5),(-1.5,0.5),(-0.5,1.5),(1.5,-0.5),(0.5,-1.5),(-1.5,-0.5),(-0.5,-1.5),], 
    2.0 :   [(1,1),(2,0),(1,-1),(0,-2),(-1,-1),(-2,0),(-1,1),(0,2)], 
    2.0 :   [(2,1),(2,0),(2,-1),(1,-2),(0,-2),(-1,-2),(-2,-1),(-2,0),(-2,1),(-1,2),(0,2),(1,2)], 
    2.5 :   [(2.5,0.5),(1.5,1.5),(0.5,2.5),(-2.5,0.5),(-1.5,1.5),(-0.5,2.5),(2.5,-0.5),(1.5,-1.5),(0.5,-2.5),(-2.5,-0.5),(-1.5,-1.5),(-0.5,-2.5),]
    }


def sign(value):
    if value == 0:
        return 1
    return abs(value) / value

class Paddle():
    def __init__(self, color = WHITE, direction = Y, pos = (20,2), up = "w", down = "s", length = 4):
        self.dir = direction
        self.pos = pos
        self.length = length
        self.shape = "#"
        self.center = "O"
        self.color = color
        self.speed = 1
        self.up = up
        self.dn = down

    def draw(self, window):
        for i in range(-self.length, self.length+1):
            if (self.pos[self.dir] + i >= 0) and (self.pos[self.dir] + i < [curses.LINES, curses.COLS-1][self.dir] ):
                new = [self.pos[Y], self.pos[X]]
                new[self.dir] += i
                if i == 0:
                    window.addstr(new[Y], new[X], self.center)
                else:
                    window.addstr(new[Y], new[X], self.shape, self.color)
        return

    def update(self, keys):
        if ord(self.up) in keys:
            newpos = [self.pos[Y],self.pos[X]]
            newpos[self.dir] -= self.speed
            self.pos = tuple(newpos)
        elif ord(self.dn) in keys:
            newpos = [self.pos[Y],self.pos[X]]
            newpos[self.dir] += self.speed
            self.pos = tuple(newpos)
        return


    def get_bounce(self, bpos, bvel, bsize = 0.5):
        bspeed = ((bvel[0]**2 + bvel[1]**2 )**0.5)*1.0005
        dist = bpos[self.dir] - self.pos[self.dir]
        if abs(dist) - bsize <= self.length:
            nspeed = dist/self.length
            bounce = [bspeed, bspeed]
            bounce[self.dir] *= nspeed
            bounce[not self.dir] *= -sign(bvel[not self.dir])
            return bounce
        return None

class Fire():
    def __init__(self, duration = None, y = 0.0, x = 0.0):
        string = ".,-~~%$##"
        self.duration = duration
        self.y = y
        self.x = x
        length = self.duration // len(string) 
        self.shape = "".join([x*length for x in string])
        if duration == None:
            self.duration = len(self.shape) - 1
        else:
            self.duration = duration

    def draw(self, window):
        newobjects = []
        if (self.duration > 0):
            if (self.y > 0) and (self.y < curses.LINES - 1) and (self.x > 0) and (self.x < curses.COLS - 1):
                if self.duration < len(self.shape) // 3:
                    window.addstr(round(self.y), round(self.x), self.shape[min(self.duration, len(self.shape) - 1)], YELLOW) 
                elif self.duration < (2 * (len(self.shape) // 3)):
                    window.addstr(round(self.y), round(self.x), self.shape[min(self.duration, len(self.shape) - 1)], ORANGE) 
                else:
                    window.addstr(round(self.y), round(self.x), self.shape[min(self.duration, len(self.shape) - 1)], RED) 
                self.duration -= 1
                """
                if self.duration > len(self.shape) - 3:
                    for d in CIRCLE[1]:
                        newfire = Fire(duration = min(self.duration - 1, len(self.shape) - 1), y = self.y + d[0], x = self.x + d[1])
                        newobjects.append(newfire)
                        """
        return newobjects
    
    def get_duration(self):
        return self.duration

class Ball():
    def __init__(self, shape = "O", y = 0.0, x = 0.0, direction = (0.0,0.0), size = 0.0, color = WHITE, burning = False, invisible = False):
        self.shape = shape
        self.pos = (y,x)
        self.vel = tuple([direction[x] + 1/333 for x in [0,1]]) # lmao I should have commented earlier but this is because the fire gets fucked up if the speed is an integer
        self.color = color
        self.size = size
        self.effects = { "burning": burning, "invisible": invisible }
        return

    def move(self):
        """ called once per game tick """
        newobjects = []
        self.pos = (self.pos[0] + self.vel[0], self.pos[1] + self.vel[1])
        if self.effects["burning"] > 0:
            for d in CIRCLE[self.size]:
                newfire = Fire(duration = 30, y = self.pos[0] - round(self.vel[0]) + d[0] , x = self.pos[1] - round(self.vel[1]) + d[1] )
                newobjects.append(newfire)
            self.set_effect("burning", self.effects["burning"] - 1)
            if self.effects["burning"] <= 0:
                self.color = WHITE 
        return newobjects

    def set_effect(self, effect, value):
        self.effects[effect] = value
        return

    def set_size(self, newsize):
        self.size = newsize
        return
        
    def get_size(self):
        return self.size
       
    def set_shape(self, newshape):
        self.shape = newshape
        return
        
    def get_shape(self):
        return self.shape
        
    def set_pos(self, newpos):
        self.pos = newpos
        return

    def get_pos(self):
        return self.pos

    def set_color(self, newcolor):
        self.color = newcolor
        return

    def get_color(self):
        return self.color


    def set_vel(self, newvel):
        self.vel = newvel
        return

    def get_vel(self):
        return self.vel

    def bounce(self, bounce):
        if bounce == "x":
            self.vel = (self.vel[0] , self.vel[1] * -1)
        elif bounce == "y":
            self.vel = (self.vel[0] * -1, self.vel[1] )
        else:
            self.vel = bounce 
        return

    def draw(self, window):
        if self.effects["invisible"]:
            return
        drawpos = [ self.pos[0], self.pos[1] ]
        for d in CIRCLE[self.size]:
            drawpos = [self.pos[0] + d[0] , self.pos[1] + d[1] ]
            if (drawpos[0] > 0) and (drawpos[0] < curses.LINES - 1):
                if (drawpos[1] > 0) and (drawpos[1] < curses.COLS - 1):
                    window.addstr(round(drawpos[0]), round(drawpos[1]), self.shape, self.color)
        """
        if self.size == 0.5:
            if (drawpos[0] > 0) and (drawpos[0] < curses.LINES - 1):
                if (drawpos[1] > 0) and (drawpos[1] < curses.COLS - 1):
                    window.addstr(round(drawpos[0]), round(drawpos[1]), self.shape, self.color)
        elif self.size == 2.5:
            for d in [(2,0),(2,1),(1,2),(0,2),(-1,2),(-2,1),(-2,0),(-2,-1),(-1,-2),(0,-2),(1,-2),(2,-1)]:
                drawpos = [self.pos[0] + d[0] , self.pos[1] + d[1] ]
                if (drawpos[0] > 0) and (drawpos[0] < curses.LINES - 1):
                    if (drawpos[1] > 0) and (drawpos[1] < curses.COLS - 1):
                        window.addstr(round(drawpos[0]), round(drawpos[1]), self.shape, self.color)
                        """
        return

class Menu():
    def __init__(self,y = 0, x = 0, name = "Menu", options = [], align = "left", selection = 1, ):
        self.selection = selection
        self.y = y
        self.x = x
        self.name = name
        self.options = options 
        self.h = len(self.options) + 3
        self.w = max([len(x) for x in options]) + 7
        if align == "middle":
            self.x -= self.w // 2
        self.win = curses.newwin(self.h,self.w,self.y,self.x)
        return 

    def display(self):
        self.win.border()
        self.win.addstr( 1, self.w//2 - len(self.name)//2, self.name, curses.A_BOLD | curses.A_UNDERLINE)
        selected = 1
        number_of_options = len(self.options)
        options = [str(x+1) for x in range(number_of_options)]
        while True:
            for i,option in enumerate(self.options):
                if i == (self.selection - 1) % number_of_options:
                    self.win.addstr(i+2, 2, f'{i+1}. {option}', curses.A_BLINK | curses.A_BOLD)
                else:
                    self.win.addstr(i+2, 2, f'{i+1}. {option}')
            self.win.nodelay(False)
            key = self.win.getkey()
            if (key == "w") or (key == curses.KEY_UP):
                self.selection -= 1
            elif (key == "s") or (key == curses.KEY_DOWN):
                self.selection += 1
            elif (key == " ") or (key == "\n"):
                if self.selection == 69:
                    xd = Menu(y = self.y, x = self.x, name = "69", options = ["haha, nice"])
                    xd.display()
                self.win.nodelay(True)
                return self.options[(self.selection - 1) % number_of_options]
            elif key in options:
                self.win.nodelay(True)
                return self.options[int(key) - 1]
            self.win.refresh()

class Startmenu(Menu):
    def __init__(self,):
        options = ["One player mode", "Two player mode", "Three player mode", "Four player mode", "Options", "Adventure", "Quit"]
        w = max([len(x) for x in options]) + 7
        y = curses.LINES // 2 - (len(options)+3) // 2
        x = curses.COLS // 2 - w // 2
        name = "Start Menu"
        super().__init__(y, x, name, options)
        return
 
class Pausemenu(Menu):
    def __init__(self,):
        options = ["Resume", "Options", "Save", "Quit",]
        w = max([len(x) for x in options]) + 7
        y = curses.LINES // 2 - (len(options)+3) // 2
        x = curses.COLS // 2 - w // 2
        name = "Pause Menu"
        super().__init__(y, x, name, options)
        return
               
def adventuregameloop(scr):
    
    drawobjects = []
    balls = [
            #Ball("O",curses.LINES / 2,curses.COLS / 2,(-0.5,-curses.COLS / 100), size = 2.5, color = GREEN), 
            Ball("O",curses.LINES / 3,curses.COLS / 2,(curses.LINES/100,-1.01))
            ]

    BACKGROUND = curses.COLOR_BLACK
    curses.init_pair(1, curses.COLOR_GREEN, BACKGROUND)
    p1 = Paddle( color = curses.color_pair(1), direction = Y, pos = (curses.LINES//2,1), up = "w", down = "s", length = curses.LINES // 10)

    scr.nodelay(True)
    keys = set()

    while True: 
        olddraw = drawobjects
        for o in olddraw:
            drawobjects += o.draw(scr)
            if o.get_duration() < 0:
                drawobjects.remove(o)

        for b in balls:
            (y,x) = b.get_pos()
            b.draw(scr)
            if (x <= 2):
                bounce1 = p1.get_bounce(b.get_pos(), b.get_vel(), b.get_size())
                if bounce1 != None:
                    b.bounce(bounce1)
                else:
                    balls.remove(b)
            if (x > curses.COLS - 3):
                b.bounce('x')
            if (y <= 1):
                b.bounce('y')
            if (y > curses.LINES - 2):
                b.bounce('y')
            drawobjects += b.move()
        if len(balls) == 0:
            break

        p1.update(keys)
        p1.draw(scr)


        curses.napms(50)
        keys = set()
        for __ in range(10000):
            keys.add(scr.getch()) 
        curses.flushinp()
        if (ord(' ') in keys):
            pausemenu = Pausemenu()
            result = pausemenu.display()
            if result == "Save":
                lolnope = Menu(y = curses.LINES // 2, x = curses.COLS // 2, align = "middle", name = "LMAO", options = ["Lol you can't save"])
                lolnope.display()
            if result == "Options":
                lolnope = Menu(y = curses.LINES // 2, x = curses.COLS // 2, align = "middle", name = "LMAO", options = ["Lol there are no options"])
                lolnope.display()
            if result == "Quit":
                break
        if (ord('q') in keys) or (27 in keys):
            break
        if (ord('b') in keys):
            for b in balls:
                b.set_effect("burning", 30)
                b.set_color(RED)
        if (ord('m') in keys):
            b.set_size(max(b.get_size() - 0.5, 0.0))
        if (ord('p') in keys):
            b.set_size(min(b.get_size() + 0.5, 2.5))
        scr.refresh()
        scr.clear()
       
def regulargameloop(scr, players):

    b = Ball("O",curses.LINES / 2,curses.COLS / 2,(0.1,curses.COLS / 500))

    p1 = Paddle( color = curses.color_pair(1), direction = Y, pos = (curses.LINES//2,1), up = "w", down = "s", length = curses.LINES // 10)
    p2 = Paddle( color = curses.color_pair(2), direction = Y, pos = (curses.LINES//2,curses.COLS - 2), up = "i", down = "k", length = curses.LINES // 10)
    p3 = Paddle( color = curses.color_pair(3), direction = X, pos = (1,curses.COLS//2), up = "c", down = "v", length = curses.COLS // 10)
    p4 = Paddle( color = curses.color_pair(4), direction = X, pos = (curses.LINES - 1, curses.COLS//2), up = "n", down = "m", length = curses.COLS // 10)

    scr.nodelay(True)
    keys = set()

    while True: 
        (y,x) = b.get_pos()
        b.draw(scr)
        if (x <= 2):
            if players < 1:
                b.bounce('x')
            else:
                bounce1 = p1.get_bounce(b.get_pos(), b.get_vel(), b.get_size())
                if bounce1 != None:
                    b.bounce(bounce1)
                else:
                    break
        if (x > curses.COLS - 3):
            if players < 2:
                b.bounce('x')
            else:
                bounce2 = p2.get_bounce(b.get_pos(), b.get_vel(), b.get_size())
                if bounce2 != None:
                    b.bounce(bounce2)
                else:
                    break
        if (y <= 1):
            if players < 3:
                b.bounce('y')
            else:
                bounce3 = p3.get_bounce(b.get_pos(), b.get_vel(), b.get_size())
                if bounce3 != None:
                    b.bounce(bounce3)
                else:
                    break
        if (y > curses.LINES - 2):
            if players < 4:
                b.bounce('y')
            else:
                bounce4 = p4.get_bounce(b.get_pos(), b.get_vel(), b.get_size())
                if bounce4 != None:
                    b.bounce(bounce4)
                else:
                    break
        b.move()

        #curses.napms(10)
        for i in range(players):
            p = [p1, p2, p3, p4][i]
            p.update(keys)
            p.draw(scr)
        keys = set()
        for __ in range(10000):
            keys.add(scr.getch()) 
        curses.flushinp()
        scr.refresh()
        scr.clear()
        if (ord('q') in keys) or (27 in keys):
            break
        if (ord('m') in keys):
            b.set_size(max(b.get_size() - 0.5, 0.0))
        if (ord('p') in keys):
            b.set_size(min(b.get_size() + 0.5, 2.5))


def main(stdscr):

    stdscr.clear()
    curses.curs_set(0)

    startmenu = Startmenu()
    result = startmenu.display()
    players = PLAYERLOOKUP.get(result,-1)
    mode = MODELOOKUP.get(result,-1)

    if mode == 0:
        regulargameloop(stdscr, players)
    elif mode == 1:
        adventuregameloop(stdscr)

curses.wrapper(main)
