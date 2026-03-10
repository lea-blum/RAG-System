'use client';

import { useState } from 'react';

// נתוני דאמי לרופאים
const mockDoctors = [
  { id: 1, name: 'ד"ר שרה כהן', specialty: 'רפואת משפחה', license: 'IL-12345' },
  { id: 2, name: 'ד"ר דוד לוי', specialty: 'עור ומין', license: 'IL-23456' },
  { id: 3, name: 'ד"ר מיכל אברהם', specialty: 'עיניים', license: 'IL-34567' },
];

// נתוני דאמי לתורים
const mockAppointments = [
  { id: 1, time: '10:00', treatment: 'בדיקה כללית', priority: 'NORMAL' },
  { id: 2, time: '11:30', treatment: 'טיפול שיניים', priority: 'NORMAL' },
  { id: 3, time: '14:00', treatment: 'בדיקת עיניים', priority: 'URGENT' },
];

export default function HomePage() {
  const [appointments, setAppointments] = useState(mockAppointments);

  const handleUrgentAppointment = () => {
    const newAppointment = {
      id: appointments.length + 1,
      time: 'דחוף',
      treatment: 'תור דחוף חדש',
      priority: 'URGENT',
    };
    setAppointments([newAppointment, ...appointments]);
  };

  const handleEmergencyAppointment = () => {
    const newAppointment = {
      id: appointments.length + 1,
      time: 'חירום',
      treatment: 'מקרה חירום',
      priority: 'EMERGENCY',
    };
    setAppointments([newAppointment, ...appointments]);
  };

  const getPriorityClass = (priority: string) => {
    switch (priority) {
      case 'URGENT':
        return 'priority-urgent';
      case 'EMERGENCY':
        return 'priority-emergency';
      default:
        return 'priority-normal';
    }
  };

  const getPriorityText = (priority: string) => {
    switch (priority) {
      case 'URGENT':
        return 'דחוף';
      case 'EMERGENCY':
        return 'חירום';
      default:
        return 'רגיל';
    }
  };

  return (
    <section className="page-section">
      <h2 className="page-title">דשבורד ניהול תורים</h2>
      <p className="page-text">
        מערכת מקצועית לניהול תורים עם תעדוף דחיפות ורשימת רופאים מלאה
      </p>

      <div className="btn-container">
        <button className="btn btn-primary" onClick={() => alert('פתיחת טופס תור רגיל')}>
          קביעת תור רגיל
        </button>
        <button className="btn btn-urgent" onClick={handleUrgentAppointment}>
          קביעת תור דחוף
        </button>
        <button className="btn btn-urgent" onClick={handleEmergencyAppointment}>
          מקרה חירום
        </button>
      </div>

      <div className="dashboard-container">
        <div className="dashboard-section">
          <h3 className="dashboard-section-title">רשימת רופאים</h3>
          <div className="doctor-list">
            {mockDoctors.map((doctor) => (
              <div key={doctor.id} className="doctor-item">
                <p className="doctor-name">{doctor.name}</p>
                <p className="doctor-specialty">{doctor.specialty}</p>
                <p className="doctor-license">רישיון: {doctor.license}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="dashboard-section">
          <h3 className="dashboard-section-title">תורים קרובים</h3>
          <div className="appointment-list">
            {appointments.map((appointment) => (
              <div key={appointment.id} className="appointment-item">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <p style={{ margin: 0, fontWeight: 600, color: '#1e3a8a' }}>
                      {appointment.time}
                    </p>
                    <p style={{ margin: '0.25rem 0 0', fontSize: '0.9rem', color: '#64748b' }}>
                      {appointment.treatment}
                    </p>
                  </div>
                  <span className={`priority-badge ${getPriorityClass(appointment.priority)}`}>
                    {getPriorityText(appointment.priority)}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

