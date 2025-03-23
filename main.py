import pygame

from constants import FPS
from models import World

pygame.init()
pygame.display.set_caption("Conway's The Game of Life")


world = World()
world.create_world_map()

grid = False
dt = 0
running = True
clock = pygame.time.Clock()
while running:
    world.surface.fill("black")

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            keys = pygame.key.get_pressed()

            if keys[pygame.K_RETURN]:
                world.start_world()

            if keys[pygame.K_ESCAPE] or keys[pygame.K_q]:
                running = False

            if keys[pygame.K_g]:
                grid = not grid

            if not world.running:
                if keys[pygame.K_UP]:
                    world.generate_world_pattern()

                if keys[pygame.K_c]:
                    world.clear_world()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            button = event.button
            pos = event.pos
            world.handle_click(button, pos)

    if grid:
        world.draw_grid()

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
    dt = clock.tick(FPS) / 1000

pygame.quit()
