FROM python:3.15.1-slim-bookworm@sha256:575f8bc12ec26542e0678bc6b60e385218248019d433157ec327264a78c3a853
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
