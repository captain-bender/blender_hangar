import bpy

offset_x = -61.5  
offset_y = -13.6 
offset_z = 0.0 

# Create a new camera
def create_camera(name, location, rotation):
    camera_data = bpy.data.cameras.new(name=name)
    camera_object = bpy.data.objects.new(name, camera_data)
    bpy.context.scene.collection.objects.link(camera_object)
    camera_object.location = (
        location[0] + offset_x,
        location[1] + offset_y,
        location[2] + offset_z,
    )
    camera_object.rotation_euler = rotation
    return camera_object

# Set render settings
def set_render_settings(resolution_x, resolution_y, file_format, output_path):
    scene = bpy.context.scene
    scene.render.resolution_x = resolution_x
    scene.render.resolution_y = resolution_y
    scene.render.image_settings.file_format = file_format
    scene.render.filepath = output_path

# Main execution
if __name__ == "__main__":
    # Create and position the camera
    camera = create_camera("Camera_1", (17.6, 2, 18), (0, 0, 1.5708))
    
    # Set it as the active camera
    bpy.context.scene.camera = camera
    
    # Use Eevee for faster rendering
    bpy.context.scene.render.engine = 'BLENDER_EEVEE_NEXT'
    
    # Configure render settings
    set_render_settings(1920, 1080, 'PNG', 'C:/Users/Bende/Documents/render.png')
    
    # Render the image
    bpy.ops.render.render(write_still=True)

    print("Rendering complete!")