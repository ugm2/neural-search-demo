import uuid

from haystack.document_stores import BaseDocumentStore
from haystack.schema import Document


def format_docs(documents):
    """Given a list of documents, format the documents and return the documents and doc ids."""
    db_docs: list = []
    for doc in documents:
        doc_id = doc["id"] if doc["id"] is not None else str(uuid.uuid4())
        db_doc = {
            "content": doc["text"],
            "content_type": "text",
            "id": str(uuid.uuid4()),
            "meta": {"id": doc_id},
        }
        db_docs.append(Document(**db_doc))
    return db_docs, [doc.meta["id"] for doc in db_docs]


def index(documents, pipeline, clear_index=True):
    documents, doc_ids = format_docs(documents)
    if clear_index:
        document_stores = pipeline.get_nodes_by_class(class_type=BaseDocumentStore)
        for docstore in document_stores:
            docstore.delete_index(docstore.index)
    pipeline.run(documents=documents)
    return doc_ids


def search(queries, pipeline):
    results = []
    matches_queries = pipeline.run_batch(queries=queries)
    for matches in matches_queries["documents"]:
        query_results = []
        score_is_empty = False
        for res in matches:
            if not score_is_empty:
                score_is_empty = True if res.score is None else False

            # Get the original text from content or meta
            original_text = res.content
            if hasattr(res, "meta") and "content_text" in res.meta:
                original_text = res.meta["content_text"]

            match = {
                "text": original_text,
                "id": res.meta["id"],
                "fragment_id": res.id,
                "meta": res.meta,
            }
            if not score_is_empty:
                match.update({"score": res.score})
            if res.content_type == "audio":
                # Add audio path from the content field
                match.update({"content_audio": res.content})
            query_results.append(match)
        if not score_is_empty:
            query_results = sorted(
                query_results, key=lambda x: x["score"], reverse=True
            )
        results.append(query_results)
    return results
