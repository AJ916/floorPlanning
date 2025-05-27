from flask import Flask, request, jsonify
from flask_cors import CORS
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import networkx as nx
import numpy as np
import random
import io
import base64
import json


app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


class Room:
    def __init__(self, name, width, height, max_expansion=20):
        self.name = name
        self.original_width = width
        self.original_height = height
        self.width = width
        self.height = height
        self.x = None
        self.y = None
        self.rotated = False
        self.max_expansion = max_expansion

    def rotate(self):
        self.width, self.height = self.height, self.width
        self.rotated = not self.rotated

    def reset_to_original_size(self):
        """Reset room to its original dimensions"""
        if self.rotated:
            self.width = self.original_height
            self.height = self.original_width
        else:
            self.width = self.original_width
            self.height = self.original_height

    def get_area(self):
        return self.width * self.height

    def to_dict(self):
        """Convert room to dictionary for JSON serialization"""
        return {
            'name': self.name,
            'original_width': self.original_width,
            'original_height': self.original_height,
            'width': self.width,
            'height': self.height,
            'x': self.x,
            'y': self.y,
            'rotated': self.rotated,
            'max_expansion': self.max_expansion,
            'area': self.get_area()
        }

    def get_boundaries(self):
        """Return room boundaries as (left, right, bottom, top)"""
        if self.x is None or self.y is None:
            return None
        return (self.x, self.x + self.width, self.y, self.y + self.height)

    def has_shared_wall_with(self, other_room):
        """Check if this room shares a wall with another room"""
        if self.x is None or self.y is None or other_room.x is None or other_room.y is None:
            return False

        left1, right1, bottom1, top1 = self.get_boundaries()
        left2, right2, bottom2, top2 = other_room.get_boundaries()

        # Check for vertical walls
        if right1 == left2:
            return max(bottom1, bottom2) < min(top1, top2)
        if right2 == left1:
            return max(bottom1, bottom2) < min(top1, top2)

        # Check for horizontal walls
        if top1 == bottom2:
            return max(left1, left2) < min(right1, right2)
        if top2 == bottom1:
            return max(left1, left2) < min(right1, right2)

        return False


