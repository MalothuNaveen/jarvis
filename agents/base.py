# ============================================================
#  agents/base.py  —  Base class all agents inherit from
# ============================================================

from abc import ABC, abstractmethod


class BaseAgent(ABC):
    """
    Every JARVIS agent must implement execute().

    Parameters
    ----------
    intent : str   — One-sentence description of what to do
    params : dict  — Structured parameters extracted by the Orchestrator
    raw    : str   — Original raw voice command text

    Returns str response (shown + spoken by Orchestrator).
    """

    @property
    @abstractmethod
    def agent_id(self) -> str:
        ...

    @abstractmethod
    async def execute(self, intent: str, params: dict, raw: str) -> str:
        ...

    def __repr__(self):
        return f"<Agent:{self.agent_id}>"
