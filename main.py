import pygame
import random
import math

pygame.init()
pygame.display.set_caption("Conway's The Game of Life")

fps = 60
screen_size = (1000, 1000)
step = 10  # 1% of screen width
padding = 50  # 5% of screen width
grid_size = (screen_size[0] - padding * 2, screen_size[1] - padding * 2)

screen = pygame.display.set_mode(screen_size)
clock = pygame.time.Clock()


class Square:
    width = step - 2
    height = step - 2

    def __init__(self, center: str, center_xy: pygame.Vector2) -> None:
        self.center = center
        self.center_x = center_xy.x
        self.center_y = center_xy.y
        self.alive = False

    def populate(self) -> None:
        if not self.alive:
            self.alive = True

        pygame.draw.rect(
            surface=screen,
            color="yellow",
            rect=pygame.Rect(
                self.center_x - Square.width // 2,
                self.center_y - Square.height // 2,
                Square.width,
                Square.height,
            ),
        )

    def kill(self) -> None:
        if self.alive:
            self.alive = False

        pygame.draw.rect(
            surface=screen,
            color="black",
            rect=pygame.Rect(
                self.center_x - Square.width // 2,
                self.center_y - Square.height // 2,
                Square.width,
                Square.height,
            ),
        )

    def count_neighbours(self, live_squares: set):

        steps = [-step, 0, step]
        live_neighbours = []
        all_neighbours = []

        for step_y in steps:
            for step_x in steps:
                if step_y != 0 or step_x != 0:
                    all_neighbours.append(
                        f"c{round(self.center_x + step_x)},{round(self.center_y + step_y)}"
                    )

        for square in all_neighbours:
            if square in live_squares:
                live_neighbours.append(square)

        return len(live_neighbours)


class World:
    max_population = 4000

    def __init__(self) -> None:
        self.world_map: dict[str, Square] = {}
        self.live_world_map: set = ()
        self.running: bool = False

    def __clean_world(self) -> None:
        for square, square_obj in self.world_map.items():
            if square_obj.alive:
                if square not in self.live_world_map:
                    square_obj.alive = False

    def clear_world(self) -> None:
        self.live_world_map = ()
        self.__clean_world()

    def start_world(self) -> None:
        self.running = True

    def update_live_world_map(self, selected_squares: list[str]) -> None:
        self.live_world_map = set(selected_squares)

    def handle_click(self, button: int, pos: tuple[int, int]) -> None:
        self.__clean_world()

        min_dist = math.sqrt(screen_size[0] ** 2 + screen_size[1] ** 2)
        current_live_squares = list(self.live_world_map)

        clicked_square = ""
        for center, square in self.world_map.items():
            dist = pygame.math.Vector2(pos).distance_to(
                (square.center_x, square.center_y)
            )
            if dist < min_dist:
                min_dist = dist
                clicked_square = center

        if clicked_square != "":
            if button == 1:
                current_live_squares.append(clicked_square)
                world.world_map[clicked_square].populate()

            if button == 3:
                current_live_squares.remove(clicked_square)
                world.world_map[clicked_square].kill()

        self.update_live_world_map(current_live_squares)

    def create_world_map(self) -> None:
        world_map = {}
        for y in range(padding - 1, grid_size[1] + padding, step):
            for x in range(padding - 1, grid_size[0] + padding, step):
                center = f"c{x},{y}"
                world_map[center] = Square(
                    center=f"c{x},{y}", center_xy=pygame.Vector2(x, y)
                )
        self.world_map = world_map

    def generate_world_pattern(self) -> None:
        self.update_live_world_map(
            random.choices(list(world.world_map.keys()), k=world.max_population)
        )
        self.__clean_world()


def draw_grid(world_map: dict[str, Square]) -> None:
    for square in world_map.values():
        pygame.draw.rect(
            surface=screen,
            color="grey",
            rect=pygame.Rect(
                square.center_x - step // 2,
                square.center_y - step // 2,
                step,
                step,
            ),
            width=1,
        )


world = World()
world.create_world_map()
# world.generate_world_pattern()

dt = 0
running = True
while running:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_RETURN]:
                world.start_world()
            
            if keys[pygame.K_ESCAPE] or keys[pygame.K_q]:
                running = False

            if not world.running:
                if keys[pygame.K_UP]:
                    world.generate_world_pattern()

                if keys[pygame.K_c]:
                    world.clear_world()

        elif event.type == pygame.MOUSEBUTTONDOWN and not world.running:
            button = event.button
            pos = event.pos
            world.handle_click(button, pos)

    screen.fill("black")
    # draw_grid(world.world_map)

    for square in world.live_world_map:
        if square in world.world_map.keys():
            world.world_map[square].populate()

    live_world_map = list(world.live_world_map)
    if world.running:
        for center, square in world.world_map.items():
            n_count = square.count_neighbours(world.live_world_map)
            if square.alive:
                if n_count < 2 or n_count > 3:
                    live_world_map.remove(center)
                    square.kill()
            else:
                if n_count == 3:
                    live_world_map.append(center)
                    square.populate()

        world.update_live_world_map(live_world_map)

    pygame.display.flip()
    dt = clock.tick(fps) / 1000

pygame.quit()