class FloorPlan:
    def __init__(self, region_specs):
        self.rooms = []
        self.adjacency_graph = nx.Graph()
        self.floor_regions = []

        # Support both formats
        if isinstance(region_specs[0], tuple):
            y_offset = 0
            for width, height in region_specs:
                self.floor_regions.append({
                    'x': 0,
                    'y': y_offset,
                    'width': width,
                    'height': height
                })
                y_offset += height
        else:
            for region in region_specs:
                self.floor_regions.append({
                    'x': region.get('x', 0),
                    'y': region.get('y', 0),
                    'width': region['width'],
                    'height': region['height']
                })

        self.floor_width = max(region['x'] + region['width'] for region in self.floor_regions)
        self.floor_height = max(region['y'] + region['height'] for region in self.floor_regions)

    def add_room(self, name, width, height, max_expansion=20):
        room = Room(name, width, height, max_expansion)
        self.rooms.append(room)
        self.adjacency_graph.add_node(name)
        return room

    def add_adjacency(self, room1_name, room2_name):
        if room1_name in self.adjacency_graph.nodes and room2_name in self.adjacency_graph.nodes:
            self.adjacency_graph.add_edge(room1_name, room2_name)

    def is_within_floor(self, x, y, width, height):
        for dx in range(width):
            for dy in range(height):
                px = x + dx
                py = y + dy
                if not self.point_in_floor(px, py):
                    return False
        return True

    def point_in_floor(self, x, y):
        for region in self.floor_regions:
            if (region['x'] <= x < region['x'] + region['width'] and
                    region['y'] <= y < region['y'] + region['height']):
                return True
        return False

    def check_overlap(self, room, x, y, width, height):
        for existing_room in self.rooms:
            if existing_room.x is not None and existing_room != room:
                if (x < existing_room.x + existing_room.width and
                        x + width > existing_room.x and
                        y < existing_room.y + existing_room.height and
                        y + height > existing_room.y):
                    return True
        return False

    def evaluate_adjacency_score(self):
        score = 0
        adjacent_pairs = []

        for room1_name, room2_name in self.adjacency_graph.edges:
            room1 = next(r for r in self.rooms if r.name == room1_name)
            room2 = next(r for r in self.rooms if r.name == room2_name)

            if room1.x is None or room2.x is None:
                continue

            if room1.has_shared_wall_with(room2):
                score += 1
                adjacent_pairs.append((room1_name, room2_name))

        return score, adjacent_pairs

    def can_expand_room(self, room, direction, amount):
        if room.x is None or room.y is None:
            return False

        # Check expansion limits
        current_expansion = 0
        if not room.rotated:
            current_expansion += room.width - room.original_width
            current_expansion += room.height - room.original_height
        else:
            current_expansion += room.width - room.original_height
            current_expansion += room.height - room.original_width

        if current_expansion + amount > room.max_expansion:
            return False

        # Calculate new dimensions
        new_x, new_y = room.x, room.y
        new_width, new_height = room.width, room.height

        if direction == 'right':
            new_width += amount
        elif direction == 'left':
            new_x -= amount
            new_width += amount
        elif direction == 'up':
            new_height += amount
        elif direction == 'down':
            new_y -= amount
            new_height += amount
        else:
            return False

        if not self.is_within_floor(new_x, new_y, new_width, new_height):
            return False

        if self.check_overlap(room, new_x, new_y, new_width, new_height):
            return False

        return True

    def expand_rooms(self):
        for room in self.rooms:
            if room.x is None or room.y is None:
                continue

            directions = ['right', 'down', 'left', 'up']
            random.shuffle(directions)

            for direction in directions:
                expanded = True
                while expanded:
                    if self.can_expand_room(room, direction, 1):
                        if direction == 'right':
                            room.width += 1
                        elif direction == 'left':
                            room.x -= 1
                            room.width += 1
                        elif direction == 'up':
                            room.height += 1
                        elif direction == 'down':
                            room.y -= 1
                            room.height += 1
                    else:
                        expanded = False

    def place_rooms_with_constraints(self, max_attempts=1000, enable_expansion=True):
        sorted_rooms = sorted(self.rooms, key=lambda r: r.get_area(), reverse=True)
        best_score = -1
        best_placement = None

        for attempt in range(max_attempts):
            # Reset placements
            for room in self.rooms:
                room.x = None
                room.y = None
                room.reset_to_original_size()
                if random.random() > 0.5:
                    room.rotate()

            # Try to place all rooms
            all_placed = True
            for room in sorted_rooms:
                placed = False

                for region in self.floor_regions:
                    if region['width'] < room.width or region['height'] < room.height:
                        continue

                    for _ in range(100):
                        max_x = region['x'] + region['width'] - room.width
                        max_y = region['y'] + region['height'] - room.height

                        if max_x >= region['x'] and max_y >= region['y']:
                            x = random.randint(region['x'], max_x)
                            y = random.randint(region['y'], max_y)

                            if not self.check_overlap(room, x, y, room.width, room.height):
                                room.x = x
                                room.y = y
                                placed = True
                                break

                    if placed:
                        break

                if not placed:
                    room.rotate()
                    for region in self.floor_regions:
                        if region['width'] < room.width or region['height'] < room.height:
                            continue

                        for _ in range(100):
                            max_x = region['x'] + region['width'] - room.width
                            max_y = region['y'] + region['height'] - room.height

                            if max_x >= region['x'] and max_y >= region['y']:
                                x = random.randint(region['x'], max_x)
                                y = random.randint(region['y'], max_y)

                                if not self.check_overlap(room, x, y, room.width, room.height):
                                    room.x = x
                                    room.y = y
                                    placed = True
                                    break

                        if placed:
                            break

                if not placed:
                    all_placed = False
                    break

            if all_placed:
                current_placement = [
                    (room.name, room.x, room.y, room.width, room.height, room.rotated, room.max_expansion)
                    for room in self.rooms]

                if enable_expansion:
                    self.expand_rooms()

                score, _ = self.evaluate_adjacency_score()

                if score > best_score:
                    best_score = score
                    best_placement = [
                        (room.name, room.x, room.y, room.width, room.height, room.rotated, room.max_expansion)
                        for room in self.rooms]

                if score == len(self.adjacency_graph.edges):
                    break

        # Restore best placement
        if best_placement:
            for room_data in best_placement:
                name, x, y, width, height, rotated, max_expansion = room_data
                room = next(r for r in self.rooms if r.name == name)
                room.x = x
                room.y = y
                room.width = width
                room.height = height
                room.rotated = rotated
                room.max_expansion = max_expansion
            return True

        return all_placed

    def generate_visualization(self):
        """Generate floor plan visualization and return as base64 encoded image"""
        fig, ax = plt.subplots(figsize=(12, 10))

        # Draw floor shape
        for region in self.floor_regions:
            rect = patches.Rectangle(
                (region['x'], region['y']),
                region['width'],
                region['height'],
                linewidth=2,
                edgecolor='black',
                facecolor='none',
                linestyle='--'
            )
            ax.add_patch(rect)

        # Draw rooms
        colors = plt.cm.tab20(np.linspace(0, 1, len(self.rooms)))
        for i, room in enumerate(self.rooms):
            if room.x is not None and room.y is not None:
                rect = patches.Rectangle(
                    (room.x, room.y),
                    room.width,
                    room.height,
                    linewidth=1,
                    edgecolor='black',
                    facecolor=colors[i],
                    alpha=0.7
                )
                ax.add_patch(rect)

                # Add room labels
                display_text = f"{room.name}\n{room.width}x{room.height}"
                if room.width != room.original_width or room.height != room.original_height:
                    if room.rotated:
                        display_text += f"\n(from {room.original_height}x{room.original_width})"
                    else:
                        display_text += f"\n(from {room.original_width}x{room.original_height})"

                ax.text(
                    room.x + room.width / 2,
                    room.y + room.height / 2,
                    display_text,
                    ha='center',
                    va='center',
                    fontsize=8,
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8)
                )

        # Draw adjacency relationships
        for room1_name, room2_name in self.adjacency_graph.edges:
            room1 = next((r for r in self.rooms if r.name == room1_name), None)
            room2 = next((r for r in self.rooms if r.name == room2_name), None)

            if room1 and room2 and room1.x is not None and room2.x is not None:
                center1 = (room1.x + room1.width / 2, room1.y + room1.height / 2)
                center2 = (room2.x + room2.width / 2, room2.y + room2.height / 2)

                if room1.has_shared_wall_with(room2):
                    ax.plot([center1[0], center2[0]], [center1[1], center2[1]], 'g-', linewidth=2)
                else:
                    ax.plot([center1[0], center2[0]], [center1[1], center2[1]], 'r:', linewidth=1)

        # Set plot properties
        ax.set_xlim(-1, self.floor_width + 1)
        ax.set_ylim(-1, self.floor_height + 1)
        ax.set_aspect('equal')
        ax.set_title('Floor Plan Layout')
        ax.set_xlabel('Width')
        ax.set_ylabel('Height')
        ax.grid(True, alpha=0.3)

        # Convert to base64
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        plt.close()

        return img_base64

    def get_statistics(self):
        """Get floor plan statistics"""
        total_area = sum(region['width'] * region['height'] for region in self.floor_regions)
        used_area = sum(room.width * room.height for room in self.rooms if room.x is not None)

        score, adjacent_pairs = self.evaluate_adjacency_score()

        room_stats = []
        for room in self.rooms:
            if room.x is not None:
                original_area = room.original_width * room.original_height
                current_area = room.width * room.height
                expansion_pct = (current_area - original_area) / original_area * 100 if original_area > 0 else 0

                if not room.rotated:
                    total_expansion = (room.width - room.original_width) + (room.height - room.original_height)
                else:
                    total_expansion = (room.width - room.original_height) + (room.height - room.original_width)

                room_stats.append({
                    'name': room.name,
                    'original_size': f"{room.original_width}x{room.original_height}",
                    'current_size': f"{room.width}x{room.height}",
                    'expansion_percentage': round(expansion_pct, 1),
                    'expansion_used': f"{total_expansion}/{room.max_expansion}",
                    'rotated': room.rotated
                })

        return {
            'total_area': total_area,
            'used_area': used_area,
            'utilization_percentage': round(used_area / total_area * 100, 2) if total_area > 0 else 0,
            'adjacency_score': f"{score}/{len(self.adjacency_graph.edges)}",
            'adjacent_pairs': adjacent_pairs,
            'room_statistics': room_stats
        }

    def to_dict(self):
        """Convert floor plan to dictionary for JSON serialization"""
        return {
            'floor_regions': self.floor_regions,
            'floor_width': self.floor_width,
            'floor_height': self.floor_height,
            'rooms': [room.to_dict() for room in self.rooms],
            'adjacencies': list(self.adjacency_graph.edges),
            'statistics': self.get_statistics()
        }


