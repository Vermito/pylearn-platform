from enum import Enum


class CourseLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class MaterialType(str, Enum):
    CHEATSHEET = "cheatsheet"
    PDF = "pdf"
    DOCUMENTATION = "documentation"
    BOOK = "book"
    VIDEO = "video"
    PROJECT = "project"


class TaskDifficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class TaskType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    PREDICT_OUTPUT = "predict_output"
    FIND_ERROR = "find_error"
    WRITE_CODE = "write_code"
    WRITE_FUNCTION = "write_function"
    PRACTICAL = "practical"


class QuestionType(str, Enum):
    SINGLE_CHOICE = "single_choice"
    MULTIPLE_CHOICE = "multiple_choice"