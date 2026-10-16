# Security & Access

## Scope
A two-day hackathon build that could credibly grow into a campus pilot. Controls chosen to be cheap to implement now and honest about what is not covered.

## 3.1 Roles and Access Matrix

| Capability | Guest (demo) | Resident | Manager | Admin |
|------------|--------------|----------|---------|-------|
| Scan an item | Yes (rate-limited) | Yes | Yes | Yes |
| View twin graph and metrics | Read-only, demo data | Yes | Yes | Yes |
| Run what-if simulation | Limited (low quota) | Yes | Yes | Yes |
| View own scan history | No | Yes | Yes | Yes |
| Generate AI advice | Cached sample only | Yes | Yes | Yes |
| Advisor chat | No | Yes | Yes | Yes |
| Edit twin config (nodes, schedules, yields) | No | No | Yes | Yes |
| Generate and export reports | No | Own summary | Yes | Yes |
| Manage users, reset or drive demo data | No | No | No | Yes |
| View audit logs | No | No | No | Yes |

**Rule**: Deny by default. Every route declares its minimum role, and ownership is checked on every record fetch (a resident can only read their own scans).

## 3.2 Authentication and Sessions

- Email and password, hashed with argon2 (or bcrypt with work factor ≥ 12)
- Never store or log plaintext passwords
- Short-lived JWT access token (15 minutes) + refresh token in httpOnly, Secure, SameSite=Lax cookie
- Rotate refresh token on use
- Seeded demo accounts (one per role) exist only when `DEMO_MODE=true`
- Production flag disables them and guest write endpoints
- Login rate limit: 5 attempts per minute per IP and account, then temporary lockout

## 3.3 Threat Model and Controls

| Threat | Control |
|--------|---------|
| Malicious or oversized upload | 5 MB limit, allowlist JPEG/PNG/WebP, verify with Pillow, cap pixel count (decompression bomb guard), re-encode before inference, never execute or serve uploaded bytes |
| Location leakage in photos | Strip EXIF and GPS data on receipt |
| Prompt injection (chat text, text visible in image sent to vision model) | Treat all user content as data. Fixed system prompt, no tools or actions exposed to model, output validated against schema, advisor numbers checked against twin data |
| API key theft | Keys live only in server environment variables, never in frontend bundle, .env git-ignored, secret scanning enabled on repo, rotate any key that ever touches a commit |
| Cost abuse and DoS | Per-IP and per-user rate limits, request size caps, LLM token caps, cached advice, global daily budget alarm |
| Broken access control (IDOR) | Ownership checks in service layer, role dependency on every router, tests for cross-user access |
| XSS | Render model output as sanitized markdown, no dangerouslySetInnerHTML, strict Content-Security-Policy |
| CSRF | SameSite cookies, bearer token on API calls, CORS allowlist of exact origins |
| SQL injection | ORM with parameterized queries only |
| Supply chain | Lockfiles, pinned versions, pip-audit and npm audit before submission, no unreviewed install scripts |
| Unsafe advice for hazardous items | Conservative defaults on uncertainty, on-screen note that guidance is informational and local rules apply |

## 3.4 Data Handling and Privacy

**Images**: Processed in memory and discarded. If adding optional "save for review" feature: require explicit consent, store with random filename, delete after 7 days.

**Minimization**: Store class, subtype, confidence, timestamp, and chosen source node. No device identifiers, no precise location.

**Personal data**: Email and password hash only. Provide delete-my-data for residents.

**Third parties**: If images or prompts go to LLM provider, say so in UI, send only what is needed, prefer provider setting that does not train on API data.

**Principles followed**: Consent, purpose limitation, data minimization — in spirit of India's DPDP Act 2023. Design intent, not legal review.

**Faces and people**: Show hint to frame only the item. Do not retain frames that include people.

## 3.5 Transport and Platform Hardening

- HTTPS everywhere (host-provided certificates), HSTS enabled
- Response headers: Content-Security-Policy, X-Content-Type-Options, Referrer-Policy, frame-ancestors none
- Disable debug mode and verbose errors in production
- Errors carry request_id, never stack traces
- Run containers as non-root user with minimal base image
- Disable `/docs` and `/openapi.json` in production or put behind admin

## 3.6 Logging and Audit

- Structured logs with request_id, user id (not email), route, status, latency
- Never log images, tokens, passwords, or full prompts. Log hash of advisor input instead
- Audit events: login, failed login, role change, demo reset, report export

## 3.7 Pre-Submission Security Checklist

- [ ] No secrets in git history (`git log -p` search for key prefixes)
- [ ] `.env.example` committed, `.env` ignored
- [ ] Demo accounts and guest limits correct for deployed environment
- [ ] Rate limits verified with quick loop test
- [ ] Upload test files: oversized, wrong type, corrupted, EXIF with GPS
- [ ] Prompt-injection test strings tried in chat
- [ ] `npm audit` and `pip-audit` reviewed
- [ ] CORS only allows deployed frontend origin