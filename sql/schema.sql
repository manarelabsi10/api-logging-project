CREATE TABLE IF NOT EXISTS items (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(50) NOT NULL CHECK (char_length(name) >= 1),
    price NUMERIC(10, 2) NOT NULL CHECK (price > 0),
    quantity INTEGER NOT NULL CHECK (quantity >= 0)
);