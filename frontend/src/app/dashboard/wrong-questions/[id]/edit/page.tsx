"use client"

import * as React from "react"
import { useParams, useRouter } from "next/navigation"
import { Loader2 } from "lucide-react"
import useSWR, { mutate } from "swr"

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

interface WrongQuestion {
  id: number
  title: string
  subject: Subject
  tags: Tag[]
  image_base64: string
  created_at: string
  updated_at: string
}

export default function EditWrongQuestionPage() {
  const params = useParams()
  const router = useRouter()
  const { toast } = useToast()

  const id = parseInt(params.id as string)

  const { data: wrongQuestion, isLoading: wrongQuestionLoading } = useSWR<WrongQuestion>(
    `/wrong-questions/${id}`,
    async () => {
      const response = await api.getWrongQuestion(id)
      return response.data
    }
  )

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

  const isLoading = wrongQuestionLoading || subjectsLoading || tagsLoading

  if (isLoading) {
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

  if (!wrongQuestion || !subjects || !tags) {
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

  const tagIds = wrongQuestion.tags.map((t) => t.id)

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-background">
        <Header />
        <main className="p-6">
          <div className="mx-auto max-w-2xl">
            <h1 className="mb-6 text-2xl font-semibold">编辑错题</h1>
            <div className="rounded-lg border bg-card p-6">
              <WrongQuestionForm
                initialData={{
                  id: wrongQuestion.id,
                  title: wrongQuestion.title,
                  subject_id: wrongQuestion.subject.id,
                  tag_ids: tagIds,
                  image_base64: wrongQuestion.image_base64,
                }}
                subjects={subjects}
                tags={tags}
                isEditing={true}
              />
            </div>
          </div>
        </main>
      </div>
    </ProtectedRoute>
  )
}
