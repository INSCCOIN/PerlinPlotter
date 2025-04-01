import numpy as np
from noise import pnoise3
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
from mpl_toolkits.mplot3d import Axes3D

# Parameters
width, height, depth = 128, 128, 128  # Dimensions of the 3D noise volume
scale = 20  # Scale for noise generation, adjust for more/less detail
octaves = 6  # Number of octaves to combine
persistence = 0.5  # Amplitude of each octave
lacunarity = 2.0  # Frequency of each octave

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
def render_slice(slice_index, axis="z"):
    """Render a 2D slice of the 3D noise volume."""
    plt.clf()
    if axis == "z":
        slice_data = noise_volume[:, :, slice_index]
        plt.title(f"Slice of 3D Perlin Noise (Z={slice_index})")
    elif axis == "y":
        slice_data = noise_volume[:, slice_index, :]
        plt.title(f"Slice of 3D Perlin Noise (Y={slice_index})")
    elif axis == "x":
        slice_data = noise_volume[slice_index, :, :]
        plt.title(f"Slice of 3D Perlin Noise (X={slice_index})")
    plt.imshow(slice_data, cmap="gray", origin="lower")
    plt.colorbar()
    plt.draw()

# Function to render the entire 3D noise volume
def render_3d():
    """Render the entire 3D noise volume as a scatter plot."""
    plt.clf()
    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")
    ax.set_title("3D Perlin Noise Volume")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")

    # Normalize the noise volume for visualization
    normalized_volume = (noise_volume - np.min(noise_volume)) / (np.max(noise_volume) - np.min(noise_volume))
    x, y, z = np.indices(noise_volume.shape)
    x, y, z = x.flatten(), y.flatten(), z.flatten()
    values = normalized_volume.flatten()

    # Use a threshold to reduce the number of points plotted
    threshold = 0.5
    mask = values > threshold
    ax.scatter(x[mask], y[mask], z[mask], c=values[mask], cmap="viridis", s=1, alpha=0.5)
    plt.show()

# Interactive visualization
def interactive_visualization():
    """Create an interactive visualization with slicing and 3D rendering."""
    fig, ax = plt.subplots()
    plt.subplots_adjust(bottom=0.25)

    # Initial slice
    initial_slice = depth // 2
    render_slice(initial_slice, axis="z")

    # Slider for slice position
    ax_slider = plt.axes([0.2, 0.1, 0.65, 0.03], facecolor="lightgoldenrodyellow")
    slider = Slider(ax_slider, "Slice", 0, depth - 1, valinit=initial_slice, valstep=1)

    # Button for 3D rendering
    ax_button = plt.axes([0.8, 0.025, 0.1, 0.04])
    button = Button(ax_button, "3D View")

    # Update function for the slider
    def update(val):
        slice_index = int(slider.val)
        render_slice(slice_index, axis="z")

    slider.on_changed(update)

    # Callback for the 3D view button
    def view_3d(event):
        render_3d()

    button.on_clicked(view_3d)

    plt.show()

# Run the interactive visualization
interactive_visualization()