"""
Utilities for parsing LLM outputs, especially handling thinking traces.
"""

import re
import json
import logging
from typing import Any, Dict


def strip_thinking_traces(text: str) -> str:
    """
    Remove thinking traces from LLM output.

    Handles various formats:
    - XML-style tags: <think>...</think>, <thinking>...</thinking>
    - Nested thinking blocks
    - Multiple thinking blocks

    Args:
        text: Raw text from LLM

    Returns:
        Text with thinking traces removed
    """
    if not text:
        return text

    # Remove XML-style thinking tags (case-insensitive, handles nesting)
    # Patterns to match: <think>...</think>, <thinking>...</thinking>
    patterns = [
        r'<think>.*?</think>',
        r'<thinking>.*?</thinking>',
        r'<THINK>.*?</THINK>',
        r'<THINKING>.*?</THINKING>',
    ]

    cleaned = text
    for pattern in patterns:
        # Use DOTALL flag to match across newlines
        cleaned = re.sub(pattern, '', cleaned, flags=re.DOTALL | re.IGNORECASE)

    # Remove any leftover orphaned tags
    cleaned = re.sub(r'</?think(?:ing)?>', '', cleaned, flags=re.IGNORECASE)

    # Clean up excessive whitespace left by removal
    cleaned = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned)  # Max 2 newlines
    cleaned = cleaned.strip()

    return cleaned


def strip_thinking_from_json(text: str) -> str:
    """
    Remove thinking fields from JSON in LLM output.

    Handles JSON objects with thinking fields like:
    {"thinking": "...", "Questions": [...]}

    Args:
        text: Raw text that might contain JSON with thinking fields

    Returns:
        Text with thinking fields removed from JSON
    """
    if not text:
        return text

    # First strip XML-style thinking traces
    cleaned = strip_thinking_traces(text)

    # Try to parse as JSON and remove thinking fields
    try:
        # Find JSON-like structures in the text
        json_match = re.search(r'\{.*\}', cleaned, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            try:
                data = json.loads(json_str)
                if isinstance(data, dict):
                    # Remove thinking-related keys (case-insensitive)
                    thinking_keys = [k for k in data.keys()
                                   if k.lower() in ('thinking', 'think', 'thought', 'reasoning')]
                    for key in thinking_keys:
                        del data[key]

                    # Replace the JSON in the original text
                    cleaned_json = json.dumps(data)
                    cleaned = cleaned.replace(json_str, cleaned_json)
            except json.JSONDecodeError:
                # If JSON parsing fails, just return the text with XML traces removed
                pass
    except Exception as e:
        logging.debug(f"Error processing JSON thinking traces: {e}")

    return cleaned


def preprocess_llm_output(text: str, strict: bool = False) -> str:
    """
    Preprocess LLM output before parsing.

    This is the main entry point for cleaning LLM outputs.
    Removes thinking traces and other artifacts that might interfere with parsing.

    Args:
        text: Raw output from LLM
        strict: If True, also removes thinking fields from JSON

    Returns:
        Cleaned text ready for parsing
    """
    if not text:
        return text

    if strict:
        return strip_thinking_from_json(text)
    else:
        return strip_thinking_traces(text)


def create_thinking_aware_parser(parser, llm):
    """
    Wrap a parser to handle thinking traces automatically.

    Args:
        parser: Original parser (e.g., JsonOutputParser, PydanticOutputParser)
        llm: LLM instance for OutputFixingParser

    Returns:
        A parser chain that strips thinking traces before parsing
    """
    from langchain.output_parsers import OutputFixingParser

    class ThinkingAwareParser:
        """Parser wrapper that strips thinking traces before parsing."""

        def __init__(self, base_parser, llm_instance):
            self.base_parser = base_parser
            self.fixing_parser = OutputFixingParser.from_llm(
                llm=llm_instance,
                parser=base_parser,
                max_retries=2  # Increased retries for thinking models
            )

        def parse(self, text: str) -> Any:
            """Parse text after removing thinking traces."""
            # First attempt: strip thinking and parse directly
            cleaned = preprocess_llm_output(text, strict=True)
            try:
                return self.base_parser.parse(cleaned)
            except Exception as e:
                logging.debug(f"Initial parse failed, trying fixing parser: {e}")
                # Second attempt: use fixing parser on cleaned text
                try:
                    return self.fixing_parser.parse(cleaned)
                except Exception as e2:
                    logging.debug(f"Fixing parser also failed: {e2}")
                    # Final attempt: use fixing parser on original text
                    return self.fixing_parser.parse(text)

        def get_format_instructions(self) -> str:
            """Get format instructions from base parser."""
            return self.base_parser.get_format_instructions()

    return ThinkingAwareParser(parser, llm)


def extract_json_from_mixed_content(text: str) -> str:
    """
    Extract JSON from text that might have other content mixed in.

    Useful when LLM outputs text before/after the JSON.

    Args:
        text: Text potentially containing JSON

    Returns:
        Extracted JSON string or original text if no JSON found
    """
    # Remove thinking traces first
    cleaned = strip_thinking_traces(text)

    # Try to find JSON objects or arrays
    # Match outermost braces/brackets
    json_patterns = [
        r'\{(?:[^{}]|(?R))*\}',  # Objects (with recursion)
        r'\[(?:[^\[\]]|(?R))*\]'  # Arrays (with recursion)
    ]

    for pattern in json_patterns:
        try:
            # Use simpler pattern since Python doesn't support (?R)
            # Find the first { or [ and match to the last } or ]
            if '{' in cleaned:
                start = cleaned.find('{')
                # Find matching closing brace
                depth = 0
                for i in range(start, len(cleaned)):
                    if cleaned[i] == '{':
                        depth += 1
                    elif cleaned[i] == '}':
                        depth -= 1
                        if depth == 0:
                            json_str = cleaned[start:i+1]
                            # Validate it's actually JSON
                            try:
                                json.loads(json_str)
                                return json_str
                            except:
                                continue
            elif '[' in cleaned:
                start = cleaned.find('[')
                depth = 0
                for i in range(start, len(cleaned)):
                    if cleaned[i] == '[':
                        depth += 1
                    elif cleaned[i] == ']':
                        depth -= 1
                        if depth == 0:
                            json_str = cleaned[start:i+1]
                            try:
                                json.loads(json_str)
                                return json_str
                            except:
                                continue
        except Exception as e:
            logging.debug(f"Error extracting JSON: {e}")

    return cleaned
