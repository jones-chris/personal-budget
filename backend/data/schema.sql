DROP TABLE IF EXISTS transactions;

DROP TABLE IF EXISTS category;

DROP TABLE IF EXISTS transaction_categories;

CREATE TABLE IF NOT EXISTS transactions(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    internal_id TEXT NOT NULL,
	payee TEXT NOT NULL,
	type TEXT,
	date TIMESTAMP NOT NULL,
	amount NUMERIC NOT NULL,
	institution_id TEXT NOT NULL,
	memo TEXT,
	sic TEXT,
	mcc TEXT,
	checknum TEXT
);

CREATE TABLE IF NOT EXISTS category(
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	name TEXT UNIQUE
);

-- Create the default category for all transactions.
INSERT INTO category (name) VALUES ('Uncategorized');

CREATE TABLE IF NOT EXISTS transaction_categories(
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	transaction_id TEXT NOT NULL,
	category_id INTEGER NOT NULL,
	amount NUMERIC NOT NULL,

	UNIQUE (id, transaction_id, category_id),
	FOREIGN KEY (transaction_id) REFERENCES transactions(id),
	FOREIGN KEY (category_id) REFERENCES category(id)
);
