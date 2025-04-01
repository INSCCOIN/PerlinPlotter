import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import noise

# Pygame setup
pygame.init()
screen_width, screen_height = 1200, 800
screen = pygame.display.set_mode((screen_width, screen_height), DOUBLEBUF | OPENGL)
pygame.display.set_caption("3D Noise Landscape Generator")

# OpenGL setup
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

# Noise parameters
scale = 100
octaves = 12
persistence = 0.7
lacunarity = 3.0

def generate_noise_map(width, height, scale, octaves, persistence, lacunarity):
    lin_x = np.linspace(0, width, width, endpoint=False)
    lin_y = np.linspace(0, height, height, endpoint=False)
    x, y = np.meshgrid(lin_x, lin_y)

    noise_map = np.vectorize(noise.pnoise2)(
        x / scale,
        y / scale,
        octaves=octaves,
        persistence=persistence,
        lacunarity=lacunarity,
        repeatx=width,
        repeaty=height,
        base=42
    )
    return noise_map

def draw_landscape(noise_map):
    rows, cols = noise_map.shape
    for x in range(rows - 1):
        glBegin(GL_TRIANGLE_STRIP)
        for y in range(cols):
            height = noise_map[x][y] * 10
            color = (0.0, 0.5 + height / 20, 0.5) if height > 0 else (0.0, 0.5, 0.5)
            glColor3fv(color)
            glVertex3f(x, height, y)
            height = noise_map[x + 1][y] * 10
            color = (0.0, 0.5 + height / 20, 0.5) if height > 0 else (0.0, 0.5, 0.5)
            glColor3fv(color)
            glVertex3f(x + 1, height, y)
        glEnd()

def main():
    noise_map = generate_noise_map(200, 200, scale, octaves, persistence, lacunarity)

    gluPerspective(45, (screen_width / screen_height), 0.1, 1000.0)
    glTranslatef(-100, -5, -300)
    glRotatef(25, 2, 1, 0)

    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    glTranslatef(1, 0, 0)
                elif event.key == pygame.K_RIGHT:
                    glTranslatef(-1, 0, 0)
                elif event.key == pygame.K_UP:
                    glTranslatef(0, -1, 0)
                elif event.key == pygame.K_DOWN:
                    glTranslatef(0, 1, 0)
                elif event.key == pygame.K_w:
                    glTranslatef(0, 0, 1)
                elif event.key == pygame.K_s:
                    glTranslatef(0, 0, -1)
                elif event.key == pygame.K_a:
                    glRotatef(5, 0, 1, 0)
                elif event.key == pygame.K_d:
                    glRotatef(-5, 0, 1, 0)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        draw_landscape(noise_map)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()