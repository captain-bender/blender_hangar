import bpy
import yaml
import math

# Camera specifications
sensor_width_mm = 11.25
sensor_height_mm = 7.03
resolution_width_px = 1920
resolution_height_px = 1200
pixel_size_um = 5.86
focal_length_mm = 18

# Origin names
WORLD_ORIGIN_NAME = "world"
ROVER_ORIGIN_NAME = "rover"
LOCAL_ORIGIN_NAME = "local"

# Rover specifications
rover_name = "rover"  # UPDATE THIS if your rover has a different name

# Define rover positions and orientations (relative to LOCAL origin for YOLO)
rover_positions = [
    {
        "id": "pos_1",
        "location": (0, 0, 0),
        "rotation": (0, 0, 0)
    },
    {
        "id": "pos_2",
        "location": (10, 5, 0),
        "rotation": (0, 0, math.radians(45))
    },
    {
        "id": "pos_3",
        "location": (15, -10, 0),
        "rotation": (0, 0, math.radians(180))
    }
]

def debug_print(message):
    """Print with clear formatting"""
    print(f"[DEBUG] {message}")

def verify_object_exists(obj_name):
    """Check if object exists and print status"""
    try:
        obj = bpy.data.objects[obj_name]
        debug_print(f"✓ Object '{obj_name}' found")
        debug_print(f"  Location: {obj.location}")
        debug_print(f"  Hidden in viewport: {obj.hide_viewport}")
        debug_print(f"  Hidden in render: {obj.hide_render}")
        return obj
    except KeyError:
        debug_print(f"✗ ERROR: Object '{obj_name}' NOT FOUND in scene!")
        debug_print(f"  Available objects: {[obj.name for obj in bpy.data.objects]}")
        return None

def get_origin(origin_name):
    """Get the location of an origin object"""
    try:
        origin_obj = bpy.data.objects[origin_name]
        debug_print(f"✓ Origin '{origin_name}' found at {origin_obj.location}")
        return origin_obj.location
    except KeyError:
        debug_print(f"✗ Warning: Origin '{origin_name}' not found. Using (0,0,0)")
        return (0, 0, 0)

def create_camera(name, location, rotation, origin_location=(0, 0, 0)):
    """Create camera positioned relative to an origin"""
    camera_data = bpy.data.cameras.new(name=name)
    camera_object = bpy.data.objects.new(name, camera_data)

    # Set camera properties
    camera_data.type = 'PERSP'
    camera_data.lens = focal_length_mm
    camera_data.sensor_width = sensor_width_mm
    camera_data.sensor_height = sensor_height_mm
    camera_data.clip_start = 0.1
    camera_data.clip_end = 1000

    bpy.context.scene.collection.objects.link(camera_object)
    camera_object.location = (
        location[0] + origin_location[0],
        location[1] + origin_location[1],
        location[2] + origin_location[2],
    )
    camera_object.rotation_euler = rotation
    
    debug_print(f"✓ Created camera '{name}'")
    debug_print(f"  World location: {camera_object.location}")
    debug_print(f"  Clip start: {camera_data.clip_start}, Clip end: {camera_data.clip_end}")
    
    return camera_object

def move_rover(rover_obj, location, rotation, origin_location=(0, 0, 0)):
    """Move rover to specified location and rotation relative to an origin"""
    if rover_obj is None:
        debug_print(f"✗ ERROR: Rover object is None!")
        return False
    
    try:
        rover_obj.location = (
            location[0] + origin_location[0],
            location[1] + origin_location[1],
            location[2] + origin_location[2],
        )
        rover_obj.rotation_euler = rotation
        
        # Make sure rover is visible for rendering
        rover_obj.hide_render = False
        rover_obj.hide_viewport = False
        
        debug_print(f"✓ Rover moved to world position {rover_obj.location}")
        debug_print(f"  Rotation: {rotation}")
        debug_print(f"  Hidden in render: {rover_obj.hide_render}")
        
        return True
    except Exception as e:
        debug_print(f"✗ ERROR moving rover: {e}")
        return False

