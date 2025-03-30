import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import noise
import ctypes

def init_pygame():
    pygame.init()
    screen_width, screen_height = 1200, 800
    screen = pygame.display.set_mode((screen_width, screen_height), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Enhanced 3D Noise Landscape Generator")
    return screen_width, screen_height

def init_opengl():
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_POSITION, (0, 50, 50, 1))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (1, 1, 1, 1))
    glLightfv(GL_LIGHT0, GL_SPECULAR, (1, 1, 1, 1))

    glEnable(GL_LIGHT1)
    glLightfv(GL_LIGHT1, GL_POSITION, (-50, 50, -50, 1))
    glLightfv(GL_LIGHT1, GL_DIFFUSE, (0.5, 0.5, 0.5, 1))
    glLightfv(GL_LIGHT1, GL_SPECULAR, (0.5, 0.5, 0.5, 1))

    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (1, 1, 1, 1))
    glMateriali(GL_FRONT_AND_BACK, GL_SHININESS, 50)

def generate_terrain(width, height, scale, octaves, persistence, lacunarity):
    lin_x = np.linspace(0, width, width, endpoint=False)
    lin_y = np.linspace(0, height, height, endpoint=False)
    x, y = np.meshgrid(lin_x, lin_y)

    terrain = np.vectorize(noise.pnoise2)(
        x / scale,
        y / scale,
        octaves=octaves,
        persistence=persistence,
        lacunarity=lacunarity,
        repeatx=width,
        repeaty=height,
        base=42
    )
    return terrain

def get_color(height):
    if height < -10:
        return 0.3, 0.3, 0.8  # Deep Blue for water
    elif height < 0:
        return 0.5, 0.5, 1.0  # Light Blue for shallow water
    elif height < 5:
        return 0.5, 1.0, 0.5  # Green for plains
    elif height < 20:
        return 0.5, 0.5, 0.0  # Brown for hills
    else:
        return 1.0, 1.0, 1.0  # White for mountains

def create_vertex_buffer(terrain):
    rows, cols = terrain.shape
    vertices = []
    for x in range(rows - 1):
        for y in range(cols):
            height = terrain[x][y] * 20
            color = get_color(height)
            vertices.append((x, height, y, *color))
            height = terrain[x + 1][y] * 20
            color = get_color(height)
            vertices.append((x + 1, height, y, *color))
    vertices = np.array(vertices, dtype='f')
    return vertices

def draw_terrain(vertices):
    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_COLOR_ARRAY)
    vertex_pointer = vertices.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
    color_pointer = ctypes.cast(ctypes.addressof(vertex_pointer.contents) + 3 * vertices.itemsize, ctypes.POINTER(ctypes.c_float))
    glVertexPointer(3, GL_FLOAT, 6 * vertices.itemsize, vertex_pointer)
    glColorPointer(3, GL_FLOAT, 6 * vertices.itemsize, color_pointer)
    glDrawArrays(GL_TRIANGLE_STRIP, 0, len(vertices))
    glDisableClientState(GL_VERTEX_ARRAY)
    glDisableClientState(GL_COLOR_ARRAY)

def main():
    try:
        print("Initializing Pygame...")
        screen_width, screen_height = init_pygame()
        
        print("Initializing OpenGL...")
        init_opengl()

        print("Generating terrain...")
        terrain = generate_terrain(400, 400, 100, 8, 0.5, 2.0)
        print("Terrain generated successfully.")

        print("Creating vertex buffer...")
        vertices = create_vertex_buffer(terrain)
        print("Vertex buffer created successfully.")

        print("Setting up the perspective and initial view...")
        gluPerspective(45, (screen_width / screen_height), 0.1, 1000.0)
        glTranslatef(-200, -20, -200)
        glRotatef(25, 2, 1, 0)

        running = True
        clock = pygame.time.Clock()

        # Mouse panning variables
        mouse_down = False
        last_mouse_pos = (0, 0)

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_w:
                        glTranslatef(0, 0, 5)
                    elif event.key == pygame.K_s:
                        glTranslatef(0, 0, -5)
                    elif event.key == pygame.K_a:
                        glRotatef(5, 0, 1, 0)
                    elif event.key == pygame.K_d:
                        glRotatef(-5, 0, 1, 0)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        mouse_down = True
                        last_mouse_pos = event.pos
                    elif event.button == 4:  # Scroll up
                        glTranslatef(0, 0, 5)
                    elif event.button == 5:  # Scroll down
                        glTranslatef(0, 0, -5)
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        mouse_down = False
                elif event.type == pygame.MOUSEMOTION:
                    if mouse_down:
                        dx, dy = event.pos[0] - last_mouse_pos[0], event.pos[1] - last_mouse_pos[1]
                        glRotatef(dx * 0.1, 0, 1, 0)
                        glRotatef(dy * 0.1, 1, 0, 0)
                        last_mouse_pos = event.pos

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            draw_terrain(vertices)
            pygame.display.flip()
            clock.tick(60)

    except Exception as e:
        print(f"Error in main loop: {e}")
        raise
    finally:
        pygame.quit()

if __name__ == "__main__":
    main()