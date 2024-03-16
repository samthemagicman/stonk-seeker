import {type MetaFunction} from "@remix-run/node";
import {db} from "~/lib/database.server";
import {useLoaderData, useRevalidator} from "@remix-run/react";
import {useEffect} from "react";
import {ColumnDef, flexRender, getCoreRowModel, useReactTable,} from "@tanstack/react-table";
import {Table, TableBody, TableCell, TableHead, TableHeader, TableRow,} from "~/components/ui/table";
import {sql} from "kysely";
import {Area, AreaChart, ResponsiveContainer, Tooltip, XAxis, YAxis,} from "recharts";
import {LoaderFunctionArgs, redirect} from "@remix-run/router";

export const meta: MetaFunction = () => {
    return [
        {title: "New Remix App"},
        {name: "description", content: "Welcome to Remix!"},
    ];
};

export async function loader({params}: LoaderFunctionArgs) {
    let symbol = params.symbol;
    if (!symbol) {
        return redirect("/main");
    }
    symbol = symbol.toUpperCase();
    const data = await db
        .selectFrom("comments")
        .innerJoin("stock_mentions", "stock_mentions.comment_id", "comments.id")
        .where("stock_mentions.symbol", "=", symbol)
        .select(["comments.body", "comments.created_at"])
        .orderBy("comments.created_at", "desc")
        .limit(10)
        .execute();
    const topStocks = await db
        .selectFrom("stock_mentions")
        .select(({fn}) => ["symbol", fn.countAll().as("mentions")])
        .where("created_at", ">", sql`(CURRENT_TIMESTAMP - interval '1 day')`)
        .groupBy("symbol")
        .orderBy("mentions", "desc")
        // .orderBy("latest_mention", "desc")
        .limit(10)
        .execute();

    const chartData = await db
        .selectFrom("stock_mentions as sm")
        .select((eb) => [
            sql`date_trunc
                ('hour', created_at)
                +
            (((date_part('minute', created_at)::integer / 10) * 10) || ' minutes')
            ::interval`.as(
                "time_interval"
            ),
            "sm.symbol as name",
            eb.fn.countAll<number>().as("amount"),
        ])
        .where("sm.symbol", "=", symbol)
        .where("sm.created_at", ">", sql`(CURRENT_TIMESTAMP - interval '1 day')`)
        .groupBy(() => [
            sql`date_trunc
                ('hour', sm.created_at)
                +
            (((date_part('minute', sm.created_at)::integer / 10) * 10) || ' minutes')
            ::interval`,
            "sm.symbol",
        ])
        .orderBy("time_interval", "asc")
        .orderBy((eb) => eb.fn.countAll(), "desc")
        .execute();
    return {topStocks, comments: data, chartData};
}

interface DataTableProps<TData, TValue> {
    columns: ColumnDef<TData, TValue>[];
    data: TData[];
}

function DataTable<TData, TValue>({
                                      columns,
                                      data,
                                  }: DataTableProps<TData, TValue>) {
    const table = useReactTable({
        data,
        columns,
        getCoreRowModel: getCoreRowModel(),
    });

    return (
        <div className="rounded-md border">
            <Table>
                <TableHeader>
                    {table.getHeaderGroups().map((headerGroup) => (
                        <TableRow key={headerGroup.id}>
                            {headerGroup.headers.map((header) => {
                                return (
                                    <TableHead key={header.id}>
                                        {header.isPlaceholder
                                            ? null
                                            : flexRender(
                                                header.column.columnDef.header,
                                                header.getContext()
                                            )}
                                    </TableHead>
                                );
                            })}
                        </TableRow>
                    ))}
                </TableHeader>
                <TableBody>
                    {table.getRowModel().rows?.length ? (
                        table.getRowModel().rows.map((row) => (
                            <TableRow
                                key={row.id}
                                data-state={row.getIsSelected() && "selected"}
                            >
                                {row.getVisibleCells().map((cell) => (
                                    <TableCell key={cell.id}>
                                        {flexRender(cell.column.columnDef.cell, cell.getContext())}
                                    </TableCell>
                                ))}
                            </TableRow>
                        ))
                    ) : (
                        <TableRow>
                            <TableCell colSpan={columns.length} className="h-24 text-center">
                                No results.
                            </TableCell>
                        </TableRow>
                    )}
                </TableBody>
            </Table>
        </div>
    );
}

export default function Index() {
    const data = useLoaderData<typeof loader>();
    const revalidator = useRevalidator();

    useEffect(() => {
        setInterval(() => {
            revalidator.revalidate();
        }, 1000 * 5);
    }, []);

    const columns: ColumnDef<{
        symbol: string | null;
        mentions: string | null;
    }>[] = [
        {
            accessorKey: "symbol",
            header: "Symbol",
        },
        {
            accessorKey: "mentions",
            header: "Mentions",
        },
    ];

    return (
        <div className="flex flex-col m-5">
            <div className="flex flex-col gap-10 flex-1">
                <div>
                    <h2 className="text-2xl font-bold tracking-tight">Welcome back!</h2>
                    <p className="text-muted-foreground">
                        Here's a list of your tasks for this month!
                    </p>
                </div>

                <div className="flex flex-row gap-2">
                    <div className="flex flex-col gap-2">
                        <h3 className="text-lg font-semibold tracking-tight">
                            Top Mentioned Tickers
                        </h3>
                        <DataTable columns={columns} data={data.topStocks}/>
                    </div>

                    <ResponsiveContainer className={"flex-1"} height={300}>
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
                                interval={5}
                            />
                            <YAxis
                                type="number"
                                dataKey="amount"
                                domain={[
                                    0,
                                    data.chartData.reduce(
                                        (max, obj) => Math.max(max, obj.amount),
                                        -Infinity
                                    ) + 10, // For some reason we have to get this manually. Rechart's way of getting maxData seems to be broken.
                                ]}
                            />
                            <Tooltip
                                labelFormatter={(val) => new Date(val).toLocaleString()}
                            />
                            <Area
                                animationDuration={0}
                                type="monotone"
                                dataKey="amount"
                                name="Mentions"
                                stroke="#82ca9d"
                            />
                        </AreaChart>
                    </ResponsiveContainer>
                </div>
            </div>

            <h2>Comments</h2>
            <ul className="flex flex-col gap-4">
                {data.comments.map((comment) => (
                    <li key={comment.created_at} className="p-2 rounded-xl border">
                        {comment.body}
                    </li>
                ))}
            </ul>
        </div>
    );
}
