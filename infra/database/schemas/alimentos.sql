CREATE TABLE alimentos (
    codigo TEXT PRIMARY KEY NOT NULL,
    descricao TEXT NOT NULL,
    classe_id INTEGER NOT NULL REFERENCES classes(id));

CREATE INDEX idx_alimentos_classe ON alimentos(classe_id);
