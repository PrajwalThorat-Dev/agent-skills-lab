"""
agent.py

Local agent harness using Ollama (llama3.2) with native tool-calling.
Wires up our skill discovery/catalog/activation system from skill_loader.py.

Flow:
    1. Build skill catalog (lightweight: name + description only)
    2. Inject catalog into system prompt
    3. Register `read_skill` as a tool the model can call
    4. Chat loop: send message -> if model calls read_skill -> intercept,
       read real SKILL.md content, send back as tool result -> model continues
"""

import os
import json
import requests
from dotenv import load_dotenv

from skill_loader import discover_skills, build_catalog_xml, read_skill_content

load_dotenv()

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
MODEL_NAME = os.getenv("MODEL_NAME", "llama3.2:latest")
SKILLS_ROOT = os.getenv(
    "SKILLS_ROOT",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), ".agents", "skills")
)

# Tool definition Ollama expects (OpenAI-style function schema)
READ_SKILL_TOOL = {
    "type": "function",
    "function": {
        "name": "read_skill",
        "description": (
            "Loads the full instructions for a specific skill by name. "
            "Call this ONLY when you have decided a skill is relevant to "
            "the user's request, based on the catalog of available skills "
            "you were given. Do not call this speculatively for every skill."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "skill_name": {
                    "type": "string",
                    "description": "The exact name of the skill to activate, as shown in the catalog."
                }
            },
            "required": ["skill_name"]
        }
    }
}


def build_system_prompt() -> str:
    """Builds the system prompt with the skill catalog injected (progressive disclosure level 1)."""
    skills = discover_skills(SKILLS_ROOT)
    catalog_xml = build_catalog_xml(skills)

    print(f"[SETUP] Discovered {len(skills)} skill(s): {[s.name for s in skills]}\n")

    return f"""You are a helpful local agent with access to a set of skills.

Below is a catalog of skills available to you. Each entry has only a name
and description — you do NOT yet have the full instructions for any skill.

{catalog_xml}

If a user's request matches a skill's description, call the `read_skill`
tool with that skill's exact name to load its full instructions before
responding. If no skill is relevant, just answer normally.
"""


def call_ollama(messages: list, include_tools: bool = True) -> dict:
    """Sends a chat request to Ollama's /api/chat endpoint with tool support."""
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "stream": False,
    }
    if include_tools:
        payload["tools"] = [READ_SKILL_TOOL]

    response = requests.post(f"{OLLAMA_HOST}/api/chat", json=payload, timeout=120)
    response.raise_for_status()
    return response.json()


def handle_tool_call(tool_call: dict) -> str:
    """Executes a requested tool call and returns the result as a string."""
    function_name = tool_call["function"]["name"]
    arguments = tool_call["function"]["arguments"]

    print(f"[TOOL CALL] Model requested: {function_name}({arguments})")

    if function_name == "read_skill":
        skill_name = arguments.get("skill_name", "")
        content = read_skill_content(skill_name, SKILLS_ROOT)
        print(f"[TOOL RESULT] Loaded {len(content)} chars from '{skill_name}/SKILL.md'\n")
        return content

    return f"ERROR: Unknown tool '{function_name}'"


def parse_slash_command(user_input: str):
    """
    Detects direct skill activation syntax: '/skill-name rest of message'.
    Returns (skill_name, remaining_text) if matched, else (None, user_input).
    This lets the USER force-activate a skill without waiting for the model
    to decide — the harness intercepts it before the model ever sees it.
    """
    if not user_input.startswith("/"):
        return None, user_input

    parts = user_input[1:].split(" ", 1)
    skill_name = parts[0].strip()
    remaining_text = parts[1].strip() if len(parts) > 1 else ""
    return skill_name, remaining_text


def chat_loop():
    system_prompt = build_system_prompt()
    messages = [{"role": "system", "content": system_prompt}]

    print("=== Local Skill Agent (llama3.2 via Ollama) ===")
    print("Type 'exit' to quit. Use /skill-name to activate a skill directly.\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ("exit", "quit"):
            break
        if not user_input:
            continue

        skill_name, remaining_text = parse_slash_command(user_input)
        already_activated = False

        if skill_name:
            # USER-triggered activation: skip the model's tool-call decision
            # entirely. We read the skill content ourselves and hand it to
            # the model already loaded, alongside the user's actual message.
            print(f"[SLASH COMMAND] Direct activation requested: '{skill_name}'")

            if not remaining_text:
                print("[SLASH COMMAND] Warning: no code/text provided after skill name.")
                print("Usage: /skill-name <your code or question>\n")
                continue

            content = read_skill_content(skill_name, SKILLS_ROOT)

            if content.startswith("ERROR:"):
                print(f"[SLASH COMMAND] {content}\n")
                continue

            print(f"[SLASH COMMAND] Loaded {len(content)} chars from '{skill_name}/SKILL.md'\n")

            combined_message = (
                f"[Skill '{skill_name}' was directly activated by the user. "
                f"Follow its instructions below. Do not call read_skill again — "
                f"it is already loaded.]\n\n{content}\n\n"
                f"User's request: {remaining_text}"
            )
            messages.append({"role": "user", "content": combined_message})
            already_activated = True
        else:
            messages.append({"role": "user", "content": user_input})

        # Loop in case the model makes multiple tool calls in sequence
        max_tool_iterations = 5
        for _ in range(max_tool_iterations):
            result = call_ollama(messages, include_tools=not already_activated)
            message = result["message"]

            tool_calls = message.get("tool_calls")
            if tool_calls:
                # Append the assistant's tool-call message to history
                messages.append(message)

                for tool_call in tool_calls:
                    tool_result = handle_tool_call(tool_call)
                    messages.append({
                        "role": "tool",
                        "content": tool_result
                    })
                # Loop again so the model can respond using the tool result
                continue
            else:
                # No tool call — this is the final answer
                messages.append(message)
                print(f"\nAssistant: {message['content']}\n")
                break
        else:
            print("\n[WARNING] Max tool iterations reached without a final answer.\n")


if __name__ == "__main__":
    chat_loop()