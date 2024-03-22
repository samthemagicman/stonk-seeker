import { type MetaFunction } from "@remix-run/node";
import { db } from "~/lib/database.server";
import { Link, useLoaderData, useRevalidator } from "@remix-run/react";
import { useEffect } from "react";
import { sql } from "kysely";
import {
  Area,
  AreaChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { LoaderFunctionArgs, redirect } from "@remix-run/router";
import { buttonVariants } from "~/components/ui/button";
import { HomeIcon } from "@radix-ui/react-icons";

export async function loader({ params }: LoaderFunctionArgs) {
  let symbol = params.symbol;
  if (!symbol) {
    return redirect("/");
  }
  const symbolExists = await db
    .selectFrom("stock_mentions")
    .where("symbol", "=", symbol)
    .execute();

  if (symbolExists.length === 0) {
    throw new Response("Symbol not found", {
      status: 404,
      statusText: "Symbol not found",
    });
  }

  symbol = symbol.toUpperCase();
  const data = await db
    .selectFrom("comments")
    .innerJoin("stock_mentions", "stock_mentions.comment_id", "comments.id")
    .where("stock_mentions.symbol", "=", symbol)
    .select(["comments.body", "comments.created_at", "comments.permalink"])
    .orderBy("comments.created_at", "desc")
    .limit(30)
    .execute();

  const chartData = await db
    .selectFrom("stock_mentions as sm")
    .select((eb) => [
      sql`date_trunc
                ('hour', created_at)
                +
            (((date_part('minute', created_at)::integer / 60) * 60) || ' minutes')
            ::interval`.as("time_interval"),
      "sm.symbol as name",
      eb.fn.countAll<number>().as("amount"),
    ])
    .where("sm.symbol", "=", symbol)
    .where("sm.created_at", ">", sql`(CURRENT_TIMESTAMP - interval '1 day')`)
    .groupBy(() => [
      sql`date_trunc
                ('hour', sm.created_at)
                +
            (((date_part('minute', sm.created_at)::integer / 60) * 60) || ' minutes')
            ::interval`,
      "sm.symbol",
    ])
    .orderBy("time_interval", "asc")
    .orderBy((eb) => eb.fn.countAll(), "desc")
    .execute();
  return { comments: data, chartData, stockName: symbol };
}

export default function Index() {
  const data = useLoaderData<typeof loader>();
  const revalidator = useRevalidator();

  useEffect(() => {
    setInterval(() => {
      if (document.hasFocus()) {
        revalidator.revalidate();
      }
    }, 1000 * 5);
  }, []);

  return (
    <div className="flex flex-col m-5">
      <div className="flex flex-col gap-10 flex-1 mb-3">
        <div className="flex flex-row gap-5">
          <Link to="/" className={buttonVariants({ variant: "outline" })}>
            <HomeIcon className="mr-2 h-4 w-4" /> Home
          </Link>
          <h2 className="text-2xl text-muted-foreground tracking-tight">
            Viewing{" "}
            <span className="text-primary font-bold">{data.stockName}</span>
          </h2>
        </div>
        <ResponsiveContainer width={"100%"} height={300}>
          <AreaChart
            data={data.chartData}
            margin={{
              top: 5,
              right: 30,
              left: 20,
              bottom: 5,
            }}
          >
            <XAxis
              name="Time Interval"
              dataKey="time_interval"
              tickFormatter={(val) => {
                let hours = new Date(val).getHours();
                const amOrPm = hours >= 12 ? "pm" : "am";
                hours = hours % 12;
                hours = hours ? hours : 12; // the hour '0' should be '12'
                return `${hours} ${amOrPm}`;
              }}
            />
            <YAxis
              type="number"
              dataKey="amount"
              domain={[
                0,
                data.chartData.reduce(
                  (max: number, obj: { amount: number }) =>
                    Math.max(max, obj.amount),
                  -Infinity
                ) + 10, // For some reason we have to get this manually. Rechart's way of getting maxData seems to be broken.
              ]}
            />
            <Tooltip labelFormatter={(val) => new Date(val).toLocaleString()} />
            <Area
              type="monotone"
              dataKey="amount"
              name="Mentions"
              stroke="bg-secondary"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <div className="mb-2">
        <h2 className="text-lg font-semibold tracking-tight">
          Comments Stream
        </h2>
      </div>
      <ul className="flex flex-col gap-4">
        {data.comments.map(
          (comment: {
            created_at: string;
            body: string;
            permalink: string;
          }) => (
            <a
              href={"https://reddit.com" + comment.permalink}
              rel="noreferrer noopener"
              target="_blank"
              key={comment.created_at}
              className="border p-3 rounded-sm"
            >
              {comment.body}
            </a>
          )
        )}
      </ul>
    </div>
  );
}
