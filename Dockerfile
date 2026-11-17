FROM python:3.12.16-slim-bookworm@sha256:935c3c5b12357a7e10caa9c1e6ca5692344d97cf229832ef584be2cec9fc03df
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /lab
RUN useradd --uid 10001 --create-home learner && mkdir /reports && chown learner:learner /reports
COPY --chown=learner:learner lab/ lab/
COPY --chown=learner:learner app/ app/
COPY --chown=learner:learner policies/ policies/
COPY --chown=learner:learner fixtures/ fixtures/
COPY --chown=learner:learner pipelines/ pipelines/
RUN touch /lab/.pipelineproof-container
USER 10001:10001
ENTRYPOINT ["python", "-m", "lab.cli"]
CMD ["run", "--output", "/reports"]
