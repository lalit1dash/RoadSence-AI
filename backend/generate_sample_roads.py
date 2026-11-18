"""
Generates realistic broken road sample images for RoadSense.
Saves to backend/uploads/ and frontend/public/sample_roads/
"""

import math
import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter


def create_asphalt_base(width=900, height=650, base_brightness=75):
    """Generate realistic textured asphalt base."""
    # Base noise
    noise = np.random.normal(loc=base_brightness, scale=14, size=(height, width)).clip(25, 140).astype(np.uint8)
    
    # Add subtle aggregate specks (light and dark gravel)
    specks = np.random.choice([0, 1, 2], size=(height, width), p=[0.92, 0.05, 0.03])
    noise = np.where(specks == 1, np.clip(noise + 40, 0, 255), noise)
    noise = np.where(specks == 2, np.clip(noise - 35, 0, 255), noise)
    
    # Asphalt cool grey tone
    r = (noise * 0.94).astype(np.uint8)
    g = (noise * 0.96).astype(np.uint8)
    b = (noise * 1.00).astype(np.uint8)
    
    return Image.fromarray(np.dstack((r, g, b)))


def draw_road_markings(img, line_type="dashed_yellow"):
    """Draw realistic road lane markings."""
    draw = ImageDraw.Draw(img)
    w, h = img.size
    
    if line_type == "dashed_white":
        # Dashed center line
        dash_len = 65
        gap_len = 45
        y = 0
        while y < h:
            draw.line([(w // 2, y), (w // 2, min(h, y + dash_len))], fill=(225, 225, 220), width=9)
            y += dash_len + gap_len
    elif line_type == "double_yellow":
        draw.line([(w // 2 - 8, 0), (w // 2 - 8, h)], fill=(235, 195, 30), width=6)
        draw.line([(w // 2 + 8, 0), (w // 2 + 8, h)], fill=(235, 195, 30), width=6)
    elif line_type == "edge_white":
        draw.line([(60, 0), (60, h)], fill=(210, 210, 205), width=8)


def draw_crack_path(draw, start_x, start_y, length=200, angle=0, branch_prob=0.3, depth=0, max_depth=3):
    """Draw recursive irregular jagged crack path with realistic micro-variations."""
    x, y = start_x, start_y
    cur_angle = angle
    points = [(x, y)]
    steps = int(length / 6)
    
    for _ in range(steps):
        cur_angle += random.uniform(-0.4, 0.4)
        step_len = random.uniform(4, 9)
        x += math.cos(cur_angle) * step_len
        y += math.sin(cur_angle) * step_len
        points.append((x, y))
        
        # Branch crack
        if depth < max_depth and random.random() < branch_prob:
            branch_angle = cur_angle + random.choice([-1, 1]) * random.uniform(0.5, 1.2)
            draw_crack_path(draw, x, y, length=length * random.uniform(0.3, 0.6), angle=branch_angle, branch_prob=branch_prob*0.7, depth=depth+1, max_depth=max_depth)
            
    # Draw crack line with dark core and eroded light rim
    width = max(1, 4 - depth)
    # Outer light halo (weathered pulverized edge)
    draw.line(points, fill=(115, 115, 115), width=width + 2)
    # Dark shadow crevice
    draw.line(points, fill=(22, 22, 25), width=width)


def draw_pothole(img, center_x, center_y, radius_x=90, radius_y=60):
    """Draw realistic jagged pothole with depth layers, inner cavity, and fractured rim."""
    w, h = img.size
    
    # 1. Generate irregular polygon contour
    num_points = 28
    points = []
    for i in range(num_points):
        theta = (2 * math.pi * i) / num_points
        jitter_r_x = radius_x * random.uniform(0.75, 1.25)
        jitter_r_y = radius_y * random.uniform(0.75, 1.25)
        px = center_x + jitter_r_x * math.cos(theta)
        py = center_y + jitter_r_y * math.sin(theta)
        points.append((px, py))
        
    draw = ImageDraw.Draw(img)
    
    # Outer fractured rim (spalled asphalt aggregate)
    rim_points = [(p[0] + random.uniform(-5, 5), p[1] + random.uniform(-5, 5)) for p in points]
    draw.polygon(rim_points, fill=(125, 120, 115), outline=(145, 140, 135))
    
    # Inner dark cavity
    inner_points = [
        (center_x + (p[0] - center_x) * 0.88, center_y + (p[1] - center_y) * 0.88)
        for p in points
    ]
    draw.polygon(inner_points, fill=(35, 33, 35))
    
    # Deepest cavity with shadow
    deep_points = [
        (center_x + (p[0] - center_x) * 0.65, center_y + (p[1] - center_y) * 0.65)
        for p in points
    ]
    draw.polygon(deep_points, fill=(18, 16, 18))
    
    # Loose gravel stones inside and around
    for _ in range(40):
        gx = center_x + random.uniform(-radius_x * 1.1, radius_x * 1.1)
        gy = center_y + random.uniform(-radius_y * 1.1, radius_y * 1.1)
        gw = random.randint(3, 7)
        gh = random.randint(2, 5)
        color = random.choice([(90, 85, 80), (135, 130, 125), (45, 42, 40)])
        draw.ellipse([(gx, gy), (gx + gw, gy + gh)], fill=color)
        
    # Radiating stress micro-cracks from pothole edge
    for i in range(0, num_points, 4):
        bx, by = points[i]
        angle = math.atan2(by - center_y, bx - center_x) + random.uniform(-0.2, 0.2)
        draw_crack_path(draw, bx, by, length=random.uniform(40, 90), angle=angle, branch_prob=0.2, max_depth=1)


def draw_alligator_cracking(img, center_x, center_y, area_w=300, area_h=220):
    """Draw interconnected hexagonal/polygonal alligator fatigue cracks."""
    draw = ImageDraw.Draw(img)
    
    # Generate grid of seed points with jitter
    cols = 6
    rows = 5
    cell_w = area_w / cols
    cell_h = area_h / rows
    
    grid = []
    for r in range(rows + 1):
        row_points = []
        for c in range(cols + 1):
            px = (center_x - area_w // 2) + c * cell_w + random.uniform(-cell_w * 0.35, cell_w * 0.35)
            py = (center_y - area_h // 2) + r * cell_h + random.uniform(-cell_h * 0.35, cell_h * 0.35)
            row_points.append((px, py))
        grid.append(row_points)
        
    # Connect mesh lines
    for r in range(rows):
        for c in range(cols):
            p1 = grid[r][c]
            p2 = grid[r][c + 1]
            p3 = grid[r + 1][c + 1]
            p4 = grid[r + 1][c]
            
            # Draw polygon perimeter cracks
            for a, b in [(p1, p2), (p2, p3), (p3, p4), (p4, p1)]:
                # Jagged line
                mid_x = (a[0] + b[0]) / 2 + random.uniform(-4, 4)
                mid_y = (a[1] + b[1]) / 2 + random.uniform(-4, 4)
                draw.line([a, (mid_x, mid_y), b], fill=(110, 110, 110), width=4)
                draw.line([a, (mid_x, mid_y), b], fill=(22, 22, 25), width=2)


def generate_images():
    backend_dir = Path(__file__).resolve().parent
    output_dirs = [
        backend_dir / "uploads",
        backend_dir.parent / "frontend" / "public" / "sample_roads",
    ]
    for d in output_dirs:
        d.mkdir(parents=True, exist_ok=True)
        
    # ── IMAGE 1: Pothole on NH-48 ─────────────────────────────────────────────
    img1 = create_asphalt_base(900, 650, base_brightness=70)
    draw_road_markings(img1, "dashed_white")
    draw_pothole(img1, 380, 360, radius_x=120, radius_y=80)
    draw_pothole(img1, 620, 240, radius_x=65, radius_y=45)
    img1 = img1.filter(ImageFilter.SMOOTH_MORE)
    
    # ── IMAGE 2: Alligator Cracking Urban Pavement ─────────────────────────────
    img2 = create_asphalt_base(900, 650, base_brightness=65)
    draw_road_markings(img2, "double_yellow")
    draw_alligator_cracking(img2, 450, 350, area_w=420, area_h=300)
    img2 = img2.filter(ImageFilter.SMOOTH_MORE)
    
    # ── IMAGE 3: Longitudinal Crack Highway ───────────────────────────────────
    img3 = create_asphalt_base(900, 650, base_brightness=74)
    draw_road_markings(img3, "dashed_white")
    draw3 = ImageDraw.Draw(img3)
    # Long longitudinal fault running along wheel path
    draw_crack_path(draw3, 320, 20, length=610, angle=math.pi / 2 + 0.05, branch_prob=0.35, max_depth=3)
    img3 = img3.filter(ImageFilter.SMOOTH_MORE)
    
    # ── IMAGE 4: Transverse Thermal Cracking ───────────────────────────────────
    img4 = create_asphalt_base(900, 650, base_brightness=78)
    draw_road_markings(img4, "edge_white")
    draw4 = ImageDraw.Draw(img4)
    # Crack crossing entire road perpendicular
    draw_crack_path(draw4, 50, 310, length=780, angle=0.03, branch_prob=0.28, max_depth=2)
    draw_crack_path(draw4, 180, 480, length=540, angle=-0.08, branch_prob=0.22, max_depth=2)
    img4 = img4.filter(ImageFilter.SMOOTH_MORE)
    
    # ── IMAGE 5: Severe Surface Damage & Raveling ─────────────────────────────
    img5 = create_asphalt_base(900, 650, base_brightness=62)
    draw_road_markings(img5, "dashed_white")
    draw_alligator_cracking(img5, 340, 280, area_w=280, area_h=200)
    draw_pothole(img5, 610, 410, radius_x=85, radius_y=55)
    draw5 = ImageDraw.Draw(img5)
    draw_crack_path(draw5, 200, 520, length=380, angle=-0.4, branch_prob=0.3, max_depth=2)
    img5 = img5.filter(ImageFilter.SMOOTH_MORE)
    
    # ── IMAGE 6: Heavy Road Failure Sector 14 ──────────────────────────────────
    img6 = create_asphalt_base(900, 650, base_brightness=68)
    draw_road_markings(img6, "double_yellow")
    draw_pothole(img6, 280, 260, radius_x=95, radius_y=70)
    draw_pothole(img6, 520, 380, radius_x=130, radius_y=85)
    draw_pothole(img6, 730, 210, radius_x=70, radius_y=50)
    draw_alligator_cracking(img6, 420, 480, area_w=320, area_h=160)
    img6 = img6.filter(ImageFilter.SMOOTH_MORE)

    samples = [
        ("pothole_severe_nh48.jpg", img1, "NH-48 Sector 21 Pothole"),
        ("alligator_crack_urban.jpg", img2, "MG Road Fatigue Cracking"),
        ("longitudinal_crack_highway.jpg", img3, "Expressway Longitudinal Crack"),
        ("transverse_crack_suburb.jpg", img4, "Outer Ring Transverse Crack"),
        ("surface_damage_multi.jpg", img5, "Multiple Surface Degradation"),
        ("heavy_damage_sector14.jpg", img6, "Critical Road Failure Sector 14"),
    ]

    for filename, img, label in samples:
        for out_dir in output_dirs:
            save_path = out_dir / filename
            img.save(save_path, "JPEG", quality=90)
            print(f"Saved: {save_path}")

    print(f"\nSuccessfully generated {len(samples)} realistic broken road images in uploads and sample_roads!")


if __name__ == "__main__":
    generate_images()
