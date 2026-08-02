from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.nlp import safety_check


@dataclass
class Chunk:
    text: str
    source: str
    section: str


def load_demo_chunks(folder: Path) -> list[Chunk]:
    chunks: list[Chunk] = []
    for path in folder.glob("*.txt"):
        paragraphs = [p.strip() for p in re.split(r"\n+", path.read_text(encoding="utf-8")) if len(p.strip()) > 25]
        chunks.extend(Chunk(text=p, source=path.name, section=f"line {i + 1}") for i, p in enumerate(paragraphs))
    return chunks


def retrieve(question: str, chunks: list[Chunk], top_k: int = 3) -> list[tuple[Chunk, float]]:
    if not chunks:
        return []
    vectorizer = TfidfVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform([c.text for c in chunks] + [question])
    scores = cosine_similarity(matrix[-1], matrix[:-1]).ravel()
    indices = scores.argsort()[::-1][:top_k]
    return [(chunks[i], float(scores[i])) for i in indices if scores[i] > 0]


def answer(question: str, chunks: list[Chunk]) -> dict:
    allowed, refusal = safety_check(question)
    if not allowed:
        return {"answer": refusal, "citations": [], "mode": "safety refusal"}
    matches = retrieve(question, chunks)
    if not matches:
        return {"answer": "I could not find that information in the available records.", "citations": [], "mode": "local retrieval"}
    citations = [f"{item.source} · {item.section}" for item, _ in matches]
    context = "\n".join(f"[{i+1}] {item.text}" for i, (item, _) in enumerate(matches))
    if os.getenv("OPENAI_API_KEY"):
        try:
            from langchain_openai import ChatOpenAI
            model = ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"), temperature=0)
            prompt = f"""You are CareBridge, a non-diagnostic medical administration assistant.
Answer only from the context. Do not diagnose, recommend treatment, or advise medication changes.
If unclear, say so. Cite statements using [1], [2], etc.\n\nContext:\n{context}\n\nQuestion: {question}"""
            response = model.invoke(prompt)
            return {"answer": str(response.content), "citations": citations, "mode": "LangChain + OpenAI"}
        except Exception:
            pass
    return {"answer": matches[0][0].text, "citations": citations[:1], "mode": "local TF-IDF retrieval"}

