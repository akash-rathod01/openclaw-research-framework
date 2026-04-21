import os
import importlib.util

SKILLS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../skills'))

def discover_skills():
    skills = []
    if not os.path.exists(SKILLS_DIR):
        return skills
    for entry in os.listdir(SKILLS_DIR):
        skill_path = os.path.join(SKILLS_DIR, entry)
        if os.path.isdir(skill_path):
            entry_point = os.path.join(skill_path, 'main.py')
            if os.path.exists(entry_point):
                skills.append({'name': entry, 'path': entry_point})
    return skills

def load_skill(skill):
    spec = importlib.util.spec_from_file_location(skill['name'], skill['path'])
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
