"""Pytest-контракт детерминированного поиска и сборки контекста."""

from pathlib import Path

import pytest
from rag_context_demo import (
    QUERY,
    Document,
    assemble_context,
    load_documents,
    retrieve,
    tokens,
    validate_documents,
)


@pytest.fixture
def documents() -> list[Document]:
    return load_documents()


def test_503_selects_runbook_with_source(documents: list[Document]) -> None:
    result = retrieve(QUERY, documents)

    assert [(item["id"], item["source"]) for item in result] == [("d01", "runbooks/api-503.md")]
    assert "HTTP 503" in assemble_context(result)


def test_no_match_does_not_invent_context(documents: list[Document]) -> None:
    assert retrieve("Расписание поездов", documents) == []
    assert assemble_context([]) == ""


def test_lexical_search_misses_paraphrase(documents: list[Document]) -> None:
    assert retrieve("Шлюз временно недоступен", documents) == []


def test_ties_order_by_document_id(documents: list[Document]) -> None:
    result = retrieve("API", documents, k=3)

    assert [item["id"] for item in result] == ["d01", "d04", "d05"]


def test_duplicate_document_id_rejected(documents: list[Document]) -> None:
    duplicate = dict(documents[0])

    with pytest.raises(ValueError, match="duplicate document id"):
        validate_documents([*documents, duplicate])


def test_invalid_document_shape_rejected() -> None:
    with pytest.raises(ValueError, match="non-empty id, source and text"):
        validate_documents([{"id": "d06", "source": "", "text": "empty source"}])
    with pytest.raises(ValueError, match="document must be an object"):
        validate_documents(["not a document"])


def test_non_list_corpus_rejected(tmp_path: Path) -> None:
    corpus = tmp_path / "documents.json"
    corpus.write_text('{"id": "d01"}', encoding="utf-8")

    with pytest.raises(ValueError, match="document corpus must be a list"):
        load_documents(corpus)


def test_invalid_k_rejected(documents: list[Document]) -> None:
    with pytest.raises(ValueError, match="k must be positive"):
        retrieve(QUERY, documents, k=0)


def test_tokenization_preserves_unicode_words() -> None:
    assert tokens("HTTP-503, Ошибка API") == {"http", "503", "ошибка", "api"}


def test_context_preserves_source_and_content(documents: list[Document]) -> None:
    context = assemble_context(retrieve(QUERY, documents))

    assert context.startswith("[d01] runbooks/api-503.md\n")
    assert "ответ языковой модели" not in context
