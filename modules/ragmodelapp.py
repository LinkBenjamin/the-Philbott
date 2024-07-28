import os
from langchain_community.llms import Ollama
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.chains import create_retrieval_chain
from langchain import hub
from langchain.chains.combine_documents import create_stuff_documents_chain

MODEL_ID = 'llama3.1'
BASE_URL = 'http://127.0.0.1:11434'
CHUNK_SIZE = 512
CHUNK_OVERLAP = 128

class RagModelApp:

    def __init__(self, input):
        self.input = input
        self.llm = Ollama(model=MODEL_ID, base_url=BASE_URL)
    
    def prepare_chain(self):

        # Create Vector Store Retriever
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
        chunks = text_splitter.split_text(self.input)
        embed_model = OllamaEmbeddings(model=MODEL_ID,
            base_url=BASE_URL
        )
        vsr = Chroma.from_texts(chunks, embed_model).as_retriever()
        retrieval_qa_chat_prompt = hub.pull("langchain-ai/retrieval-qa-chat")
        combine_docs_chain = create_stuff_documents_chain(
            self.llm, retrieval_qa_chat_prompt
        )
        
        self.retrieval_chain = create_retrieval_chain(vsr, combine_docs_chain)

    def invoke(self, command):
        response = self.retrieval_chain.invoke({"input": command})
        return response['answer']