import os
import json
from datasets import Dataset
import numpy as np

from ragas import evaluate
from ragas.metrics import (
    answer_relevancy,
    faithfulness,
    context_precision,
    context_recall,
)

# ---- LangChain + Hugging Face setup ----
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace

from langchain_community.embeddings import HuggingFaceEmbeddings

from dotenv import load_dotenv
load_dotenv()

HF_TOKEN = os.getenv("HF_API_KEY")
if not HF_TOKEN:
    raise RuntimeError("HF_API_KEY is not set in environment")


# Build an LLM that uses the SAME HF model as your chatbot
base_llm = HuggingFaceEndpoint(
    repo_id="meta-llama/Meta-Llama-3-8B-Instruct",
    huggingfacehub_api_token=HF_TOKEN,
    temperature=0.0,      # <-- moved out of model_kwargs
    max_new_tokens=1024,   # <-- moved out of model_kwargs
)


# Wrap in a ChatModel for RAGAS / LangChain
eval_llm = ChatHuggingFace(llm=base_llm)

# Embeddings used for similarity-based metrics
eval_embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


def load_ragas_dataset(jsonl_path: str) -> Dataset:
    """
    Load a RAGAS-style dataset from JSONL.
    Each line must contain: question, answer, contexts (list[str]), optional ground_truth.
    """
    questions = []
    answers = []
    contexts = []
    ground_truths = []

    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            data = json.loads(line)

            q = data["question"]
            a = data["answer"]

            c = data.get("contexts", [])
            if isinstance(c, str):
                # naive split – adapt if your format differs
                c = [p.strip() for p in c.split("\n\n") if p.strip()]

            gt = data.get("ground_truth", "")

            questions.append(q)
            answers.append(a)
            contexts.append(c)
            ground_truths.append(gt)

    ds_dict = {
        "question": questions,
        "answer": answers,
        "contexts": contexts,
    }

    # ground_truth is optional and not required for the metrics we use,
    # but we include it if present.
    if any(gt.strip() for gt in ground_truths):
        ds_dict["ground_truth"] = ground_truths

    return Dataset.from_dict(ds_dict)


def main():
    jsonl_path = "ragas_data.jsonl"  # adjust if needed
    dataset = load_ragas_dataset(jsonl_path)

    metrics = [
        answer_relevancy,
        faithfulness,
        context_precision,
        context_recall,
    ]

    print(f"Running RAGAS evaluation on {len(dataset)} samples...")

    result = evaluate(
        dataset=dataset,
        metrics=metrics,
        llm=eval_llm,           # <-- LangChain ChatHuggingFace
        embeddings=eval_embeddings,  # <-- LangChain HF embeddings
    )

    print("\n===== RAGAS METRICS (AGGREGATED) =====")
    for m in metrics:
        m_name = m.name if hasattr(m, "name") else m.__name__
        values = np.array(result[m_name], dtype=float)
        score = float(np.nanmean(values)) if values.size > 0 else float("nan")

        print(f"{m_name}: {score:.4f}")

    print("\n===== SAMPLE-LEVEL SCORES (first 5) =====")
    num_samples = len(dataset)
    for i in range(min(5, num_samples)):
        print(f"\nSample {i + 1}")
        print("Q:", dataset["question"][i])
        print("A:", dataset["answer"][i])
        for m in metrics:
            m_name = m.name if hasattr(m, "name") else m.__name__
            value_i = result[m_name][i]  # i-th score from list
            print(f"  {m_name}: {value_i:.4f}")


if __name__ == "__main__":
    main()
