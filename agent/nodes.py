import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from agent.state import AgentState
from utils.prompts import (
    SELECT_STORY_PROMPT, CONVERT_TO_EMOJI_PROMPT, 
    EVALUATE_GUESS_PROMPT, REVEAL_STORY_PROMPT
)
from pydantic import BaseModel, Field
from collections import Counter

class EmojiOutput(BaseModel):
    emojis: str = Field(description="The generated emoji sequence")

class StorySelectOutput(BaseModel):
    selected_story: str = Field(description="The exact chosen story name")
    story_type: str = Field(description="Genre or type")
    setting_hint: str = Field(description="Hint about where/when")
    main_character_hint: str = Field(description="Hint about who")
    central_conflict: str = Field(description="Hint about the plot")
    theme: str = Field(description="Hint about core theme")
    short_summary: str = Field(description="2-3 sentence summary without names")

class EvaluationOutput(BaseModel):
    result: str = Field(description='Must be "Correct", "Partially Correct", or "Incorrect"')
    feedback: str = Field(description="Short reason")

def get_llm(temperature=0.9):
    api_key = os.environ.get("GROQ_API_KEY")
    return ChatGroq(
        model="llama-3.3-70b-versatile", 
        temperature=temperature,
        model_kwargs={"top_p": 0.95},
        api_key=api_key
    )

def select_story_node(state: AgentState):
    difficulty = state.get("difficulty", "Medium")
    
    history = state.get("history", [])
    past_stories = [r.get("selected_story", "") for r in history if r.get("selected_story")]
    history_str = "None yet." if not past_stories else "\n".join(f"- {s}" for s in past_stories[-15:])
    
    prompt = PromptTemplate.from_template(SELECT_STORY_PROMPT)
    formatted_prompt = prompt.format(difficulty=difficulty.upper(), history=history_str)
    
    llm = get_llm(temperature=0.9).with_structured_output(StorySelectOutput)
    
    max_retries = 3
    response = None
    
    for _ in range(max_retries):
        response = llm.invoke(formatted_prompt)
        
        # Validation checks ensuring single-source mapping isn't dropping context
        if not response.selected_story or not response.short_summary or not response.story_type:
            continue
        if len(response.short_summary) < 10:
            continue
            
        break
    
    return {
        "selected_story": response.selected_story,
        "story_metadata": {
            "story_type": response.story_type,
            "setting_hint": response.setting_hint,
            "main_character_hint": response.main_character_hint,
            "central_conflict": response.central_conflict,
            "theme": response.theme,
            "short_summary": response.short_summary
        },
        "hints_revealed": 0
    }

def convert_to_emoji_node(state: AgentState):
    difficulty = state.get("difficulty", "Medium")
    selected_story = state.get("selected_story", "")
    
    meta = state.get("story_metadata", {})
    short_summary = meta.get("short_summary", "")
    
    prompt = PromptTemplate.from_template(CONVERT_TO_EMOJI_PROMPT)
    formatted_prompt = prompt.format(
        difficulty=difficulty.upper(), 
        selected_story=selected_story,
        short_summary=short_summary
    )
    
    llm = get_llm(temperature=0.9).with_structured_output(EmojiOutput)
    
    max_retries = 3
    response = None
    
    for _ in range(max_retries):
        response = llm.invoke(formatted_prompt)
        
        emotes = [c for c in response.emojis if ord(c) > 127 and c not in ('\ufe0f', '\u200d')]
        count = len(emotes)
        
        valid = False
        if difficulty == "Easy" and 8 <= count <= 14:
            valid = True
        elif difficulty == "Medium" and 5 <= count <= 9:
            valid = True
        elif difficulty == "Hard" and 3 <= count <= 7:
            valid = True
            
        counts = Counter(emotes)
        if any(v > 2 for v in counts.values()):
            valid = False
            
        if valid:
            break
            
    return {
        "emoji_story": response.emojis,
        "user_guess": "",
        "evaluation_result": "",
        "feedback": "",
        "explanation": ""
    }

def evaluate_guess_node(state: AgentState):
    llm = get_llm(temperature=0.2).with_structured_output(EvaluationOutput)
    prompt = PromptTemplate.from_template(EVALUATE_GUESS_PROMPT)
    chain = prompt | llm
    
    meta = state.get("story_metadata", {})
    short_summary = meta.get("short_summary", state.get("selected_story"))
    
    response = chain.invoke({
        "short_summary": short_summary,
        "user_guess": state.get("user_guess", "")
    })
    
    return {
        "evaluation_result": response.result,
        "feedback": response.feedback
    }

def reveal_story_node(state: AgentState):
    llm = get_llm(temperature=0.5)
    prompt = PromptTemplate.from_template(REVEAL_STORY_PROMPT)
    chain = prompt | llm
    
    meta = state.get("story_metadata", {})
    short_summary = meta.get("short_summary", "")
    
    response = chain.invoke({
        "selected_story": state.get("selected_story", ""),
        "emoji_story": state.get("emoji_story", ""),
        "short_summary": short_summary
    })
    
    return {
        "explanation": response.content
    }

def update_score_node(state: AgentState):
    score_increment = 0
    result = state.get("evaluation_result", "")
    if result == "Correct":
        score_increment = 2
    elif result == "Partially Correct":
        score_increment = 1
        
    current_score = state.get("score", 0)
    new_score = current_score + score_increment
    
    round_info = {
        "emoji_story": state.get("emoji_story"),
        "selected_story": state.get("selected_story"),
        "user_guess": state.get("user_guess"),
        "result": result,
        "points_earned": score_increment
    }
    
    history = state.get("history", [])
    new_history = list(history) + [round_info]
    new_history = new_history[-15:] # Enforce limit to last 15 stories
    
    return {
        "score": new_score,
        "history": new_history
    }
