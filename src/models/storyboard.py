from pydantic import BaseModel
from typing import List

class Asset(BaseModel):
    name: str
    type: str
    details: str

class Action(BaseModel):
    description: str
    start: int
    end: int
    startPosition: str
    endPosition: str

class Scene(BaseModel):
    description: str
    assets: List[Asset]
    dialogue: List[str]
    actions: List[Action]

class Storyboard(BaseModel):
    mainGoal: str
    objectives: List[str]
    keyScenes: List[Scene]
    transitions: List[str] 
