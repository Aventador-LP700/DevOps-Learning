# Technical demonstration

1. Run `bash ./setup.sh --lab-only` to reproduce the 24 local exercises.
2. Read `reports/assessment.md` and compare vulnerable, fixed and legitimate results.
3. Run `python3 -m unittest discover -s tests -v` for automated regression checks.
4. Run the optional browser tests to verify actual CORS enforcement and stored-XSS execution.
5. Run `make k8s-up k8s-test` for the separate real Kubernetes API exercise.
6. Inspect the security-tool reports, including blocked release decisions.

The [operating guide](OPERATING_LABS.md) lists prerequisites and cleanup commands.
The [knowledge checks](KNOWLEDGE_CHECKS.md) explain technical reasoning and limitations.
The [audit](SCENARIO_AUDIT.md) records what was executed and any corrections.
