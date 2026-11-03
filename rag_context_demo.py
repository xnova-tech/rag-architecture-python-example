"""Поиск фрагмента и подготовка контекста для RAG; генератор не вызывается."""

import json
import re
from collections.abc import Sequence
from pathlib import Path
from typing import TypedDict


class Document(TypedDict):
    """Документ корпуса с устойчивым идентификатором и источником."""

    id: str
    source: str
    text: str


DOCUMENTS_PATH = Path(__file__).with_name("documents.json")
QUERY = "Что делать при HTTP 503 у API?"


def validate_documents(documents: Sequence[object]) -> list[Document]:
    """Проверить и нормализовать записи, загруженные из JSON."""
    validated: list[Document] = []
    ids: set[str] = set()

    for raw_document in documents:
        if not isinstance(raw_document, dict):
            raise ValueError("document must be an object")

        document_id = raw_document.get("id")
        source = raw_document.get("source")
        text = raw_document.get("text")
        if not isinstance(document_id, str) or not document_id:
            raise ValueError("document requires non-empty id, source and text")
        if not isinstance(source, str) or not source:
            raise ValueError("document requires non-empty id, source and text")
        if not isinstance(text, str) or not text:
            raise ValueError("document requires non-empty id, source and text")
        if document_id in ids:
            raise ValueError("duplicate document id")

        ids.add(document_id)
        validated.append({"id": document_id, "source": source, "text": text})

    return validated


def load_documents(path: Path = DOCUMENTS_PATH) -> list[Document]:
    """Загрузить JSON-массив и вернуть проверенные документы."""
    payload: object = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("document corpus must be a list")
    return validate_documents(payload)


def tokens(text: str) -> set[str]:
    """Выделить регистронезависимое множество Unicode-слов."""
    return set(re.findall(r"[^\W_]+", text.casefold()))


def retrieve(
    query: str,
    documents: Sequence[Document],
    k: int = 1,
) -> list[Document]:
    """Вернуть до k документов с ненулевым лексическим пересечением."""
    if k < 1:
        raise ValueError("k must be positive")

    validated = validate_documents(documents)
    query_tokens = tokens(query)
    scored = [(len(query_tokens & tokens(document["text"])), document) for document in validated]
    ranked = sorted(
        ((score, document) for score, document in scored if score > 0),
        key=lambda item: (-item[0], item[1]["id"]),
    )
    return [document for _, document in ranked[:k]]


def assemble_context(documents: Sequence[Document]) -> str:
    """Собрать контекст, сохранив идентификатор и источник фрагмента."""
    return "\n\n".join(f"[{document['id']}] {document['source']}\n{document['text']}" for document in documents)


def main() -> None:
    matches = retrieve(QUERY, load_documents())
    print(f"question: {QUERY}")
    if not matches:
        print("selected: none")
        print("context: empty")
    else:
        print(f"selected: {matches[0]['id']} ({matches[0]['source']})")
        print("context:")
        print(assemble_context(matches))
    print("generator_called: false")


if __name__ == "__main__":
    main()
