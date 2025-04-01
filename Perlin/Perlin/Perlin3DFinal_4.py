import numpy as np
from noise import pnoise3
import random
from math import sqrt
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go

# Parameters
width, height, depth = 64, 128, 64  # Reduced dimensions for better performance
scale = 15
octaves = 12
persistence = 1
lacunarity = 2

# Generate 3D Perlin noise
def generate_noise_volume(width, height, depth, scale, octaves, persistence, lacunarity):
    """Generate a 3D Perlin noise volume."""
    noise_volume = np.zeros((width, height, depth))
    for x in range(width):
        for y in range(height):
            for z in range(depth):
                noise_volume[x][y][z] = pnoise3(
                    x / scale, y / scale, z / scale,
                    octaves=octaves, persistence=persistence,
                    lacunarity=lacunarity, base=42
                )
    return noise_volume

# Map space density
def map_space_density(noise_volume, threshold=0.2):
    """Map space density based on Perlin noise."""
    space_map = np.zeros_like(noise_volume, dtype=int)
    space_map[noise_volume > threshold] = 1  # Stars
    space_map[(noise_volume > threshold / 2) & (noise_volume <= threshold)] = 2  # Gas clouds
    space_map[noise_volume < -threshold] = 3  # Black holes
    space_map[(noise_volume >= -threshold / 2) & (noise_volume <= threshold / 2)] = 0  # Voids
    return space_map

# Simulate the evolution of the space quadrant
def simulate_space_evolution(space_map, steps=1):
    """Simulate the evolution of the space quadrant over time."""
    for step in range(steps):
        star_positions = np.argwhere(space_map == 1)
        for pos in star_positions:
            x, y, z = pos
            dx, dy, dz = random.randint(-1, 1), random.randint(-1, 1), random.randint(-1, 1)
            new_x, new_y, new_z = (x + dx) % width, (y + dy) % height, (z + dz) % depth
            space_map[x, y, z] = 0  # Clear old position
            space_map[new_x, new_y, new_z] = 1  # Move to new position
    return space_map

# Create initial data
noise_volume = generate_noise_volume(width, height, depth, scale, octaves, persistence, lacunarity)
space_map = map_space_density(noise_volume)

# Dash App
app = dash.Dash(__name__)
app.title = "Interactive Space Quadrant"
app.layout = html.Div([
    html.H1("Interactive Space Quadrant", style={"textAlign": "center"}),
    dcc.Graph(id="3d-visualization"),
    html.Div([
        html.Label("View Mode:"),
        dcc.RadioItems(
            id="view-mode",
            options=[
                {"label": "Full 3D View", "value": "full"},
                {"label": "Slice View", "value": "slice"}
            ],
            value="full",
            inline=True
        ),
        html.Label("Slice Axis (only for Slice View):"),
        dcc.RadioItems(
            id="slice-axis",
            options=[
                {"label": "X-Axis", "value": "x"},
                {"label": "Y-Axis", "value": "y"},
                {"label": "Z-Axis", "value": "z"}
            ],
            value="z",
            inline=True
        ),
        html.Label("Slice Position (only for Slice View):"),
        dcc.Slider(id="slice-slider", min=0, max=depth - 1, step=1, value=depth // 2),
    ], style={"margin": "20px"}),
    html.Button("Simulate Steps", id="simulate-button", n_clicks=0),
    html.Div(id="step-output", style={"marginTop": "20px", "textAlign": "center"})
])

# Update 3D Visualization
@app.callback(
    Output("3d-visualization", "figure"),
    [Input("view-mode", "value"), Input("slice-axis", "value"), Input("slice-slider", "value"), Input("simulate-button", "n_clicks")]
)
def update_visualization(view_mode, axis, slice_position, n_clicks):
    global space_map
    if n_clicks > 0:
        space_map = simulate_space_evolution(space_map, steps=1)

    fig = go.Figure()

    if view_mode == "full":
        # Full 3D view
        for obj_type, color, size in [(1, "yellow", 2), (2, "blue", 2), (3, "black", 4)]:
            positions = np.argwhere(space_map == obj_type)
            if positions.size > 0:
                fig.add_trace(go.Scatter3d(
                    x=positions[:, 0], y=positions[:, 1], z=positions[:, 2],
                    mode="markers",
                    marker=dict(size=size, color=color),
                    name=f"Type {obj_type}"
                ))
    else:
        # Slice view
        if axis == "x":
            slice_data = space_map[slice_position, :, :]
            for obj_type, color, size in [(1, "yellow", 2), (2, "blue", 2), (3, "black", 4)]:
                positions = np.argwhere(slice_data == obj_type)
                if positions.size > 0:
                    fig.add_trace(go.Scatter3d(
                        x=np.full(positions.shape[0], slice_position),  # X is constant
                        y=positions[:, 0],  # Y comes from the row index
                        z=positions[:, 1],  # Z comes from the column index
                        mode="markers",
                        marker=dict(size=size, color=color),
                        name=f"Type {obj_type}"
                    ))
        elif axis == "y":
            slice_data = space_map[:, slice_position, :]
            for obj_type, color, size in [(1, "yellow", 2), (2, "blue", 2), (3, "black", 4)]:
                positions = np.argwhere(slice_data == obj_type)
                if positions.size > 0:
                    fig.add_trace(go.Scatter3d(
                        x=positions[:, 0],  # X comes from the row index
                        y=np.full(positions.shape[0], slice_position),  # Y is constant
                        z=positions[:, 1],  # Z comes from the column index
                        mode="markers",
                        marker=dict(size=size, color=color),
                        name=f"Type {obj_type}"
                    ))
        else:  # axis == "z"
            slice_data = space_map[:, :, slice_position]
            for obj_type, color, size in [(1, "yellow", 2), (2, "blue", 2), (3, "black", 4)]:
                positions = np.argwhere(slice_data == obj_type)
                if positions.size > 0:
                    fig.add_trace(go.Scatter3d(
                        x=positions[:, 0],  # X comes from the row index
                        y=positions[:, 1],  # Y comes from the column index
                        z=np.full(positions.shape[0], slice_position),  # Z is constant
                        mode="markers",
                        marker=dict(size=size, color=color),
                        name=f"Type {obj_type}"
                    ))

    fig.update_layout(
        title="Interactive 3D Visualization of Space Quadrant",
        scene=dict(
            xaxis_title="X",
            yaxis_title="Y",
            zaxis_title="Z",
            bgcolor="#2E2E2E"
        ),
        showlegend=True
    )
    return fig

# Update Step Output
@app.callback(
    Output("step-output", "children"),
    [Input("simulate-button", "n_clicks")]
)
def update_step_output(n_clicks):
    return f"Simulated {n_clicks} step(s)."

# Run the app
if __name__ == "__main__":
    app.run(debug=True)