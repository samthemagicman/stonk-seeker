// Example model schema from the Drizzle docs
// https://orm.drizzle.team/docs/sql-schema-declaration

import { sql } from "drizzle-orm";
import {
  index,
  pgTableCreator,
  serial,
  timestamp,
  varchar,
  text,
} from "drizzle-orm/pg-core";

/**
 * This is an example of how to use the multi-project schema feature of Drizzle ORM. Use the same
 * database instance for multiple projects.
 *
 * @see https://orm.drizzle.team/docs/goodies#multi-project-schema
 */
export const createTable = pgTableCreator((name) => name);

export const subreddits = createTable("subreddits", {
  id: text("id").primaryKey(),
  name: text("name").unique().notNull(),
});

export const posts = createTable("posts", {
  id: text("id").primaryKey(),
  link: text("link"),
  subreddit_id: text("subreddit_id").references(() => subreddits.id, {
    onDelete: "cascade",
  }),
});

export const comments = createTable("comments", {
  id: text("id").primaryKey(),
  postId: text("post_id").references(() => posts.id, {
    onDelete: "cascade",
  }),
  body: text("body"),
});

export const stockMentions = createTable("stock_mentions", {
  id: text("id").primaryKey(),
  commentId: text("comment_id").references(() => comments.id, {
    onDelete: "cascade",
  }),
  symbol: text("symbol"),
  companyName: text("company_name"),
  created_at: timestamp("created_at", { withTimezone: true }).default(
    sql`now()`,
  ),
});
