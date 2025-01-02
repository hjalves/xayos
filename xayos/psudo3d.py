import math


def generate_sphere(radius, segments, rings):
    """Generate vertices and edges for a sphere."""
    vertices = []
    edges = []

    # Generate vertices
    for i in range(rings + 1):
        theta = math.pi * i / rings
        for j in range(segments):
            phi = 2 * math.pi * j / segments
            x = radius * math.sin(theta) * math.cos(phi)
            y = radius * math.cos(theta)
            z = radius * math.sin(theta) * math.sin(phi)
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
    cos_theta = math.cos(angle)
    sin_theta = math.sin(angle)
    rotated = []
    for x, y, z in vertices:
        y_new = cos_theta * y - sin_theta * z
        z_new = sin_theta * y + cos_theta * z
        rotated.append((x, y_new, z_new))
    return rotated


def rotate_y(vertices, angle):
    """Rotate vertices around the Y-axis by the given angle."""
    cos_theta = math.cos(angle)
    sin_theta = math.sin(angle)
    rotated = []
    for x, y, z in vertices:
        x_new = cos_theta * x + sin_theta * z
        z_new = -sin_theta * x + cos_theta * z
        rotated.append((x_new, y, z_new))
    return rotated


def rotate_z(vertices, angle):
    """Rotate vertices around the Z-axis by the given angle."""
    cos_theta = math.cos(angle)
    sin_theta = math.sin(angle)
    rotated = []
    for x, y, z in vertices:
        x_new = cos_theta * x - sin_theta * y
        y_new = sin_theta * x + cos_theta * y
        rotated.append((x_new, y_new, z))
    return rotated


def rotate_model(vertices, angle_x=0, angle_y=0, angle_z=0, order="xyz"):
    """Rotate vertices around the X and Y axes by the given angles."""
    rotated = vertices
    calls = [rotate_x, rotate_y, rotate_z]
    calls = [calls[order.index(axis)] for axis in "xyz"]
    for call, angle in zip(calls, [angle_x, angle_y, angle_z]):
        if angle:
            rotated = call(rotated, angle * math.pi / 180)
    return rotated


def render_wireframe(
    renderer, vertices, edges, width, height, scale=100, color=(255, 255, 255)
):
    """Render the wireframe using draw_line."""
    # Project vertices to 2D screen space using a simple orthographic projection
    projected_vertices = [project_vertex(v, width, height, scale) for v in vertices]

    all_points = []

    for edge in edges:
        v1, v2 = edge
        x1, y1 = projected_vertices[v1]
        x2, y2 = projected_vertices[v2]
        renderer.draw_line((x1, y1, x2, y2), color)


def render_point_cloud(
    renderer, vertices, width, height, scale=100, color=(255, 255, 255)
):
    """Render a point cloud of vertices."""
    projected_vertices = [project_vertex(v, width, height, scale) for v in vertices]
    renderer.draw_point(projected_vertices, color)
