"use client"

import * as React from "react"
import { Loader2 } from "lucide-react"
import useSWR from "swr"

import { ProtectedRoute } from "@/components/ProtectedRoute"
import { Header } from "@/components/Header"
import { WrongQuestionForm } from "@/components/WrongQuestionForm"
import { api } from "@/lib/api"
import { useToast } from "@/components/ui/use-toast"

interface Subject {
  id: number
  name: string
  description: string | null
}

interface Tag {
  id: number
  name: string
  is_preset: boolean
}

export default function NewWrongQuestionPage() {
  const { toast } = useToast()

  const { data: subjects, isLoading: subjectsLoading } = useSWR<Subject[]>(
    "/subjects",
    async () => {
      const response = await api.getSubjects()
      return response.data
    }
  )

  const { data: tags, isLoading: tagsLoading } = useSWR<Tag[]>(
    "/tags",
    async () => {
      const response = await api.getTags()
      return response.data
    }
  )

  if (subjectsLoading || tagsLoading) {
    return (
      <ProtectedRoute>
        <div className="min-h-screen bg-background">
          <Header />
          <main className="flex h-[calc(100vh-64px)] items-center justify-center">
            <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
          </main>
        </div>
      </ProtectedRoute>
    )
  }

  if (!subjects || !tags) {
    return (
      <ProtectedRoute>
        <div className="min-h-screen bg-background">
          <Header />
          <main className="flex h-[calc(100vh-64px)] items-center justify-center">
            <p className="text-muted-foreground">加载数据失败</p>
          </main>
        </div>
      </ProtectedRoute>
    )
  }

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-background">
        <Header />
        <main className="p-6">
          <div className="mx-auto max-w-2xl">
            <h1 className="mb-6 text-2xl font-semibold">新增错题</h1>
            <div className="rounded-lg border bg-card p-6">
              <WrongQuestionForm
                subjects={subjects}
                tags={tags}
                isEditing={false}
              />
            </div>
          </div>
        </main>
      </div>
    </ProtectedRoute>
  )
}
