"use client";

import { useState } from "react";
import { Shield } from "lucide-react";

import { AdminRoute } from "@/components/AdminRoute";
import { Header } from "@/components/Header";
import { AdminSidebar, type AdminNavItem } from "@/components/AdminSidebar";
import { UserManagement } from "@/components/admin/UserManagement";
import { SubjectManagement } from "@/components/admin/SubjectManagement";
import { TagManagement } from "@/components/admin/TagManagement";
import { SystemSettings } from "@/components/admin/SystemSettings";

export default function AdminPage() {
  const [activeItem, setActiveItem] = useState<AdminNavItem>("users");

  const renderContent = () => {
    switch (activeItem) {
      case "users":
        return <UserManagement />;
      case "subjects":
        return <SubjectManagement />;
      case "tags":
        return <TagManagement />;
      case "settings":
        return <SystemSettings />;
      default:
        return <UserManagement />;
    }
  };

  return (
    <AdminRoute>
      <div className="min-h-screen bg-background">
        <Header />
        <div className="flex">
          <AdminSidebar activeItem={activeItem} onItemChange={setActiveItem} />
          <main className="flex-1 p-6">
            <div className="mx-auto max-w-6xl">
              <div className="mb-6 flex items-center gap-3 md:hidden">
                <Shield className="h-6 w-6 text-muted-foreground" />
                <h1 className="text-2xl font-semibold">管理面板</h1>
              </div>
              {renderContent()}
            </div>
          </main>
        </div>
      </div>
    </AdminRoute>
  );
}
