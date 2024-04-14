import { drizzle } from "drizzle-orm/postgres-js";
import postgres from "postgres";

import { env } from "~/env";
import * as schema from "./schema";
import { and, sql } from "drizzle-orm";

/**
 * Cache the database connection in development. This avoids creating a new connection on every HMR
 * update.
 */
const globalForDb = globalThis as unknown as {
  conn: postgres.Sql | undefined;
};

const conn = globalForDb.conn ?? postgres(env.DATABASE_URL);
if (env.NODE_ENV !== "production") globalForDb.conn = conn;

export const db = drizzle(conn, { schema });

export async function getTrendingStocks() {
  const stocks = await db
    .select({
      symbol: schema.stockMentions.symbol,
      companyName: schema.stockMentions.companyName,
      mentionCount: sql<number>`cast(count(symbol) as int)`,
    })
    .from(schema.stockMentions)
    .groupBy(schema.stockMentions.symbol, schema.stockMentions.companyName)
    .where(sql`created_at > now() - interval '1 day'`)
    .orderBy(sql`count(symbol) DESC`)
    .limit(100);

  return stocks;
}
export async function getDayOldTrendingStocks() {
  const stocks = await db
    .select({
      symbol: schema.stockMentions.symbol,
      companyName: schema.stockMentions.companyName,
      mentionCount: sql<number>`cast(count(symbol) as int)`,
    })
    .from(schema.stockMentions)
    .groupBy(schema.stockMentions.symbol, schema.stockMentions.companyName)
    .where(
      and(
        sql`created_at > now() - interval '2 day'`,
        sql`created_at < now() - interval '1 day'`,
      ),
    )
    .orderBy(sql`count(symbol) DESC`)
    .limit(100);

  return stocks;
}
