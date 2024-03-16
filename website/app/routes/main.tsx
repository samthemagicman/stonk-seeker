import {type MetaFunction} from "@remix-run/node";
import {db} from "~/lib/database.server";
import {useLoaderData, useRevalidator} from "@remix-run/react";
import {useEffect} from "react";
import {ColumnDef, flexRender, getCoreRowModel, useReactTable,} from "@tanstack/react-table";
import {Table, TableBody, TableCell, TableHead, TableHeader, TableRow,} from "~/components/ui/table";
import {sql} from "kysely";

export const meta: MetaFunction = () => {
    return [
        {title: "New Remix App"},
        {name: "description", content: "Welcome to Remix!"},
    ];
};

export async function loader() {
    // const topStocks = await db
    //     .selectFrom("stock_mentions")
    //     .select(({fn}) => [
    //         "symbol",
    //         fn.countAll().as("mentions"), "company_name",
    //         fn.agg<string[]>('ROW_NUMBER').over((eb) => eb.orderBy("mentions", "desc")).as('rank'),
    //     ])
    //
    //     .where("created_at", ">", sql`(CURRENT_TIMESTAMP - interval '1 day')`)
    //     .groupBy("symbol")
    //     .groupBy("company_name")
    //     .orderBy("mentions", "desc")
    //     // .orderBy("latest_mention", "desc")
    //     .limit(100)
    //     .execute();

    //  TODO: Swap all this nonsense to Slonik
    const topStocks = await db
        .selectFrom((eb) => eb.selectFrom("stock_mentions")
            .select(({fn}) => [
                "symbol",
                fn.countAll().as("mentions"), "company_name"
            ])

            .where("created_at", ">", sql`(CURRENT_TIMESTAMP - interval '1 day')`)
            .groupBy("symbol")
            .groupBy("company_name")
            .orderBy("mentions", "desc")
            // .orderBy("latest_mention", "desc")
            .limit(100))
        .selectAll()
        .select(({fn}) => fn.agg<string[]>('ROW_NUMBER').over((eb) => eb.orderBy("mentions", "desc")).as('rank'),)
        .execute();

    db.selectFrom((eb) => eb.selectFrom("stock_mentions"))

    return {topStocks};
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

    data.topStocks.map((stock) => {
        return stock
    })

    const columns: ColumnDef<{
        company_name: string | null;
        rank: string | null;
        name: string | null;
        symbol: string | null;
        mentions: string | null;
    }>[] = [
        {
            accessorKey: "rank",
            header: "Rank"
        },
        {
            accessorKey: "company_name",
            header: "Name",
            cell: props => {
                /* eslint-disable react/prop-types */ // TODO: upgrade to latest eslint tooling
                const symbol = props.row.original.symbol;
                return (
                    <a className="flex items-center" href={`/stock/${symbol}`}>
                        <div className="flex flex-row gap-3 items-center">
                            {/*<img src={`https://eodhd.com/img/logos/US/${symbol}.png`}*/}
                            {/*     className={"h-4 w-4 aspect-square"}*/}
                            {/*     alt={"symbol"}*/}
                            {/*/>*/}
                            <span>{props.cell.getValue()}</span>
                        </div>
                    </a>
                );
            }
        },
        {
            accessorKey: "symbol",
            header: "Symbol",
        },
        {
            accessorKey: "mentions",
            header: "Mentions",
        },
    ];

    useEffect(() => {
        setInterval(() => {
            revalidator.revalidate();
        }, 1000 * 5);
    }, []);

    return (
        <div className={"flex justify-center"}>
            <div className="flex flex-col m-5 max-w-screen-lg w-full">
                <div className="flex flex-col gap-10 flex-1">
                    <div>
                        <h2 className="text-2xl font-bold tracking-tight">Welcome back!</h2>
                        <p className="text-muted-foreground">
                            Here's a list of your tasks for this month!
                        </p>
                    </div>

                    <div className="flex flex-col gap-2">
                        <h3 className="text-lg font-semibold tracking-tight">
                            Top Mentioned Tickers
                        </h3>
                        <DataTable columns={columns} data={data.topStocks}/>
                    </div>
                </div>
            </div>
        </div>
    );
}
