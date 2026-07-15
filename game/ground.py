class Ground:
    def __init__(self, width=800, height=80):
        self.offset = 0.0
        self._width = width
        self._height = height

    def update(self, speed, dt):
        self.offset += speed * dt
        if self.offset >= self._width:
            self.offset -= self._width
