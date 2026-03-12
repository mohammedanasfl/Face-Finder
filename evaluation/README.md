Create a small labeled file at `evaluation/sample-eval.json` with records like:

```json
[
  {
    "query": "queries/person-a-1.jpg",
    "expected_matches": ["event-photo-a.jpg"],
    "scores": [
      { "filename": "event-photo-a.jpg", "score": 0.82 },
      { "filename": "event-photo-b.jpg", "score": 0.31 }
    ]
  }
]
```

Run:

```bash
python src/evaluate_search.py evaluation/sample-eval.json --threshold 0.40
```

Use this to compare hit rate as you adjust `SEARCH_SIMILARITY_THRESHOLD`.
