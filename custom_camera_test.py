import bpy

offset_x = -61.5  
offset_y = -13.6 
offset_z = 0.0 

# Camera specifications
sensor_width_mm = 36  # Example: Width of the camera sensor in mm
sensor_height_mm = 24  # Example: Height of the camera sensor in mm
resolution_width_px = 6000  # Width in pixels
resolution_height_px = 4000  # Height in pixels
pixel_size_um = 4.2  # Pixel size in micrometers
focal_length_mm = 50  # Focal length in mm

# Create a new camera
def create_camera(name, location, rotation):
    camera_data = bpy.data.cameras.new(name=name)
    camera_object = bpy.data.objects.new(name, camera_data)

    # Set camera properties
    camera_data.type = 'PERSP'  # Perspective camera
    camera_data.lens = focal_length_mm  # Focal length in mm
    camera_data.sensor_width = sensor_width_mm  # Sensor width
    camera_data.sensor_height = sensor_height_mm  # Sensor height
    camera_data.clip_start = 0.1  # Near clipping plane
    camera_data.clip_end = 1000  # Far clipping plane

    bpy.context.scene.collection.objects.link(camera_object)
    camera_object.location = (
        location[0] + offset_x,
        location[1] + offset_y,
        location[2] + offset_z,
    )
    camera_object.rotation_euler = rotation
    return camera_object

# Set render settings
def set_render_settings(resolution_x, resolution_y, output_path):
    scene = bpy.context.scene
    scene.render.resolution_x = resolution_x
    scene.render.resolution_y = resolution_y
    scene.render.pixel_aspect_x = 1
    scene.render.pixel_aspect_y = 1
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = output_path

# Main execution
if __name__ == "__main__":
    print('Create and position the camera')
    camera = create_camera("Camera_1", (17.6, 2, 18), (0, 0, 1.5708))
    
    # Set it as the active camera
    bpy.context.scene.camera = camera
    
    # Use Eevee for faster rendering
    bpy.context.scene.render.engine = 'BLENDER_EEVEE_NEXT'
    
    # Configure render settings
    set_render_settings(resolution_width_px, resolution_height_px, 'C:/Users/Bende/Documents/render.png')
    
    print("Rendering started!")

    # Render the image
    bpy.ops.render.render(write_still=True)

    print("Rendering completd!")