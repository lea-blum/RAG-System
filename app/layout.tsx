import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "מערכת לניהול תורים למרפאה",
  description: "מערכת Fullstack לניהול תורים, רופאים ומטופלים."
};

export default function RootLayout({
  children
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="he" dir="rtl">
      <body className="app-root">
        <header className="app-header">
          <div className="app-header-inner">
            <h1 className="app-title">מערכת לניהול תורים למרפאה</h1>
            <p className="app-subtitle">
              זימון תורים, ניהול רופאים ומטופלים – בעיצוב מקצועי
            </p>
          </div>
        </header>
        <main className="app-main">{children}</main>
      </body>
    </html>
  );
}