def set_render_settings(resolution_x, resolution_y, output_path):
    """Configure render output settings"""
    scene = bpy.context.scene
    scene.render.resolution_x = resolution_x
    scene.render.resolution_y = resolution_y
    scene.render.pixel_aspect_x = 1
    scene.render.pixel_aspect_y = 1
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = output_path
    
    debug_print(f"✓ Render settings configured")
    debug_print(f"  Resolution: {resolution_x}x{resolution_y}")
    debug_print(f"  Output: {output_path}")

def load_cameras_from_yaml(filepath):
    """Load camera configuration from YAML"""
    try:
        with open(filepath, 'r') as file:
            data = yaml.safe_load(file)
        debug_print(f"✓ Loaded {len(data['cameras'])} cameras from YAML")
        return data
    except FileNotFoundError:
        debug_print(f"✗ ERROR: YAML file not found at {filepath}")
        return None
    except Exception as e:
        debug_print(f"✗ ERROR loading YAML: {e}")
        return None

# Main execution
if __name__ == "__main__":
    print("\n" + "="*60)
    print("RENDER SCRIPT WITH FRAME ORIGINS - DEBUG MODE")
    print("="*60 + "\n")
    
    # Step 1: Verify all objects exist
    print("STEP 1: Verifying objects...")
    print("-" * 60)
    
    verify_object_exists(WORLD_ORIGIN_NAME)
    verify_object_exists(LOCAL_ORIGIN_NAME)
    verify_object_exists("frame_calibration_L")
    rover_obj = verify_object_exists(rover_name)
    
    if rover_obj is None:
        print("\n✗ STOP: Rover not found! Update 'rover_name' variable to match your rover's name")
        print("="*60 + "\n")
        exit()
    
    # Step 2: Load cameras
    print("\nSTEP 2: Loading camera configuration...")
    print("-" * 60)
    
    yaml_path = "C:/Users/Bende/Documents/blender_hangar/cameras_locations/cameras_case_D.yaml"
    cameras = load_cameras_from_yaml(yaml_path)
    
    if cameras is None:
        print("\n✗ STOP: Could not load cameras from YAML")
        print("="*60 + "\n")
        exit()
    
    # Step 3: Get origins
    print("\nSTEP 3: Getting origin positions...")
    print("-" * 60)
    
    world_origin = get_origin(WORLD_ORIGIN_NAME)
    local_origin = get_origin(LOCAL_ORIGIN_NAME)
    
    # Step 4: Configure render engine
    print("\nSTEP 4: Configuring render settings...")
    print("-" * 60)
    
    bpy.context.scene.render.engine = 'BLENDER_EEVEE_NEXT'
    debug_print(f"✓ Render engine set to BLENDER_EEVEE_NEXT")
    
    # Step 5: Main render loop
    print("\nSTEP 5: Starting render loop...")
    print("="*60 + "\n")
    
    render_count = 0
    
    for cam in cameras['cameras']:
        cam_id = cam['id']
        location = cam['location']
        rotation = cam['rotation']
    
        # Create camera
        camera_name = f"Camera_{cam_id}"
        camera = create_camera(camera_name, location, rotation, world_origin)
        bpy.context.scene.camera = camera
        
        # Loop through rover positions
        for rover_pos in rover_positions:
            rover_id = rover_pos['id']
            rover_location = rover_pos['location']
            rover_rotation = rover_pos['rotation']
            
            print(f"\n--- Rendering {render_count + 1}: Camera {cam_id} + Rover {rover_id} ---")
            
            # Move rover
            if not move_rover(rover_obj, rover_location, rover_rotation, local_origin):
                debug_print("✗ Skipping this render due to rover positioning error")
                continue
            
            # Configure render output
            output_path = f"C:/Users/Bende/Documents/blender_hangar/renderings/render_{cam_id}_{rover_id}.png"
            set_render_settings(resolution_width_px, resolution_height_px, output_path)
            
            # Render
            debug_print(f"Starting render...")
            try:
                bpy.ops.render.render(write_still=True)
                debug_print(f"✓ Render completed successfully!")
                render_count += 1
            except Exception as e:
                debug_print(f"✗ Render failed: {e}")
    
    print("\n" + "="*60)
    print(f"ALL RENDERS COMPLETED: {render_count} images rendered")
    print("="*60 + "\n")