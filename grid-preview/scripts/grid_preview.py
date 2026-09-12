#!/usr/bin/env python3
"""Grid Preview — Quartermaster. Preview Instagram grid layout before posting."""

import json
from datetime import datetime
from pathlib import Path

GRID_SIZES = [(3, 3), (3, 4), (3, 5)]  # 9, 12, 15 posts

def generate_grid_preview(posts, grid_size=(3, 3)):
    """Generate a grid preview layout."""
    cols, rows = grid_size
    total_slots = cols * rows
    
    # Pad with placeholders if needed
    while len(posts) < total_slots:
        posts.append({
            "id": f"placeholder_{len(posts)}",
            "type": "placeholder",
            "color": "#E5E7EB",
            "content": "Upcoming post"
        })
    
    grid = []
    for row in range(rows):
        grid_row = []
        for col in range(cols):
            idx = row * cols + col
            post = posts[idx] if idx < len(posts) else None
            grid_row.append({
                "position": (row, col),
                "post": post,
                "coordinates": f"R{row+1}C{col+1}"
            })
        grid.append(grid_row)
    
    return {
        "grid_size": grid_size,
        "total_posts": len(posts),
        "grid": grid,
        "generated_at": datetime.now().isoformat()
    }

def analyze_grid_balance(posts):
    """Analyze visual balance and variety in the grid."""
    types = [p.get("type", "unknown") for p in posts if p]
    colors = [p.get("dominant_color", "unknown") for p in posts if p]
    
    type_counts = {t: types.count(t) for t in set(types)}
    color_counts = {c: colors.count(c) for c in set(colors)}
    
    # Check for clustering (same type/color in adjacent positions)
    clusters = []
    for i, post in enumerate(posts):
        if i > 0 and post and posts[i-1]:
            if post.get("type") == posts[i-1].get("type"):
                clusters.append({
                    "positions": [i-1, i],
                    "issue": "adjacent_same_type",
                    "type": post.get("type")
                })
    
    return {
        "type_distribution": type_counts,
        "color_distribution": color_counts,
        "clusters_detected": len(clusters),
        "clusters": clusters,
        "variety_score": min(10, len(set(types)) + len(set(colors))),
        "recommendations": generate_grid_recommendations(clusters, type_counts)
    }

def generate_grid_recommendations(clusters, type_counts):
    """Generate recommendations for grid improvement."""
    recs = []
    if len(clusters) > 2:
        recs.append("Too many similar posts adjacent - mix it up")
    if len(type_counts) < 3:
        recs.append("Add more content variety (carousels, reels, stories, static posts)")
    if max(type_counts.values(), default=0) > len(type_counts) * 2:
        recs.append("One content type is dominating - balance with other formats")
    return recs

def run():
    """Demo: generate a grid preview."""
    print("[Grid Preview] Generating Instagram grid preview...")
    
    # Sample posts
    posts = [
        {"id": "p1", "type": "carousel", "dominant_color": "#1E40AF", "content": "5 tips for agencies"},
        {"id": "p2", "type": "reel", "dominant_color": "#DC2626", "content": "Behind the scenes"},
        {"id": "p3", "type": "static", "dominant_color": "#059669", "content": "Quote graphic"},
        {"id": "p4", "type": "carousel", "dominant_color": "#1E40AF", "content": "Case study"},
        {"id": "p5", "type": "reel", "dominant_color": "#7C3AED", "content": "Tutorial"},
        {"id": "p6", "type": "static", "dominant_color": "#EA580C", "content": "Testimonial"},
        {"id": "p7", "type": "carousel", "dominant_color": "#0891B2", "content": "Framework"},
        {"id": "p8", "type": "reel", "dominant_color": "#BE185D", "content": "Day in the life"},
        {"id": "p9", "type": "static", "dominant_color": "#1E40AF", "content": "CTA graphic"},
    ]
    
    preview = generate_grid_preview(posts, (3, 3))
    analysis = analyze_grid_balance(posts)
    
    out_dir = Path(__file__).parent.parent / "data"
    out_dir.mkdir(exist_ok=True)
    
    result = {
        "preview": preview,
        "analysis": analysis,
        "posts": posts,
        "generated_at": datetime.now().isoformat()
    }
    
    out_path = out_dir / "grid_preview.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"[Grid Preview] Grid preview generated:")
    print(f"  Grid size: {preview['grid_size'][0]}x{preview['grid_size'][1]}")
    print(f"  Posts: {preview['total_posts']}")
    print(f"  Variety score: {analysis['variety_score']}/10")
    print(f"  Clusters detected: {analysis['clusters_detected']}")
    print(f"  Content types: {len(analysis['type_distribution'])}")
    print(f"  Saved to: {out_path}")
    return result

if __name__ == "__main__":
    run()
