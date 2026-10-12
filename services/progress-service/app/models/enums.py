from enum import Enum


class SubmissionStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    ERROR = "error"
    TIMEOUT = "timeout"


class ProgressStatus(str, Enum):
    LOCKED = "locked"
    AVAILABLE = "available"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"