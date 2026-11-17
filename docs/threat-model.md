# Threat model

## Assets and actors

Assets: CI credentials, build-step integrity, artifact contents, release decisions,
and namespace deployment permissions. The learner controls only lab inputs. Attackers
represent an untrusted contributor, a reader of build logs, a writer to mutable
artifact storage, or a compromised CI deployment identity. The workstation, Docker
daemon, trusted build digest, repository policy and test administrator are trusted.

## Boundaries and mitigations

| Boundary | Attacker capability | Failure | Control | Residual limitation |
|---|---|---|---|---|
| Contribution metadata → build shell | Set change title | Execute interpolated shell code | Argument arrays; no shell interpolation | Other steps may still execute untrusted code |
| Credential → build log | Read job output | Retrieve credential | Omit secret values; verify output | Debug tracing or third-party steps can leak elsewhere |
| Artifact store → release | Modify artifact bytes | Deploy untrusted contents | Compare against trusted digest | Builder and digest source remain trusted |
| Scanner report → release decision | Exploit advisory configuration | Release despite critical findings | Enforced fail-closed policy | Forged or incomplete reports require provenance controls |
| CI identity → Kubernetes API | Use deployment identity | Read namespace Secrets | Scoped Role limited to named Deployment | Deployment patch may still permit workload code execution |

## Important RBAC residual risk

Permission to patch a Deployment can change its container image or pod template.
That can access any secrets available to that workload and execute code with its
identity. This lab proves that direct Secret API access is blocked; it does not
claim that deployment rights are harmless. Production systems also need admission
policy, protected release provenance, constrained workloads and identity separation.

## Excluded claims

No host escape, organization compromise, cloud-account takeover, dependency
confusion, internet target exploitation or full GitHub event/token emulation is
implemented. The scan fixture is synthetic. Findings here are educational expected
behaviors, not vulnerabilities discovered in GitHub, Docker or Kubernetes.
