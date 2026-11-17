# Five-minute reviewer demonstration

1. Explain the threat boundary: contribution metadata reaches a shell command.
2. Run `make lab` and show the command-injection payload and temporary marker evidence.
3. Compare `pipelines/vulnerable/metadata.py` and its hardened counterpart.
4. Open the assessment and explain why both vulnerable and hardened results must pass.
5. Show the Kubernetes Secret read denial and successful deployment patch if you ran
   the optional real-cluster exercise. Explain the remaining power of deployment rights.
6. Open repository CI and show the actual run, commit, permissions, and uploaded evidence.

## Interview discussion

Be prepared to explain the trusted-digest assumption, why secret masking alone is
insufficient, how untrusted PR execution differs from string injection, why a scan
must fail closed, and why patching a Deployment still carries significant privilege.
Discuss what this lab does not emulate and how you would extend it safely.

## Evidence-based profile wording

After reproducing and understanding the lab, adapt this wording to your own work:

> Built and validated a CI/CD security learning lab with reproducible pipeline
> injection, synthetic secret exposure, artifact tampering and release-policy bypass
> exercises, hardened retests, and machine-readable assessment evidence.

Mention Kubernetes API integration, live image scans or signed SBOMs only after
running and understanding those extensions. State tool assistance honestly where
relevant. Do not claim a real organization's breach or guarantee of production security.

Record a short video with terminal commands, the code diff and report. Add a reviewed
assessment to `docs/evidence/` with the tested commit and date. Explain a design choice
in your own words; that is stronger evidence than a list of tools or a green badge alone.
