from enum import Enum


class AgentStatus(str, Enum):
    """Agent status enumeration"""
    IDLE = "IDLE"
    PLANNING = "PLANNING"
    THINKING = "THINKING"
    EXECUTING = "EXECUTING"
    FINISHED = "FINISHED"
    ERROR = "ERROR"
