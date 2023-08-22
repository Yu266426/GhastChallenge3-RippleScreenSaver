import random

import pygame


class RippleGrid:
	def __init__(self, size: tuple[float, float], resolution: int, flow: float, damping: float):
		self.size = size
		self.resolution = resolution

		self.flow_factor = flow
		self.damping = damping

		self.tile_size = size[0] / resolution
		self.grid_size = int(size[0] / self.tile_size) + 2, int(size[1] / self.tile_size) + 2  # +2 to exclude edges

		self.grid = [[0 for _ in range(self.grid_size[0])] for _ in range(self.grid_size[1])]

		self.previous = self.grid.copy()
		self.next = self.grid.copy()

		self.ripple_strength = 100

	def add_ripple(self, pos: tuple[float, float], radius: int):
		center_pos = int(pos[0] / self.tile_size), int(pos[1] / self.tile_size)
		distance = radius ** 2

		for row in range(center_pos[1] - radius, center_pos[1] + radius):
			for col in range(center_pos[0] - radius, center_pos[0] + radius):
				if (row - center_pos[1]) ** 2 + (col - center_pos[0]) ** 2 < distance:
					ripple_grid.grid[row][col] += self.ripple_strength

	def update(self):
		self.next = [[0 for _ in range(self.grid_size[0])] for _ in range(self.grid_size[1])]

		for row, grid_row in enumerate(self.grid):
			for col, tile in enumerate(grid_row):
				if row == self.grid_size[1] - 1:
					continue

				if col == self.grid_size[0] - 1:
					continue

				# Average of surrounding
				flow = (
						self.grid[row + 1][col] +
						self.grid[row - 1][col] +
						self.grid[row][col + 1] +
						self.grid[row][col - 1]
				)
				flow /= 4

				previous = self.previous[row][col]

				self.next[row][col] = (2 * (flow * self.flow_factor + tile) / (self.flow_factor + 1) - previous) * self.damping

		self.previous = self.grid
		self.grid = self.next

	def draw(self, surface: pygame.Surface):
		for row, grid_row in enumerate(self.grid):
			for col, tile in enumerate(grid_row):
				colour_factor = pygame.math.clamp(tile / (self.ripple_strength * 6) + 0.5, 0.0, 1.0)

				pygame.draw.rect(
					surface,
					(int(colour_factor * 100), int(colour_factor * 100), int(colour_factor * 255)),
					((col - 1) * self.tile_size, (row - 1) * self.tile_size, self.tile_size, self.tile_size)
				)


class Timer:
	def __init__(self, cooldown: float, start_done: bool, repeating: bool):
		self._cooldown = cooldown
		self._repeating = repeating

		self._time = 0 if start_done else cooldown

		self._is_done = start_done
		self._is_just_done = start_done

	def set_cooldown(self, cooldown: float):
		self._cooldown = cooldown

	def tick(self, delta: float = 1 / 60):
		self._time -= delta

		if self._repeating:
			self._is_done = False
			self._is_just_done = False

			if self._time < 0:
				self._time += self._cooldown
				self._is_done = True
				self._is_just_done = True
		else:
			if self._time < 0:
				if self._is_done:
					self._is_just_done = False
				else:
					self._is_done = True
					self._is_just_done = True

				self._time = 0

	def start(self):
		self._time = self._cooldown
		self._is_done = False
		self._is_just_done = False

	def done(self):
		return self._is_done

	def just_done(self):
		return self._is_just_done


pygame.init()

screen = pygame.display.set_mode((400, 400), flags=0, vsync=1)
clock = pygame.time.Clock()

ripple_grid = RippleGrid(screen.get_size(), 133, 1, 0.97)

ripple_timer = Timer(random.uniform(1.5, 2.5), True, True)

running = True
while running:
	delta = clock.tick(30) / 1000
	pygame.display.set_caption(str(round(clock.get_fps())))

	mouse_pos = pygame.mouse.get_pos()
	keys_pressed = pygame.key.get_pressed()

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False

		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_ESCAPE:
				running = False

	ripple_timer.tick(delta)

	if ripple_timer.just_done():
		for _ in range(random.randint(1, 4)):
			ripple_grid.add_ripple((random.uniform(50, screen.get_width() - 50), random.uniform(50, screen.get_height() - 50)), random.randint(3, 6))
		ripple_timer.set_cooldown(random.uniform(1.5, 2.5))

	ripple_grid.update()

	screen.fill("black")

	ripple_grid.draw(screen)

	pygame.display.flip()

pygame.quit()
