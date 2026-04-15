SELECT_STORY_PROMPT = """
You are preparing a story for a guessing game.

Step 1:
Select ONE real, well-defined story based on difficulty.

Step 2:
Generate structured metadata STRICTLY based on that exact story.

Difficulty: {difficulty}

Avoid these stories:
{history}

Rules:
- All hints MUST directly relate to selected_story.
- Do NOT invent unrelated elements.
- Hints must be factually accurate.
- setting_hint must describe actual story setting.
- main_character_hint must describe real protagonist.
- central_conflict must reflect real plot.
- theme must reflect real theme.
- short_summary must describe actual story events.
- Do NOT reveal spoilers beyond core plot.
- Ensure internal consistency.
"""

CONVERT_TO_EMOJI_PROMPT = """
You must convert this story into emojis:

Story: {selected_story}
Summary: {short_summary}
Difficulty: {difficulty}

Rules:
- Follow emoji count constraints strictly:
  - Easy: 10-12 emojis
  - Medium: 6-8 emojis
  - Hard: 4-6 emojis
- Maintain logical mapping.
- Use symbolic consistency.
- Output ONLY the emojis.
- No text.
- No explanation.

Return ONLY a JSON object:
{{
  "emojis": "your emojis here"
}}
"""

EVALUATE_GUESS_PROMPT = """
The true story summary is:
{short_summary}

User guessed:
{user_guess}

Determine if the user correctly identified the story meaning.
Classify:
Respond STRICTLY with a JSON object containing:
- "result": "Correct", "Partially Correct", "Incorrect"
- "feedback": short reason

Do not output anything outside the JSON.
"""

REVEAL_STORY_PROMPT = """
Explain briefly how these emojis represent this story:
Emoji Story: {emoji_story}
Story: {selected_story}
Summary: {short_summary}

Keep explanation under 3 sentences.
"""
