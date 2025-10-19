import bpy
import bmesh
import math

"""
Step-by-Step Coordinate System Setup
1. Move world origin to (0, 0, 0)
2. Create camera at world origin
3. Create L-marker at frame top-left corner
4. Place rover relative to L-marker (local origin)
"""

# L-Marker Dimensions
L_LINE_LENGTH = 1.0
L_LINE_WIDTH = 0.05

# Camera specifications
sensor_width_mm = 11.25
sensor_height_mm = 7.03
focal_length_mm = 18
camera_height = 10.0  # Camera position: 10m above world origin

def setup_world_origin():
    """Move world origin empty to (0, 0, 0)"""
    try:
        world = bpy.data.objects["world"]
        world.location = (0, 0, 0)
        print(f"✓ World origin at: {world.location}")
        return world
    except KeyError:
        print("✗ World origin not found!")
        return None

def create_camera_at_world():
    """Create camera at world origin looking down"""
    # Delete existing cameras first (optional)
    for obj in bpy.data.objects:
        if obj.type == 'CAMERA' and "test_camera" in obj.name.lower():
            bpy.data.objects.remove(obj, do_unlink=True)
    
    camera_data = bpy.data.cameras.new("test_camera")
    camera_obj = bpy.data.objects.new("test_camera", camera_data)
    bpy.context.scene.collection.objects.link(camera_obj)
    
    # Position camera above world origin, looking down
    camera_obj.location = (0, 0, camera_height)
    camera_obj.rotation_euler = (math.radians(90), 0, 0)  # Looking down
    
    # Camera properties
    camera_data.lens = focal_length_mm
    camera_data.sensor_width = sensor_width_mm
    camera_data.sensor_height = sensor_height_mm
    camera_data.clip_start = 0.1
    camera_data.clip_end = 1000
    
    bpy.context.scene.camera = camera_obj
    
    print(f"✓ Camera created at: {camera_obj.location}")
    print(f"  Rotation (Euler): {camera_obj.rotation_euler}")
    print(f"  Looking at: (0, 0, 0)")
    
    return camera_obj

def create_l_marker_at_frame_corner():
    """Create L-marker at frame top-left corner (0, 0) of the rendered frame"""
    # Delete existing if present
    if "frame_calibration_L" in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects["frame_calibration_L"], do_unlink=True)
    
    mesh = bpy.data.meshes.new("frame_L_mesh")
    obj = bpy.data.objects.new("frame_calibration_L", mesh)
    bpy.context.scene.collection.objects.link(obj)
    
    # Create bmesh for L-shape
    bm = bmesh.new()
    
    # Vertical line of L
    v0 = bm.verts.new((0, 0, 0))
    v1 = bm.verts.new((L_LINE_WIDTH, 0, 0))
    v2 = bm.verts.new((L_LINE_WIDTH, -L_LINE_LENGTH, 0))
    v3 = bm.verts.new((0, -L_LINE_LENGTH, 0))
    
    # Horizontal line of L
    v4 = bm.verts.new((0, -L_LINE_LENGTH, 0))
    v5 = bm.verts.new((L_LINE_LENGTH, -L_LINE_LENGTH, 0))
    v6 = bm.verts.new((L_LINE_LENGTH, -L_LINE_LENGTH - L_LINE_WIDTH, 0))
    v7 = bm.verts.new((0, -L_LINE_LENGTH - L_LINE_WIDTH, 0))
    
    bm.faces.new([v0, v1, v2, v3])
    bm.faces.new([v4, v5, v6, v7])
    
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    
    # Add red material
    mat = bpy.data.materials.new("L_marker_material")
    mat.diffuse_color = (1.0, 0.0, 0.0, 1.0)  # Red
    obj.data.materials.append(mat)
    
    # Position at frame origin (you'll adjust this after seeing the render)
    obj.location = (0, 0, 0)
    
    print(f"✓ L-marker created at: {obj.location}")
    print(f"  This should appear at frame top-left corner")
    
    return obj

def create_local_origin_at_l_marker():
    """Create local origin empty at L-marker position"""
    if "local" in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects["local"], do_unlink=True)
    
    local = bpy.data.objects.new("local", None)
    bpy.context.scene.collection.objects.link(local)
    
    # Position same as L-marker
    local.location = (0, 0, 0)
    local.empty_display_size = 0.2
    local.empty_display_type = 'PLAIN_AXES'
    
    print(f"✓ Local origin created at: {local.location}")
    
    return local

def place_rover_at_local_origin():
    """Place rover at local origin"""
    try:
        rover = bpy.data.objects["rover"]
        rover.location = (0, 0, 0)
        rover.rotation_euler = (0, 0, 0)
        rover.hide_render = False
        
        print(f"✓ Rover placed at local origin: {rover.location}")
        
        return rover
    except KeyError:
        print("✗ Rover not found!")
        return None

# Main execution
if __name__ == "__main__":
    print("\n" + "="*60)
    print("STEP-BY-STEP COORDINATE SYSTEM SETUP")
    print("="*60 + "\n")
    
    print("STEP 1: Setting up world origin at (0, 0, 0)")
    print("-"*60)
    world = setup_world_origin()
    
    print("\nSTEP 2: Creating camera at world origin, looking down")
    print("-"*60)
    camera = create_camera_at_world()
    
    print("\nSTEP 3: Creating L-marker at frame top-left corner")
    print("-"*60)
    l_marker = create_l_marker_at_frame_corner()
    
    print("\nSTEP 4: Creating local origin at L-marker")
    print("-"*60)
    local = create_local_origin_at_l_marker()
    
    print("\nSTEP 5: Placing rover at local origin")
    print("-"*60)
    rover = place_rover_at_local_origin()
    
    print("\n" + "="*60)
    print("SETUP COMPLETE!")
    print("="*60)
    print("\nNow:")
    print("1. Press Numpad 0 to view through camera")
    print("2. Verify you can see:")
    print("   - The red L-marker at top-left of frame")
    print("   - The rover near the L-marker")
    print("3. If L-marker is not visible in frame, adjust its position")
    print("4. Report back with observations!")
    print("\n")