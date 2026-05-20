# save_onnx.py
from pathlib import Path
from optimum.onnxruntime import ORTModelForSequenceClassification
from transformers import AutoTokenizer

SAVE_PATH = Path(__file__).resolve().parent / "app" / "models" / "reranker-onnx"
SAVE_PATH.mkdir(parents=True, exist_ok=True)

print("Exporting model to ONNX...")
model = ORTModelForSequenceClassification.from_pretrained(
    "cross-encoder/ms-marco-MiniLM-L-6-v2",
    export=True
)
model.save_pretrained(str(SAVE_PATH))

print("Saving tokenizer...")
tokenizer = AutoTokenizer.from_pretrained("cross-encoder/ms-marco-MiniLM-L-6-v2")
tokenizer.save_pretrained(str(SAVE_PATH))
print(f"Done. Files: {list(SAVE_PATH.iterdir())}")