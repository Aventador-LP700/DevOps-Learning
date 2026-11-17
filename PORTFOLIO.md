# Portfolio review guide

PipelineProof demonstrates offensive reasoning and defensive verification across
25 learning scenarios. New work extends the existing project rather than replacing
its original CI/CD exercises. Repository location and commit history make that
engineering progression reviewable.

## Five-minute demonstration

1. Show the scenario catalog and explain why 24 native exercises plus one real kind
   integration is an honest count of 25, rather than 25 claimed native passes.
2. Run `bash ./setup.sh --lab-only` and open the JSON/Markdown assessment.
3. Compare an object-authorization, injection or supply-chain vulnerable/fixed pair.
4. Show all three regression results: exploit, blocked attack and legitimate success.
5. Run browser integration for actual stored-JavaScript execution and CORS enforcement.
6. Show GitHub CI and security artifacts. Explain a correctly blocked release rather
   than concealing dependency findings behind a green badge.

## Skills evidenced

Threat modeling, API authorization review, injection analysis, supply-chain trust,
authentication/session controls, policy failure analysis, safe lab design, test
automation, Docker/kind operation, SAST/DAST/SCA, SBOM integrity and clear reporting.

## Evidence-based CV wording

> Extended a reproducible CI/CD and application-security learning lab with 20
> vulnerable/fixed scenario pairs, safe local proofs, automated regression contracts,
> browser-verified CORS/XSS behavior and security-gated CI evidence.

Mention real Kubernetes validation, live scanner results and signing only after
reviewing the linked run and reproducing the relevant exercise. State tool assistance
honestly. Do not describe synthetic findings as real customer vulnerabilities or
claim guaranteed remote employment.

The [matrix](docs/VULNERABILITY_MATRIX.md), [validation](docs/EXPANSION_VALIDATION.md),
[threat model](docs/THREAT_MODEL.md) and [interview guide](docs/INTERVIEW_GUIDE.md)
provide a review path. Future production capabilities are explicitly labeled planned.
