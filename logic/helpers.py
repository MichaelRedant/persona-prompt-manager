def find_persona_by_id(personas, persona_id):
    return next((p for p in personas if p.id == persona_id), None)

def find_prompt_by_id(prompts, prompt_id):
    return next((p for p in prompts if p.id == prompt_id), None)

def get_related_prompts(prompts, persona_id):
    return [p for p in prompts if p.persona_id == persona_id]

def format_persona_description(persona):
    return (
        f"🔹 Naam: {persona.name}\n"
        f"🔹 Categorie: {persona.category}\n"
        f"🔹 Tags: {', '.join(persona.tags)}\n\n"
        f"{persona.description}"
    )

def format_prompt_metadata(prompt, persona_name):
    return (
        f"🔗 Koppeling: <b>{persona_name}</b> · 📏 Lengte: {len(prompt.content)} tekens · 🕒 Laatst gebruikt: {prompt.last_used}"
    )
