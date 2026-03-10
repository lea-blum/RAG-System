from llama_index.core import SimpleDirectoryReader

# הגדרת הנתיבים לתיקיות של הכלים השונים
# ודאי שהשמות תואמים בדיוק למה שנוצר בפרויקט שלך
input_dirs = ["./docs_cursor", "./kiro_metadata"]

# טעינת הנתונים
# ה-Loader עובר על כל התיקיות ברשימה ושואב את כל קבצי ה-md
reader = SimpleDirectoryReader(input_files=None, input_dir=None, recursive=True)

all_docs = []
for data_dir in input_dirs:
    # טוען כל תיקייה בנפרד ומקבץ אותם
    documents = SimpleDirectoryReader(input_dir=data_dir).load_data()
    all_docs.extend(documents)

print(f"נטענו בהצלחה {len(all_docs)} מסמכים משני הכלים.")