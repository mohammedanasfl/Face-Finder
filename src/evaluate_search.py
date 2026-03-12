import argparse
import json
import os


def load_dataset(dataset_path: str):
    with open(dataset_path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def evaluate(dataset, threshold: float):
    total = len(dataset)
    hits = 0
    false_negatives = 0

    for item in dataset:
        scores = item.get("scores", [])
        expected = set(item.get("expected_matches", []))
        predicted = {entry["filename"] for entry in scores if entry["score"] >= threshold}

        if expected & predicted:
            hits += 1
        elif expected:
            false_negatives += 1

    hit_rate = (hits / total) if total else 0.0
    return {
        "queries": total,
        "threshold": threshold,
        "hit_rate": round(hit_rate, 4),
        "false_negatives": false_negatives,
    }


def main():
    parser = argparse.ArgumentParser(description="Evaluate search threshold against a small labeled dataset.")
    parser.add_argument("dataset", help="Path to evaluation JSON file")
    parser.add_argument("--threshold", type=float, default=0.40, help="Similarity threshold to evaluate")
    args = parser.parse_args()

    dataset = load_dataset(args.dataset)
    summary = evaluate(dataset, args.threshold)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
