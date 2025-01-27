"""
Haystack Pipelines
"""

import os
from pathlib import Path

from haystack import Pipeline
from haystack.document_stores import InMemoryDocumentStore
from haystack.nodes.preprocessor import PreProcessor
from haystack.nodes.ranker import SentenceTransformersRanker
from haystack.nodes.retriever import DensePassageRetriever, TfidfRetriever
from text2speech import DocumentToSpeech

data_path = "data/"
audio_path = os.path.join(data_path, "audio")
os.makedirs(data_path, exist_ok=True)
os.makedirs(audio_path, exist_ok=True)
# Ensure proper permissions
os.chmod(audio_path, 0o777)

index = "documents"

document_store = InMemoryDocumentStore(index=index)


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
        document_store = InMemoryDocumentStore(index=index)
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
            generated_audio_dir=Path(audio_path),
        )
        search_pipeline.add_node(
            doc2speech, name="DocumentToSpeech", inputs=["TfidfRetriever"]
        )

    return search_pipeline, index_pipeline


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
    document_store = InMemoryDocumentStore(index=index)
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
        document_to_speech = DocumentToSpeech(
            model_name_or_path="espnet/kan-bayashi_ljspeech_vits",
            generated_audio_dir=Path(audio_path),
        )
        search_pipeline.add_node(
            document_to_speech, name="DocumentToSpeech", inputs=["DPRRetriever"]
        )

    return search_pipeline, index_pipeline


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
        document_to_speech = DocumentToSpeech(
            model_name_or_path="espnet/kan-bayashi_ljspeech_vits",
            generated_audio_dir=Path(audio_path),
        )
        search_pipeline.add_node(
            document_to_speech, name="DocumentToSpeech", inputs=["Ranker"]
        )

    return search_pipeline, index_pipeline
