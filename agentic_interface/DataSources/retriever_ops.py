# Upload documents to Pinecone Database

# Libraries
from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
from langchain_huggingface import HuggingFaceEmbeddings

# Constants
INDEX = 'podcastTranscripts'

# Initialize embeddings model once at module level (global variable)
# This avoids repeated HuggingFace API calls and prevents 429 rate limiting errors
_embeddings = None

def get_embeddings():
    """Lazy initialization of embeddings model - only loads once"""
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/bert-large-nli-stsb-mean-tokens')
    return _embeddings

class PineconeClass:
    def __init__(self, key):
        try:
            # Initialize Pinecone client
            self.pc = Pinecone(api_key = key)
            self.index = self.pc.Index(host = "https://ourahuberman-2qajcgl.svc.aped-4627-b74a.pinecone.io")
            # Use global embeddings instance (loaded once)
            self.embeddings = get_embeddings()
            self.vector_store = PineconeVectorStore(embedding = self.embeddings, index = self.index)
        except RuntimeError as r:
            # This is an internal endpoint - users do not need to provide any information
            # Build out further exceptions to handle connection errors, etc.
            raise RuntimeError("Pinecone Server Error")

    def insert(self, docs):
        _ = self.vector_store.add_documents(namespace = INDEX,documents = docs)

    def search(self, query):
        index = self.index

        # Convert query to vector space using embeddings model
        query_vec = self.embeddings.embed_query(query)

        self.results = index.query(
            namespace = INDEX,
            vector = query_vec,
            top_k = 10,
            include_metadata = True
        )

        # Return the documents and the query - note that this will not be returning any metadata
        return {
            "documents": self.extract_text(),
            "query": query
        }
    
    def extract_text(self):
        # return array of only text
        docs = [match['metadata']['text'] for match in self.results['matches']]
        return docs

    

        