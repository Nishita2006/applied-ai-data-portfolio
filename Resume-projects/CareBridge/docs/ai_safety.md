# AI safety design

CareBridge is administrative and non-diagnostic. A request classifier blocks diagnosis, treatment, medication changes, prognoses, and surgery recommendations. Emergency-related language receives a clear limitation and immediate direction to local emergency services or professional help.

Permitted generations use only authorized patient input, appointment data, and source chunks. Factual statements require citations. Low-confidence or conflicting retrieval produces uncertainty rather than a completed claim. Uploaded text is treated as untrusted data, never as system instructions. Structured outputs are schema-validated. Original patient text and documents remain preserved, and AI-organized wording requires explicit patient approval.

The demo guard is deterministic and intentionally conservative. It is not a certified medical safety system.

