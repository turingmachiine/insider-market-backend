import re

from src.etl_service.application.dto import RawPublicationDTO, SourceDTO
from src.etl_service.domain.entities import NormalizedRumorCandidate


class RuleBasedRumorExtractor:
    _KEYWORD_RULES = {
        "transfer": (
            "трансфер",
            "перейдет",
            "перешел",
            "подпишет",
            "подписал",
            "аренда",
            "контракт",
        ),
        "coach": ("тренер", "уволен", "назначен", "возглавит", "отставка"),
        "conflict": ("конфликт", "скандал", "ссора", "разногласия"),
        "injury": ("травма", "повреждение", "выбыл"),
    }

    def extract(
        self,
        publication: RawPublicationDTO,
        source: SourceDTO,
    ) -> list[NormalizedRumorCandidate]:
        normalized_text = self._normalize_text(publication.text)
        tags = self._extract_tags(normalized_text)
        if not tags:
            return []

        confidence_score = self._confidence_score(source.weight, tags)
        title = self._title_from_text(publication.text)
        return [
            NormalizedRumorCandidate(
                source_id=publication.source_id,
                title=title,
                text=publication.text,
                normalized_text=normalized_text,
                raw_publication_id=publication.id,
                confidence_score=confidence_score,
                tags=tags,
                event_candidate_payload={
                    "source_name": source.name,
                    "rules_matched": tags,
                    "extractor": "rule_based_v1",
                },
            )
        ]

    @classmethod
    def _extract_tags(cls, normalized_text: str) -> list[str]:
        tags = []
        for tag, keywords in cls._KEYWORD_RULES.items():
            if any(keyword in normalized_text for keyword in keywords):
                tags.append(tag)
        return tags

    @staticmethod
    def _normalize_text(text: str) -> str:
        return re.sub(r"\s+", " ", text.strip().lower())

    @staticmethod
    def _title_from_text(text: str) -> str:
        title = re.split(r"[.!?\n]", text.strip(), maxsplit=1)[0].strip()
        return title[:120] or text.strip()[:120]

    @staticmethod
    def _confidence_score(source_weight: float, tags: list[str]) -> float:
        base_score = 0.35 + min(source_weight, 10.0) / 20.0
        tag_bonus = min(len(tags) * 0.05, 0.15)
        return min(base_score + tag_bonus, 1.0)
