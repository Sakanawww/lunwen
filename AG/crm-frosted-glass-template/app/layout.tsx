import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "KONTUR Ledger CRM",
  description: "Swiss-ledger CRM workspace on warm paper: pipeline kanban, contact ledger, pure-CSS revenue chart, and an activity timeline.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
