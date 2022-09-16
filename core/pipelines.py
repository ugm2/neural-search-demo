"""
Haystack Pipelines
"""

from haystack import Pipeline
from haystack.document_stores import InMemoryDocumentStore
from haystack.nodes.retriever import DensePassageRetriever, TfidfRetriever
from haystack.nodes.preprocessor import PreProcessor
from haystack.nodes.ranker import SentenceTransformersRanker


def keyword_search(
    index="documents",
):
    document_store = InMemoryDocumentStore(index=index)
    keyword_retriever = TfidfRetriever(document_store=(document_store))
    processor = PreProcessor(
        clean_empty_lines=True,
        clean_whitespace=True,
        clean_header_footer=True,
        split_by="word",
        split_length=100,
        split_respect_sentence_boundary=True,
        split_overlap=0,
    )
    # SEARCH PIPELINE
    search_pipeline = Pipeline()
    search_pipeline.add_node(keyword_retriever, name="TfidfRetriever", inputs=["Query"])

    # INDEXING PIPELINE
    index_pipeline = Pipeline()
    index_pipeline.add_node(processor, name="Preprocessor", inputs=["File"])
    index_pipeline.add_node(
        keyword_retriever, name="TfidfRetriever", inputs=["Preprocessor"]
    )
    index_pipeline.add_node(
        document_store, name="DocumentStore", inputs=["TfidfRetriever"]
    )

    return search_pipeline, index_pipeline


def dense_passage_retrieval(
    index="documents",
    query_embedding_model="facebook/dpr-question_encoder-single-nq-base",
    passage_embedding_model="facebook/dpr-ctx_encoder-single-nq-base",
):
    document_store = InMemoryDocumentStore(index=index)
    dpr_retriever = DensePassageRetriever(
        document_store=document_store,
        query_embedding_model=query_embedding_model,
        passage_embedding_model=passage_embedding_model,
    )
    processor = PreProcessor(
        clean_empty_lines=True,
        clean_whitespace=True,
        clean_header_footer=True,
        split_by="word",
        split_length=100,
        split_respect_sentence_boundary=True,
        split_overlap=0,
    )
    # SEARCH PIPELINE
    search_pipeline = Pipeline()
    search_pipeline.add_node(dpr_retriever, name="DPRRetriever", inputs=["Query"])

    # INDEXING PIPELINE
    index_pipeline = Pipeline()
    index_pipeline.add_node(processor, name="Preprocessor", inputs=["File"])
    index_pipeline.add_node(dpr_retriever, name="DPRRetriever", inputs=["Preprocessor"])
    index_pipeline.add_node(
        document_store, name="DocumentStore", inputs=["DPRRetriever"]
    )

    return search_pipeline, index_pipeline


def dense_passage_retrieval_ranker(
    index="documents",
    query_embedding_model="facebook/dpr-question_encoder-single-nq-base",
    passage_embedding_model="facebook/dpr-ctx_encoder-single-nq-base",
    ranker_model="cross-encoder/ms-marco-MiniLM-L-12-v2",
):
    search_pipeline, index_pipeline = dense_passage_retrieval(
        index=index,
        query_embedding_model=query_embedding_model,
        passage_embedding_model=passage_embedding_model,
    )
    ranker = SentenceTransformersRanker(model_name_or_path=ranker_model)

    search_pipeline.add_node(ranker, name="Ranker", inputs=["DPRRetriever"])

    return search_pipeline, index_pipeline
