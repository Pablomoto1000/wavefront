import pygame, time, sys
from pygame.locals import *


WORLD = """
0000000
00oo0o0
0o00o00
0o0000o
0o0o0oo
000o000
"""
WORLD_WIDTH = len(WORLD.strip().split('\n')[0])
WORLD_HEIGHT = len(WORLD.strip().split('\n'))
assert ['bad width' for x in WORLD.strip().split('\n') if len(x) != WORLD_WIDTH] == [], "WORLD should be rectangular"

print("\nWelcome to the Wavefront Algorithm by Pablo Morales\n")
print("\nThe map will be created in a 7x6 matrix\n")

robotX = int(input("\nPlease input the start position of the robot in the X axis (1-7)\n"))
while robotX < 1 or robotX > 7:
    robotX = int(input("\nPlease input the start position of the robot in the X axis (1-7)\n"))

robotY = int(input("\nPlease input the start position of the robot in the Y axis (1-6)\n"))
while robotY < 1 or robotY > 6:
    robotY = int(input("\nPlease input the start position of the robot in the Y axis (1-6)\n"))

goalX = int(input("\nPlease input the goal position in the X axis (1-7)\n"))
while goalX < 1 or goalX > 7:
    goalX = int(input("\nPlease input the goal position in the X axis (1-7)\n"))

goalY = int(input("\nPlease input the goal position in the Y axis (1-6)\n"))
while goalY < 1 or goalY > 6 or (goalX == robotX and goalY == robotY): 
    goalY = int(input("\nPlease input the goal position in the Y axis (1-6)\n"))

# pygame init config
pygame.init()
pygame.font.init()
winWidth = 50 * WORLD_WIDTH
winHeight = 50 * WORLD_HEIGHT
windowSurface = pygame.display.set_mode((winWidth, winHeight), 0, 32)
pygame.display.set_caption('Wavefront Algorithm')
myfont = pygame.font.SysFont('sans', 17)

# constants for pygame
WHITE = (255, 255, 255)

WINDOW_BG = WHITE
TRACK_IMG = pygame.image.load('assets/track.png')
PATH_IMG = pygame.image.load('assets/white_floor.jpeg')
PATH_WALKED_IMG = pygame.image.load('assets/white_floor.jpeg')
ROBOT_IMG = pygame.image.load('assets/robot.png')
OBS_IMG = pygame.image.load('assets/obstacle.png')
GOAL_IMG = pygame.image.load('assets/goal.png')
DELAY = 0.3 # seconds between showing the next step
SAVEIMAGES = False # save images of each step
if SAVEIMAGES:
    DELAY = 0.0


