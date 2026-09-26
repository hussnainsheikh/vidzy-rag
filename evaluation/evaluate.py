from __future__ import annotations

import argparse
import json
import statistics
import time
from collections import defaultdict
from pathlib import Path

from api.app.config import Settings
from api.app.embeddings import get_embeddings
from api.app.retrieval import RetrievalService
from api.app.retrieval.confidence import classify_confidence
from api.app.vectorstore import VectorStoreManager


ROOT = Path(__file__).resolve().parents[1]


def load_cases(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def evaluate(settings: Settings, dataset: Path) -> dict:
    service = RetrievalService(VectorStoreManager(settings, get_embeddings(settings.embedding_model, settings.embedding_device)))
    cases = load_cases(dataset)
    answerable = [case for case in cases if case["should_answer"]]
    no_answer = [case for case in cases if case["kind"] in {"no_answer", "out_of_domain"}]
    ambiguous_cases = [case for case in cases if case["kind"] == "ambiguous"]
    hits = {1: 0, 3: 0, 5: 0}
    no_answer_correct = 0
    false_positives = 0
    ambiguous_correct = 0
    supported_outcomes = 0
    latencies: list[float] = []
    by_kind: dict[str, list[bool]] = defaultdict(list)
    rows = []

    for case in cases:
        started = time.perf_counter()
        results = service.retrieve(case["query"], scope="public", limit=5, metadata_filter={"document_type": "canonical_question"})
        latencies.append((time.perf_counter() - started) * 1000)
        ids = [item.document.metadata.get("question_id") for item in results]
        top_score = results[0].score if results else 0.0
        expected = set(case["expected_question_ids"])
        outcome = classify_confidence(
            case["query"],
            results,
            direct_threshold=settings.direct_answer_threshold,
            related_threshold=settings.related_results_threshold,
            ambiguity_margin=settings.ambiguity_margin,
        )
        if case["should_answer"]:
            for k in hits:
                hits[k] += bool(expected.intersection(ids[:k]))
            by_kind[case["kind"]].append(bool(expected.intersection(ids[:1])))
            supported_outcomes += outcome != "no_reliable_answer"
        elif case["kind"] == "ambiguous":
            correctly_hedged = outcome != "direct_answer"
            ambiguous_correct += correctly_hedged
            by_kind[case["kind"]].append(correctly_hedged)
        else:
            rejected = outcome == "no_reliable_answer"
            no_answer_correct += rejected
            false_positives += not rejected
            by_kind[case["kind"]].append(rejected)
        rows.append({"id": case["id"], "top_id": ids[0] if ids else None, "score": round(top_score, 4)})

    return {
        "dataset_size": len(cases),
        "answerable": len(answerable),
        "no_answer_cases": len(no_answer),
        "ambiguous_cases": len(ambiguous_cases),
        "top_1_accuracy": round(hits[1] / len(answerable), 4),
        "recall_at_3": round(hits[3] / len(answerable), 4),
        "recall_at_5": round(hits[5] / len(answerable), 4),
        "supported_query_response_rate": round(supported_outcomes / len(answerable), 4),
        "no_answer_accuracy": round(no_answer_correct / len(no_answer), 4),
        "false_positive_rate": round(false_positives / len(no_answer), 4),
        "ambiguous_query_accuracy": round(ambiguous_correct / len(ambiguous_cases), 4),
        "latency_ms": {
            "median": round(statistics.median(latencies), 2),
            "p95": round(sorted(latencies)[max(0, int(len(latencies) * .95) - 1)], 2),
        },
        "thresholds": {
            "direct": settings.direct_answer_threshold,
            "related": settings.related_results_threshold,
            "ambiguity_margin": settings.ambiguity_margin,
        },
        "accuracy_by_kind": {kind: round(sum(values) / len(values), 4) for kind, values in by_kind.items()},
        "cases": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, default=ROOT / "evaluation" / "dataset.jsonl")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = evaluate(Settings(), args.dataset)
    rendered = json.dumps(result, indent=2)
    print(rendered)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
