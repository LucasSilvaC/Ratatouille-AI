CREATE TABLE "alimento_nutrientes" (
 alimento_codigo TEXT NOT NULL REFERENCES alimento(codigo),
 nutriente_id INTEGER NOT NULL REFERENCES nutriente(id),
 valor_numerico REAL
 );

CREATE INDEX idx_an_alimento ON alimento_nutrientes(alimento_codigo);

CREATE INDEX idx_an_nutriente_valor ON alimento_nutrientes(nutriente_id,valor_numerico);
