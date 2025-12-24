from time import perf_counter

from langchain_classic.chains.constitutional_ai.prompts import revision_example
from langchain_classic.chains.retrieval_qa.base import RetrievalQA

from langchain_classic.retrievers import ParentDocumentRetriever
# WebBaseLoader USER_AGENT environment variable not set
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.stores import InMemoryStore
from langchain_ollama import OllamaLLM, OllamaEmbeddings
from langchain_text_splitters import CharacterTextSplitter, RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

from setup import get_embed, get_llm


def check_embedding(
    doc_link="https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/96-FDF8f7coh0ooim7NyEQ/langchain-paper.pdf",
):
    loader = PyPDFLoader(doc_link)

    document = loader.load()

    text_splitter = CharacterTextSplitter(
        chunk_size=200, chunk_overlap=20, separator="\n"
    )

    chunks = text_splitter.split_documents(document)

    texts = [text.page_content for text in chunks]

    embedding_model = get_embed()
    embedding_result = embedding_model.embed_documents(texts)

    #? Trying Vector Store
    docsearch = Chroma.from_documents(chunks, embedding_model)

    query = "What is the issue of mental health?"

    docs = docsearch.similarity_search(query)
    for doc in docs:
        print(doc)

    print("="*10)
    retriever = docsearch.as_retriever()

    # ? Trying Retrievers
    docs = retriever.invoke("Mental Health")
    for doc in docs:
        print(doc)
    print("="*10)

    #? Parent Document Retriever
    # Strikes balance by splitting and storing small chunks of data. During retrieval, this retriever first fetches the small chunks, but then looks up the parent IDs for the data and returns those larger documents.
    # This is used to split documents into larger, more contextually complete sections
    parent_splitter = CharacterTextSplitter(chunk_size=2000, chunk_overlap=20, separator="\n")

    # This is used to split the parent chunks into smaller pieces for more precise retrieval
    child_splitter = CharacterTextSplitter(chunk_size=400, chunk_overlap=20, separator='\n')

    vectorstore = Chroma(
        collection_name="split_parents", embedding_function=embedding_model
    )

    # Set up an in-memory storage layer for the parent documents
    # This will store the larger chunks that provide context, but won't be directly embedded
    store = InMemoryStore()

    retriever = ParentDocumentRetriever(
        # The vector store where child document embeddings will be stored and searched
        # This Chroma instance will contain the embeddings for the smaller chunks
        vectorstore=vectorstore,
        # The document store where parent documents will be stored
        # These larger chunks won't be embedded but will be retrieved by ID when needed
        docstore=store,
        # The splitter used to create small chunks (400 chars) for precise vector search
        # These smaller chunks are embedded and used for similarity matching
        child_splitter=child_splitter,
        # The splitter used to create larger chunks (2000 chars) for better context
        # These parent chunks provide more complete information when retrieved
        parent_splitter=parent_splitter,
    )

    retriever.add_documents(document)
    query = "mental health"
    print("Number of parent docs", len(list(store.yield_keys())))
    sub_docs = vectorstore.similarity_search(query)
    print("== Top sub doc:", sub_docs[0].page_content)
    retrieved_docs = retriever.invoke(query)
    print("== Top main doc:", retrieved_docs[0].page_content)
    print("="*10)
    #? QA Retrieval
    llm = get_llm()

    qa = RetrievalQA.from_chain_type(
        llm=llm,
        # The chain type "stuff" means all retrieved documents are simply concatenated and passed to the LLM
        chain_type="stuff",
        retriever=docsearch.as_retriever(),
        return_source_documents=False
    )

    query = "what is this paper discussing?"
    resp = qa.invoke(query)
    print(resp)

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def simple_retrieval_system(simple=True):
    # Load doc and split into chunks for RAG
    loader = WebBaseLoader("https://python.langchain.com/v0.2/docs/introduction/")

    # loader = PyPDFLoader("https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/96-FDF8f7coh0ooim7NyEQ/langchain-paper.pdf")
    document = loader.load()


    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=20, separator=["\n\n", "\n", ". ", " ", ""] )
    chunks = text_splitter.split_documents(document)

    # Embed doc into vector and store in RAG
    embedding_model: OllamaEmbeddings = get_embed()
    vector_store = Chroma.from_documents(chunks, embedding_model)
    retriever = vector_store.as_retriever(search_kwargs={"k": 4})

    template = """Answer the question based only on the following context:
    Context: {context}
    Question: {question}
    """

    prompt = ChatPromptTemplate(template)

    print("=" * 10)
    if simple:
        # Create and run simple retriever
        respo = retriever.invoke("Mental Health")
        for re in respo:
            print(re.page_content)
            print("-"*10)
    else:
        # Create and run QA retriever
        llm: OllamaLLM = get_llm()

        qa_retriever = RetrievalQA.from_chain_type(
            llm=llm,
            # # The chain type "stuff" means all retrieved documents are simply concatenated and passed to the LLM
            # chain_type="stuff",
            retriever=vector_store.as_retriever(),
            return_source_documents=False
        )

        query = "what is this document discussing?"

        resp = qa_retriever.invoke(query)
        print(resp)






if __name__ == "__main__":
    start = perf_counter()
    # check_embedding()
    simple_retrieval_system(simple=False)
    end = perf_counter()
    print(f"Total time: {end - start}")
    print("done")
