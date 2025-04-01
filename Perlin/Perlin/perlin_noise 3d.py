from panda3d.core import Point3, Vec3, TextNode, NodePath
from panda3d. import ShowBase
from panda3d.core import AmbientLight, DirectionalLight
from noise import pnoise3
import random
import math

class SpaceExplorationGame(ShowBase):
    def __init__(self):
        super().__init__()

        # Set up the environment
        self.disableMouse()  # Disable default mouse camera control
        self.camera.setPos(0, -50, 10)  # Set initial camera position
        self.camera.lookAt(0, 0, 0)

        # Player attributes
        self.player = self.loader.loadModel("models/smiley")  # Use a built-in model for the player
        self.player.setScale(1)
        self.player.setPos(0, 0, 0)
        self.player.reparentTo(self.render)

        # Lighting
        ambient_light = AmbientLight("ambient_light")
        ambient_light.setColor((0.5, 0.5, 0.5, 1))
        self.render.setLight(self.render.attachNewNode(ambient_light))

        directional_light = DirectionalLight("directional_light")
        directional_light.setDirection(Vec3(-1, -1, -1))
        directional_light.setColor((0.8, 0.8, 0.8, 1))
        self.render.setLight(self.render.attachNewNode(directional_light))

        # Quadrant tracking
        self.current_quadrant = (0, 0, 0)
        self.generated_quadrants = {}  # Store generated quadrants
        self.space_objects = []  # Store all space objects

        # Generate the initial quadrant
        self.generate_quadrant(self.current_quadrant)

        # Key controls
        self.accept("w", self.move_player, [Vec3(0, 1, 0)])  # Move forward
        self.accept("s", self.move_player, [Vec3(0, -1, 0)])  # Move backward
        self.accept("a", self.move_player, [Vec3(-1, 0, 0)])  # Move left
        self.accept("d", self.move_player, [Vec3(1, 0, 0)])  # Move right
        self.accept("arrow_up", self.move_player, [Vec3(0, 0, 1)])  # Move up
        self.accept("arrow_down", self.move_player, [Vec3(0, 0, -1)])  # Move down

        # HUD (Heads-Up Display)
        self.score = 0
        self.hud = self.create_hud()

    def create_hud(self):
        """Create a HUD to display the player's score and position."""
        hud = TextNode("hud")
        hud.setText(f"Score: {self.score} | Position: {self.player.getPos()}")
        hud.setAlign(TextNode.ALeft)
        hud_node = self.aspect2d.attachNewNode(hud)
        hud_node.setScale(0.05)
        hud_node.setPos(-1.3, 0, 0.9)  # Top-left corner
        return hud

    def update_hud(self):
        """Update the HUD with the latest score and position."""
        self.hud.node().setText(f"Score: {self.score} | Position: {self.player.getPos()}")

    def calculate_density(self, quadrant):
        """Calculate the density of objects based on the player's distance from the quadrant."""
        distance = math.sqrt(
            (quadrant[0] - self.current_quadrant[0]) ** 2 +
            (quadrant[1] - self.current_quadrant[1]) ** 2 +
            (quadrant[2] - self.current_quadrant[2]) ** 2
        )
        max_density = 0.1  # Maximum density for nearby quadrants
        min_density = 0.02  # Minimum density for distant quadrants
        density = max(min_density, max_density / (1 + distance))  # Inverse distance scaling
        return density

    def generate_quadrant(self, quadrant):
        """Generate stars, gas clouds, and black holes in the specified quadrant."""
        if quadrant in self.generated_quadrants:
            return  # Quadrant already generated

        print(f"Generating quadrant: {quadrant}")

        # Create a parent node for the quadrant
        quadrant_node = NodePath(f"quadrant_{quadrant}")
        quadrant_node.reparentTo(self.render)

        self.generated_quadrants[quadrant] = quadrant_node  # Store the quadrant node

        base_x, base_y, base_z = quadrant[0] * 50, quadrant[1] * 50, quadrant[2] * 50
        scale = 10
        density = self.calculate_density(quadrant)  # Dynamic density based on distance

        for x in range(-10, 10):
            for y in range(-10, 10):
                for z in range(-10, 10):
                    value = pnoise3((base_x + x) / scale, (base_y + y) / scale, (base_z + z) / scale, octaves=3, persistence=0.5, lacunarity=2.0)
                    if random.random() < density:
                        if value > 0.2:
                            obj = self.loader.loadModel("models/sphere")  # Star
                            obj.setColor(1, 1, 0, 1)  # Yellow
                        elif value > 0.0:
                            obj = self.loader.loadModel("models/box")  # Gas cloud
                            obj.setColor(0, 0, 1, 1)  # Blue
                        elif value < -0.2:
                            obj = self.loader.loadModel("models/sphere")  # Black hole
                            obj.setColor(0, 0, 0, 1)  # Black
                            obj.setScale(1.5)
                        else:
                            continue
                        obj.setScale(0.5)
                        obj.setPos(base_x + x * 5, base_y + y * 5, base_z + z * 5)
                        obj.reparentTo(quadrant_node)  # Attach to the quadrant node
                        self.space_objects.append(obj)

        # Batch render the quadrant
        quadrant_node.flattenStrong()

    def move_player(self, direction):
        """Move the player in the specified direction."""
        self.player.setPos(self.player.getPos() + direction)

        # Check for interactions with objects
        for obj in self.space_objects:
            if (self.player.getPos() - obj.getPos()).length() < 1.5:  # Collision detection
                if obj.getColor() == (1, 1, 0, 1):  # Star
                    print("Collected a star!")
                    self.score += 10
                    obj.removeNode()  # Remove the star
                elif obj.getColor() == (0, 0, 1, 1):  # Gas cloud
                    print("Entered a gas cloud! Slowing down...")
                elif obj.getColor() == (0, 0, 0, 1):  # Black hole
                    print("Pulled by a black hole!")
                    pull_direction = (obj.getPos() - self.player.getPos()).normalized()
                    self.player.setPos(self.player.getPos() + pull_direction * 0.5)  # Gradual pull

        # Update the HUD
        self.update_hud()

        # Check if the player has moved to a new quadrant
        new_quadrant = (
            int(self.player.getX() // 50),
            int(self.player.getY() // 50),
            int(self.player.getZ() // 50),
        )
        if new_quadrant != self.current_quadrant:
            self.current_quadrant = new_quadrant
            self.generate_quadrant(new_quadrant)
            self.remove_distant_quadrants()  # Remove distant quadrants

# Run the game
game = SpaceExplorationGame()
game.run()