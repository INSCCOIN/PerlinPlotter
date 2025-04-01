import numpy as np
from noise import pnoise3
from scipy.spatial.distance import cdist
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go

# Parameters
width, height, depth = 64, 128, 64
scale = 15
octaves = 12
persistence = 1
lacunarity = 2

# Generate 3D Perlin noise using vectorized operations
def generate_noise_volume(width, height, depth, scale, octaves, persistence, lacunarity):
    """Generate a 3D Perlin noise volume using vectorized operations."""
    x, y, z = np.meshgrid(
        np.arange(width) / scale,
        np.arange(height) / scale,
        np.arange(depth) / scale,
        indexing="ij"
    )
    noise_volume = np.vectorize(lambda x, y, z: pnoise3(
        x, y, z, octaves=octaves, persistence=persistence, lacunarity=lacunarity, base=42
    ))(x, y, z)
    return noise_volume

# Map space density using a sigmoid function
def map_space_density(noise_volume, threshold=0.2):
    """Map space density using a sigmoid function for smoother classification."""
    sigmoid = lambda x: 1 / (1 + np.exp(-10 * (x - threshold)))
    space_map = np.zeros_like(noise_volume, dtype=int)
    space_map[sigmoid(noise_volume) > 0.8] = 1  # Stars
    space_map[(sigmoid(noise_volume) > 0.5) & (sigmoid(noise_volume) <= 0.8)] = 2  # Gas clouds
    space_map[sigmoid(noise_volume) < 0.2] = 3  # Black holes
    return space_map

# Simulate gravitational pull using inverse-square law
def simulate_gravitational_pull(space_map, steps=1):
    """Simulate gravitational pull using inverse-square law."""
    for step in range(steps):
        star_positions = np.argwhere(space_map == 1)
        gas_positions = np.argwhere(space_map == 2)
        black_hole_positions = np.argwhere(space_map == 3)

        if black_hole_positions.size == 0:
            break  # No black holes to pull objects toward

        # Calculate gravitational pull for stars and gas clouds
        for positions, obj_type in [(star_positions, 1), (gas_positions, 2)]:
            if positions.size == 0:
                continue
            distances = cdist(positions, black_hole_positions)
            nearest_bh_indices = np.argmin(distances, axis=1)
            nearest_bh_positions = black_hole_positions[nearest_bh_indices]

            for i, pos in enumerate(positions):
                x, y, z = pos
                bh_x, bh_y, bh_z = nearest_bh_positions[i]
                dx, dy, dz = bh_x - x, bh_y - y, bh_z - z
                distance = np.sqrt(dx**2 + dy**2 + dz**2)
                if distance > 0:
                    # Apply inverse-square law
                    force = 1 / (distance**2)
                    move = np.round(force * np.array([dx, dy, dz]) / distance).astype(int)
                    new_x, new_y, new_z = (x + move[0]) % width, (y + move[1]) % height, (z + move[2]) % depth
                    space_map[x, y, z] = 0  # Clear old position
                    space_map[new_x, new_y, new_z] = obj_type  # Move to new position
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

@app.callback(
    Output("3d-visualization", "figure"),
    [Input("view-mode", "value"), Input("slice-axis", "value"), Input("slice-slider", "value"), Input("simulate-button", "n_clicks")]
)
def update_visualization(view_mode, axis, slice_position, n_clicks):
    global space_map
    if n_clicks > 0:
        space_map = simulate_gravitational_pull(space_map, steps=1)

    fig = go.Figure()

    object_types = {
        1: ("Stars", "yellow", 2),
        2: ("Gas Clouds", "blue", 2),
        3: ("Black Holes", "black", 4),
    }

    if view_mode == "full":
        # Full 3D view
        for obj_type, (name, color, size) in object_types.items():
            positions = np.argwhere(space_map == obj_type)
            if positions.size > 0:
                fig.add_trace(go.Scatter3d(
                    x=positions[:, 0], y=positions[:, 1], z=positions[:, 2],
                    mode="markers",
                    marker=dict(size=size, color=color),
                    name=name
                ))
    else:
        # Slice view
        if axis == "x":
            slice_data = space_map[slice_position, :, :]
        elif axis == "y":
            slice_data = space_map[:, slice_position, :]
        else:  # axis == "z"
            slice_data = space_map[:, :, slice_position]

        for obj_type, (name, color, size) in object_types.items():
            positions = np.argwhere(slice_data == obj_type)
            if positions.size > 0:
                fig.add_trace(go.Scatter3d(
                    x=positions[:, 0] if axis != "x" else np.full(positions.shape[0], slice_position),
                    y=positions[:, 1] if axis != "y" else np.full(positions.shape[0], slice_position),
                    z=positions[:, 2] if axis != "z" else np.full(positions.shape[0], slice_position),
                    mode="markers",
                    marker=dict(size=size, color=color),
                    name=name
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

@app.callback(
    Output("step-output", "children"),
    [Input("simulate-button", "n_clicks")]
)
def update_step_output(n_clicks):
    return f"Simulated {n_clicks} step(s)."

# Run the app
if __name__ == "__main__":
    app.run(debug=True)