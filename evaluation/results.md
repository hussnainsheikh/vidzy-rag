# Retrieval Evaluation Baseline

The initial configuration uses `sentence-transformers/all-MiniLM-L6-v2`, normalized embeddings, cosine-scored Chroma retrieval, a `0.68` direct-answer threshold, a `0.35` related-results threshold, a meaningful-term overlap safeguard, and a `0.035` ambiguity margin.

Measured on the 26-case dataset after a warm model load:

| Metric | Result |
| --- | ---: |
| Top-1 accuracy (supported questions) | 93.3% |
| Recall@3 | 100% |
| Recall@5 | 100% |
| Supported-query response rate | 93.3% |
| No-answer accuracy | 100% |
| False-positive rate | 0% |
| Ambiguous-query handling accuracy | 100% |
| Median retrieval latency | 22.03 ms |
| P95 retrieval latency | 30.67 ms |

Run `python -m evaluation.evaluate --output evaluation/results.local.json` after indexing to reproduce the benchmark. Latency is machine-dependent.

The dataset is intentionally broader than Phase 1 aliases: it contains exact canonical questions, newly written paraphrases, terminology variations, ambiguous prompts, unrelated prompts, and unsupported-product/no-answer prompts. No LLM is involved in scoring.

The one Top-1 miss is the terminology query “Can an offer message be scheduled over the player?” The correct popup results remain within the top three, but the confidence policy safely declines rather than returning the incorrect top candidate. This is preferable to lowering the threshold and increasing false positives; adding more reviewed popup phrasing is the clearest future improvement.
