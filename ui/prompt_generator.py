from collections import Counter

def generate_prompt(persona):
    parts = [
        generate_role_intro(persona),
        generate_tasks_workflows(persona),
        generate_sector_context(persona),
        generate_tools_and_jargon(persona),
        generate_goals(persona),
        generate_structure_guidelines(persona),
        generate_followups(persona)
    ]
    return "\n\n".join([p for p in parts if p])

def generate_role_intro(persona):
    return f"""🧠 **Je bent**: {persona.name}.
Neem de rol aan van een {persona.category.lower()}.
"""

def generate_tasks_workflows(persona):
    if hasattr(persona, 'tasks') and persona.tasks:
        return "🔧 **Belangrijkste Taken**:\n" + "\n".join(f"- {task}" for task in persona.tasks)
    return ""

def generate_sector_context(persona):
    if hasattr(persona, 'applications') and persona.applications:
        return "🏢 **Sectorgerichte Toepassingen**:\n" + "\n".join(f"- {app}" for app in persona.applications)
    return ""

def generate_tools_and_jargon(persona):
    jargon = getattr(persona, 'jargon', [])
    tools = getattr(persona, 'tools', [])
    lines = []
    if jargon:
        lines.append("📚 **Jargon & Technieken**:\n" + ", ".join(jargon))
    if tools:
        lines.append("🛠️ **Tools & Software**:\n" + ", ".join(tools))
    return "\n\n".join(lines)

def generate_goals(persona):
    if hasattr(persona, 'goals') and persona.goals:
        return "🎯 **Doelen**:\n" + "\n".join(f"- {g}" for g in persona.goals)
    return ""

def generate_structure_guidelines(persona):
    if hasattr(persona, 'structure') and persona.structure:
        return "📐 **Gebruik deze structuur in je antwoord**:\n" + ", ".join(persona.structure)
    return ""

def generate_followups(persona):
    if hasattr(persona, 'followups') and persona.followups:
        return "🤔 **Stel daarna deze vragen**:\n" + "\n".join(f"- {q}" for q in persona.followups)
    return ""
