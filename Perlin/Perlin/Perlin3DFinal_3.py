import numpy as np
from noise import pnoise3
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons
import matplotlib.animation as animation

# Parameters
width, height, depth = 128, 512, 256  # Dimensions of the 3D space quadrant
scale = 15  # Scale for noise generation, adjust for more/less detail
octaves = 12  # Number of octaves to combine
persistence = 1  # Amplitude of each octave
lacunarity = 2  # Frequency of each octave

# Generate 3D Perlin noise
noise_volume = np.zeros((width, height, depth))
for x in range(width):
    for y in range(height):
        for z in range(depth):
            noise_volume[x][y][z] = pnoise3(
                x / scale, y / scale, z / scale,
                octaves=octaves, persistence=persistence,
                lacunarity=lacunarity, base=42
            )

# Function to map space density
def map_space_density(noise_volume, threshold=0.2):
    """Map space density based on Perlin noise."""
    width, height, depth = noise_volume.shape
    space_map = np.zeros((width, height, depth), dtype=int)

    for x in range(width):
        for y in range(height):
            for z in range(depth):
                value = noise_volume[x, y, z]
                if value > threshold:  # High-density regions
                    space_map[x, y, z] = 1  # Represent stars or dense regions
                elif value > threshold / 2:  # Medium-density regions
                    space_map[x, y, z] = 2  # Represent gas clouds
                else:  # Low-density regions
                    space_map[x, y, z] = 0  # Empty space
    return space_map

# Function to render a 2D slice of the 3D noise or space map
def render_slice(ax, slice_index, axis="z", colorbar=None):
    """Render a 2D slice of the 3D noise or space map."""
    ax.clear()
    if axis == "z":
        slice_data = noise_volume[:, :, slice_index]
        ax.set_title(f"Slice of Space Quadrant (Z={slice_index})")
    elif axis == "y":
        slice_data = noise_volume[:, slice_index, :]
        ax.set_title(f"Slice of Space Quadrant (Y={slice_index})")
    elif axis == "x":
        slice_data = noise_volume[slice_index, :, :]
        ax.set_title(f"Slice of Space Quadrant (X={slice_index})")
    im = ax.imshow(slice_data, cmap="viridis", origin="lower")
    
    # Update or create the colorbar
    if colorbar is not None:
        colorbar.update_normal(im)
    else:
        colorbar = plt.colorbar(im, ax=ax, orientation="vertical")
    plt.draw()
    return colorbar

# Function to simulate star formation
def simulate_star_formation(space_map, star_threshold=0.8):
    """Simulate star formation in high-density regions."""
    width, height, depth = space_map.shape
    stars = []

    for x in range(width):
        for y in range(height):
            for z in range(depth):
                if space_map[x, y, z] == 1 and np.random.random() > star_threshold:
                    stars.append((x, y, z))  # Add a star at this position
    return stars

# Function to simulate black holes
def simulate_black_holes(space_map, black_hole_threshold=0.95):
    """Simulate black holes in extremely high-density regions."""
    width, height, depth = space_map.shape
    black_holes = []

    for x in range(width):
        for y in range(height):
            for z in range(depth):
                if space_map[x, y, z] == 1 and np.random.random() > black_hole_threshold:
                    black_holes.append((x, y, z))  # Add a black hole at this position
    return black_holes

# Function to simulate galaxy distributions
def simulate_galaxies(space_map, galaxy_threshold=0.7):
    """Simulate galaxy distributions in medium-density regions."""
    width, height, depth = space_map.shape
    galaxies = []

    for x in range(width):
        for y in range(height):
            for z in range(depth):
                if space_map[x, y, z] == 2 and np.random.random() > galaxy_threshold:
                    galaxies.append((x, y, z))  # Add a galaxy at this position
    return galaxies

# Function to visualize celestial objects
def visualize_celestial_objects(stars, black_holes, galaxies):
    """Visualize stars, black holes, and galaxies in 3D."""
    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")

    # Plot stars
    if stars:
        stars = np.array(stars)
        ax.scatter(stars[:, 0], stars[:, 1], stars[:, 2], c="yellow", label="Stars", s=1)

    # Plot black holes
    if black_holes:
        black_holes = np.array(black_holes)
        ax.scatter(black_holes[:, 0], black_holes[:, 1], black_holes[:, 2], c="black", label="Black Holes", s=10)

    # Plot galaxies
    if galaxies:
        galaxies = np.array(galaxies)
        ax.scatter(galaxies[:, 0], galaxies[:, 1], galaxies[:, 2], c="blue", label="Galaxies", s=5)

    ax.set_title("Celestial Objects in Space Quadrant")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.legend()
    plt.show()

# Interactive visualization
def interactive_visualization():
    """Create an interactive visualization for mapping space quadrants."""
    fig, ax = plt.subplots()
    plt.subplots_adjust(left=0.25, bottom=0.35)  # Adjust layout to fit widgets

    # Initial slice
    initial_slice = depth // 2
    current_axis = "z"
    colorbar = render_slice(ax, initial_slice, axis=current_axis)

    # Slider for slice position
    ax_slider = plt.axes([0.25, 0.2, 0.65, 0.03], facecolor="lightgoldenrodyellow")
    slider = Slider(ax_slider, "Slice", 0, depth - 1, valinit=initial_slice, valstep=1)

    # Radio buttons for axis selection
    ax_radio = plt.axes([0.05, 0.4, 0.15, 0.15], facecolor="lightgoldenrodyellow")
    radio = RadioButtons(ax_radio, ("x", "y", "z"), active=2)

    # Button for celestial object simulation
    ax_button_simulate = plt.axes([0.05, 0.025, 0.15, 0.04])
    button_simulate = Button(ax_button_simulate, "Simulate Objects")

    # Update function for the slider
    def update(val):
        slice_index = int(slider.val)
        nonlocal colorbar
        colorbar = render_slice(ax, slice_index, axis=current_axis, colorbar=colorbar)

    slider.on_changed(update)

    # Callback for the radio buttons
    def change_axis(label):
        nonlocal current_axis, colorbar
        current_axis = label

        # Update slider range based on the selected axis
        if current_axis == "x":
            slider.valmax = width - 1
        elif current_axis == "y":
            slider.valmax = height - 1
        elif current_axis == "z":
            slider.valmax = depth - 1
        slider.ax.set_xlim(slider.valmin, slider.valmax)
        slider.set_val(slider.valmin)  # Reset slider to the minimum value
        colorbar = render_slice(ax, int(slider.val), axis=current_axis, colorbar=colorbar)

    radio.on_clicked(change_axis)

    # Callback for the celestial object simulation button
    def simulate_objects(event):
        space_map = map_space_density(noise_volume)
        stars = simulate_star_formation(space_map)
        black_holes = simulate_black_holes(space_map)
        galaxies = simulate_galaxies(space_map)
        visualize_celestial_objects(stars, black_holes, galaxies)

    button_simulate.on_clicked(simulate_objects)

    plt.show()

# Run the interactive visualization
interactive_visualization()