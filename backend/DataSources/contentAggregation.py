# Use Langchain WebBaseLoad() to extract information from the Huberman website
# Target key words Sleep, Heart Rate, Stress

# Libraries
from langchain_community.document_loaders.text import TextLoader
from langchain_community.document_loaders.rtf import UnstructuredRTFLoader
from langchain_community.document_loaders import UnstructuredHTMLLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from uploadToVectorStore import PineconeClass
import os

# Constants
# PINECONE = 'pcsk_3sDCPS_57sis6H1dsGDzkpEoQ8dJzDLHTzcL9eQM7a5o1VCNEpWMqGX4kh6guFnZCwemBH'
BASEURL = 'https://www.hubermanlab.com/newsletter/'
TESTURLS = ["improve-your-sleep", "your-top-questions-on-sleep-answered","breathwork-protocols-for-health-focus-stress", "foundational-fitness-protocol"]
CLEANUP_WORDS = ['Stay Connected', 'Subscribe', '\n']
TRANSCRIPTNAV = 'https://www.hubermanlab.com/members/members-transcripts/10eb3186_page='
TESTNAV = 'https://www.hubermanlab.com/members/members-transcripts/'
EXAMPLETRANSCRIPT = 'https://www.hubermanlab.com/episode/essentials-how-to-focus-to-change-your-brain'


# Create class to encapsulate the response data
# Can't scrape data because of the premium member login
class HubermanData:
    def __init__(self):
        # Create list structure to hold documents for all TestURLS
        self.data = []
        self.loadPodcastTranscripts()

        # print(self.data)
        # upload to pinecone
        uploader = PineconeClass()
        for item in self.data:
           uploader.insert(item, "podcastTranscripts")

    def loadPodcastTranscripts(self):
        # get path for all transcript .txt files
        path = 'Huberman/Transcripts/html/'
        files = os.listdir(path)
        files= [path + f for f in files]

        for file in files:
            # create documents
            loader = UnstructuredHTMLLoader(
                file_path = file
            )

            docs = loader.load()
            # Split
            # work on splitter
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size = 1000,
                chunk_overlap = 200,
                add_start_index = True
            )

            all_splits = text_splitter.split_documents(docs)
            # upload to data
            self.data.append(all_splits)




