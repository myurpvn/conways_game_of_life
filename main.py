import pygame
import random
import math

from constants import POPULATION, SCREEN_X, SCREEN_Y, FPS, STEP, PADDING

pygame.init()
pygame.display.set_caption("Conway's The Game of Life")


GRID_SIZE = (SCREEN_X - PADDING * 2, SCREEN_Y - PADDING * 2)

screen: pygame.Surface = pygame.display.set_mode((SCREEN_X, SCREEN_Y))
clock = pygame.time.Clock()


class Square:
    width: int = STEP - 2
    height: int = STEP - 2

    def __init__(self, center: str, center_xy: pygame.Vector2) -> None:
        self.center: str = center
        self.center_x: float = center_xy.x
        self.center_y: float = center_xy.y
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

        steps: list[int] = [-STEP, 0, STEP]
        live_neighbours = []
        all_neighbours = []

        for STEP_y in steps:
            for STEP_x in steps:
                if STEP_y != 0 or STEP_x != 0:
                    all_neighbours.append(
                        f"c{round(self.center_x + STEP_x)},{round(self.center_y + STEP_y)}"
                    )

        for square in all_neighbours:
            if square in live_squares:
                live_neighbours.append(square)

        return len(live_neighbours)


class World:
    max_population: int = min(POPULATION, SCREEN_X * SCREEN_Y // STEP**2)

    def __init__(self) -> None:
        self.world_map: dict[str, Square] = {}
        self.live_world_map: set = set()
        self.running: bool = False

    def __clean_world(self) -> None:
        for square, square_obj in self.world_map.items():
            if square_obj.alive:
                if square not in self.live_world_map:
                    square_obj.alive = False

    def clear_world(self) -> None:
        self.live_world_map = set()
        self.__clean_world()

    def start_world(self) -> None:
        self.running = True

    def update_live_world_map(self, selected_squares: list[str]) -> None:
        self.live_world_map = set(selected_squares)

    def handle_click(self, button: int, pos: tuple[int, int]) -> None:
        self.__clean_world()

        min_dist: float = math.sqrt(SCREEN_X**2 + SCREEN_Y**2)
        current_live_squares = list(self.live_world_map)

        clicked_square: str = ""
        for center, square in self.world_map.items():
            dist: float = pygame.math.Vector2(pos).distance_to(
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
        for y in range(PADDING - 1, GRID_SIZE[1] + PADDING, STEP):
            for x in range(PADDING - 1, GRID_SIZE[0] + PADDING, STEP):
                center: str = f"c{x},{y}"
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
                square.center_x - STEP // 2,
                square.center_y - STEP // 2,
                STEP,
                STEP,
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

        elif event.type == pygame.MOUSEBUTTONDOWN:
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
            n_count: int = square.count_neighbours(world.live_world_map)
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
    dt: float = clock.tick(FPS) / 1000

pygame.quit()
