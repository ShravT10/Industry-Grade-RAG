# app/retrieval/reranker.py
import os
from pathlib import Path
from optimum.onnxruntime import ORTModelForSequenceClassification
from transformers import AutoTokenizer

# Path object handles Windows backslashes correctly
ONNX_PATH = Path(__file__).resolve().parent.parent / "models" / "reranker-onnx"

tokenizer = AutoTokenizer.from_pretrained(str(ONNX_PATH))
ort_model = ORTModelForSequenceClassification.from_pretrained(str(ONNX_PATH))


def rerank_results(query, results, top_k=5):
    pairs = [(query, result["text"]) for result in results]

    encoded = tokenizer(
        [q for q, _ in pairs],
        [p for _, p in pairs],
        padding=True,
        truncation=True,
        max_length=512,
        return_tensors="np"
    )

    outputs = ort_model(**encoded)
    scores = outputs.logits.flatten().tolist()

    reranked = []
    for result, score in zip(results, scores):
        result["rerank_score"] = float(score)
        reranked.append(result)

    reranked.sort(key=lambda x: x["rerank_score"], reverse=True)
    return reranked[:top_k]