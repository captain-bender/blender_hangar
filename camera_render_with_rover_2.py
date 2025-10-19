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

# Object names
LOCAL_ORIGIN_NAME = "local"  # Frame top-left corner (manually positioned)
L_MARKER_NAME = "frame_calibration_L"  # L-shape marker (do not move)
rover_name = "rover"

# Define rover positions relative to LOCAL frame origin
# These are frame coordinates where (0, 0) = top-left corner where L-marker is
rover_positions = [
    {
        "id": "at_frame_origin",
        "location": (0, 0, 0.9),           # At L-marker (top-left corner)
        "rotation": (0, 0, 0)
    },
    {
        "id": "frame_right",
        "location": (1.0, 0, 0),         # 1m to the right
        "rotation": (0, 0, 0)
    },
    {
        "id": "frame_down",
        "location": (0, 1.0, 0),         # 1m down
        "rotation": (0, 0, 0)
    },
    {
        "id": "frame_diagonal",
        "location": (0.5, 0.5, 0),       # Center area
        "rotation": (0, 0, math.radians(45))
    }
]

def debug_print(message):
    """Print with clear formatting"""
    print(f"[DEBUG] {message}")

def verify_and_lock_objects():
    """Verify local origin and L-marker exist and report their positions"""
    try:
        local = bpy.data.objects[LOCAL_ORIGIN_NAME]
        l_marker = bpy.data.objects[L_MARKER_NAME]
        
        debug_print(f"✓ Local origin '{LOCAL_ORIGIN_NAME}' at: {local.location}")
        debug_print(f"✓ L-marker '{L_MARKER_NAME}' at: {l_marker.location}")
        debug_print(f"✓ These objects will NOT be moved during rendering")
        
        return local, l_marker
    except KeyError as e:
        debug_print(f"✗ ERROR: Missing object: {e}")
        return None, None

def verify_rover_exists():
    """Check if rover exists"""
    try:
        rover = bpy.data.objects[rover_name]
        debug_print(f"✓ Rover '{rover_name}' found")
        return rover
    except KeyError:
        debug_print(f"✗ ERROR: Rover '{rover_name}' NOT FOUND")
        debug_print(f"  Available objects: {[obj.name for obj in bpy.data.objects if obj.type not in ['CAMERA']]}")
        return None

def create_or_update_camera(name, location, rotation):
    """Create or update camera at specified location and rotation"""
    # Delete if exists
    if name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)
    
    camera_data = bpy.data.cameras.new(name=name)
    camera_obj = bpy.data.objects.new(name, camera_data)
    bpy.context.scene.collection.objects.link(camera_obj)
    
    # Set camera properties
    camera_data.type = 'PERSP'
    camera_data.lens = focal_length_mm
    camera_data.sensor_width = sensor_width_mm
    camera_data.sensor_height = sensor_height_mm
    camera_data.clip_start = 0.1
    camera_data.clip_end = 1000
    
    camera_obj.location = location
    camera_obj.rotation_euler = rotation
    
    debug_print(f"✓ Camera '{name}' created at {camera_obj.location}")
    
    return camera_obj

def move_rover_in_frame(rover_obj, location_in_frame, rotation, local_origin_loc):
    """
    Move rover relative to LOCAL (frame) origin
    location_in_frame: (x, y, z) relative to frame top-left corner (local origin)
    """
    if rover_obj is None:
        debug_print(f"✗ ERROR: Rover object is None!")
        return False
    
    try:
        # Convert frame coordinates to world coordinates
        world_location = (
            location_in_frame[0] + local_origin_loc[0],
            location_in_frame[1] + local_origin_loc[1],
            location_in_frame[2] + local_origin_loc[2],
        )
        
        rover_obj.location = world_location
        rover_obj.rotation_euler = rotation
        rover_obj.hide_render = False
        rover_obj.hide_viewport = False
        
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
    print("\n" + "="*70)
    print("RENDER SCRIPT - FIXED LOCAL FRAME COORDINATES")
    print("Local origin and L-marker will NOT be moved")
    print("="*70 + "\n")
    
    # Step 1: Verify fixed objects
    print("STEP 1: Verifying fixed objects...")
    print("-"*70)
    
    local_obj, l_marker_obj = verify_and_lock_objects()
    rover_obj = verify_rover_exists()
    
    if local_obj is None or rover_obj is None:
        print("\n✗ STOP: Required objects missing")
        print("="*70 + "\n")
        exit()
    
    # Get local origin position (will remain fixed)
    local_origin_position = local_obj.location
    
    # Step 2: Load cameras
    print("\nSTEP 2: Loading camera configuration...")
    print("-"*70)
    
    yaml_path = "C:/Users/Bende/Documents/blender_hangar/cameras_case_D.yaml"
    cameras = load_cameras_from_yaml(yaml_path)
    
    if cameras is None:
        print("\n✗ STOP: Could not load cameras from YAML")
        print("="*70 + "\n")
        exit()
    
    # Step 3: Configure render engine
    print("\nSTEP 3: Configuring render settings...")
    print("-"*70)
    
    bpy.context.scene.render.engine = 'BLENDER_EEVEE_NEXT'
    debug_print(f"✓ Render engine set to BLENDER_EEVEE_NEXT")
    
    # Step 4: Main render loop
    print("\nSTEP 4: Starting render loop...")
    print("="*70 + "\n")
    
    render_count = 0
    
    for cam in cameras['cameras']:
        cam_id = cam['id']
        location = cam['location']
        rotation = cam['rotation']
        
        # Create camera
        camera_name = f"Camera_{cam_id}"
        camera = create_or_update_camera(camera_name, location, rotation)
        bpy.context.scene.camera = camera
        
        # Loop through rover positions in frame coordinates
        for rover_pos in rover_positions:
            rover_id = rover_pos['id']
            rover_location_in_frame = rover_pos['location']
            rover_rotation = rover_pos['rotation']
            
            print(f"\n--- Render {render_count + 1}: Camera {cam_id} + Rover {rover_id} ---")
            debug_print(f"Rover frame coords: {rover_location_in_frame}")
            
            # Move rover relative to LOCAL frame origin
            if not move_rover_in_frame(rover_obj, rover_location_in_frame, rover_rotation, local_origin_position):
                debug_print("✗ Skipping this render")
                continue
            
            # Configure render output
            output_path = f"C:/Users/Bende/Documents/blender_hangar/case_D/render_{cam_id}_{rover_id}.png"
            set_render_settings(resolution_width_px, resolution_height_px, output_path)
            
            # Render
            debug_print(f"Rendering...")
            try:
                bpy.ops.render.render(write_still=True)
                debug_print(f"✓ Saved to {output_path}")
                render_count += 1
            except Exception as e:
                debug_print(f"✗ Render failed: {e}")
    
    print("\n" + "="*70)
    print(f"RENDERING COMPLETE: {render_count} images rendered")
    print(f"Local origin position (FIXED): {local_origin_position}")
    print(f"Output directory: C:/Users/Bende/Documents/blender_hangar/case_D/")
    print("="*70 + "\n")