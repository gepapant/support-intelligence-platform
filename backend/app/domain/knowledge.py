from enum import Enum


class KnowledgeIndexStatus(str, Enum):
    queued = "queued"
    indexing = "indexing"
    ready = "ready"
    failed = "failed"
