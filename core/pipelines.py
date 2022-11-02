"""
Haystack Pipelines
"""

from pathlib import Path
from haystack import Pipeline
from haystack.document_stores import InMemoryDocumentStore, ElasticsearchDocumentStore
from haystack.nodes.retriever import (
    DensePassageRetriever,
    TfidfRetriever,
    BM25Retriever,
)
from haystack.nodes.preprocessor import PreProcessor
from haystack.nodes.ranker import SentenceTransformersRanker
from haystack.nodes.audio.document_to_speech import DocumentToSpeech
import logging
import os
from time import sleep

from core.elasticsearch import CustomElasticSearchContainer
from core.utils import is_pipeline


logger = logging.getLogger("Neural Search Demo - Pipelines")
logger.setLevel(os.environ.get("LOGGER_LEVEL", logging.WARNING))

data_path = "data/"
os.makedirs(data_path, exist_ok=True)

index = "documents"
es_host = "127.0.0.1"
es_port = 9200

es = CustomElasticSearchContainer(
    image="docker.elastic.co/elasticsearch/elasticsearch:7.9.2",
    port_to_expose=es_port,
    name="elasticsearch_neural",
)
es.start_if_not_running()


def init_document_store(document_store, index, initial_rump_up_time=20):
    # Try instantiating of Elasticsearch Document Store or default to InMemoryDocumentStore
    try:
        document_store = ElasticsearchDocumentStore(
            host=es_host, port=es_port, index=index
        )
    except Exception as e:
        logger.info(
            f"First connection to Elasticsearch failed. Waiting {initial_rump_up_time} seconds for the initial ramp up"
        )
        sleep(initial_rump_up_time)
        try:
            document_store = ElasticsearchDocumentStore(
                host=es_host, port=es_port, index=index
            )
            logger.info("Elasticsearch connected")
        except Exception as e:
            logger.error(f"Error loading the ElasticsearchDocumentStore. Detail: {e}")

            document_store = InMemoryDocumentStore(index=index)
    return document_store


document_store = init_document_store(None, index)


@is_pipeline
def keyword_search(
    index="documents", split_word_length=100, top_k=10, audio_output=False
):
    """
    **Keyword Search Pipeline**

    It looks for words in the documents that match the query by using TF-IDF.

    TF-IDF is a commonly used baseline for information retrieval that exploits two key intuitions:

      - Documents that have more lexical overlap with the query are more likely to be relevant
      - Words that occur in fewer documents are more significant than words that occur in many documents
    """
    global document_store
    if index != document_store.index:
        document_store = init_document_store(document_store, index)

    if isinstance(document_store, ElasticsearchDocumentStore):
        keyword_retriever = BM25Retriever(document_store=(document_store), top_k=top_k)
    else:
        keyword_retriever = TfidfRetriever(document_store=(document_store), top_k=top_k)
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

    if audio_output:
        doc2speech = DocumentToSpeech(
            model_name_or_path="espnet/kan-bayashi_ljspeech_vits",
            generated_audio_dir=Path(data_path + "audio"),
        )
        search_pipeline.add_node(
            doc2speech, name="DocumentToSpeech", inputs=["TfidfRetriever"]
        )

    return search_pipeline, index_pipeline


@is_pipeline
def dense_passage_retrieval(
    index="documents",
    split_word_length=100,
    query_embedding_model="facebook/dpr-question_encoder-single-nq-base",
    passage_embedding_model="facebook/dpr-ctx_encoder-single-nq-base",
    top_k=10,
    audio_output=False,
):
    """
    **Dense Passage Retrieval Pipeline**

    Dense Passage Retrieval is a highly performant retrieval method that calculates relevance using dense representations. Key features:

      - One BERT base model to encode documents
      - One BERT base model to encode queries
      - Ranking of documents done by dot product similarity between query and document embeddings
    """
    global document_store
    if index != document_store.index:
        document_store = init_document_store(document_store, index)
    dpr_retriever = DensePassageRetriever(
        document_store=document_store,
        query_embedding_model=query_embedding_model,
        passage_embedding_model=passage_embedding_model,
        top_k=top_k,
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

    if audio_output:
        doc2speech = DocumentToSpeech(
            model_name_or_path="espnet/kan-bayashi_ljspeech_vits",
            generated_audio_dir=Path(data_path + "audio"),
        )
        search_pipeline.add_node(
            doc2speech, name="DocumentToSpeech", inputs=["DPRRetriever"]
        )

    return search_pipeline, index_pipeline


@is_pipeline
def dense_passage_retrieval_ranker(
    index="documents",
    split_word_length=100,
    query_embedding_model="facebook/dpr-question_encoder-single-nq-base",
    passage_embedding_model="facebook/dpr-ctx_encoder-single-nq-base",
    ranker_model="cross-encoder/ms-marco-MiniLM-L-12-v2",
    top_k=10,
    audio_output=False,
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
        top_k=top_k,
    )
    ranker = SentenceTransformersRanker(model_name_or_path=ranker_model, top_k=top_k)

    search_pipeline.add_node(ranker, name="Ranker", inputs=["DPRRetriever"])

    if audio_output:
        doc2speech = DocumentToSpeech(
            model_name_or_path="espnet/kan-bayashi_ljspeech_vits",
            generated_audio_dir=Path(data_path + "audio"),
        )
        search_pipeline.add_node(doc2speech, name="DocumentToSpeech", inputs=["Ranker"])

    return search_pipeline, index_pipeline
