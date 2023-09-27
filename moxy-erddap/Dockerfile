FROM mambaorg/micromamba:1.5.1

COPY --chown=$MAMBA_USER:$MAMBA_USER environment.yml /tmp/env.yml

RUN micromamba install -y -n base -f /tmp/env.yml && \
    micromamba clean --all --yes

WORKDIR /app

COPY --chown=$MABMA_USER:$MAMBA_USER . .

CMD ["uvicorn", "--host", "0.0.0.0", "app:app"]
