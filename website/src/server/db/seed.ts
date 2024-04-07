import * as dotenv from "dotenv";
dotenv.config();

import postgres from "postgres";
import { drizzle } from "drizzle-orm/postgres-js";
import * as schema from "~/server/db/schema";
import { posts, subreddits, comments, stockMentions } from "~/server/db/schema";
import { faker } from "@faker-js/faker";
import invariant from "tiny-invariant";

const db_url = process.env.DATABASE_URL;

// eslint-disable-next-line @typescript-eslint/no-unsafe-call
invariant(db_url, "DATABASE_URL must be defined");

const db = drizzle(postgres(db_url), { schema });

console.log("Clearing old data");
// eslint-disable-next-line drizzle/enforce-delete-with-where
await db.delete(subreddits);
// eslint-disable-next-line drizzle/enforce-delete-with-where
await db.delete(posts);
// eslint-disable-next-line drizzle/enforce-delete-with-where
await db.delete(comments);
// eslint-disable-next-line drizzle/enforce-delete-with-where
await db.delete(stockMentions);

console.log("Seeding new data");
const subredditId = faker.string.alphanumeric(10);
await db.insert(subreddits).values({
  id: subredditId,
  name: "stocks",
});

for (let i = 0; i < 10; i++) {
  const postId = faker.string.alphanumeric(10);
  await db.insert(posts).values({
    id: postId,
    link: faker.internet.url(),
    subreddit_id: subredditId,
  });

  // 10 comments per post
  for (let j = 0; j < 10; j++) {
    const cmtId = faker.string.alphanumeric(10);
    await db.insert(comments).values({
      id: cmtId,
      postId,
      body: faker.lorem.sentence(),
    });

    // 5 stock mentions per comment
    for (let k = 0; k < 5; k++) {
      const companyName = faker.company.name();
      const companySymbol = faker.finance.currencyCode();

      // Random number of mentions
      for (let m = 0; m < Math.random() * 30; m++) {
        await db.insert(stockMentions).values({
          id: faker.string.alphanumeric(10),
          commentId: cmtId,
          symbol: companySymbol,
          companyName: companyName,
        });
      }
    }
  }
}

process.exit(0);
