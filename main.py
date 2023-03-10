import pyglet

pyglet.options["debug_gl"] = False
pyglet.options["shadow_window"] = False
pyglet.options["vsync"] = True
pyglet.image.Texture.default_mag_filter = pyglet.gl.GL_NEAREST

import array
import random
from random import choice, randint, randrange
import draw

WIDTH = 320
HEIGHT = 240
ZOOM = 3
FRAMERATE = 30

import gc
from time import perf_counter


class World:
    def rnd(self):
        return random.randrange(0, WIDTH * HEIGHT)

    def __init__(self, sharks, fish, fish_repro_time, shark_repro_time):
        self.fish_repro = array.array("L", [0] * WIDTH * HEIGHT)
        self.shark_life = array.array("L", [0] * WIDTH * HEIGHT)
        self.shark_repro = array.array("L", [0] * WIDTH * HEIGHT)
        self.empty = array.array("L", [0] * WIDTH * HEIGHT)

        for _ in range(fish):
            while True:
                pos = self.rnd()
                if self.fish_repro[pos]:
                    continue
                self.fish_repro[pos] = randint(1, fish_repro_time)
                break

        for _ in range(sharks):
            while True:
                pos = self.rnd()
                if self.shark_repro[pos] or self.fish_repro[pos]:
                    continue
                self.shark_repro[pos] = randint(1, shark_repro_time)
                self.shark_life[pos] = 1
                break


class Window(pyglet.window.Window):
    def __init__(self, *a, **ka):
        super().__init__(*a, **ka)

        self.texture = pyglet.image.Texture.create(WIDTH, HEIGHT)

        self.blank = array.array("B", b"\x00" * WIDTH * HEIGHT * 4)
        self.buffer = array.array("B", b"\x00" * WIDTH * HEIGHT * 4)

        self.shark_starves = 30
        self.shark_repro_time = 35
        self.fish_repro_time = 60
        self.starting_fish = 3000
        self.starting_sharks = 1000

        self.worlds = [
            World(
                self.starting_sharks,
                self.starting_fish,
                self.fish_repro_time,
                self.shark_repro_time,
            )
            for _ in range(2)
        ]
        self.world = 0

        self.batch = pyglet.graphics.Batch()
        self.sprite = pyglet.sprite.Sprite(self.texture, x=0, y=0, batch=self.batch)
        self.sprite.scale = ZOOM

        colors = (
            [32, 0, 64, 255],
            [255, 32, 32, 255],
            [0, 255, 0, 255],
            [0, 0, 255, 255],
            [255, 0, 255, 255],
        )
        self.colors = [array.array("B", x) for x in colors]

        self.vectors = (
            (-1, 0),
            (0, -1),
            (0, 1),
            (1, 0),
        )

        # This ensures that the grid elements are processed in random order.
        # Not doing this causes "ocean current" effects, which manifest
        # noticeably when the water is most full of fish.

        self.seq = list(range(WIDTH * HEIGHT))
        random.shuffle(self.seq)

        # For fun, swap the above lines with the below line to see what I mean!
        # self.seq = list(range(WIDTH * HEIGHT))

        self.seqarr = array.array("L", self.seq)

        self.offsets = [None] * WIDTH * HEIGHT * 4
        for pos in self.seq:
            x, y = (pos % WIDTH), (pos // WIDTH)
            for i, v in enumerate(self.vectors):
                r = (((y + v[1]) % HEIGHT) * WIDTH) + ((x + v[0]) % WIDTH)
                self.offsets[pos * 4 + i] = r
        self.offsetarr = array.array("L", self.offsets)

        self.timing = 0.0

        self.ww = WIDTH
        self.hh = HEIGHT

        print("Time to render each frame | Percentage of render time per frame")

    def event(self, *a):
        start = perf_counter()
        draw.event(self)
        self.timing += perf_counter() - start

    def timer(self, *a):
        render_time = self.timing / FRAMERATE
        print(render_time, ((render_time) / (1 / FRAMERATE)) * 100)
        self.timing = 0.0

    def on_draw(self, *a):
        # pyglet.gl.glViewport(0, 0, int(WIDTH * (ZOOM**2)), int(HEIGHT * (ZOOM**2)))
        self.texture.blit_into(
            pyglet.image.ImageData(WIDTH, HEIGHT, "RGBA", self.buffer.tobytes()),
            0,
            0,
            0,
        )
        self.clear()
        self.batch.draw()

        gc.collect()


w = Window(WIDTH * ZOOM, HEIGHT * ZOOM)
pyglet.clock.schedule_interval(w.event, 1 / FRAMERATE)
pyglet.clock.schedule_interval(w.timer, 1)
gc.freeze()
gc.disable()
gc.collect()
pyglet.app.run()
