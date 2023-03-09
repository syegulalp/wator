# cython: boundscheck=False
# cython: wraparound=False

from random import randint, choice
import cython

if cython.compiled:
    from cython.cimports.cpython import array as arr  # type: ignore
else:
    import array as arr


def event(self, *a):
    world = self.worlds[self.world]
    other = self.worlds[not self.world]

    self.buffer[:] = self.blank
    other.fish_repro[:] = world.blank
    other.shark_repro[:] = world.blank
    other.shark_life[:] = world.blank

    fish_repro: list = world.fish_repro
    shark_repro: list = world.shark_repro
    shark_life: list = world.shark_life
    fish_repro_time: int = self.fish_repro_time
    shark_repro_time: int = self.shark_repro_time
    shark_starves: int = self.shark_starves
    other_fish_repro: list = other.fish_repro
    other_shark_repro: list = other.shark_repro
    other_shark_life: list = other.shark_life

    offsets: list = self.offsets
    offset: int
    pos: int

    moves: list = []
    eats: list = []
    b: arr.array = self.buffer

    clear_moves = moves.clear
    clear_eats = eats.clear
    append_moves = moves.append
    append_eats = eats.append

    c1 = self.colors[1]
    # c1: cython.uchar[4] = (255, 32, 32, 255)
    c2 = self.colors[2]
    # c2: cython.uchar[4] = (0, 255, 0, 255)

    ch = choice
    ri = randint

    repro: int
    target_move: int

    seq: list = self.seq

    for pos in seq:
        repro = fish_repro[pos]
        if repro:
            repro += 1

            clear_moves()
            for offset in offsets[pos]:
                if fish_repro[offset] == 0 and other_fish_repro[offset] == 0:
                    append_moves(offset)
            if moves:
                target_move = ch(moves)
                if repro >= fish_repro_time:
                    other_fish_repro[pos] = ri(1, fish_repro_time)
                    other_fish_repro[target_move] = ri(1, fish_repro_time)
                else:
                    other_fish_repro[target_move] = repro
            else:
                other_fish_repro[pos] = repro
            fish_repro[pos] = 0

            b[pos * 4 : pos * 4 + 4] = c2[:]

        repro = shark_repro[pos]
        if repro:
            repro += 1
            life = shark_life[pos] + 1
            if life > shark_starves:
                shark_repro[pos] = 0
                continue

            clear_moves()
            clear_eats()
            for offset in offsets[pos]:
                if other_fish_repro[offset] != 0:
                    append_eats(offset)
                if shark_repro[offset] == 0 and other_shark_repro[offset] == 0:
                    append_moves(offset)
            if eats:
                target_move = ch(eats)
                other_shark_repro[target_move] = repro
                other_shark_life[target_move] = 1
                other_fish_repro[target_move] = 0
            elif moves:
                target_move = ch(moves)
                if repro > shark_repro_time:
                    other_shark_repro[pos] = 1
                    other_shark_life[pos] = 1
                    other_shark_life[target_move] = 1
                    other_shark_repro[target_move] = 1
                else:
                    other_shark_life[target_move] = life
                    other_shark_repro[target_move] = repro

            else:
                other_shark_repro[pos] = repro
                other_shark_life[life] = life
            shark_repro[pos] = 0

            b[pos * 4 : pos * 4 + 4] = c1[:]

    self.world = not self.world
