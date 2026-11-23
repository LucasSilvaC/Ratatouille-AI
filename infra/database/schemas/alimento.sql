CREATE TABLE alimento (
    codigo VARCHAR(6) PRIMARY KEY NOT NULL,
    descricao TEXT NOT NULL,
    classe_id INTEGER NOT NULL REFERENCES classes(id), CONSTRAINT alimento_codigo_seis CHECK (length(codigo) = 6));

CREATE INDEX idx_alimentos_classe ON alimento(classe_id);
