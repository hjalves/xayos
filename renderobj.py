import sys
import tkinter as tk
import numpy as np


def generate_sphere(radius, segments, rings):
    """Generate vertices and edges for a sphere."""
    vertices = []
    edges = []

    # Generate vertices
    for i in range(rings + 1):
        theta = np.pi * i / rings
        for j in range(segments):
            phi = 2 * np.pi * j / segments
            x = radius * np.sin(theta) * np.cos(phi)
            y = radius * np.cos(theta)
            z = radius * np.sin(theta) * np.sin(phi)
            vertices.append((x, y, z))

    # Generate edges
    for i in range(rings):
        for j in range(segments):
            current = i * segments + j
            next_segment = current + 1 if (j + 1) < segments else i * segments
            next_ring = current + segments if (i + 1) <= rings else -1

            edges.append((current, next_segment))  # Horizontal edge
            if next_ring != -1:
                edges.append((current, next_ring))  # Vertical edge

    return vertices, edges


def load_obj(file_path):
    """Load vertices and edges from an OBJ file."""
    vertices = []
    edges = []

    with open(file_path, "r") as file:
        for line in file:
            parts = line.strip().split()
            if not parts or parts[0] == "#":
                continue

            if parts[0] == "v":
                vertices.append(tuple(map(float, parts[1:4])))
            elif parts[0] == "f":
                # Parse face indices, assuming faces are triangles or quads
                indices = [int(idx.split("/")[0]) - 1 for idx in parts[1:]]
                for i in range(len(indices)):
                    edges.append((indices[i], indices[(i + 1) % len(indices)]))

    return vertices, edges


def project_vertex(vertex, width, height, scale=1):
    """Project a 3D vertex to 2D screen space."""
    x, y, z = vertex
    x_proj = int(width / 2 + scale * x)
    y_proj = int(height / 2 - scale * y)
    return x_proj, y_proj


def rotate_x(vertices, angle):
    """Rotate vertices around the X-axis by the given angle."""
    cos_theta = np.cos(angle)
    sin_theta = np.sin(angle)
    rotated = []
    for x, y, z in vertices:
        y_new = cos_theta * y - sin_theta * z
        z_new = sin_theta * y + cos_theta * z
        rotated.append((x, y_new, z_new))
    return rotated


def rotate_y(vertices, angle):
    """Rotate vertices around the Y-axis by the given angle."""
    cos_theta = np.cos(angle)
    sin_theta = np.sin(angle)
    rotated = []
    for x, y, z in vertices:
        x_new = cos_theta * x + sin_theta * z
        z_new = -sin_theta * x + cos_theta * z
        rotated.append((x_new, y, z_new))
    return rotated


def render_wireframe(canvas, vertices, edges, width, height, scale=1):
    """Render the wireframe using draw_line."""
    # Project vertices to 2D screen space using a simple orthographic projection
    projected_vertices = [project_vertex(v, width, height, scale) for v in vertices]

    for edge in edges:
        v1, v2 = edge
        x1, y1 = projected_vertices[v1]
        x2, y2 = projected_vertices[v2]
        canvas.create_line(x1, y1, x2, y2, fill="white")


def render_point_cloud(canvas, vertices, width, height, scale=1):
    """Render a point cloud of vertices."""
    projected_vertices = [project_vertex(v, width, height, scale) for v in vertices]

    for x, y in projected_vertices:
        canvas.create_oval(x - 1, y - 1, x + 1, y + 1, fill="white")


def update():
    """Update the canvas to apply rotation and redraw the object."""
    global vertices, angle_y, angle_x
    canvas.delete("all")
    rotated_vertices = rotate_x(vertices, angle_x)
    rotated_vertices = rotate_y(rotated_vertices, angle_y)
    # render_wireframe(canvas, rotated_vertices, edges, width, height, scale=20)
    angle_x += 0.04
    angle_y += 0.01
    root.after(30, update)


# Initialize the Tkinter window
width, height = 800, 600
root = tk.Tk()
root.title("OBJ Wireframe Viewer")
canvas = tk.Canvas(root, width=width, height=height, bg="black")
canvas.pack()

# Load the OBJ file and render it
obj_file_path = sys.argv[1]

vertices, edges = load_obj(obj_file_path)
# radius = 1.0
# segments = 16
# rings = 16
# vertices, edges = generate_sphere(radius, segments, rings)

angle_x = 0.0
angle_y = 0.0

# Start the update loop
update()

# Run the Tkinter main loop
root.mainloop()
