import os
import trimesh

tools_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(tools_dir)
v12_dir = os.path.join(root_dir, "Hybrid_Grenade_v1.2")

rod_glb = os.path.join(v12_dir, "04_Rod_Assembly_And_Locks", "Custom_Rod_Assembly.glb")
barrel_glb = os.path.join(v12_dir, "03_Internal_Barrel_And_Upper_Station", "Custom_Internal_Barrel_And_Upper_Station_Assembly.glb")

print("--- Rod GLB Nodes & Meshes ---")
rod_scene = trimesh.load(rod_glb)
for k, g in rod_scene.geometry.items():
    print(f"Rod Geom: {k}, vertices: {len(g.vertices)}, faces: {len(g.faces)}")

print("\n--- Barrel GLB Nodes & Meshes ---")
barrel_scene = trimesh.load(barrel_glb)
for k, g in barrel_scene.geometry.items():
    print(f"Barrel Geom: {k}, vertices: {len(g.vertices)}, faces: {len(g.faces)}")

