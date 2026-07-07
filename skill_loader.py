"""
skill_loader.py
Handles discovery, cataloging, and activation of local agent skills.

Directory convention:
    ~/.agents/skills/<skill-name>/SKILL.md   (required)
                                  /scripts/    (optional)
                                  /references/ (optional)
                                  /templates/  (optional)
                                  /examples/   (optional)
"""

import os
import re
from pathlib import Path
from dataclasses import dataclass


@dataclass
class SkillMeta:
    name: str
    description: str
    location: str  # full path to SKILL.md


def _normalize_newlines(text: str) -> str:
    """Windows saves files with \\r\\n, which breaks our \\n-based regexes."""
    return text.replace("\r\n", "\n").replace("\r", "\n")


def _parse_frontmatter(text: str) -> dict:
    """
    Extracts YAML-style frontmatter between the first two '---' lines.
    Simple key: value parser only — our frontmatter is intentionally flat.
    """
    text = _normalize_newlines(text)
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not match:
        return {}

    frontmatter_block = match.group(1)
    data = {}
    for line in frontmatter_block.splitlines():
        line = line.strip()
        if not line or ":" not in line:
            continue
        key, _, value = line.partition(":")
        data[key.strip()] = value.strip()
    return data


def discover_skills(skills_root: str) -> list[SkillMeta]:
    """
    Scans skills_root for valid skill directories (must contain SKILL.md).
    Returns lightweight metadata only — NOT full file content.
    This is progressive disclosure, level 1.
    """
    root = Path(skills_root)
    if not root.exists():
        return []

    skills = []
    for entry in sorted(root.iterdir()):
        if not entry.is_dir():
            continue  # ignore stray files like README.md at root

        skill_file = entry / "SKILL.md"
        if not skill_file.exists():
            continue  # not a valid skill directory

        raw = skill_file.read_text(encoding="utf-8")
        meta = _parse_frontmatter(raw)

        name = meta.get("name", entry.name)
        description = meta.get("description", "No description provided.")

        skills.append(SkillMeta(
            name=name,
            description=description,
            location=str(skill_file.resolve())
        ))

    return skills


def build_catalog_xml(skills: list[SkillMeta]) -> str:
    """
    Builds the <available_skills> XML block to inject into the system prompt.
    Just name + description + location. No instructions, no scripts.
    """
    if not skills:
        return "<available_skills>\n  <!-- no skills found -->\n</available_skills>"

    lines = ["<available_skills>"]
    for s in skills:
        lines.append("  <skill>")
        lines.append(f"    <name>{s.name}</name>")
        lines.append(f"    <description>{s.description}</description>")
        lines.append(f"    <location>{s.location}</location>")
        lines.append("  </skill>")
    lines.append("</available_skills>")
    return "\n".join(lines)


def read_skill_content(skill_name: str, skills_root: str) -> str:
    """
    Progressive disclosure, level 2.
    Called ONLY when the model activates a skill via the read_skill tool.
    Returns the FULL SKILL.md body (instructions), not just frontmatter.
    """
    skills = discover_skills(skills_root)
    match = next((s for s in skills if s.name == skill_name), None)

    if not match:
        return f"ERROR: No skill named '{skill_name}' found in {skills_root}."

    full_text = _normalize_newlines(Path(match.location).read_text(encoding="utf-8"))

    # Strip frontmatter before returning — model already saw name/description
    body = re.sub(r"^---\s*\n.*?\n---\s*\n", "", full_text, flags=re.DOTALL)
    return body.strip()


# Quick manual test when run directly
if __name__ == "__main__":
    SKILLS_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".agents", "skills")

    print("=== Discovered skills ===")
    found = discover_skills(SKILLS_ROOT)
    for s in found:
        print(f"- {s.name}: {s.description}")

    print("\n=== Catalog XML (what the model sees first) ===")
    print(build_catalog_xml(found))

    if found:
        print(f"\n=== Full content of '{found[0].name}' (what model sees on activation) ===")
        print(read_skill_content(found[0].name, SKILLS_ROOT))