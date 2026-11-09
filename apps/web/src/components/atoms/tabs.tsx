"use client";

import { Tabs as TabsPrimitive } from "radix-ui";
import * as React from "react";

import { cn } from "@/lib/utils";

export const Tabs = TabsPrimitive.Root;
export function TabsList({ className, ...props }: React.ComponentProps<typeof TabsPrimitive.List>) {
  return (
    <TabsPrimitive.List
      className={cn("bg-muted inline-flex flex-wrap items-center gap-1 rounded-xl p-1", className)}
      {...props}
    />
  );
}
export function TabsTrigger({
  className,
  ...props
}: React.ComponentProps<typeof TabsPrimitive.Trigger>) {
  return (
    <TabsPrimitive.Trigger
      className={cn(
        "text-muted-foreground focus-visible:ring-ring data-[state=active]:bg-card data-[state=active]:text-foreground min-h-11 rounded-lg px-4 py-2 text-sm font-semibold outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:opacity-50 data-[state=active]:shadow-sm",
        className,
      )}
      {...props}
    />
  );
}
export function TabsContent({
  className,
  ...props
}: React.ComponentProps<typeof TabsPrimitive.Content>) {
  return (
    <TabsPrimitive.Content
      className={cn("focus-visible:ring-ring mt-6 outline-none focus-visible:ring-2", className)}
      {...props}
    />
  );
}
