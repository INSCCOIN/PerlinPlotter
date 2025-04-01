import numpy as np
from noise import pnoise3
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons
from mpl_toolkits.mplot3d import Axes3D

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

# Function to render the entire 3D noise volume
def render_3d():
    """Render the entire 3D noise volume as a scatter plot."""
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

    # Button for 3D rendering
    ax_button_3d = plt.axes([0.8, 0.025, 0.1, 0.04])
    button_3d = Button(ax_button_3d, "3D View")

    # Button for resetting the view
    ax_button_reset = plt.axes([0.6, 0.025, 0.1, 0.04])
    button_reset = Button(ax_button_reset, "Reset View")

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

    # Callback for the 3D view button
    def view_3d(event):
        render_3d()

    button_3d.on_clicked(view_3d)

    # Callback for the reset button
    def reset_view(event):
        nonlocal current_axis, colorbar
        current_axis = "z"
        slider.valmax = depth - 1
        slider.ax.set_xlim(slider.valmin, slider.valmax)
        slider.set_val(depth // 2)
        radio.set_active(2)  # Set to "z" axis
        colorbar = render_slice(ax, depth // 2, axis=current_axis, colorbar=colorbar)

    button_reset.on_clicked(reset_view)

    plt.show()

# Run the interactive visualization
interactive_visualization()