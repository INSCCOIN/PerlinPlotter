import pygame # Import Pygame for graphics and event handling
import numpy as np # Import NumPy for numerical operations
import noise # Import the noise library for Perlin noise generation
import pygame.freetype # Import freetype for better font rendering
import datetime # Import datetime for timestamping screenshots
import os # Import os for directory handling

# Pygame setup
pygame.init()
screen_width, screen_height = 1600, 900
screen = pygame.display.set_mode((screen_width, screen_height), pygame.DOUBLEBUF)
pygame.display.set_caption("Seamless Infinite Perlin Noise Landscape")

# Colors
white = (255, 255, 255)
black = (0, 0, 0)

# Noise parameters
scale = 25 # Scale of the noise, larger values produce smoother landscapes
octaves = 12 # Number of layers of noise to combine
persistence = 0.3 # Controls the amplitude of each octave
lacunarity = 3.0 # Controls the frequency of each octave

# Panning and zooming parameters
pan_x, pan_y = 0, 0 # Initial panning coordinates
pan_speed = 15 # Speed of panning, adjust as needed
zoom_level = 1.0 # Initial zoom level, adjust as needed

# Font for displaying parameters
pygame.freetype.init()
font = pygame.freetype.SysFont(None, 24)

# Flags for toggling features
paused = False

# Screenshot directory
screenshot_dir = "screenshots"
os.makedirs(screenshot_dir, exist_ok=True)

# FPS cap
fps_cap = 10

# Precompute gradient colors for performance
def precompute_gradient():
    gradient = np.zeros((256, 3), dtype=np.uint8) # Create an array to hold RGB values for each index
    for i in range(256):
        value = i / 255.0 # Normalize the index to [0, 1]
        if value < 0.3:  # Water
            gradient[i] = (0, 0, int(255 * value * 3))  # Blue gradient
        elif value < 0.6:  # Land
            gradient[i] = (0, int(255 * (value - 0.3) * 3), 0)  # Green gradient
        else:  # Mountains
            r = int(255 * (value - 0.6) * 3) # Red gradient for mountains
            g = int(255 * (value - 0.6) * 3) # Green gradient for mountains (less intense)
            b = int(255 * value) # Blue gradient for mountains (less intense)
            gradient[i] = (min(255, r), min(255, g), min(255, b))  # Clamp values to 255
    return gradient # Returns a 256x3 array with RGB values for each index

gradient_cache = precompute_gradient()

def generate_noise_map(pan_x, pan_y, zoom_level, screen_width, screen_height, scale, octaves, persistence, lacunarity):
   # Generates a seamless noise map for the visible area
    visible_width = int(screen_width / zoom_level)  # Calculate the width of the visible area based on zoom level
    visible_height = int(screen_height / zoom_level) # Calculate the height of the visible area based on zoom level
    noise_map = np.zeros((visible_height, visible_width)) # Initialize a 2D array to hold noise values for the visible area

    for y in range(visible_height):
        for x in range(visible_width): # Iterate over each pixel in the visible area
            nx = (pan_x + x) / scale # Normalize x coordinate based on scale
            ny = (pan_y + y) / scale # Normalize y coordinate based on scale
            noise_value = noise.pnoise2(
                nx, ny, # Normalized coordinates for noise generation
                octaves=octaves, # Number of octaves to combine
                persistence=persistence, # Amplitude of each octave
                lacunarity=lacunarity, # Frequency of each octave
                repeatx=2048,  # Large repeat values for seamless infinite generation
                repeaty=2048,  # Large repeat values for seamless infinite generation
                base=84    # 42 Base for consistent noise generation
            )
            noise_map[y][x] = noise_value # Store the generated noise value in the map

    return normalize_noise(noise_map) # Normalize the noise map to the range [0, 1] for consistent color mapping

