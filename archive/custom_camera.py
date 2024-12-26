import bpy

# Camera specifications
sensor_width_mm = 36  # Example: Width of the camera sensor in mm
sensor_height_mm = 24  # Example: Height of the camera sensor in mm
resolution_width_px = 6000  # Width in pixels
resolution_height_px = 4000  # Height in pixels
pixel_size_um = 4.2  # Pixel size in micrometers
focal_length_mm = 50  # Focal length in mm

# Convert pixel size to mm
pixel_size_mm = pixel_size_um / 1000

# Create a new camera
camera_data = bpy.data.cameras.new(name="MyCamera")
camera_object = bpy.data.objects.new("MyCamera", camera_data)

# Set camera properties
camera_data.type = 'PERSP'  # Perspective camera
camera_data.lens = focal_length_mm  # Focal length in mm
camera_data.sensor_width = sensor_width_mm  # Sensor width
camera_data.sensor_height = sensor_height_mm  # Sensor height
camera_data.clip_start = 0.1  # Near clipping plane
camera_data.clip_end = 1000  # Far clipping plane

# Add the camera to the scene
bpy.context.scene.collection.objects.link(camera_object)

# Set render resolution
scene = bpy.context.scene
scene.render.resolution_x = resolution_width_px
scene.render.resolution_y = resolution_height_px
scene.render.pixel_aspect_x = 1
scene.render.pixel_aspect_y = 1

# Set the camera as the active camera
scene.camera = camera_object

# Position the camera (optional, modify as needed)
camera_object.location = (0, -10, 5)  # Example position
camera_object.rotation_euler = (1.2, 0, 0)  # Example rotation
