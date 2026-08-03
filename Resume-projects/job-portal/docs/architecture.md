# Architecture decisions

## One deployable application

The frontend is served from Spring Boot's static resources and calls same-origin `/api` endpoints. This keeps deployment simple while still maintaining a clean boundary between the REST API and client.

## Layer boundaries

- Controllers translate HTTP requests into validated DTOs.
- Services own application rules, authorization ownership checks, and transactions.
- Repositories contain database access and filtered/paginated queries.
- Entities model persistence; response DTOs avoid exposing password hashes or internal fields.

## Authentication

Spring Security authenticates passwords with BCrypt and issues an eight-hour HMAC-signed JWT. The token contains the user's subject, ID, and role. Endpoint and method authorization enforce candidate/recruiter separation.

## Storage

H2 provides a zero-setup local experience. The same JPA model runs against PostgreSQL by setting environment variables. Resume bytes are intentionally kept out of relational tables and stored by path for the MVP.
