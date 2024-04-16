import "~/styles/globals.css";

import { Inter } from "next/font/google";

import { TRPCReactProvider } from "~/trpc/react";
import { cn } from "./_lib/utils";
import { ThemeProvider } from "./_components/theme-provider";
import { Navbar } from "./_components/navbar";
import { TooltipProvider } from "./_components/ui/tooltip";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-sans",
});

export const metadata = {
  title: "Stonk Seeker",
  description: "Top trending Reddit stocks",
  icons: [{ rel: "icon", url: "/favicon.ico" }],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body
        className={cn(
          "min-h-screen font-sans antialiased",
          inter.variable + " font-sans",
        )}
      >
        <TRPCReactProvider>
          <ThemeProvider attribute="class" defaultTheme="dark" enableSystem>
            <TooltipProvider delayDuration={300}>
              <Navbar />
              {children}
            </TooltipProvider>
          </ThemeProvider>
        </TRPCReactProvider>
      </body>
    </html>
  );
}
