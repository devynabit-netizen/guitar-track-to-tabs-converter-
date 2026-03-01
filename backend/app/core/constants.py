"""Shared constants for project processing lifecycle."""
from enum import Enum


class ProjectStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETE = "complete"
    FAILED = "failed"


class ProjectErrorCode(str, Enum):
    PREPROCESSING_FAILED = "preprocessing_failed"
    TRANSCRIPTION_FAILED = "transcription_failed"
    TAB_GENERATION_FAILED = "tab_generation_failed"
    VERSION_PERSIST_FAILED = "version_persist_failed"
    UNKNOWN = "unknown"


TOTAL_PHASES = 5
PHASE_NAMES = {
    1: "uploaded",
    2: "preprocessing",
    3: "transcribing",
    4: "tab_generation",
    5: "finalizing",
}
