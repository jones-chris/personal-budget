-- The unique "natural id(ish)" of a transaction.
CREATE UNIQUE INDEX ux_internal_id ON transactions(internal_id);
