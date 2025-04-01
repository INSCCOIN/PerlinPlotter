import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons
from mpl_toolkits.mplot3d import Axes3D

# Parameters
width, height, depth = 128, 512, 256  # Dimensions of the 3D space quadrant

# Load real astronomical data (e.g., HYG Database for stars)
def load_real_data(filepath):
    """Load real astronomical data from a CSV file."""
    data = pd.read_csv(filepath)
    return data

def load_galaxy_data(filepath):
    """Load galaxy data from a CSV file."""
    data = pd.read_csv(filepath)
    return data

def load_solar_system_data(filepath):
    """Load solar system data (e.g., exoplanets) from a CSV file."""
    data = pd.read_csv(filepath)
    return data


# Map real astronomical data to a 3D space
def map_real_data_to_space(data, width, height, depth):
    """Map real astronomical data to a 3D space."""
    space_map = np.zeros((width, height, depth), dtype=int)

    for _, row in data.iterrows():
        # Adjust coordinates to fit within the 3D space dimensions
        x = int((row['x'] - data['x'].min()) / (data['x'].max() - data['x'].min()) * (width - 1))
        y = int((row['y'] - data['y'].min()) / (data['y'].max() - data['y'].min()) * (height - 1))
        z = int((row['z'] - data['z'].min()) / (data['z'].max() - data['z'].min()) * (depth - 1))
        if 0 <= x < width and 0 <= y < height and 0 <= z < depth:
            space_map[x, y, z] = 1  # Mark as a star or celestial object
    return space_map

# Function to render a 2D slice of the 3D space map
def render_slice(ax, slice_index, axis="z", colorbar=None):
    """Render a 2D slice of the 3D space map."""
    ax.clear()
    if axis == "z":
        slice_data = space_map[:, :, slice_index]
        ax.set_title(f"Slice of Space Quadrant (Z={slice_index})")
    elif axis == "y":
        slice_data = space_map[:, slice_index, :]
        ax.set_title(f"Slice of Space Quadrant (Y={slice_index})")
    elif axis == "x":
        slice_data = space_map[slice_index, :, :]
        ax.set_title(f"Slice of Space Quadrant (X={slice_index})")
    im = ax.imshow(slice_data, cmap="viridis", origin="lower")
    
    # Update or create the colorbar
    if colorbar is not None:
        colorbar.update_normal(im)
    else:
        colorbar = plt.colorbar(im, ax=ax, orientation="vertical")
    plt.draw()
    return colorbar

# Function to visualize celestial objects
def visualize_celestial_objects(data):
    """Visualize stars in 3D."""
    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")

    # Plot stars
    ax.scatter(data['x'], data['y'], data['z'], c="yellow", label="Stars", s=1)

    ax.set_title("Real Astronomical Data")
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

    # Button for celestial object visualization
    ax_button_visualize = plt.axes([0.05, 0.025, 0.15, 0.04])
    button_visualize = Button(ax_button_visualize, "Visualize Objects")

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

    # Callback for the celestial object visualization button
    def visualize_objects(event):
        visualize_celestial_objects(real_data)

    button_visualize.on_clicked(visualize_objects)

    plt.show()

# Load real data and map it to the 3D space
real_data = load_real_data("hygdata_v41.csv.gz")  # Replace with the actual path to your dataset
space_map = map_real_data_to_space(real_data, width, height, depth)

# Run the interactive visualization
interactive_visualization()