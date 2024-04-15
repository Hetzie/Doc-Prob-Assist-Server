from queue import Queue
from .models import Document


def extract_tables_from_document():
    pass


def get_splitted_document_chunks():
    pass


def embedd_documents(embedding_queue: Queue):
    while True:
        document: Document = embedding_queue.get()
        print(document)
