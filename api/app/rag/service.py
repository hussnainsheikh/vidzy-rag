from __future__ import annotations

from api.app.config import Settings
from api.app.generation import GenerationUnavailable, create_generator
from api.app.models.schemas import ChatResponse, RelatedQuestion, Source
from api.app.retrieval import RetrievalService, ScoredDocument
from api.app.retrieval.confidence import classify_confidence


NO_ANSWER = (
    "I couldn't find a reliable answer in Vidzy's verified public knowledge. "
    "Try rephrasing the question or ask about Vidzy videos, playback, engagement, leads, embeds, or analytics."
)


def public_source(item: ScoredDocument) -> Source:
    metadata = item.document.metadata
    return Source(
        id=str(metadata.get("question_id") or metadata.get("fact_id") or "public-knowledge"),
        label=str(metadata.get("canonical_question") or metadata.get("source_label") or "Vidzy product knowledge"),
        category=metadata.get("category"),
        document_type=str(metadata.get("document_type", "knowledge")),
    )


class RagService:
    def __init__(self, settings: Settings, retrieval: RetrievalService):
        self.settings = settings
        self.retrieval = retrieval

    def answer(self, question: str) -> ChatResponse:
        results = self.retrieval.retrieve(
            question,
            scope="public",
            limit=self.settings.retrieval_k,
            metadata_filter={"document_type": "canonical_question"},
        )
        if not results:
            return self._no_answer()

        top = results[0]
        outcome = classify_confidence(
            question,
            results,
            direct_threshold=self.settings.direct_answer_threshold,
            related_threshold=self.settings.related_results_threshold,
            ambiguity_margin=self.settings.ambiguity_margin,
        )
        related = [self._related(item) for item in results if item.score >= self.settings.related_results_threshold][:3]

        if outcome == "no_reliable_answer":
            return self._no_answer(top.score)

        if outcome == "related_results":
            return ChatResponse(
                answer="I found related verified information, but not one answer with enough confidence.",
                response_type="related_results",
                confidence=round(top.score, 4),
                sources=[public_source(item) for item in results[:3]],
                related=related,
                response_mode="retrieval",
                retrieval_details=self._debug(results),
            )

        answer = str(top.document.metadata["canonical_answer"])
        response_mode = "retrieval"
        if self.settings.rag_response_mode == "generative":
            try:
                generator = create_generator(self.settings)
                answer = generator.generate(question, [item.document for item in results[:3]])
                response_mode = "generative"
            except GenerationUnavailable:
                if not self.settings.llm_fallback_to_retrieval:
                    raise

        return ChatResponse(
            answer=answer,
            response_type="direct_answer",
            confidence=round(top.score, 4),
            sources=[public_source(top)],
            related=[item for item in related[1:3]],
            response_mode=response_mode,
            retrieval_details=self._debug(results),
        )

    def _no_answer(self, score: float = 0.0) -> ChatResponse:
        return ChatResponse(
            answer=NO_ANSWER,
            response_type="no_reliable_answer",
            confidence=round(score, 4),
            response_mode="retrieval",
        )

    @staticmethod
    def _related(item: ScoredDocument) -> RelatedQuestion:
        metadata = item.document.metadata
        return RelatedQuestion(
            question=str(metadata.get("canonical_question", "Related Vidzy information")),
            answer=metadata.get("canonical_answer"),
            score=round(item.score, 4),
            category=metadata.get("category"),
        )

    @staticmethod
    def _debug(results: list[ScoredDocument]) -> list[dict]:
        return [
            {
                "id": str(
                    item.document.metadata.get("question_id")
                    or item.document.metadata.get("fact_id")
                    or "public-knowledge"
                ),
                "label": item.document.metadata.get("canonical_question", "Public knowledge"),
                "score": round(item.score, 4),
                "category": item.document.metadata.get("category"),
                "document_type": str(item.document.metadata.get("document_type", "knowledge")),
            }
            for item in results[:5]
        ]
