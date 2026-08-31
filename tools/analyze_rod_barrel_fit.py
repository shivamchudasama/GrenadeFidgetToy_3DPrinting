import os
import numpy as np
import trimesh

tools_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(tools_dir)
v12_dir = os.path.join(root_dir, "Hybrid_Grenade_v1.2")

rod_glb_path = os.path.join(v12_dir, "04_Rod_Assembly_And_Locks", "Custom_Rod_Assembly.glb")
barrel_glb_path = os.path.join(v12_dir, "03_Internal_Barrel_And_Upper_Station", "Custom_Internal_Barrel_And_Upper_Station_Assembly.glb")

print("--- Loading GLBs ---")
rod_scene = trimesh.load(rod_glb_path)
barrel_scene = trimesh.load(barrel_glb_path)

print("\n[ROD SCENE]")
if isinstance(rod_scene, trimesh.Scene):
    for name, geom in rod_scene.geometry.items():
        print(f"  Geom: {name}, vertices: {len(geom.vertices)}, bounds: {geom.bounds.tolist()}")
    print("  Overall Scene Bounds:", rod_scene.bounds.tolist())
    print("  Overall Scene Extents:", rod_scene.extents.tolist())
else:
    print("  Rod bounds:", rod_scene.bounds.tolist())

print("\n[BARREL SCENE]")
if isinstance(barrel_scene, trimesh.Scene):
    for name, geom in barrel_scene.geometry.items():
        print(f"  Geom: {name}, vertices: {len(geom.vertices)}, bounds: {geom.bounds.tolist()}")
    print("  Overall Scene Bounds:", barrel_scene.bounds.tolist())
    print("  Overall Scene Extents:", barrel_scene.extents.tolist())
else:
    print("  Barrel bounds:", barrel_scene.bounds.tolist())