# function to convert the text to a game map
def convertAsciiMapToWorld(ascii_map):
    ascii_map = ascii_map.strip().split('\n')
    ascii_map[robotY-1] = ascii_map[robotY-1][:robotX-1] + 'r' + ascii_map[robotY-1][robotX:]
    ascii_map[goalY-1] = ascii_map[goalY-1][:goalX-1] + '1' + ascii_map[goalY-1][goalX:]
    width = len(ascii_map[0])
    height = len(ascii_map)

    # Perception 
    mapperY = 0
    mapperX = 0
    found_path = False
    north_path = False
    south_path = False
    east_path = False 
    west_path = False

    # Perception function (determines if there's an obstacle or a path)
    def perception(mapp, mapperY, mapperX, north_path, south_path, east_path, west_path, found_path):

        # watch north
        try:
            if mapp[mapperY][mapperX] == 'r' and mapperY == height-1:
                north_path = True
            elif (mapp[mapperY-1][mapperX] == '1' or mapp[mapperY-1][mapperX] == 'r' or int(mapp[mapperY-1][mapperX]) >= 3) and mapperY != 0:
                if mapp[mapperY-1][mapperX] == '1' and mapp[mapperY][mapperX] != 'o' and mapp[mapperY][mapperX] != 'r':
                    mapp[mapperY] = mapp[mapperY][:mapperX] + '3' + mapp[mapperY][mapperX+1:]
                    counter = 3

                elif mapp[mapperY-1][mapperX] == 'r' and (int(mapp[mapperY][mapperX]) >= 3 or mapp[mapperY][mapperX] == 'o' or mapp[mapperY][mapperX] == '1' or mapperY == 0):
                    north_path = True

                elif int(mapp[mapperY-1][mapperX]) >= 3 and int(mapp[mapperY][mapperX]) < 3 and mapp[mapperY][mapperX] != '1' and mapp[mapperY][mapperX] != 'o' and mapp[mapperY][mapperX] != 'r':
                    counter = int(mapp[mapperY-1][mapperX]) + 1
                    if counter < 10:
                        mapp[mapperY] = mapp[mapperY][:mapperX] + str(counter) + mapp[mapperY][mapperX+1:]
                    else:
                        symbol = chr(counter + 87)
                        mapp[mapperY] = mapp[mapperY][:mapperX] + str(symbol) + mapp[mapperY][mapperX+1:]
        except:
            pass

        # watch north alphabet
        try:
            if mapp[mapperY-1][mapperX] == 'r' and ord(mapp[mapperY][mapperX]) >= 97:
                north_path = True

            elif ord(mapp[mapperY-1][mapperX]) >= 97 and int(mapp[mapperY][mapperX]) < 3 and mapperY != 0 and mapp[mapperY-1][mapperX] != 'r' and mapp[mapperY][mapperX] != 'r' and mapp[mapperY-1][mapperX] != 'o' and mapp[mapperY][mapperX] != 'o' and mapp[mapperY][mapperX] != '1':
                symbol = chr(ord(mapp[mapperY-1][mapperX]) + 1)
                mapp[mapperY] = mapp[mapperY][:mapperX] + str(symbol) + mapp[mapperY][mapperX+1:]
            
        except:
            pass
        
        # watch south
        try:
            if mapp[mapperY][mapperX] == 'r' and mapperY == 0:
                south_path = True
            elif (mapp[mapperY+1][mapperX] == '1' or mapp[mapperY+1][mapperX] == 'r' or int(mapp[mapperY+1][mapperX]) >= 3) and mapperY != height-1:
                if mapp[mapperY+1][mapperX] == '1' and mapp[mapperY][mapperX] != 'o' and mapp[mapperY][mapperX] != 'r':
                    mapp[mapperY] = mapp[mapperY][:mapperX] + '3' + mapp[mapperY][mapperX+1:]
                    counter = 3
                elif mapp[mapperY+1][mapperX] == 'r' and (int(mapp[mapperY][mapperX]) >= 3 or mapp[mapperY][mapperX] == 'o' or mapp[mapperY][mapperX] == '1' or mapperY == height-1):
                    south_path = True
                elif int(mapp[mapperY+1][mapperX]) >= 3 and int(mapp[mapperY][mapperX]) < 3 and mapp[mapperY][mapperX] != '1' and mapp[mapperY][mapperX] != 'o' and mapp[mapperY][mapperX] != 'r':
                    counter = int(mapp[mapperY+1][mapperX]) + 1
                    if counter < 10:
                        mapp[mapperY] = mapp[mapperY][:mapperX] + str(counter) + mapp[mapperY][mapperX+1:]
                    else:
                        symbol = chr(counter + 87)
                        mapp[mapperY] = mapp[mapperY][:mapperX] + symbol + mapp[mapperY][mapperX+1:]
        except:
            pass

        # watch south alphabet
        try:
            if mapp[mapperY+1][mapperX] == 'r' and ord(mapp[mapperY][mapperX]) >= 97:
                south_path = True
            elif ord(mapp[mapperY+1][mapperX]) >= 97 and int(mapp[mapperY][mapperX]) < 3 and mapperY != height-1 and mapp[mapperY+1][mapperX] != 'r' and mapp[mapperY][mapperX] != 'r' and mapp[mapperY+1][mapperX] != 'o' and mapp[mapperY][mapperX] != 'o' and mapp[mapperY][mapperX] != '1':
                symbol = chr(ord(mapp[mapperY+1][mapperX]) + 1)
                mapp[mapperY] = mapp[mapperY][:mapperX] + str(symbol) + mapp[mapperY][mapperX+1:]
        except:
            pass

        # watch east
        try:
            if mapp[mapperY][mapperX] == 'r' and mapperX == width-1:
                east_path = True
            elif (mapp[mapperY][mapperX-1] == '1' or mapp[mapperY][mapperX-1] == 'r' or int(mapp[mapperY][mapperX-1]) >= 3) and mapperX != 0:
                if mapp[mapperY][mapperX-1] == '1' and mapp[mapperY][mapperX] != 'o' and mapp[mapperY][mapperX] != 'r':
                    mapp[mapperY] = mapp[mapperY][:mapperX] + '3' + mapp[mapperY][mapperX+1:]
                    counter = 3
                elif mapp[mapperY][mapperX-1] == 'r' and (int(mapp[mapperY][mapperX]) >= 3 or mapp[mapperY][mapperX] == 'o' or mapp[mapperY][mapperX] == '1' or mapperX == 0):
                    east_path = True
                elif int(mapp[mapperY][mapperX-1]) >= 3 and int(mapp[mapperY][mapperX]) < 3 and mapp[mapperY][mapperX] != '1' and mapp[mapperY][mapperX] != 'o' and mapp[mapperY][mapperX] != 'r':
                    counter = int(mapp[mapperY][mapperX-1]) + 1
                    if counter < 10:
                        mapp[mapperY] = mapp[mapperY][:mapperX] + str(counter) + mapp[mapperY][mapperX+1:]
                    else:
                        symbol = chr(counter + 87)
                        mapp[mapperY] = mapp[mapperY][:mapperX] + symbol + mapp[mapperY][mapperX+1:]
        except:
            pass
        
        # watch east alphabet
        try:
            if mapp[mapperY][mapperX-1] == 'r' and ord(mapp[mapperY][mapperX]) >= 97:
                    east_path = True
            elif ord(mapp[mapperY][mapperX-1]) >= 97 and int(mapp[mapperY][mapperX]) < 3 and mapperX != 0 and mapp[mapperY][mapperX-1] != 'r' and mapp[mapperY][mapperX] != 'r' and mapp[mapperY][mapperX-1] != 'o' and mapp[mapperY][mapperX] != 'o' and mapp[mapperY][mapperX] != '1':
                symbol = chr(ord(mapp[mapperY][mapperX-1]) + 1)
                mapp[mapperY] = mapp[mapperY][:mapperX] + str(symbol) + mapp[mapperY][mapperX+1:]
        except:
            pass

        # watch west
        try:
            if mapp[mapperY][mapperX] == 'r' and mapperX == 0:
                    west_path = True
            elif (mapp[mapperY][mapperX+1] == '1' or mapp[mapperY][mapperX+1] == 'r' or int(mapp[mapperY][mapperX+1]) >= 3) and mapperX != width-1:
                if mapp[mapperY][mapperX+1] == '1' and mapp[mapperY][mapperX] != 'o' and mapp[mapperY][mapperX] != 'r':
                    mapp[mapperY] = mapp[mapperY][:mapperX] + '3' + mapp[mapperY][mapperX+1:]
                elif mapp[mapperY][mapperX+1] == 'r' and (int(mapp[mapperY][mapperX]) >= 3 or mapp[mapperY][mapperX] == 'o' or mapp[mapperY][mapperX] == '1' or mapperX == width-1):
                    west_path = True
                elif int(mapp[mapperY][mapperX+1]) >= 3 and int(mapp[mapperY][mapperX]) < 3 and mapp[mapperY][mapperX] != '1' and mapp[mapperY][mapperX] != 'o' and mapp[mapperY][mapperX] != 'r':
                    counter = int(mapp[mapperY][mapperX+1]) + 1
                    if counter < 10:
                        mapp[mapperY] = mapp[mapperY][:mapperX] + str(counter) + mapp[mapperY][mapperX+1:]
                    else:
                        symbol = chr(counter + 87)
                        mapp[mapperY] = mapp[mapperY][:mapperX] + symbol + mapp[mapperY][mapperX+1:]
        except:
            pass
        
        # watch west alphabet
        try:
            if mapp[mapperY][mapperX+1] == 'r' and ord(mapp[mapperY][mapperX]) >= 97:
                    west_path = True
            elif ord(mapp[mapperY][mapperX+1]) >= 97 and int(mapp[mapperY][mapperX]) < 3 and mapperX != width-1 and mapp[mapperY][mapperX+1] != 'r' and mapp[mapperY][mapperX] != 'r' and mapp[mapperY][mapperX+1] != 'o' and mapp[mapperY][mapperX] != 'o' and mapp[mapperY][mapperX] != '1':
                symbol = chr(ord(mapp[mapperY][mapperX+1]) + 1)
                mapp[mapperY] = mapp[mapperY][:mapperX] + str(symbol) + mapp[mapperY][mapperX+1:]
            
        except:
            pass

        # watch robot sides
        try:
            if north_path == True and south_path == True and east_path == True and west_path == True:
                found_path = True
                return found_path
            pass
        except:
            pass
        
        if mapperX == width-1 and mapperY == height-1:
            return found_path

        if mapperY == height-1:
            mapperY = 0
            return perception(mapp, mapperY, mapperX + 1, north_path, south_path, east_path, west_path, found_path)
        else:
            return perception(mapp, mapperY + 1, mapperX, north_path, south_path, east_path, west_path, found_path)
        
    while found_path != True:
        found_path = perception(ascii_map, mapperY, mapperX, north_path, south_path, east_path, west_path, found_path)

    # Shortest path function finder
    def shortest(ascii_map, world, x, y, north, south, east, west, shortest_path):

        # Check north
        if y != 0 and ascii_map[y-1][x] != 'o' and ascii_map[y-1][x] != '1':
            if ord(ascii_map[y-1][x]) >= 97:
                north = ord(ascii_map[y-1][x])
            elif int(ascii_map[y-1][x]) >= 3:
                north = int(ascii_map[y-1][x])
        elif y != 0 and ascii_map[y-1][x] == '1':
            shortest_path = True
            return shortest_path
        
        # Check south
        if y != height-1 and ascii_map[y+1][x] != 'o' and ascii_map[y+1][x] != '1':
            if ord(ascii_map[y+1][x]) >= 97:
                south = ord(ascii_map[y+1][x])
            elif int(ascii_map[y+1][x]) >= 3:
                south = int(ascii_map[y+1][x])
        elif y != height-1 and ascii_map[y+1][x] == '1':
            shortest_path = True
            return shortest_path

        # Check east
        if x != width-1 and ascii_map[y][x+1] != 'o' and ascii_map[y][x+1] != '1':
            if ord(ascii_map[y][x+1]) >= 97:
                east = ord(ascii_map[y][x+1])
            elif int(ascii_map[y][x+1]) >= 3:
                east = int(ascii_map[y][x+1])
        elif x != width-1 and ascii_map[y][x+1] == '1':
            shortest_path = True
            return shortest_path

        # Check west
        if x != 0 and ascii_map[y][x-1] != 'o' and ascii_map[y][x-1] != '1':
            if ord(ascii_map[y][x-1]) >= 97:
                west = ord(ascii_map[y][x-1])
            elif int(ascii_map[y][x-1]) >= 3:
                west = int(ascii_map[y][x-1])
        elif x != 0 and ascii_map[y][x-1] == '1':
            shortest_path = True
            return shortest_path

        # Compare sides values
        if north < south:
            if north < east:
                if north < west:
                    world[x][y-1] = PATH_IMG
                    y = y-1
                else:
                    world[x-1][y] = PATH_IMG
                    x = x-1
            else:
                if east < west:
                    world[x+1][y] = PATH_IMG
                    x = x+1
                else:
                    world[x-1][y] = PATH_IMG
                    x = x-1
        else:
            if south < east:
                if south < west:
                    world[x][y+1] = PATH_IMG
                    y = y+1
                else:
                    world[x-1][y] = PATH_IMG
                    x = x-1
            else:
                if east < west:
                    world[x+1][y] = PATH_IMG
                    x = x+1
                else:
                    world[x-1][y] = PATH_IMG
                    x = x-1
        # return True
        while shortest_path != True:
            return shortest(ascii_map, world, x, y, north, south, east, west, shortest_path)

    shortest_path = False
    max_value = 10000000000
    north = max_value
    south = max_value
    east = max_value
    west = max_value
    world = []

    # adds spaces unused
    for i in range(width):
        world.append([TRACK_IMG] * height)

    for x in range(width):
        for y in range(height):
            # adds blockades to the map
            if ascii_map[y][x] == 'o':
                world[x][y] = OBS_IMG
            # robot start point
            elif ascii_map[y][x] == 'r':
                world[x][y] = ROBOT_IMG
                shortest_path = shortest(ascii_map, world, x, y, north, south, east, west, shortest_path)
            # goal point
            elif ascii_map[y][x] == '1':
                world[x][y] = GOAL_IMG
    
    return world

