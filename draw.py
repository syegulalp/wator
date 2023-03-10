# cython: boundscheck=False
# cython: wraparound=False
# cython: cdivision=True

import cython

if cython.compiled:
    from cython.cimports.cpython import array as arr  # type: ignore
    from cython.cimports.libc.stdlib import rand  # type: ignore

    @cython.cfunc
    @cython.exceptval(check=False)
    def randint(a: cython.int, b: cython.int) -> cython.int:
        if a == b:
            return a
        return a + (rand() % (b + 1) - a)

    @cython.cfunc
    def ptr(arr_obj: arr.array) -> cython.p_uchar:
        array_ptr: cython.p_uchar = arr_obj.data.as_uchars
        return array_ptr

    @cython.cfunc
    def ptrui(arr_obj: arr.array) -> cython.p_uint:
        array_ptr: cython.p_uint = arr_obj.data.as_uints
        return array_ptr

else:
    import array as arr
    from random import randint

    def ptr(x):
        return x

    def ptrui(x):
        return x


def event(self, *a):
    world = self.worlds[self.world]
    other = self.worlds[not self.world]

    length: cython.int = len(other.fish_repro)

    f = arr.array("L", [0] * length)

    self.buffer[:] = self.blank
    other.fish_repro[:] = f[:]
    other.shark_repro[:] = f[:]
    other.shark_life[:] = f[:]

    # world.fish_repro: arr.array
    # other.fish_repro: arr.array

    fish_repro = ptrui(world.fish_repro)
    other_fish_repro = ptrui(other.fish_repro)

    shark_repro = ptrui(world.shark_repro)
    shark_life = ptrui(world.shark_life)

    other_shark_repro = ptrui(other.shark_repro)
    other_shark_life = ptrui(other.shark_life)

    fish_repro_time: cython.int = self.fish_repro_time
    shark_repro_time: cython.int = self.shark_repro_time
    shark_starves: cython.int = self.shark_starves

    offsets = ptrui(self.offsetarr)

    offset: cython.int
    pos: cython.int

    b: cython.p_uchar = ptr(self.buffer)

    c1: cython.uchar[4] = self.colors[1]
    c2: cython.uchar[4] = self.colors[2]

    repro: cython.int
    target_move: cython.int

    mov: cython.int[4] = [0, 0, 0, 0]
    eat: cython.int[4] = [0, 0, 0, 0]
    movptr: cython.int
    eatptr: cython.int
    x: cython.int
    xx: cython.int

    seq = ptrui(self.seqarr)

    for xx in range(length):
        pos = seq[xx]
        repro = fish_repro[pos]
        if repro:
            repro += 1
            movptr = 0
            for x in range(4):
                offset = offsets[pos * 4 + x]
                if fish_repro[offset] == 0 and other_fish_repro[offset] == 0:
                    mov[movptr] = offset
                    movptr += 1
            if movptr:
                target_move = mov[randint(0, movptr - 1)]
                if repro >= fish_repro_time:
                    other_fish_repro[pos] = randint(1, fish_repro_time)
                    other_fish_repro[target_move] = randint(1, fish_repro_time)
                else:
                    other_fish_repro[target_move] = repro
            else:
                other_fish_repro[pos] = repro
            fish_repro[pos] = 0

            for x in range(4):
                b[pos * 4 + x] = c2[x]

        repro = shark_repro[pos]
        if repro:
            repro += 1
            life = shark_life[pos] + 1
            if life > shark_starves:
                shark_repro[pos] = 0
                continue

            movptr = 0
            eatptr = 0
            for x in range(4):
                offset = offsets[pos * 4 + x]
                if other_fish_repro[offset] != 0:
                    eat[eatptr] = offset
                    eatptr += 1
                if shark_repro[offset] == 0 and other_shark_repro[offset] == 0:
                    mov[movptr] = offset
                    movptr += 1
            if eatptr:
                target_move = eat[randint(0, eatptr - 1)]
                other_shark_repro[target_move] = repro
                other_shark_life[target_move] = 1
                other_fish_repro[target_move] = 0
            elif movptr:
                target_move = mov[randint(0, movptr - 1)]
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

            for x in range(4):
                b[pos * 4 + x] = c1[x]

    self.world = not self.world
