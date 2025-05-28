from collections import Counter

def determine_ai_mood(personas):
    tag_counter = Counter()
    category_counter = Counter()

    for p in personas:
        category = p.category.lower() if p.category else ""
        category_counter[category] += 1
        tag_counter.update([t.lower() for t in p.tags if t])

    top_tags = [tag for tag, _ in tag_counter.most_common(3)]
    tooltip = f"Top tags: {', '.join(top_tags)}"

    # Logica voor dominante mood
    if category_counter["design"] + tag_counter["creative"] + tag_counter["ui"] > 2:
        return {
            "emoji": "🎨",
            "label": "Creatieve Flow",
            "tooltip": tooltip,
            "bg": "#ede9fe",
            "fg": "#7c3aed"
        }

    elif tag_counter["data"] + tag_counter["analysis"] + category_counter["development"] > 2:
        return {
            "emoji": "🔍",
            "label": "Strategisch Denken",
            "tooltip": tooltip,
            "bg": "#e0f2fe",
            "fg": "#0369a1"
        }

    elif tag_counter["ai"] + tag_counter["automation"] + tag_counter["tech"] > 2:
        return {
            "emoji": "🚀",
            "label": "Innovatief",
            "tooltip": tooltip,
            "bg": "#fef3c7",
            "fg": "#b45309"
        }

    elif tag_counter["coach"] + tag_counter["psychologie"] + category_counter["mens"] > 2:
        return {
            "emoji": "🤝",
            "label": "Empathisch",
            "tooltip": tooltip,
            "bg": "#dcfce7",
            "fg": "#166534"
        }

    elif tag_counter["ads"] + tag_counter["funnels"] + tag_counter["campaigns"] > 2:
        return {
            "emoji": "📢",
            "label": "Marketing Mastermind",
            "tooltip": tooltip,
            "bg": "#fef2f2",
            "fg": "#b91c1c"
        }

    elif tag_counter["prompt engineering"] + tag_counter["sora"] + tag_counter["chatgpt"] > 2:
        return {
            "emoji": "🧠",
            "label": "AI Architect",
            "tooltip": tooltip,
            "bg": "#f0fdfa",
            "fg": "#0f766e"
        }

    elif tag_counter["javascript"] + tag_counter["code"] + tag_counter["node.js"] > 2:
        return {
            "emoji": "⚙️",
            "label": "Developer Mode",
            "tooltip": tooltip,
            "bg": "#f3f4f6",
            "fg": "#1f2937"
        }

    elif len(category_counter) >= 3:
        return {
            "emoji": "🧩",
            "label": "Gebalanceerde Mix",
            "tooltip": tooltip,
            "bg": "#e0f2f1",
            "fg": "#065f46"
        }

    # Fallback default
    return {
        "emoji": "💡",
        "label": "GPT paraat",
        "tooltip": tooltip,
        "bg": "#e0e7ff",
        "fg": "#1e3a8a"
    }
