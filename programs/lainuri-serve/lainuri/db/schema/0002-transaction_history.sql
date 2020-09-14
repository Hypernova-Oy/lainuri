CREATE TABLE transaction_history_types (
  id INTEGER PRIMARY KEY ASC,
  name TEXT NOT NULL UNIQUE
);
CREATE INDEX transaction_history_types_name_idx ON transaction_history_types (name);
INSERT INTO transaction_history_types VALUES
  (NULL, 'checkin'),
  (NULL, 'checkout');

CREATE TABLE transaction_history (
  id INTEGER PRIMARY KEY ASC,
  transaction_type TEXT NOT NULL REFERENCES transaction_history_types (name) ON DELETE NO ACTION ON UPDATE NO ACTION,
  transaction_date INTEGER NOT NULL,
  borrower_barcode TEXT,
  item_barcode TEXT NOT NULL
);
CREATE INDEX transaction_type_idx ON transaction_history (transaction_type);
CREATE INDEX transaction_date_idx ON transaction_history (transaction_date);