# Global variable to store current floor plan
current_floor_plan = None


@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'Floor Plan API is running', 'version': '1.0.0'})


@app.route('/api/create-floor-plan', methods=['POST'])
def create_floor_plan():
    """Create a new floor plan with specified regions"""
    global current_floor_plan

    try:
        data = request.get_json()

        if not data or 'regions' not in data:
            return jsonify({'error': 'Missing regions data'}), 400

        regions = data['regions']
        current_floor_plan = FloorPlan(regions)

        return jsonify({
            'message': 'Floor plan created successfully',
            'floor_plan': current_floor_plan.to_dict()
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/add-room', methods=['POST'])
def add_room():
    """Add a room to the current floor plan"""
    global current_floor_plan

    if not current_floor_plan:
        return jsonify({'error': 'No floor plan created. Create a floor plan first.'}), 400

    try:
        data = request.get_json()

        required_fields = ['name', 'width', 'height']
        if not all(field in data for field in required_fields):
            return jsonify({'error': f'Missing required fields: {required_fields}'}), 400

        max_expansion = data.get('max_expansion', 20)

        room = current_floor_plan.add_room(
            data['name'],
            data['width'],
            data['height'],
            max_expansion
        )

        return jsonify({
            'message': f'Room {data["name"]} added successfully',
            'room': room.to_dict()
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/add-adjacency', methods=['POST'])
def add_adjacency():
    """Add adjacency constraint between two rooms"""
    global current_floor_plan

    if not current_floor_plan:
        return jsonify({'error': 'No floor plan created. Create a floor plan first.'}), 400

    try:
        data = request.get_json()

        if 'room1' not in data or 'room2' not in data:
            return jsonify({'error': 'Missing room1 or room2'}), 400

        current_floor_plan.add_adjacency(data['room1'], data['room2'])

        return jsonify({
            'message': f'Adjacency added between {data["room1"]} and {data["room2"]}',
            'adjacencies': list(current_floor_plan.adjacency_graph.edges)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/generate-layout', methods=['POST'])
def generate_layout():
    """Generate room layout with optional parameters"""
    global current_floor_plan

    if not current_floor_plan:
        return jsonify({'error': 'No floor plan created. Create a floor plan first.'}), 400

    try:
        data = request.get_json() or {}

        max_attempts = data.get('max_attempts', 1000)
        enable_expansion = data.get('enable_expansion', True)

        success = current_floor_plan.place_rooms_with_constraints(
            max_attempts=max_attempts,
            enable_expansion=enable_expansion
        )

        if success:
            return jsonify({
                'message': 'Layout generated successfully',
                'success': True,
                'floor_plan': current_floor_plan.to_dict()
            })
        else:
            return jsonify({
                'message': 'Failed to place all rooms optimally',
                'success': False,
                'floor_plan': current_floor_plan.to_dict()
            })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/visualize', methods=['GET'])
def visualize_floor_plan():
    """Generate and return floor plan visualization"""
    global current_floor_plan

    if not current_floor_plan:
        return jsonify({'error': 'No floor plan created. Create a floor plan first.'}), 400

    try:
        image_base64 = current_floor_plan.generate_visualization()

        return jsonify({
            'message': 'Visualization generated successfully',
            'image': image_base64,
            'statistics': current_floor_plan.get_statistics()
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/get-floor-plan', methods=['GET'])
def get_floor_plan():
    """Get current floor plan data"""
    global current_floor_plan

    if not current_floor_plan:
        return jsonify({'error': 'No floor plan created'}), 400

    try:
        return jsonify({
            'floor_plan': current_floor_plan.to_dict()
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/bulk-setup', methods=['POST'])
def bulk_setup():
    """Set up entire floor plan in one request"""
    global current_floor_plan

    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Create floor plan
        if 'regions' not in data:
            return jsonify({'error': 'Missing regions data'}), 400

        current_floor_plan = FloorPlan(data['regions'])

        # Add rooms
        if 'rooms' in data:
            for room_data in data['rooms']:
                current_floor_plan.add_room(
                    room_data['name'],
                    room_data['width'],
                    room_data['height'],
                    room_data.get('max_expansion', 20)
                )

        # Add adjacencies
        if 'adjacencies' in data:
            for adj in data['adjacencies']:
                current_floor_plan.add_adjacency(adj[0], adj[1])

        # Generate layout if requested
        generate_layout_flag = data.get('generate_layout', True)
        if generate_layout_flag:
            max_attempts = data.get('max_attempts', 1000)
            enable_expansion = data.get('enable_expansion', True)

            success = current_floor_plan.place_rooms_with_constraints(
                max_attempts=max_attempts,
                enable_expansion=enable_expansion
            )
        else:
            success = True

        return jsonify({
            'message': 'Floor plan setup completed',
            'success': success,
            'floor_plan': current_floor_plan.to_dict()
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/reset', methods=['POST'])
def reset_floor_plan():
    """Reset/clear the current floor plan"""
    global current_floor_plan
    current_floor_plan = None

    return jsonify({'message': 'Floor plan reset successfully'})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)