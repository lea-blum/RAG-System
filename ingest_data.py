

import os
import json
from typing import List, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from pinecone import Pinecone
import time
# LlamaIndex Imports
from llama_index.core import SimpleDirectoryReader, StorageContext, VectorStoreIndex, Settings
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.embeddings.cohere import CohereEmbedding
from llama_index.core.node_parser import MarkdownNodeParser
from llama_index.core.program import LLMTextCompletionProgram
from llama_index.llms.gemini import Gemini

# --- הגדרות נטפרי ---
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
os.environ["CURL_CA_BUNDLE"] = ""
os.environ["PYTHONHTTPSVERIFY"] = "0"

load_dotenv()

# --- 1. הגדרת הסכמה לחילוץ (זה מה שהיה חסר!) ---
# --- 1. הגדרת הסכמה לחילוץ (גרסה משודרגת ומאוחדת) ---
class TechItem(BaseModel):
    item_type: str = Field(description="סוג הפריט: 'החלטה', 'אזהרה', 'כלל פיתוח', או 'שינוי'")
    title: str = Field(description="כותרת קצרה של הממצא")
    summary: str = Field(description="פירוט הממצא בתמצות")
    source_file: str = Field(description="שם הקובץ ממנו נלקח המידע")
    impact_level: str = Field(description="מידת ההשפעה: Low, Medium, High")
    tags: List[str] = Field(description="תגיות רלוונטיות (UI, DB, Auth וכו')")

class ExtractionResult(BaseModel):
    items: List[TechItem] # שימי לב ששינינו מ-decisions ל-items



# --- 2. הגדרת מודלים (Gemini מותאם לנטפרי) ---
Settings.llm = Gemini(
    model="models/gemini-2.5-flash", 
    api_key=os.environ["GOOGLE_API_KEY"],
    transport="rest"
)

Settings.embed_model = CohereEmbedding(
    cohere_api_key=os.environ["COHERE_API_KEY"],
    model_name="embed-multilingual-v3.0"
)

# --- 3. חיבור ל-Pinecone ---
pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
pinecone_index = pc.Index(os.environ["INDEX_NAME"])

try:
    print("מנקה נתונים ישנים מהאינדקס...")
    pinecone_index.delete(delete_all=True)
except Exception as e:
    print(f"האינדקס כבר ריק: {e}")

# --- 4. טעינת מסמכים ---
dirs_to_scan = ["./docs", "./kiro_metadata", "./prisma"]
all_docs = []
for d in dirs_to_scan:
    if os.path.exists(d):
        reader = SimpleDirectoryReader(input_dir=d, recursive=True)
        all_docs.extend(reader.load_data())

# --- 5. פירוק ל-Nodes ---
parser = MarkdownNodeParser()
nodes = parser.get_nodes_from_documents(all_docs)
print(f"המסמכים פוצלו ל-{len(nodes)} Nodes.")

# --- 6. שלב ג': Structured Data Extraction ---
prompt_template_str = """
עבור הטקסט הבא מתוך תיעוד פרויקט, חלץ את כל ההחלטות הטכניות והשינויים שבוצעו.
החזר את המידע במבנה JSON תקין.
טקסט:
{desktop_text}
"""

program = LLMTextCompletionProgram.from_defaults(
    output_cls=ExtractionResult,
    prompt_template_str=prompt_template_str,
    llm=Settings.llm
)

extracted_data = []
print("מתחיל חילוץ נתונים מובנים מה-Nodes (עם השהיה למניעת חריגת מכסה)...")

# ננסה לחלץ רק מ-5 ה-Nodes הראשונים כדי לוודא שזה עובד בלי להיחסם
interesting_nodes = [n for n in nodes if any(word in n.get_content() for word in ["ביקורת", "Kiro", "החלטה", "שינוי"])]

for node in nodes[:5]: # רק ה-3 הכי רלוונטיים
    try:
        # בדיקה אם ה-Node בכלל מכיל טקסט משמעותי
        content = node.get_content()
        if len(content) < 50: # דילוג על Nodes קטנים מדי/ריקים
            continue
            
        result = program(desktop_text=content)
        extracted_data.extend(result.decisions)
        print(f"חולצו {len(result.decisions)} פריטים מה-Node הנוכחי...")
        
        # השהיה של 10 שניות בין בקשה לבקשה עבור ה-Free Tier
        print("ממתין 10 שניות לבקשה הבאה...")
        time.sleep(10) 
        
    except Exception as e:
        if "429" in str(e):
            print("הגענו למכסת ה-API. ממתין דקה...")
            time.sleep(60) # אם נחסמנו, נחכה דקה שלמה
        else:
            print(f"שגיאה אחרת בחילוץ: {e}")

# שמירה לקובץ (רק אם חולצו נתונים)
if extracted_data:
    with open("project_knowledge.json", "w", encoding="utf-8") as f:
        json.dump([d.dict() for d in extracted_data], f, ensure_ascii=False, indent=4)
    print(f"סיום! חולצו סה\"כ {len(extracted_data)} פריטים.")
else:
    print("לא חולצו פריטים. נסי להריץ שוב בעוד כמה דקות.")


print(f"סיום! חולצו סהכ {len(extracted_data)} פריטים ל-project_knowledge.json")

# --- 7. יצירת האינדקס הוקטורי (Pinecone) ---
vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

index = VectorStoreIndex(
    nodes, 
    storage_context=storage_context,
    embed_model=Settings.embed_model
)

print("הנתונים נשלחו בהצלחה ל-Pinecone!")