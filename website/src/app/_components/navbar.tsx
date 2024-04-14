"use client";

import Link from "next/link";
import { StonkSeekerLogo } from "./icons";
import {
  NavigationMenu,
  NavigationMenuContent,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  NavigationMenuTrigger,
} from "./ui/navigation-menu";

export function Navbar() {
  return (
    <div className={"border-b-[1px] border-accent"}>
      <NavigationMenu className="mx-auto my-2 max-w-7xl px-4 sm:px-6 md:px-8">
        <NavigationMenuList>
          <NavigationMenuItem>
            <Link href="/">
              <StonkSeekerLogo height={60} />
            </Link>
          </NavigationMenuItem>
        </NavigationMenuList>
      </NavigationMenu>
    </div>
  );
}