# world creation
def drawWorld(surf, world):
    width = len(world)
    height = len(world[0])
    for x in range(width):
        for y in range(height):
            surf.blit(world[x][y], (x * 50, y * 50, 50, 50))

def robotStep(world, x, y, stepsCounter):
    worldWidth = len(world)
    worldHeight = len(world[0])
    robotOneStep = False

    # North
    if y != 0 and world[x][y-1] == PATH_IMG:
        world[x][y] = PATH_WALKED_IMG
        world[x][y-1] = ROBOT_IMG
        robotOneStep = True
    elif y != 0 and world[x][y-1] == GOAL_IMG:
        world[x][y] = PATH_WALKED_IMG
        world[x][y-1] = ROBOT_IMG
        windowSurface.fill(WHITE)
        drawWorld(windowSurface, world)
        textsurface = myfont.render('The robot walked ' +str(stepsCounter)+ ' steps to reach the goal', True, (30,144,255))
        windowSurface.blit(textsurface,(0,0))
        robotOneStep = False

    # South 
    elif y != worldHeight-1 and world[x][y+1] == PATH_IMG:
        world[x][y] = PATH_WALKED_IMG
        world[x][y+1] = ROBOT_IMG
        robotOneStep = True
    elif y != worldHeight-1 and world[x][y+1] == GOAL_IMG:
        world[x][y] = PATH_WALKED_IMG
        world[x][y+1] = ROBOT_IMG
        windowSurface.fill(WHITE)
        drawWorld(windowSurface, world)
        textsurface = myfont.render('The robot walked ' +str(stepsCounter)+ ' steps to reach the goal', True, (30,144,255))
        windowSurface.blit(textsurface,(0,0))
        robotOneStep = False

    # East
    elif x != worldWidth-1 and world[x+1][y] == PATH_IMG:
        world[x][y] = PATH_WALKED_IMG
        world[x+1][y] = ROBOT_IMG
        robotOneStep = True
    elif x != worldWidth-1 and world[x+1][y] == GOAL_IMG:
        world[x][y] = PATH_WALKED_IMG
        world[x+1][y] = ROBOT_IMG
        windowSurface.fill(WHITE)
        drawWorld(windowSurface, world)
        textsurface = myfont.render('The robot walked ' +str(stepsCounter)+ ' steps to reach the goal', True, (30,144,255))
        windowSurface.blit(textsurface,(0,0))
        robotOneStep = False

    # West
    elif x != 0 and world[x-1][y] == PATH_IMG:
        world[x][y] = PATH_WALKED_IMG
        world[x-1][y] = ROBOT_IMG
        robotOneStep = True
    elif x != 0 and world[x-1][y] == GOAL_IMG:
        world[x][y] = PATH_WALKED_IMG
        world[x-1][y] = ROBOT_IMG
        windowSurface.fill(WHITE)
        drawWorld(windowSurface, world)
        textsurface = myfont.render('The robot walked ' +str(stepsCounter)+ ' steps to reach the goal', True, (30,144,255))
        windowSurface.blit(textsurface,(0,0))
        robotOneStep = False

    return robotOneStep

