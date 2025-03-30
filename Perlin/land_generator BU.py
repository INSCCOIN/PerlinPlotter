import pygame
import numpy as np
import noise
import pygame.freetype

# Pygame setup
pygame.init()
screen_width, screen_height = 1200, 800
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("3D Noise Landscape Generator")

# Colors
white = (255, 255, 255)
black = (0, 0, 0)

# Noise parameters
scale = 100
octaves = 6
persistence = 0.5
lacunarity = 2.0

# Panning and zooming parameters
pan_x, pan_y = 0, 0
pan_speed = 10
zoom_level = 1.0

# Font for displaying parameters
pygame.freetype.init()
font = pygame.freetype.SysFont(None, 24)

def generate_noise(width, height, scale, octaves, persistence, lacunarity):
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

def draw_noise(screen, noise_map, pan_x, pan_y, zoom_level):
    width, height = noise_map.shape
    visible_noise_map = noise_map[int(pan_x/zoom_level):int((pan_x + screen_width)/zoom_level), 
                                  int(pan_y/zoom_level):int((pan_y + screen_height)/zoom_level)]
    visible_noise_map = (visible_noise_map + 0.5) * 255  # Normalize to 0-255
    visible_noise_map = visible_noise_map.astype(np.uint8)
    depth_color = np.zeros((visible_noise_map.shape[0], visible_noise_map.shape[1], 3), dtype=np.uint8)
    depth_color[..., 1] = visible_noise_map  # Set green channel
    depth_color[..., 2] = 255 - visible_noise_map  # Set blue channel

    zoomed_surface = pygame.surfarray.make_surface(depth_color)
    zoomed_surface = pygame.transform.scale(zoomed_surface, (screen_width, screen_height))
    screen.blit(zoomed_surface, (0, 0))

def display_parameters(screen, scale, octaves, persistence, lacunarity, zoom_level):
    params_text = f"Scale: {scale}, Octaves: {octaves}, Persistence: {persistence}, Lacunarity: {lacunarity}, Zoom: {zoom_level:.2f}"
    font.render_to(screen, (10, 10), params_text, white)

def save_screenshot(screen, filename="landscape.png"):
    pygame.image.save(screen, filename)

def main():
    global pan_x, pan_y, scale, octaves, persistence, lacunarity, zoom_level
    running = True
    clock = pygame.time.Clock()

    noise_map = generate_noise(screen_width * 2, screen_height * 2, scale, octaves, persistence, lacunarity)
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    pan_x = max(0, pan_x - pan_speed)
                elif event.key == pygame.K_RIGHT:
                    pan_x = min((screen_width * 2) - screen_width, pan_x + pan_speed)
                elif event.key == pygame.K_UP:
                    pan_y = max(0, pan_y - pan_speed)
                elif event.key == pygame.K_DOWN:
                    pan_y = min((screen_height * 2) - screen_height, pan_y + pan_speed)
                elif event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:
                    zoom_level = min(4.0, zoom_level + 0.1)
                elif event.key == pygame.K_MINUS:
                    zoom_level = max(0.5, zoom_level - 0.1)
                elif event.key == pygame.K_s:
                    save_screenshot(screen)
                elif event.key == pygame.K_1:
                    scale = max(10, scale - 10)
                elif event.key == pygame.K_2:
                    scale = min(500, scale + 10)
                elif event.key == pygame.K_3:
                    octaves = max(1, octaves - 1)
                elif event.key == pygame.K_4:
                    octaves = min(10, octaves + 1)
                elif event.key == pygame.K_5:
                    persistence = max(0.1, persistence - 0.1)
                elif event.key == pygame.K_6:
                    persistence = min(1.0, persistence + 0.1)
                elif event.key == pygame.K_7:
                    lacunarity = max(0.5, lacunarity - 0.5)
                elif event.key == pygame.K_8:
                    lacunarity = min(4.0, lacunarity + 0.5)

        screen.fill(black)
        draw_noise(screen, noise_map, pan_x, pan_y, zoom_level)
        display_parameters(screen, scale, octaves, persistence, lacunarity, zoom_level)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()