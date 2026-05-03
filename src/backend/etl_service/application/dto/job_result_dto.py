from dataclasses import dataclass


@dataclass(frozen=True)
class ImportRawPublicationsResultDTO:
    sources_seen: int
    publications_seen: int
    publications_created: int
    publications_skipped: int


@dataclass(frozen=True)
class NormalizeRumorsResultDTO:
    sources_seen: int
    publications_seen: int
    rumors_created: int
    publications_skipped: int
