import sys
import time
from operator import add
from shutil import get_terminal_size
from random import randint


class World:
    def __init__(self, size, bounces, blocks, slow):
        self.rows = size[0]
        self.columns = size[1]
        self.max_bounces = bounces
        self.blocks = blocks
        self.slow = slow
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
        if max_columns < self.columns+3 or max_rows < self.rows+3:
            print("Console is too small for specified grid")
            sys.exit(1)

        sys.stdout.write("\x1b[?25l")
        sys.stdout.write("\x1b[2J")
        sys.stdout.flush()

    def __str__(self):
        # chars = ["▔", "▁", "▏", "▕", "╲", "╱", "╳", " ", "@"]
        # chars = ["▔", "╲", "▕", "╱", "▁", "╲", "▏", "╱", "╳", "@", " "]
        chars = ["─", "╲", "│", "╱", "─", "╲", "│", "╱", "┼", "╳",
                 "░", "▒", "▓", "█", "⦀", "@", " "]

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

    def calculate_point(self, point, direction):
        if point in [-2, -3]:
            # Hit a light source or object
            # TODO: handle light/object collisions better
            return None

        if self.blocks is 0:
            # Just lines, no blocks
            if point is not -1:
                # Already light in point
                if point not in [direction, self.reverse_map[direction]]:
                    if direction in [0, 2, 4, 6]:
                        point = 8
                    else:
                        point = 9
            else:
                # No light or object in point yet
                point = direction
        elif self.blocks is 1:
            # Replace busy intersections with blocks
            if point is not -1:
                # Already light in point
                if point in [8, 9]:
                    point = 10
                elif point is 10:
                    point = 11
                elif point is 11:
                    point = 12
                elif point in [12, 13]:
                    point = 13
                elif point not in [direction, self.reverse_map[direction]]:
                    if direction in [0, 2, 4, 6]:
                        point = 8
                    else:
                        point = 9
            else:
                # No light or object in point yet
                point = direction
        elif self.blocks is 2:
            # Just blocks, no lines
            if point is -1:
                point = 10
            elif point < 13:
                point += 1

        return point

    def next(self):
        direction = randint(0, 7)
        pos = self.light
        bounces = 0
        while bounces < self.max_bounces:
            pos = list(map(add, pos, self.directions[direction]))
            while 0 <= pos[0] < self.rows and 0 <= pos[1] < self.columns:

                curr_point = self.calculate_point(self.content[pos[0]][pos[1]], direction)

                if curr_point is None:
                    # Hit object or light source
                    bounces = self.max_bounces
                    break

                self.content[pos[0]][pos[1]] = curr_point
                # Move to next point
                pos = list(map(add, pos, self.directions[direction]))

                if self.slow:
                    # Print each point
                    print(self)
            if not self.slow:
                # Or print each line
                print(self)

            # Calculate bounce
            if pos[0] < 0 or pos[0] >= self.rows:
                direction = self.bounce_map_vert[direction]
            if pos[1] < 0 or pos[1] >= self.columns:
                direction = self.bounce_map_hori[direction]

            bounces += 1


def main(size):
    world = World(size, 5, 2, True)

    world.start()

    for _ in range(2):
        world.set_light_source(randint(0, size[0]-1), randint(0, size[1]-1))
        for progress in range(20):
            world.next()
            # time.sleep(0.05)

    world.end()


if __name__ == '__main__':
    # Exits with:
    #   0 if success
    #   1 if error while running
    #   2 if invalid arguments

    # Reads the size of the world from commandline or uses terminal size if not given
    if len(sys.argv) is 1:
        max_size = get_terminal_size()
        size = [max_size[1]-3, max_size[0]-3]
        print(size)
        if size[0] < 1 or size[1] < 1:
            print("Terminal is too small")
            sys.exit(2)
    elif len(sys.argv) is 3:
        try:
            size = int(sys.argv[1]), int(sys.argv[2])
        except ValueError:
            print("Given arguments not integers")
            print("Usage:", sys.argv[0], "[rows columns]")
            sys.exit(2)
    else:
        print("Incorrect arguments given")
        print("Usage:", sys.argv[0], "[rows columns]")
        sys.exit(2)

    main(size)
