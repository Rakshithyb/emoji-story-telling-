from typing import TypedDict

class AgentState(TypedDict, total=False):
    emoji_story: str
    selected_story: str
    story_metadata: dict
    hints_revealed: int
    user_guess: str
    evaluation_result: str
    feedback: str
    explanation: str
    score: int
    history: list[dict]
    difficulty: str
    refresh_counter: int
    generation_id: str
