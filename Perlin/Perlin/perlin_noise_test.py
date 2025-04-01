import numpy as np
from noise import pnoise3


# Parameters
width, height, depth = 128, 512, 256 # Dimensions of the 3D noise volume
scale = 15 # Scale for noise generation, adjust for more/less detail
octaves = 12 # Number of octaves to combine
persistence = 1 # Amplitude of each octave
lacunarity = 2 # Frequency of each octave

# Generate 3D Perlin noise
noise_volume = np.zeros((width, height, depth))
for x in range(width):
    for y in range(height):
        for z in range(depth):
            noise_volume[x][y][z] = pnoise3(x / scale, y / scale, z / scale, octaves=octaves, persistence=persistence, lacunarity=lacunarity, base=42) # Base for consistent noise generation

# Example usage: Slicing the 3D noise to visualize one layer
import matplotlib.pyplot as plt
plt.imshow(noise_volume[:, :, int(depth / 2)], cmap="gray") # Take a slice at the middle of the depth
plt.title("Slice of 3D Perlin Noise")
plt.colorbar()
plt.show()
