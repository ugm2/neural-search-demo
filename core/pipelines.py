"""
Haystack Pipelines
"""

from haystack import Pipeline
from haystack.document_stores import InMemoryDocumentStore
from haystack.nodes.retriever import DensePassageRetriever, TfidfRetriever
from haystack.nodes.preprocessor import PreProcessor
from haystack.nodes.ranker import SentenceTransformersRanker


def keyword_search(index="documents", split_word_length=100):
    """
    **Keyword Search Pipeline**

    It looks for words in the documents that match the query by using TF-IDF.

    TF-IDF is a commonly used baseline for information retrieval that exploits two key intuitions:

      - Documents that have more lexical overlap with the query are more likely to be relevant
      - Words that occur in fewer documents are more significant than words that occur in many documents

    :warning: **(HAYSTACK BUG) Keyword Search doesn't work if you reindex:** Please refresh page in order to reindex
    """
    document_store = InMemoryDocumentStore(index=index)
    keyword_retriever = TfidfRetriever(document_store=(document_store))
    processor = PreProcessor(
        clean_empty_lines=True,
        clean_whitespace=True,
        clean_header_footer=True,
        split_by="word",
        split_length=split_word_length,
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
        document_store, name="DocumentStore", inputs=["Preprocessor"]
    )

    return search_pipeline, index_pipeline


def dense_passage_retrieval(
    index="documents",
    split_word_length=100,
    query_embedding_model="facebook/dpr-question_encoder-single-nq-base",
    passage_embedding_model="facebook/dpr-ctx_encoder-single-nq-base",
):
    """
    **Dense Passage Retrieval Pipeline**

    Dense Passage Retrieval is a highly performant retrieval method that calculates relevance using dense representations. Key features:

      - One BERT base model to encode documents
      - One BERT base model to encode queries
      - Ranking of documents done by dot product similarity between query and document embeddings
    """
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
        split_length=split_word_length,
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
    split_word_length=100,
    query_embedding_model="facebook/dpr-question_encoder-single-nq-base",
    passage_embedding_model="facebook/dpr-ctx_encoder-single-nq-base",
    ranker_model="cross-encoder/ms-marco-MiniLM-L-12-v2",
):
    """
    **Dense Passage Retrieval Ranker Pipeline**

    It adds a Ranker to the `Dense Passage Retrieval Pipeline`.

      - A Ranker reorders a set of Documents based on their relevance to the Query.
      - It is particularly useful when your Retriever has high recall but poor relevance scoring.
      - The improvement that the Ranker brings comes at the cost of some additional computation time.
    """
    search_pipeline, index_pipeline = dense_passage_retrieval(
        index=index,
        split_word_length=split_word_length,
        query_embedding_model=query_embedding_model,
        passage_embedding_model=passage_embedding_model,
    )
    ranker = SentenceTransformersRanker(model_name_or_path=ranker_model)

    search_pipeline.add_node(ranker, name="Ranker", inputs=["DPRRetriever"])

    return search_pipeline, index_pipeline
