
import os
import asyncio
import gradio as gr
import json
from pinecone import Pinecone
from dotenv import load_dotenv
from typing import List, Optional, Any

# --- הגדרות נטפרי (SSL Bypass) ---
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
os.environ["CURL_CA_BUNDLE"] = ""
os.environ["PYTHONHTTPSVERIFY"] = "0"

from llama_index.llms.gemini import Gemini
from llama_index.core import VectorStoreIndex, Settings
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.embeddings.cohere import CohereEmbedding
from llama_index.core.workflow import Workflow, step, StartEvent, StopEvent, Event
from llama_index.core.query_engine import RouterQueryEngine, CustomQueryEngine
from llama_index.core.selectors import LLMSingleSelector
from llama_index.core.tools import QueryEngineTool

load_dotenv()

# --- 1. הגדרות מודלים ---
Settings.embed_model = CohereEmbedding(
    api_key=os.environ["COHERE_API_KEY"], 
    model_name="embed-multilingual-v3.0"
)

Settings.llm = Gemini(
    model="models/gemini-2.5-flash", 
    api_key=os.environ["GOOGLE_API_KEY"],
    transport="rest"
)

# --- 2. הגדרת אירועים (Events) ל-Workflow ---
class RoutingEvent(Event):
    query: str
    engine: Any
    source_name: str

class RetrievalEvent(Event):
    query: str
    context: str

# --- 3. מנוע שאילתות JSON מותאם ---
class JSONQueryEngine(CustomQueryEngine):
    json_path: str = "project_knowledge.json"
    llm: Any = None 

    def custom_query(self, query_str: str):
        if not os.path.exists(self.json_path):
            return "שגיאה: קובץ project_knowledge.json לא נמצא. יש להריץ את ingest_data.py קודם."
        with open(self.json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        prompt = f"""
        להלן נתונים מובנים על הפרויקט (החלטות, אזהרות ושינויים):
        {json.dumps(data, ensure_ascii=False, indent=2)}
        
        שאלה: {query_str}
        
        הנחיות: ענה בצורה מדויקת על סמך הנתונים בלבד. אם המידע לא קיים, ציין זאת.
        """
        return str(self.llm.complete(prompt))

# --- 4. הכנת האינדקס וה-Router ---
pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
pinecone_index = pc.Index(os.environ["INDEX_NAME"])
vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
index = VectorStoreIndex.from_vector_store(vector_store)

json_engine = JSONQueryEngine(llm=Settings.llm)
vector_engine = index.as_query_engine(similarity_top_k=3)

vector_tool = QueryEngineTool.from_defaults(
    query_engine=vector_engine,
    description="שימושי לשאלות עומק, הבנת רציונל, הסברים טכניים וחיפוש בתיעוד הטקסטואלי."
)

structured_tool = QueryEngineTool.from_defaults(
    query_engine=json_engine,
    description="שימושי לשאלות על החלטות טכנולוגיות ספציפיות, רשימות של בחירות (Next.js, Prisma וכו') וסיכומי פרויקט."
)

# תיקון: הגדרת הסלקטור כמשתנה עצמאי כדי למנוע את שגיאת ה-AttributeError
my_selector = LLMSingleSelector.from_defaults()

router_query_engine = RouterQueryEngine(
    selector=my_selector,
    query_engine_tools=[vector_tool, structured_tool],
    verbose=True
)

# --- 5. הגדרת ה-Workflow ---
class KiroRouterWorkflow(Workflow):
    
    @step
    async def route_step(self, ev: StartEvent) -> RoutingEvent | StopEvent:
        query = ev.get("query", "").strip()
        if not query:
            return StopEvent(result="נא להזין שאלה.")
        
        print(f"--- שלב 1: ניתוב שאילתה: {query} ---")
        
        # תיקון: שימוש ב-my_selector ישירות
        selector_result = my_selector.select(
            [vector_tool.metadata, structured_tool.metadata], 
            query
        )
        
        if selector_result.ind == 1:
            print("החלטת הנתב: שימוש בנתונים מובנים (JSON)")
            return RoutingEvent(query=query, engine=json_engine, source_name="JSON")
        else:
            print("החלטת הנתב: שימוש בחיפוש סמנטי (Pinecone)")
            return RoutingEvent(query=query, engine=vector_engine, source_name="Pinecone")

    @step
    async def retrieve_step(self, ev: RoutingEvent) -> RetrievalEvent:
        print(f"--- שלב 2: שליפה ממקור {ev.source_name} ---")
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, ev.engine.query, ev.query)
        return RetrievalEvent(query=ev.query, context=str(response))

    @step
    async def synthesize_step(self, ev: RetrievalEvent) -> StopEvent:
        print("--- שלב 3: ניסוח תשובה סופית ---")
        # בדיקה קטנה כדי להוסיף את התווית הנכונה למקור
        is_json = "Next.js" in ev.context or "Prisma" in ev.context or "SQLite" in ev.context
        source_label = "📂 שליפה מנתונים מובנים (JSON)" if is_json else "🔍 חיפוש סמנטי (Pinecone)"
        
        final_answer = f"{ev.context}\n\n---\n*מקור המידע: {source_label}*"
        return StopEvent(result=final_answer)

# --- 6. ממשק Gradio והרצה ---
async def run_validated_rag(message, history):
    try:
        wf = KiroRouterWorkflow(timeout=60)
        result = await wf.run(query=message)
        return result
    except Exception as e:
        return f"שגיאה במערכת: {str(e)}"

def chat_wrapper(message, history):
    return asyncio.run(run_validated_rag(message, history))

demo = gr.ChatInterface(
    fn=chat_wrapper,
    title="Kiro Smart Router RAG",
    description="מערכת המנתבת בין נתונים מובנים (JSON) לחיפוש סמנטי (Pinecone) דרך Workflow מרובה שלבים.",
)


if __name__ == "__main__":
    demo.launch(server_port=7860)