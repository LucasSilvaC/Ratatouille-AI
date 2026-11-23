CREATE TABLE nutriente (
    id INTEGER PRIMARY KEY,
    componente TEXT NOT NULL,
    unidade TEXT NOT NULL,
    UNIQUE (componente, unidade)
);
