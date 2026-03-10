from llama_index.core.workflow import Event
from llama_index.core.schema import Document
from typing import List

# אירוע שקורה אחרי שהקבצים נטענו מהדיסק
class DocumentsLoadedEvent(Event):
    documents: List[Document]

# אירוע שקורה אחרי שהמידע אונדקס ב-Pinecone
class IndexingCompletedEvent(Event):
    index_id: str

# אירוע שנושא את התשובה הסופית למשתמש
class AnswerReadyEvent(Event):
    answer: str