import { TopStocksTable } from "./_components/top-stocks-table";
import Main from "./_components/ui/main";

export const revalidate = 1800;

export default async function Home() {
  return (
    <Main>
      <h1 className="text-center text-2xl font-bold">
        Trending Stocks on Reddit
      </h1>
      <div className="mx-auto w-full max-w-screen-lg">
        <TopStocksTable />
      </div>
    </Main>
  );
}
