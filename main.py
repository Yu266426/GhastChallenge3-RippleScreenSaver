import pygame


def clamp_colour(value: float) -> int:
	return int(pygame.math.clamp(value, 0.0, 255.0))


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

		max_value = 0
		min_value = float("INF")

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
				max_value = max(max_value, self.next[row][col])
				min_value = min(min_value, self.next[row][col])

		self.previous = self.grid
		self.grid = self.next

		print(max_value, min_value)

	def draw(self, surface: pygame.Surface):
		for row, grid_row in enumerate(self.grid):
			for col, tile in enumerate(grid_row):
				pygame.draw.rect(
					surface,
					[clamp_colour((tile / (self.ripple_strength * 6) + 0.5) * 255) for _ in range(3)],
					((col - 1) * self.tile_size, (row - 1) * self.tile_size, self.tile_size, self.tile_size)
				)


pygame.init()

screen = pygame.display.set_mode((400, 400), vsync=1)
clock = pygame.time.Clock()

ripple_grid = RippleGrid((400, 400), 133, 1, 0.99)

running = True
while running:
	delta = clock.tick() / 1000
	pygame.display.set_caption(str(round(clock.get_fps())))

	mouse_pos = pygame.mouse.get_pos()
	keys_pressed = pygame.key.get_pressed()

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False

		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_ESCAPE:
				running = False

			if event.key == pygame.K_SPACE:
				ripple_grid.add_ripple(mouse_pos, 4)

	# if keys_pressed[pygame.K_SPACE]:
	# 	spawn_pos = int(mouse_pos[0] / ripple_grid.tile_size), int(mouse_pos[1] / ripple_grid.tile_size)
	# 	radius = 1
	#

	ripple_grid.update()

	screen.fill("black")

	ripple_grid.draw(screen)

	pygame.display.flip()

pygame.quit()
