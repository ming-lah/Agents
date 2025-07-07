"""
TypedDict 统一描述状态
"""
from typing import List, Dict, TypedDict

class DebateState(TypedDict):
    messages: List[Dict[str, str]]
    current:  str
    phase:    str
    round:    int
    terminated: bool
