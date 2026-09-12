#!/usr/bin/env python3
"""Generate Saturday post queue JSON."""
import json
from datetime import datetime
from posts_part1 import posts_part1
from posts_part2 import posts_part2

posts = posts_part1 + posts_part2

data = {
    "campaign": "Whiteboard Launch — Saturday 8-hour blast",
    "schedule": "Every 25-30 minutes, mixed formats",
    "total_posts": len(posts),
    "generated": datetime.now().strftime("%Y-%m-%d"),
    "hashtags": ["SuperagentChallenge", "BuildInPublic", "AgencyOS", "Quartermaster"],
    "tag": "@Rodion Trach",
    "link": "https://github.com/ypc-ux/quartermaster-agents",
    "posts": posts
}

output_path = "/Users/thefuckingman/.cline/data/workspaces/chat/quartermaster-agents/saturday-post-queue.json"
with open(output_path, "w") as f:
    json.dump(data, f, indent=2)

print(f"✓ Saturday post queue written to {output_path}")
print(f"  Total posts: {len(posts)}")
print(f"  Time range: {posts[0]['time']} - {posts[-1]['time']}")
