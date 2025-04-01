import numpy as np
from noise import pnoise3
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons
import matplotlib.animation as animation

# Parameters
width, height, depth = 128, 512, 256  # Dimensions of the 3D noise volume
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

# Function to render a 2D slice of the 3D noise
def render_slice(ax, slice_index, axis="z", colorbar=None):
    """Render a 2D slice of the 3D noise volume."""
    ax.clear()
    if axis == "z":
        slice_data = noise_volume[:, :, slice_index]
        ax.set_title(f"Slice of 3D Perlin Noise (Z={slice_index})")
    elif axis == "y":
        slice_data = noise_volume[:, slice_index, :]
        ax.set_title(f"Slice of 3D Perlin Noise (Y={slice_index})")
    elif axis == "x":
        slice_data = noise_volume[slice_index, :, :]
        ax.set_title(f"Slice of 3D Perlin Noise (X={slice_index})")
    im = ax.imshow(slice_data, cmap="gray", origin="lower")
    
    # Update or create the colorbar
    if colorbar is not None:
        colorbar.update_normal(im)
    else:
        colorbar = plt.colorbar(im, ax=ax, orientation="vertical")
    plt.draw()
    return colorbar

# Function to generate a binary voxel world
def generate_voxel_world(threshold=0.0):
    """Generate a binary voxel world based on a threshold."""
    return (noise_volume > threshold).astype(int)

# Function to apply biome-based coloring
def apply_biome_color(noise_volume):
    """Apply biome-based coloring to the noise volume."""
    width, height, depth = noise_volume.shape  # Correctly unpack dimensions
    color_volume = np.zeros((width, height, depth, 3), dtype=np.uint8)

    for x in range(width):
        for y in range(height):
            for z in range(depth):
                value = noise_volume[x, y, z]
                if value < -0.2:  # Water
                    color_volume[x, y, z] = (0, 0, 255)  # Blue
                elif value < 0.2:  # Grass
                    color_volume[x, y, z] = (34, 139, 34)  # Green
                else:  # Mountains
                    color_volume[x, y, z] = (139, 137, 137)  # Gray
    return color_volume

# Function to animate slices through the noise volume
def animate_slices(axis="z"):
    """Create an animation cycling through slices of the 3D noise volume."""
    fig, ax = plt.subplots()

    def update(frame):
        ax.clear()
        if axis == "z":
            slice_data = noise_volume[:, :, frame]
            ax.set_title(f"Slice {frame} (Z-axis)")
        elif axis == "y":
            slice_data = noise_volume[:, frame, :]
            ax.set_title(f"Slice {frame} (Y-axis)")
        elif axis == "x":
            slice_data = noise_volume[frame, :, :]
            ax.set_title(f"Slice {frame} (X-axis)")
        ax.imshow(slice_data, cmap="gray", origin="lower")

    ani = animation.FuncAnimation(fig, update, frames=depth if axis == "z" else (height if axis == "y" else width), interval=100)
    plt.show()

# Interactive visualization
def interactive_visualization():
    """Create an interactive visualization with slicing, voxel world, and biome coloring."""
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

    # Button for voxel world visualization
    ax_button_voxel = plt.axes([0.05, 0.025, 0.15, 0.04])
    button_voxel = Button(ax_button_voxel, "Voxel World")

    # Button for biome coloring
    ax_button_biome = plt.axes([0.25, 0.025, 0.15, 0.04])
    button_biome = Button(ax_button_biome, "Biome Colors")

    # Button for animation
    ax_button_animate = plt.axes([0.45, 0.025, 0.15, 0.04])
    button_animate = Button(ax_button_animate, "Animate")

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

    # Callback for the voxel world button
    def view_voxel(event):
        voxel_world = generate_voxel_world(threshold=0.0)
        ax.clear()
        ax.imshow(voxel_world[:, :, depth // 2], cmap="gray", origin="lower")
        ax.set_title("Voxel World Slice")
        plt.draw()

    button_voxel.on_clicked(view_voxel)

    # Callback for the biome coloring button
    def view_biome(event):
        biome_volume = apply_biome_color(noise_volume)
        ax.clear()
        ax.imshow(biome_volume[:, :, depth // 2])
        ax.set_title("Biome-Based Coloring")
        plt.draw()

    button_biome.on_clicked(view_biome)

    # Callback for the animation button
    def start_animation(event):
        animate_slices(axis=current_axis)

    button_animate.on_clicked(start_animation)

    plt.show()

# Run the interactive visualization
interactive_visualization()