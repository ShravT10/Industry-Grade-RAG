# app/retrieval/reranker.py
import os
import numpy as np
from pathlib import Path
from transformers import AutoTokenizer
import onnxruntime as ort

ONNX_PATH = Path(__file__).resolve().parent.parent / "models" / "reranker-onnx"
MODEL_FILE = str(ONNX_PATH / "model.onnx")

tokenizer = AutoTokenizer.from_pretrained(str(ONNX_PATH))
session = ort.InferenceSession(MODEL_FILE, providers=["CPUExecutionProvider"])


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

    # onnxruntime expects plain numpy int64
    inputs = {
        "input_ids": encoded["input_ids"].astype(np.int64),
        "attention_mask": encoded["attention_mask"].astype(np.int64),
        "token_type_ids": encoded["token_type_ids"].astype(np.int64),
    }

    outputs = session.run(None, inputs)
    scores = outputs[0].flatten().tolist()

    reranked = []
    for result, score in zip(results, scores):
        result["rerank_score"] = float(score)
        reranked.append(result)

    reranked.sort(key=lambda x: x["rerank_score"], reverse=True)
    return reranked[:top_k]