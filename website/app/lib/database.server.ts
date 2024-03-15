import { DB } from "kysely-codegen"; // this is the Database interface we defined earlier
import pg from "pg";
import { Kysely, PostgresDialect } from "kysely";

export const pool = new pg.Pool({
  database: "postgres",
  host: "localhost",
  user: "postgres",
  password: "postgres",
  port: 5433,
  max: 10,
});

const dialect = new PostgresDialect({
  pool: pool,
});

// Database interface is passed to Kysely's constructor, and from now on, Kysely
// knows your database structure.
// Dialect is passed to Kysely's constructor, and from now on, Kysely knows how
// to communicate with your database.
export const db = new Kysely<DB>({
  dialect,
});
