"use client";

import { useRouter } from "next/navigation";
import { Plus } from "lucide-react";

import { Header } from "@/components/Header";
import { Button } from "@/components/ui/button";

export function DashboardContent() {
  const router = useRouter();
  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main className="p-6">
        <div className="mx-auto max-w-4xl">
          <div className="mb-6 flex items-center justify-between">
            <h1 className="text-2xl font-semibold">Dashboard</h1>
            <Button onClick={() => router.push("/wrong-questions/new")}>
              <Plus className="mr-2 h-4 w-4" />
              新增错题
            </Button>
          </div>
          <div className="rounded-lg border bg-card p-6">
            <p className="text-muted-foreground">
              Welcome to the Kids Homework Review dashboard!
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
