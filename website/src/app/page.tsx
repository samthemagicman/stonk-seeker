import { StonkSeekerLogo } from "./_components/icons";
import { Button } from "./_components/ui/button";
import Image from "next/image";

export default async function Home() {
  return (
    <main>
      <StonkSeekerLogo />
      <h1 className="text-4xl font-bold">Welcome to tRPC</h1>
      <Button>Click me</Button>
    </main>
  );
}
