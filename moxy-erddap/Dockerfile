FROM mambaorg/micromamba:1.5.1

USER root
RUN apt-get update && apt-get install -y curl \
    && rm -rf /var/lib/apt/lists/*
USER $MAMBA_USER

COPY --chown=$MAMBA_USER:$MAMBA_USER environment.yml /tmp/env.yml

RUN micromamba install -y -n base -f /tmp/env.yml && \
    micromamba clean --all --yes

WORKDIR /app

COPY --chown=$MAMBA_USER:$MAMBA_USER . .

CMD ["uvicorn", "--host", "0.0.0.0", "app:app"]
