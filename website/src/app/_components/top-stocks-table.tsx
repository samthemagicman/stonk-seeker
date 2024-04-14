import { cache } from "react";
import "server-only";
import * as db from "~/server/db";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "./ui/table";
import { Tooltip, TooltipContent, TooltipTrigger } from "./ui/tooltip";
import Link from "next/link";

const getTrendingStocks = cache(async () => {
  const stocks = await db.getTrendingStocks();
  const oldStocks = await db.getDayOldTrendingStocks();
  return { stocks, oldStocks };
});

function percentage(partialValue: number, totalValue: number) {
  return Math.round((partialValue / totalValue) * 10000) / 100;
}

export async function TopStocksTable() {
  const { stocks, oldStocks } = await getTrendingStocks();

  return (
    <Table className="w-full">
      <TableHeader>
        <TableRow>
          <TableHead>Rank</TableHead>
          <TableHead>Company Name</TableHead>
          <TableHead>Symbol</TableHead>
          <TableHead>Mentions</TableHead>
          <TableHead>
            <Tooltip>
              <TooltipTrigger>Change</TooltipTrigger>
              <TooltipContent>
                <p>Change compared to the last 24 hours</p>
              </TooltipContent>
            </Tooltip>
          </TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {stocks.map((stock, index) => (
          <TableRow key={stock.symbol}>
            <TableCell>{index + 1}</TableCell>
            <TableCell>
              <Link
                href={`/stock/${stock.symbol}`}
                className="block hover:underline"
              >
                {stock.companyName}
              </Link>
            </TableCell>
            <TableCell className="font-medium">{stock.symbol}</TableCell>
            <TableCell>{stock.mentionCount}</TableCell>
            <TableCell>
              {oldStocks[index]?.mentionCount === undefined
                ? "N/A"
                : percentage(
                    stock.mentionCount,
                    oldStocks[index].mentionCount,
                  ) +
                  "% (" +
                  oldStocks[index].mentionCount +
                  ")"}
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
