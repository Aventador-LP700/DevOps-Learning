# Excessive deployment permissions

Reference: CWE-250. A compromised CI service account has a wildcard namespace Role.
This exercise makes real Kubernetes API requests in a dedicated local kind cluster.

```bash
make k8s-up
make k8s-test
cat reports/rbac.json
make k8s-down
```

The vulnerable Role allows reading a fake Secret. The test administrator impersonates
the service account and reads the fake token through the Kubernetes API. The hardened
Role allows only get/patch/update on the named `demo` Deployment. Repeating the Secret
read must return Forbidden; patching the intended Deployment must still succeed.
The test restores hardened permissions on exit, including on failure.

Evidence: `reports/rbac.json`, `reports/rbac-secret.stderr` and test command output.
The Forbidden response demonstrates enforcement, not a network error.

No API audit logging stack is shipped. Production detection would correlate CI identity
requests with API audit records and alert on unexpected Secret access. Do not present
this test output as a deployed SIEM or runtime detection capability.

Residual risk: deployment patch rights can change the workload. Direct Secret API denial
does not eliminate indirect access to secrets available to that workload. See the
[threat model](../../docs/threat-model.md).
