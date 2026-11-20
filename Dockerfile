FROM python:3.15.2-slim-bookworm@sha256:96599df822d0e1c6bb700014a05c7f3c8cabc6e0f7ff3c4f9f69cee033b4b5d9
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /lab
RUN useradd --uid 10001 --create-home learner && mkdir /reports && chown learner:learner /reports
COPY --chown=learner:learner lab/ lab/
COPY --chown=learner:learner labs/ labs/
COPY --chown=learner:learner app/ app/
COPY --chown=learner:learner policies/ policies/
COPY --chown=learner:learner fixtures/ fixtures/
COPY --chown=learner:learner pipelines/ pipelines/
RUN touch /lab/.pipelineproof-container
USER 10001:10001
ENTRYPOINT ["python", "-m", "lab.cli"]
CMD ["run", "--output", "/reports"]
