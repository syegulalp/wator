import pyglet

pyglet.options["debug_gl"] = False
pyglet.options["shadow_window"] = False
pyglet.options["vsync"] = True
pyglet.image.Texture.default_mag_filter = pyglet.gl.GL_NEAREST

import array
import random
from random import randint
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
        self.blank = array.array("L", [0] * WIDTH * HEIGHT)

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

        self.set_location(
            self.screen.width // 2 - self.width // 2,
            self.screen.height // 2 - self.height // 2,
        )

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
        self.text_batch = pyglet.graphics.Batch()

        self.sprites = []
        for _ in range(4):
            s = pyglet.sprite.Sprite(
                self.texture,
                0,
                0,
                batch=self.batch,
            )
            s.scale = ZOOM
            self.sprites.append(s)

        self.sprites[1].x = -WIDTH * ZOOM
        self.sprites[2].x = -WIDTH * ZOOM
        self.sprites[2].y = -HEIGHT * ZOOM
        self.sprites[3].y = -HEIGHT * ZOOM

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

        # seq = []
        # for n in range(HEIGHT):
        #     w = n * WIDTH
        #     sseq = list(range(w, w + WIDTH))
        #     random.shuffle(sseq)
        #     seq.extend(sseq)

        seq = list(range(WIDTH * HEIGHT))
        random.shuffle(seq)

        # For fun, swap the above lines with the below line to see what I mean!
        # self.seq = list(range(WIDTH * HEIGHT))

        self.seqarr = array.array("L", seq)

        self.offsets = [None] * WIDTH * HEIGHT * 4
        for pos in seq:
            # for pos in range(WIDTH * HEIGHT):
            x, y = (pos % WIDTH), (pos // WIDTH)
            for i, v in enumerate(self.vectors):
                r = (((y + v[1]) % HEIGHT) * WIDTH) + ((x + v[0]) % WIDTH)
                self.offsets[pos * 4 + i] = r
        self.offsetarr = array.array("L", self.offsets)

        self.timing = 0.0
        self.render_time = 0.0
        self.framerate = 0.0

        self.ww = WIDTH
        self.hh = HEIGHT

        self.fish_pop = 0
        self.shark_pop = 0

        self.label = pyglet.text.Label(
            "",
            multiline=True,
            width=self.width // 2,
            anchor_x="left",
            anchor_y="top",
            x=8,
            y=self.height - 8,
            batch=self.text_batch,
        )
        self.update_text()

    def on_mouse_drag(self, x, y, dx, dy, *a):
        for _ in self.sprites:
            _.x = ((_.x + dx) % (WIDTH * ZOOM * 2)) - WIDTH * ZOOM
            _.y = ((_.y + dy) % (HEIGHT * ZOOM * 2)) - HEIGHT * ZOOM

    def event(self, *a):
        start = perf_counter()
        draw.event(self)
        self.timing += perf_counter() - start

    def on_key_press(self, symbol, modifiers):
        if symbol == 65289:
            self.label.visible = not self.label.visible
            self.update_text()

    def timer(self, *a):
        self.render_time = self.timing / FRAMERATE
        self.framerate = ((1 / FRAMERATE) / self.render_time) * FRAMERATE
        # (self.render_time / (1 / FRAMERATE)) * 100
        self.timing = 0.0
        if self.label.visible:
            self.update_text()

    def update_text(self):
        self.label.text = f"Fish: {self.fish_pop}\nSharks: {self.shark_pop}\n\nTime per frame: {self.render_time:.3}\nFramerate: {int(self.framerate)} @ {FRAMERATE} fps"

    def on_draw(self, *a):
        self.texture.blit_into(
            pyglet.image.ImageData(WIDTH, HEIGHT, "RGBA", self.buffer.tobytes()),
            0,
            0,
            0,
        )
        self.clear()
        self.batch.draw()
        self.text_batch.draw()

        gc.collect()


w = Window(WIDTH * ZOOM, HEIGHT * ZOOM)
pyglet.clock.schedule_interval(w.event, 1 / FRAMERATE)
pyglet.clock.schedule_interval(w.timer, 1)
gc.freeze()
gc.disable()
gc.collect()
pyglet.app.run()