def main():
    saveTimestamp = int(time.time())
    saveCounter = 0
    stepsCounter = 1
    world = convertAsciiMapToWorld(WORLD)
    worldWidth = len(world)
    worldHeight = len(world[0])

    windowSurface.fill(WHITE)
    drawWorld(windowSurface, world)

    if SAVEIMAGES:
        pygame.image.save(windowSurface, 'wavefront_%s_%s.png' % (saveTimestamp, str(saveCounter).rjust(4, '0')))
        saveCounter += 1

    startTime = time.time()

    # run the game loop
    while True:
        if time.time() > startTime + DELAY:
            robotOneStep = False
            originalRobot = []
            for x in range(worldWidth):
                for y in range(worldHeight):
                    if world[x][y] == ROBOT_IMG:
                        originalRobot.append((x, y))

            for x, y in originalRobot:
                if robotStep(world, x, y, stepsCounter):
                    robotOneStep = True
                    stepsCounter += 1

            if robotOneStep:
                # redraw the world since there has been a change
                windowSurface.fill(WHITE)
                drawWorld(windowSurface, world)
                if SAVEIMAGES:
                    pygame.image.save(windowSurface, 'wavefront_%s_%s.png' % (saveTimestamp, str(saveCounter).rjust(4, '0')))
                    saveCounter += 1

            startTime = time.time()

        # check for any quit events
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()

        pygame.display.update()

if __name__ == '__main__':
    main()