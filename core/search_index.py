from haystack.schema import Document
import uuid


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


def index(documents, pipeline):
    documents, doc_ids = format_docs(documents)
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
            match = {
                "text": res.content,
                "id": res.meta["id"],
                "fragment_id": res.id,
            }
            if not score_is_empty:
                match.update({"score": res.score})
            if hasattr(res, "content_audio"):
                match.update({"content_audio": res.content_audio})
            query_results.append(match)
        if not score_is_empty:
            query_results = sorted(
                query_results, key=lambda x: x["score"], reverse=True
            )
        results.append(query_results)
    return results
