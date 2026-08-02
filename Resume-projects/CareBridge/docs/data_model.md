# Data model

The production model is organized around `User`, `PatientProfile`, `Appointment`, `PreparationTask`, `Symptom`, `TimelineEvent`, `Medication`, `Allergy`, `MedicalHistory`, `Document`, `DocumentChunk`, `PatientQuestion`, `VisitSummary`, `FollowUpTask`, `SharingPermission`, `AuditEvent`, and `ConsentRecord`.

All sensitive records carry a patient owner. Appointment-scoped records additionally carry an appointment identifier. Share grants are explicit, resource-scoped, expiring, and revocable. Summary versions are immutable after approval; edits create a new version. Audit events are append-only.

The demo JSON mirrors the central workflow and intentionally contains only fictional data.

