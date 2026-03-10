# אבולוציה של סכמת הנתונים - Kiro Layer

## תאריך
26 בפברואר 2026

## סקירה כללית
Kiro מרחיב את סכמת הנתונים הקיימת בשתי דרכים מרכזיות:
1. הוספת טבלת Doctors (רופאים)
2. הוספת שדה priority_level לטבלת Appointments

## שינויים בפירוט

### 1. טבלה חדשה: Doctors

```prisma
model Doctor {
  id              Int      @id @default(autoincrement())
  name            String
  specialty       String
  license_number  String   @unique
  createdAt       DateTime @default(now())
  updatedAt       DateTime @updatedAt
  
  @@map("doctors")
}
```

#### שדות:
- **id**: מזהה ייחודי אוטומטי
- **name**: שם הרופא המלא
- **specialty**: תחום ההתמחות (לדוגמה: "רפואת משפחה", "עור", "עיניים")
- **license_number**: מספר רישיון ייחודי - חובה להיות ייחודי במערכת
- **createdAt**: תאריך יצירת הרשומה
- **updatedAt**: תאריך עדכון אחרון

#### נימוקים:
- הטבלה הקיימת (Appointments) לא הייתה מקושרת לרופאים ספציפיים
- מספר הרישיון מבטיח אימות מקצועי ומונע כפילויות
- שדות הזמן (createdAt, updatedAt) מאפשרים מעקב אחר שינויים

### 2. שדה חדש: priority_level בטבלת Appointments

```prisma
model Appointment {
  id            Int               @id @default(autoincrement())
  scheduledAt   DateTime
  treatmentType String
  status        AppointmentStatus
  priority_level PriorityLevel    @default(NORMAL)
  
  @@map("appointments")
}

enum PriorityLevel {
  NORMAL
  URGENT
  EMERGENCY
}
```

#### רמות עדיפות:
- **NORMAL**: תור רגיל (ברירת מחדל)
- **URGENT**: תור דחוף - טיפול תוך 24-48 שעות
- **EMERGENCY**: חירום - טיפול מיידי

#### נימוקים:
- מאפשר תעדוף תורים לפי דחיפות רפואית
- משפר את יכולת המרפאה לטפל במקרים דחופים
- מספק גמישות בניהול התורים

## קשרים עתידיים (Future Relations)
בשלב הבא, מומלץ להוסיף:
- קשר בין Appointment ל-Doctor (doctorId)
- קשר בין Appointment ל-Patient (patientId)
- טבלת Patients

## השפעה על ה-UI
- דשבורד חדש יציג רשימת רופאים
- כפתור "קביעת תור דחוף" יאפשר הגדרת priority_level=URGENT
- סינון תורים לפי רמת עדיפות

## Migration
לאחר עדכון הסכימה, יש להריץ:
```bash
npx prisma migrate dev --name add_doctors_and_priority
npx prisma generate
```
