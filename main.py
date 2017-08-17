import sys
import time
from operator import add
from shutil import get_terminal_size
from random import randint


class World:
    def __init__(self, size, bounces, blocks, verbose):
        self.rows = size[0]
        self.columns = size[1]
        self.max_bounces = bounces
        self.blocks = blocks
        self.verbose = verbose
        self.content = [[-1 for _ in range(self.columns)] for _ in range(self.rows)]
        self.light = [self.rows//2, self.columns//2]
        self.content[self.light[0]][self.light[1]] = -2
        
        self.directions = [[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]]
        self.reverse_map = [4, 5, 6, 7, 0, 1, 2, 3]
        self.bounce_map_vert = [None, 7, 6, 5, None, 3, 2, 1]
        self.bounce_map_hori = [4, 3, None, 1, 0, 7, None, 5]

    def set_light_source(self, x, y):
        if 0 <= x < self.rows and 0 <= y < self.columns:
            self.content[self.light[0]][self.light[1]] = -1
            self.light = [x, y]
            self.content[self.light[0]][self.light[1]] = -2
        else:
            print("Light placed outside world")
            sys.exit(1)

    def start(self):
        max_columns, max_rows = get_terminal_size()

        # Check console dimensions
        if max_columns < len(self.content[0])+3 or max_rows < len(self.content)+3:
            print("Console is too small for specified grid")
            sys.exit(1)

        sys.stdout.write("\x1b[?25l")
        sys.stdout.write("\x1b[2J")
        sys.stdout.flush()

    def __str__(self):
        # chars = ["▔", "▁", "▏", "▕", "╲", "╱", "╳", " ", "@"]
        # chars = ["▔", "╲", "▕", "╱", "▁", "╲", "▏", "╱", "╳", "@", " "]
        chars = ["─", "╲", "│", "╱", "─", "╲", "│", "╱", "┼", "╳", "░", "▒", "▓", "█", "@", " "]

        sys.stdout.write("\x1b[H")
        sys.stdout.flush()
        output = "╭" + "─"*self.columns + "╮\n"
        for line in self.content:
            output += "│"
            for point in line:
                output += chars[point]
            output += "│\n"
        output += "╰" + "─"*self.columns + "╯"

        return output

    def end(self):
        height = self.rows+3
        sys.stdout.write("\x1b[{}H".format(height))
        sys.stdout.write("\x1b[?25h")
        sys.stdout.flush()

    def next(self):
        # self.content[randint(0, self.rows - 1)][randint(0, self.columns - 1)] = randint(1, 7)

        direction = randint(0, 7)
        pos = self.light
        bounces = 0
        while bounces < self.max_bounces:
            pos = list(map(add, pos, self.directions[direction]))
            while 0 <= pos[0] < self.rows and 0 <= pos[1] < self.columns:
                if self.content[pos[0]][pos[1]] in [-2, -3]:
                    # Hit a light source or object TODO: handle light/object collisions
                    break
                if self.content[pos[0]][pos[1]] is not -1:
                    # Already light in point
                    if self.blocks and self.content[pos[0]][pos[1]] in [8, 9]:
                        # Replace busy intersections with blocks
                        self.content[pos[0]][pos[1]] = 10
                    elif self.blocks and self.content[pos[0]][pos[1]] is 10:
                        # Replace busy intersections with blocks
                        self.content[pos[0]][pos[1]] = 11
                    elif self.blocks and self.content[pos[0]][pos[1]] in [11, 12]:
                        # Replace busy intersections with blocks
                        self.content[pos[0]][pos[1]] = 12
                    elif self.content[pos[0]][pos[1]] not in [direction, self.reverse_map[direction]]:
                        if direction in [0, 2, 4, 6]:
                            self.content[pos[0]][pos[1]] = 8
                        else:
                            self.content[pos[0]][pos[1]] = 9
                else:
                    self.content[pos[0]][pos[1]] = direction
                pos = list(map(add, pos, self.directions[direction]))

                if self.verbose:
                    print(self)
            if not self.verbose:
                print(self)

            # Bounce
            if pos[0] < 0 or pos[0] >= self.rows:
                direction = self.bounce_map_vert[direction]
            if pos[1] < 0 or pos[1] >= self.columns:
                direction = self.bounce_map_hori[direction]

            bounces += 1


def main(size):
    world = World(size, 3, True, False)

    world.start()

    for _ in range(10):
        world.set_light_source(randint(0, size[0]-1), randint(0, size[1]-1))
        for progress in range(15):
            world.next()
            # time.sleep(0.05)

    world.end()


if __name__ == '__main__':
    # Exits with:
    #   0 if success
    #   1 if error while running
    #   2 if invalid arguments

    # Reads the size of the world from commandline
    if len(sys.argv) is not 3:
        print("Incorrect arguments")
        print("Usage:", sys.argv[0], "rows columns")
        sys.exit(2)

    try:
        size = int(sys.argv[1]), int(sys.argv[2])
    except ValueError:
        print("Given arguments not integers")
        print("Usage:", sys.argv[0], "rows columns")
        sys.exit(2)

    # size = 15, 20
    # size = 4, 8
    main(size)
