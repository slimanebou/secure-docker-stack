# ============ Étape 1 : builder (jetée à la fin) ============
FROM python:3.13-slim-bookworm AS builder

# Environnement virtuel isolé : facile à copier d'une étape à l'autre
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# requirements.txt copié seul d'abord : ce cache Docker n'est
# invalidé que si les dépendances changent, pas à chaque modif du code
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# ============ Étape 2 : image finale ============
FROM python:3.13-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

# Utilisateur système sans shell ni home, UID fixe
RUN groupadd --system --gid 10001 appuser \
 && useradd --system --uid 10001 --gid appuser \
            --no-create-home --shell /usr/sbin/nologin appuser

# On récupère UNIQUEMENT le venv construit dans l'étape builder
COPY --from=builder /opt/venv /opt/venv

WORKDIR /app
# Le code appartient à root : appuser peut le lire, pas le modifier
COPY app.py .

USER appuser
EXPOSE 5000

# Forme exec (tableau JSON) : gunicorn est PID 1 et reçoit bien SIGTERM
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", \
     "--access-logfile", "-", "app:app"]