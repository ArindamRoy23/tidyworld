"""Module containing prompt templates for LLM interactions."""

from typing import Dict, List

# Dictionary containing all prompt templates
PROMPTS: Dict[str, str] = {
    # Add your prompts here
    # Example:
    # "task_name": """
    # Your prompt template here.
    # Use {placeholder} for dynamic content.
    # """
}

# Optional: Add any helper functions for prompt manipulation
def format_prompt(prompt_name: str, **kwargs) -> str:
    """Format a prompt template with the given arguments."""
    if prompt_name not in PROMPTS:
        raise ValueError(f"Unknown prompt template: {prompt_name}")
    return PROMPTS[prompt_name].format(**kwargs)
