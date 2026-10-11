from dataclasses import dataclass
from enum import Enum


class JobState(str, Enum):
    queued = "queued"
    processing = "processing"
    succeeded = "succeeded"
    failed = "failed"


@dataclass(frozen=True)
class Asset:
    asset_id: str
    title: str
    creator_phone: str


@dataclass(frozen=True)
class ProcessingJob:
    job_id: str
    asset: Asset
    state: JobState


@dataclass(frozen=True)
class AlertResult:
    sent: bool
    message_id: str | None = None

