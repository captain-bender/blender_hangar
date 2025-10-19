import bpy
import bmesh
import math
from mathutils import Vector

"""
Frame Origin Setup Script for YOLO Calibration
Creates:
- "world" origin (renamed from CustomOrigin)
- "rover" origin (already exists, just rename)
- "local" origin (at frame top-left corner)
- L-shaped calibration marker at frame top-left corner
"""

# L-Marker Dimensions (in world units - meters)
L_LINE_LENGTH = 1.0      # Length of each L arm
L_LINE_WIDTH = 0.05      # Thickness/width of the line
L_LINE_HEIGHT = 0.02     # Height/depth of the line (visual thickness)

# Fixed local origin position (your manually found position)
LOCAL_ORIGIN_POSITION = (-43.869, -13.619, 0.0)

# Camera parameters (from your render setup)
sensor_width_mm = 11.25
sensor_height_mm = 7.03
focal_length_mm = 18

def rename_origin(old_name, new_name):
    """Rename an existing origin object"""
    try:
        obj = bpy.data.objects[old_name]
        obj.name = new_name
        print(f"Renamed '{old_name}' to '{new_name}'")
        return obj
    except KeyError:
        print(f"Warning: '{old_name}' not found")
        return None

def create_empty_origin(name, location=(0, 0, 0)):
    """Create an empty object to use as an origin reference"""
    empty = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(empty)
    empty.location = location
    empty.empty_display_size = 0.2
    empty.empty_display_type = 'PLAIN_AXES'
    print(f"Created empty origin: {name} at {location}")
    return empty

def create_l_marker(name, location=(0, 0, 0)):
    """
    Create an L-shaped calibration marker at the specified location.
    The L marks the top-left corner (0,0) of the frame in pixel space.
    """
    # Create mesh and object
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.location = location
    
    # Create bmesh
    bm = bmesh.new()
    
    # Vertical line of the L (going down from top-left)
    v0 = bm.verts.new((0, 0, 0))
    v1 = bm.verts.new((L_LINE_WIDTH, 0, 0))
    v2 = bm.verts.new((L_LINE_WIDTH, -L_LINE_LENGTH, 0))
    v3 = bm.verts.new((0, -L_LINE_LENGTH, 0))
    
    # Horizontal line of the L (going right from bottom of vertical)
    v4 = bm.verts.new((0, -L_LINE_LENGTH, 0))
    v5 = bm.verts.new((L_LINE_LENGTH, -L_LINE_LENGTH, 0))
    v6 = bm.verts.new((L_LINE_LENGTH, -L_LINE_LENGTH - L_LINE_WIDTH, 0))
    v7 = bm.verts.new((0, -L_LINE_LENGTH - L_LINE_WIDTH, 0))
    
    # Create faces for vertical part
    bm.faces.new([v0, v1, v2, v3])
    
    # Create faces for horizontal part
    bm.faces.new([v4, v5, v6, v7])
    
    # Update mesh
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    
    # Add material to make it visible
    mat = bpy.data.materials.new(name=f"{name}_Material")
    mat.diffuse_color = (1.0, 0.0, 0.0, 1.0)  # Red color
    obj.data.materials.append(mat)
    
    print(f"Created L-marker: {name} at {location}")
    return obj

def calculate_frame_corner_offset(camera_obj, distance_from_camera=0.1):
    """
    Calculate the world position of the top-left corner of the camera frame.
    This is where the 'local' origin and L-marker should be placed.
    
    Args:
        camera_obj: The camera object
        distance_from_camera: How far in front of camera to place the marker (in world units)
    
    Returns:
        tuple: (x, y, z) position of the top-left frame corner
    """
    # Camera properties
    sensor_width = sensor_width_mm / 1000  # Convert to meters
    sensor_height = sensor_height_mm / 1000
    focal_length = focal_length_mm / 1000
    
    # Calculate FOV
    fov_x = 2 * math.atan(sensor_width / (2 * focal_length))
    fov_y = 2 * math.atan(sensor_height / (2 * focal_length))
    
    # Half-dimensions at the distance plane
    half_width = distance_from_camera * math.tan(fov_x / 2)
    half_height = distance_from_camera * math.tan(fov_y / 2)
    
    # Top-left corner offset (in camera space: left = -X, up = +Y, forward = -Z)
    left_offset = camera_obj.matrix_world @ Vector((-half_width, half_height, -distance_from_camera))
    
    return tuple(left_offset)

# Main execution
if __name__ == "__main__":
    print("=== Frame Origin Setup ===\n")
    
    # Step 1: Rename existing origins
    print("Step 1: Renaming origins...")
    world_origin = rename_origin("world", "world")
    rover_origin = rename_origin("rover", "rover")  # Already named, but confirms it exists
    
    if world_origin is None:
        print("ERROR: CustomOrigin not found. Please ensure it exists before running this script.")
    else:
        world_loc = world_origin.location
        print(f"World origin location: {world_loc}\n")
        
        # Step 2: Get the active camera
        print("Step 2: Setting up local frame origin...")
        active_camera = bpy.context.scene.camera
        
        if active_camera is None:
            print("ERROR: No active camera in scene. Please set a camera first.")
        else:
            # Use the manually verified position
            frame_corner_loc = LOCAL_ORIGIN_POSITION
            print(f"Frame corner (top-left, 0,0) location: {frame_corner_loc}\n")
            
            # Step 3: Create local origin empty
            print("Step 3: Creating 'local' origin empty...")
            local_origin = create_empty_origin("local", frame_corner_loc)
            
            # Step 4: Create L-shaped marker at local origin
            print("Step 4: Creating L-shaped calibration marker...")
            l_marker = create_l_marker("frame_calibration_L", frame_corner_loc)
            
            # Optional: Parent L-marker to local origin for easy management
            l_marker.parent = local_origin
            l_marker.matrix_parent_inverse = local_origin.matrix_world.inverted()
            
            print("\n=== Setup Complete ===")
            print(f"Origins created:")
            print(f"  - 'world' at {world_loc}")
            print(f"  - 'rover' (already exists)")
            print(f"  - 'local' at {frame_corner_loc}")
            print(f"\nL-Marker dimensions:")
            print(f"  - Line length: {L_LINE_LENGTH}m")
            print(f"  - Line width: {L_LINE_WIDTH}m")
            print(f"  - Line height: {L_LINE_HEIGHT}m")
            print(f"\nNext steps:")
            print(f"  1. Verify the red L-marker appears at top-left of your camera view")
            print(f"  2. Adjust L_LINE_LENGTH/WIDTH if marker is too small/large in frame")
            print(f"  3. Update your render script to use these origins")