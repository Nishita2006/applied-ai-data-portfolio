PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS patients (id INTEGER PRIMARY KEY, name TEXT NOT NULL, synthetic INTEGER NOT NULL DEFAULT 1);
CREATE TABLE IF NOT EXISTS appointments (id INTEGER PRIMARY KEY, patient_id INTEGER NOT NULL, title TEXT, provider TEXT, visit_date TEXT, reason TEXT, FOREIGN KEY(patient_id) REFERENCES patients(id));
CREATE TABLE IF NOT EXISTS preparation_tasks (id INTEGER PRIMARY KEY, appointment_id INTEGER NOT NULL, title TEXT NOT NULL, status TEXT NOT NULL, due_date TEXT, FOREIGN KEY(appointment_id) REFERENCES appointments(id));
CREATE TABLE IF NOT EXISTS symptoms (id INTEGER PRIMARY KEY, appointment_id INTEGER NOT NULL, symptom TEXT NOT NULL, onset_date TEXT, severity INTEGER CHECK(severity BETWEEN 0 AND 10), pattern TEXT, source TEXT DEFAULT 'patient_entered', FOREIGN KEY(appointment_id) REFERENCES appointments(id));
CREATE TABLE IF NOT EXISTS symptom_responses (id INTEGER PRIMARY KEY, appointment_id INTEGER NOT NULL, response_text TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(appointment_id) REFERENCES appointments(id));
CREATE TABLE IF NOT EXISTS medications (id INTEGER PRIMARY KEY, patient_id INTEGER NOT NULL, name TEXT, strength TEXT, frequency TEXT, status TEXT, FOREIGN KEY(patient_id) REFERENCES patients(id));
CREATE TABLE IF NOT EXISTS documents (id INTEGER PRIMARY KEY, appointment_id INTEGER NOT NULL, title TEXT, category TEXT, organization TEXT, citation TEXT, FOREIGN KEY(appointment_id) REFERENCES appointments(id));
CREATE TABLE IF NOT EXISTS questions (id INTEGER PRIMARY KEY, appointment_id INTEGER NOT NULL, question TEXT, priority INTEGER DEFAULT 0, FOREIGN KEY(appointment_id) REFERENCES appointments(id));
