# Security policy

Report vulnerabilities privately to the RatatouilleAI repository maintainers through the repository's private reporting channel, if available. Do not include credentials, customer information, or exploit details in public issues. Rotate any accidentally exposed credential immediately.

RatatouilleAI uses Zod for the existing server input validation, keeps server modules server-only, and avoids exposing environment values. The frontend demonstration uses fictitious data in memory and does not perform clinical validation. A Content Security Policy is not provided; configure one for the application's actual integrations before production.
