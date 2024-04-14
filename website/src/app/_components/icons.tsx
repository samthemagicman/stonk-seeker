import * as React from "react";
import { cn } from "../_lib/utils";
export function StonkSeekerLogo({
  className,
  ...props
}: React.SVGAttributes<SVGElement>) {
  return (
    <svg
      viewBox="0 0 536.9499 221.4531"
      height={100}
      className={cn("fill-black dark:fill-white", className)}
      preserveAspectRatio="none"
      {...props}
    >
      <use href="/logo.svg#main"></use>
    </svg>
  );
}
