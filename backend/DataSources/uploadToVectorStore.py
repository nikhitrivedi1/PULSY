# Upload documents to Pinecone Database

# Libraries
from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
from langchain_huggingface import HuggingFaceEmbeddings


# Constants
APIKEY = 'pcsk_3sDCPS_57sis6H1dsGDzkpEoQ8dJzDLHTzcL9eQM7a5o1VCNEpWMqGX4kh6guFnZCwemBH'
INDEX = 'podcastTranscripts'


class PineconeClass:
    def __init__(self):
        # Initialize Pinecone client
        self.pc = Pinecone(api_key = APIKEY)
        self.index = self.pc.Index(host = "https://ourahuberman-2qajcgl.svc.aped-4627-b74a.pinecone.io")
        self.embeddings = HuggingFaceEmbeddings(model_name = 'sentence-transformers/bert-large-nli-stsb-mean-tokens')
        self.vectorStore = PineconeVectorStore(embedding = self.embeddings, index = self.index)

    def insert(self, docs):
        _ = self.vectorStore.add_documents(namespace = INDEX,documents = docs)

    def search(self, query):
        index = self.index

        # Convert query to vector space using embeddings model
        queryVec = self.embeddings.embed_query(query)
        # print(queryVec)

        self.results = index.query(
            namespace = INDEX,
            vector = queryVec,
            top_k = 3,
            include_metadata = True
        )

        # Return the documents and the query - note that this will not be returning any metadata
        return {
            "documents": self.extractText(),
            "query": query
        }
    
    def extractText(self):
        # return array of only text
        docs = [match['metadata']['text'] for match in self.results['matches']]
        return docs

    

        