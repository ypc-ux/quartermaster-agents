#!/usr/bin/env python3
"""Bio Optimizer — Quartermaster. Optimize social media bios for conversion."""

import json
from datetime import datetime
from pathlib import Path

PLATFORMS = ["twitter", "instagram", "linkedin", "tiktok"]

BIO_ELEMENTS = {
    "hook": "Opening line that grabs attention",
    "value_prop": "What you do and who it's for",
    "proof": "Credibility (numbers, results, credentials)",
    "personality": "Voice and tone that matches your brand",
    "cta": "Clear call-to-action"
}

def analyze_bio(bio_text, platform="twitter"):
    """Analyze a bio and score it on key elements."""
    scores = {
        "clarity": 0,
        "specificity": 0,
        "credibility": 0,
        "personality": 0,
        "cta_strength": 0
    }
    
    # Simple heuristic scoring
    words = bio_text.split()
    scores["clarity"] = min(10, len(words) // 5 + 5)
    scores["specificity"] = 8 if any(c.isdigit() for c in bio_text) else 5
    scores["credibility"] = 7 if any(w in bio_text.lower() for w in ["years", "clients", "revenue", "followers"]) else 4
    scores["personality"] = 7 if any(c in bio_text for c in ["!", "?", "→", "•"]) else 5
    scores["cta_strength"] = 8 if any(w in bio_text.lower() for w in ["book", "join", "get", "download", "follow"]) else 4
    
    total = sum(scores.values())
    
    return {
        "platform": platform,
        "bio": bio_text,
        "char_count": len(bio_text),
        "scores": scores,
        "total_score": total,
        "max_score": 50,
        "grade": "A" if total >= 40 else "B" if total >= 30 else "C" if total >= 20 else "D",
        "recommendations": generate_recommendations(scores)
    }

def generate_recommendations(scores):
    """Generate improvement recommendations based on scores."""
    recs = []
    if scores["clarity"] < 6:
        recs.append("Simplify your bio - be more direct about what you do")
    if scores["specificity"] < 6:
        recs.append("Add specific numbers or results (e.g., '500+ clients served')")
    if scores["credibility"] < 6:
        recs.append("Include proof points (years of experience, results, credentials)")
    if scores["personality"] < 6:
        recs.append("Inject more personality - use emojis, arrows, or unique formatting")
    if scores["cta_strength"] < 6:
        recs.append("Add a clear call-to-action (book a call, follow for more, etc.)")
    return recs

def optimize_bio(current_bio, platform="twitter", target_audience=None):
    """Generate optimized bio variations."""
    variations = []
    
    # Template variations
    templates = [
        f"{current_bio} → Book a call",
        f"Helping {target_audience or 'agencies'} [specific result]\n{current_bio}",
        f"8 years building agencies\n{current_bio}\n↓ Free resource below",
    ]
    
    for i, template in enumerate(templates, 1):
        variations.append({
            "variation": i,
            "bio": template,
            "platform": platform,
            "char_count": len(template)
        })
    
    return {
        "current": current_bio,
        "variations": variations,
        "optimized_at": datetime.now().isoformat()
    }

def run(current_bio="Building operating systems for agencies | 8 years | 14K followers", platform="twitter"):
    """Analyze and optimize a bio."""
    print(f"[Bio Optimizer] Analyzing {platform} bio...")
    
    analysis = analyze_bio(current_bio, platform)
    optimizations = optimize_bio(current_bio, platform, "agency owners")
    
    out_dir = Path(__file__).parent.parent / "data"
    out_dir.mkdir(exist_ok=True)
    
    result = {
        "analysis": analysis,
        "optimizations": optimizations,
        "platform": platform,
        "generated_at": datetime.now().isoformat()
    }
    
    out_path = out_dir / f"bio_optimization_{platform}.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"[Bio Optimizer] Bio analysis:")
    print(f"  Platform: {platform}")
    print(f"  Grade: {analysis['grade']}")
    print(f"  Score: {analysis['total_score']}/50")
    print(f"  Char count: {analysis['char_count']}")
    print(f"  Recommendations: {len(analysis['recommendations'])}")
    print(f"  Variations generated: {len(optimizations['variations'])}")
    print(f"  Saved to: {out_path}")
    return result

if __name__ == "__main__":
    import sys
    bio = sys.argv[1] if len(sys.argv) > 1 else "Building operating systems for agencies"
    platform = sys.argv[2] if len(sys.argv) > 2 else "twitter"
    run(bio, platform)
