import type { Metadata } from "next";

import { ThemeProvider } from "@/components/organisms/theme-provider";

import "./globals.css";

export const metadata: Metadata = {
  title: "Acrux Project Template",
  description: "A reusable fullstack baseline for Acrux web applications.",
};

interface IRootLayoutProps {
  children: React.ReactNode;
}

export default function RootLayout({ children }: IRootLayoutProps): React.ReactElement {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <ThemeProvider>{children}</ThemeProvider>
      </body>
    </html>
  );
}
