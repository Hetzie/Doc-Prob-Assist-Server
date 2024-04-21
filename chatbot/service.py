import json
from queue import Queue
from chatbot.models import Document
from . import utils
from threading import Thread


class QueryChain:
    def __init__(self) -> None:
        self.temp = {}
        self.embedding_queue = Queue()
        self.thread = Thread(target=utils.embedd_documents,
                             args=(self.embedding_queue,), daemon=True)
        self.thread.start()

    def embedd_document(self, document):
        self.embedding_queue.put(document)

    def remove_document_embeddings(self, doc_id):
        doc_obj = Document.objects.get(pk=doc_id)
        print(doc_obj.file.path)
        ids = utils.vector_db.get(where={"source": doc_obj.file.path})['ids']
        utils.vector_db.delete(ids=ids)

    def retrieve_documents(self, query, doc_id=None):
        pass

    def create_prompt(self, documents):
        pass

    def save_references(self, chat_id, documents):
        pass

    def query_llm(self, prompt):
        pass

    def resolve_query(self, query):
        response = self.temp.get(
            query, ["DocProbe Assit will help you soon.DocProbe Assit will help you soon.DocProbe Assit will help you soon.DocProbe Assit will help you soon.DocProbe Assit will help you soon.DocProbe Assit will help you soon.DocProbe Assit will help you soon.DocProbe Assit will help you soon.DocProbe Assit will help you soon.\n\nDocProbe Assit will help you soon.DocProbe Assit will help you soon.DocProbe Assit will help you soon.DocProbe Assit will help you soon.\n\nDocProbe Assit will help you soon.DocProbe Assit will help you soon.DocProbe Assit will help you soon.DocProbe Assit will help you soon."])[0]
        references = json.load(open('references/1.json', 'r'))
        return response, '', references

    def regenerate_answer(self, prompt):

        return self.temp.get(
            prompt, ["", "Regenerated DocProbe Assit will help you soon."])[1]
