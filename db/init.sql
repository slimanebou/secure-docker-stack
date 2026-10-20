-- Exécuté automatiquement par l'image postgres, UNIQUEMENT si le volume est vide
CREATE TABLE IF NOT EXISTS clients (
    id         SERIAL PRIMARY KEY,
    nom        VARCHAR(100) NOT NULL,
    email      VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMPTZ  NOT NULL DEFAULT now()
);

INSERT INTO clients (nom, email) VALUES
    ('Alice Martin',  'alice.martin@example.com'),
    ('Karim Benali',  'karim.benali@example.com'),
    ('Sophie Durand', 'sophie.durand@example.com')
ON CONFLICT (email) DO NOTHING;