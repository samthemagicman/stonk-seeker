import { drizzle } from "drizzle-orm/postgres-js";
import postgres from "postgres";

import { env } from "~/env";
import * as schema from "./schema";
import { and, eq, gt, ne, sql } from "drizzle-orm";
import { alias } from "drizzle-orm/pg-core";

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
export async function getStockComments(symbol: string) {
  const stockMentions = alias(schema.stockMentions, "stock_mentions_1");
  const comments = await db
    .select()
    .from(schema.stockMentions)
    .innerJoin(
      schema.comments,
      eq(schema.comments.id, schema.stockMentions.commentId),
    )
    .innerJoin(
      stockMentions,
      and(
        eq(stockMentions.commentId, schema.stockMentions.commentId),
        ne(stockMentions.id, schema.stockMentions.id),
      ),
    )
    .where(eq(schema.stockMentions.symbol, symbol))
    .orderBy(schema.comments.createdAt)
    .limit(100);

  const result = comments.reduce<
    Record<string, { comment: string; mentions: string[] }>
  >((acc, row) => {
    const comment = row.comments;
    const mention = row.stock_mentions;
    const mention2 = row.stock_mentions_1;
    const commentId: string = comment.id;
    if (!acc[commentId]) {
      acc[commentId] = { comment: comment.body, mentions: [] };
    }
    if (mention?.symbol && !acc[commentId].mentions.includes(mention.symbol)) {
      acc[commentId].mentions.push(mention.symbol);
    }
    if (
      mention2?.symbol &&
      !acc[commentId].mentions.includes(mention2.symbol)
    ) {
      acc[commentId].mentions.push(mention2.symbol);
    }
    return acc;
  }, {});

  return result;
}

export async function getStockMentionsOverTime(symbol: string) {
  const mentions = await db
    .select({
      date: sql`date_trunc('hour', created_at)`,
      count: sql<number>`count(*)`,
    })
    .from(schema.stockMentions)
    .where(
      and(
        eq(schema.stockMentions.symbol, symbol),
        gt(schema.stockMentions.createdAt, sql`now() - interval '1 day'`),
      ),
    )
    .groupBy(sql`date_trunc('hour', created_at)`)
    .orderBy(sql`date_trunc('hour', created_at)`);

  return mentions;
}
