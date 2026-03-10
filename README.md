Kiro Smart Router RAG - Documentation Agent 🚀
פרויקט זה מציג סוכן חכם (Agent) מבוסס LlamaIndex Workflows, שנועד לספק מענה טכני ואדמיניסטרטיבי על מערכת לניהול תורים למרפאה. המערכת משלבת ניתוב חכם (Routing) בין מקורות מידע שונים לקבלת תשובות מדויקות.

🏥 אודות המערכת המתועדת (Clinic Queue Management)
הסוכן מספק מידע על פרויקט Fullstack לניהול תורים, המבוסס על:

Framework: Next.js 15.3 (App Router).

ORM: Prisma 7.4.1.

Database: SQLite (Development).

Language: TypeScript.

🎯 מטרת הסוכן (The RAG System)
המערכת מנתבת שאלות משתמש לשני ערוצים מרכזיים בהתאם לסוג השאלה:

נתונים מובנים (Structured Data): שליפה ישירה מקובץ project_knowledge.json עבור שאלות על גרסאות, רשימות טכנולוגיות והחלטות ספציפיות.

חיפוש סמנטי (Semantic Search): שליפה מתוך Pinecone Vector DB עבור שאלות עומק, הבנת רציונל וחיפוש בתיעוד הטקסטואלי הרחב.

🛠 טכנולוגיות ה-AI
LLM: Google Gemini 2.5 Flash (עבודה במצב REST לעקיפת חסימות SSL).

Orchestration: LlamaIndex Workflows (Event-Driven architecture).

Vector DB: Pinecone.

Embeddings: Cohere Multilingual v3.0.

UI: Gradio.

📊 תרשים זרימה של ה-Workflow
Code snippet
```mermaid
graph TD
    A[User Input] --> B{Router Step}
    B -->|Structured Query| C[JSON Query Engine]
    B -->|Semantic Query| D[Pinecone Vector Store]
    C --> E[Retrieval Event]
    D --> E
    E --> F[Synthesize Step]
    F --> G[Final Answer with Source Label]```
🚀 הוראות הרצה
1. התקנת סביבה
יש להתקין את הספריות הנדרשות:

Bash
pip install llama-index llama-index-llms-gemini llama-index-embeddings-cohere pinecone-client gradio python-dotenv urllib3
2. הגדרת משתני סביבה
יש ליצור קובץ .env (ניתן להיעזר ב-.env.example) ולהזין את המפתחות הבאים:

GOOGLE_API_KEY

COHERE_API_KEY

PINECONE_API_KEY

INDEX_NAME

3. הכנת הנתונים (Ingestion)
לפני הרצת הממשק, יש לוודא שקובץ ה-JSON נוצר והנתונים עלו ל-Vector DB:

Bash
python ingest_data.py
4. הרצת המערכת
Bash
python app.py
הממשק יהיה זמין בכתובת: http://127.0.0.1:7860

❓ דוגמאות לשאלות שהסוכן יודע לענות
שאלת נתונים מובנים: "אילו טכנולוגיות נבחרו לפרויקט ומה הגרסאות שלהן?"

שאלת חיפוש סמנטי: "מדוע הוחלט להשתמש ב-Prisma כ-ORM?"

שאלת סטטוס: "מהן האזהרות המרכזיות לגבי המעבר לסביבת Production?"