def normalize_noise(noise_map):
    """Normalize noise values to the range [0, 1]."""
    min_val = np.min(noise_map) # Find the minimum value in the noise map
    max_val = np.max(noise_map) # Find the maximum value in the noise map
    return (noise_map - min_val) / (max_val - min_val) # Normalize to [0, 1]

def apply_gradient_color_optimized(noise_map, gradient_cache):
    """Apply precomputed gradient colors to the noise map."""
    indices = (noise_map * 255).astype(np.uint8) # Scale noise values to [0, 255] and convert to uint8
    return gradient_cache[indices] # Use the indices to map to the precomputed gradient

def draw_noise(screen, pan_x, pan_y, zoom_level):
    """Render the seamless noise map."""
    noise_map = generate_noise_map(pan_x, pan_y, zoom_level, screen_width, screen_height, scale, octaves, persistence, lacunarity) # Generate the noise map for the current view
    color_map = apply_gradient_color_optimized(noise_map, gradient_cache) # Apply the precomputed gradient colors to the noise map
    surface = pygame.surfarray.make_surface(color_map) # Create a Pygame surface from the color map
    surface = pygame.transform.scale(surface, (screen_width, screen_height)) # Scale the surface to fit the screen
    screen.blit(surface, (0, 0)) # Blit the scaled surface to the screen

def display_parameters(screen, scale, octaves, persistence, lacunarity, zoom_level):
    """Display noise parameters on the screen."""
    params_text = f"Scale: {scale}, Octaves: {octaves}, Persistence: {persistence}, Lacunarity: {lacunarity}, Zoom: {zoom_level:.2f}"
    font.render_to(screen, (16, 16), params_text, white)  # 10 , 10 not 16, 16 for better visibility

def save_screenshot(screen):
    """Save a screenshot of the current view."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S") # Create a timestamp for the screenshot filename
    filename = os.path.join(screenshot_dir, f"landscape_{timestamp}.png")  # Create a filename with timestamp
    pygame.image.save(screen, filename) # Save the screenshot to the specified directory

def display_fps(screen, clock):
    """Display the current FPS on the screen."""
    fps_text = f"FPS: {int(clock.get_fps())}" # Get the current FPS  currently BROKEN
    font.render_to(screen, (10, 40), fps_text, white) # 10, 40 for better visibility currently BROKEN

def main(): # Main function to run the noise landscape generator
    global pan_x, pan_y, scale, octaves, persistence, lacunarity, zoom_level, paused # Use global variables to maintain state across functions
    global pan_speed, fps_cap # Use global variables for panning speed and FPS cap
    running = True # Flag to control the main loop
    paused = False # Initially not paused
    clock = pygame.time.Clock() # Initialize the clock for FPS control

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    pan_x -= pan_speed
                elif event.key == pygame.K_RIGHT:
                    pan_x += pan_speed
                elif event.key == pygame.K_UP:
                    pan_y -= pan_speed
                elif event.key == pygame.K_DOWN:
                    pan_y += pan_speed
                elif event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:
                    zoom_level = min(4.0, zoom_level + 0.1)
                elif event.key == pygame.K_MINUS:
                    zoom_level = max(0.5, zoom_level - 0.1)
                elif event.key == pygame.K_s:
                    save_screenshot(screen)
                elif event.key == pygame.K_r:
                    pan_x, pan_y = 0, 0
                    zoom_level = 1.0
                elif event.key == pygame.K_p:
                    paused = not paused

        screen.fill(black) # Clear the screen with black color
        if not paused:
            draw_noise(screen, pan_x, pan_y, zoom_level) # Draw the noise landscape
        display_parameters(screen, scale, octaves, persistence, lacunarity, zoom_level) # Display the noise parameters
        display_fps(screen, clock) # Display the current FPS
        if paused:
            font.render_to(screen, (screen_width // 2 - 50, screen_height // 2), "PAUSED", white)

        pygame.display.flip()
        clock.tick(fps_cap)

    pygame.quit()

if __name__ == "__main__":
    main()