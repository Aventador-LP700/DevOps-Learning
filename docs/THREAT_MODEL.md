# Expanded threat model

## Assets and attackers

Assets include synthetic user objects, administrative capabilities, protected profile
fields, internal mock metadata, package origin, build execution, password records,
query structure, browser execution context, synthetic private files, coupon state,
authentication attempts, session identifiers, artifact origin and audit evidence.

Actors model an ordinary user, a log reader, a malicious contribution/dependency
publisher, a storage writer or a compromised deployment identity. The shipped test
harness, workstation/VM, ephemeral lab keys and database administration remain trusted.

| Boundary | Representative failure | Control demonstrated |
|---|---|---|
| User → object/function | BOLA/BFLA/mass assignment | Ownership, role checks, writable-field schema |
| App → internal service | SSRF | Exact destination policy within a separate mock safety envelope |
| Browser → authenticated origin | CORS/XSS | Exact origin policy, contextual encoding, CSP |
| Source/dependency → build | Confusion/hook execution | Private source, pinning, no untrusted hook execution |
| Credential → stored verifier | Fast unsalted hashing | Salted scrypt and constant-time verification |
| Data → interpreter | SQL/shell/pickle injection | Bound parameters, argument arrays, schema-validated JSON |
| User path → filesystem | Traversal | Canonical public-root containment |
| Checkout requests → ledger | Coupon replay | Database uniqueness and transaction |
| Authentication → session | Unlimited attempts/fixation | Rate policy, fresh identifier and invalidation |
| Artifact → consumer | Unauthenticated origin | Protected-key HMAC verification; not public-key signing |
| Action/fault → policy evidence | Missing logs/fail-open | Structured audit events; explicit allow required |

## Safety controls

- New persistent services always bind to 127.0.0.1 and require both vulnerable flags
  to start an intentionally vulnerable HTTP instance.
- Existing setup defaults still serve the lightweight safe API. The new HTTP adapter
  defaults to fixed implementations and validates Host/state-changing Origin headers.
- Dummy data/credentials only. No real exfiltration, reverse shell, persistence,
  host-file theft, cloud credential use or public target scanning.
- SSRF cannot leave allocated loopback mock origins; redirects and environment proxies
  are disabled. Traversal has an outer lab-root guard even in the vulnerable function.
- Command/build/pickle proofs create only temporary markers and are not HTTP endpoints.
- Docker drops capabilities, runs non-root, has no external network and mounts no
  Docker socket or host checkout. Reports are copied out separately.
- Native mode retains user privileges and network access; use a disposable VM for
  modified/untrusted code. Loopback binding alone is not isolation from local processes.

## Residual and excluded risks

This is a teaching system, not a production identity service. The HTTP login uses
one known synthetic credential; there is no real user account lifecycle. scrypt
storage is a separate module. CORS does not replace authorization. In-process rate
limits do not coordinate replicas. File resolution can race on a mutable production
filesystem. The local audit file is not append-only external custody. HMAC signers
and verifiers share authority; a production asymmetric signing design is separate.

Deployment patch permissions can still change workload code and access secrets
available to that workload, even when direct Secret API reads are denied. See the
[preserved original threat model](threat-model.md). A passing lab or SAST result is
not certification of a production pipeline; the pinned image's actual vulnerability
gate can remain blocked and is reported honestly.
