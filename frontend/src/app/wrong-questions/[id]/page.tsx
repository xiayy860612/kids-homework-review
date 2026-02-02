"use client"

import * as React from "react"
import { useParams } from "next/navigation"
import { Loader2, Sparkles } from "lucide-react"
import useSWR, { useSWRConfig } from "swr"

import { ProtectedRoute } from "@/components/ProtectedRoute"
import { Header } from "@/components/Header"
import { WrongQuestionForm } from "@/components/WrongQuestionForm"
import { Button } from "@/components/ui/button"
import { useToast } from "@/components/ui/use-toast"
import { api, type WrongQuestion } from "@/lib/api"

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

export default function ViewWrongQuestionPage() {
  const params = useParams()
  const { mutate } = useSWRConfig()
  const { toast } = useToast()

  const id = parseInt(params.id as string)
  const [isAnalyzing, setIsAnalyzing] = React.useState(false)

  const fetcher = React.useCallback(
    async (key: string) => {
      if (key.startsWith("/wrong-questions/")) {
        const response = await api.getWrongQuestion(id)
        return response.data
      }
      if (key === "/subjects") {
        const response = await api.getSubjects()
        return response.data
      }
      if (key === "/tags") {
        const response = await api.getTags()
        return response.data
      }
      return null
    },
    [id]
  )

  const { data: wrongQuestion, isLoading: wrongQuestionLoading } = useSWR<WrongQuestion>(
    `/wrong-questions/${id}`,
    fetcher,
    {
      refreshInterval: (data) => {
        // Poll every 3 seconds when analysis is processing
        return data?.analysis_status === "processing" ? 3000 : 0
      },
      revalidateOnFocus: true,
      revalidateOnReconnect: true,
    }
  )

  const { data: subjects, isLoading: subjectsLoading } = useSWR<Subject[]>(
    "/subjects",
    fetcher
  )

  const { data: tags, isLoading: tagsLoading } = useSWR<Tag[]>(
    "/tags",
    fetcher
  )

  const isLoading = wrongQuestionLoading || subjectsLoading || tagsLoading

  const handleAnalyze = async () => {
    setIsAnalyzing(true)
    try {
      await api.analyzeWrongQuestion(id)
      mutate(`/wrong-questions/${id}`)
      toast({
        title: "开始解析",
        description: "AI 正在分析错题，请稍候...",
      })
    } catch (error) {
      console.error("Failed to analyze:", error)
      toast({
        title: "解析失败",
        description: "启动 AI 解析失败，请重试",
        variant: "destructive",
      })
    } finally {
      setIsAnalyzing(false)
    }
  }

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
  const isCompleted = wrongQuestion.analysis_status === "completed"
  const isProcessing = wrongQuestion.analysis_status === "processing"

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-background">
        <Header />
        <main className="p-6">
          <div className="mx-auto max-w-2xl">
            <div className="mb-6 flex items-center justify-between">
              <h1 className="text-2xl font-semibold">查看错题</h1>
              <Button
                onClick={handleAnalyze}
                disabled={isAnalyzing || isProcessing}
                size="sm"
                variant={isCompleted ? "outline" : "default"}
              >
                {isAnalyzing ? (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                ) : isCompleted ? (
                  <Sparkles className="mr-2 h-4 w-4" />
                ) : (
                  <Sparkles className="mr-2 h-4 w-4" />
                )}
                {isCompleted ? "重新解析" : "AI 解析"}
              </Button>
            </div>
            <div className="rounded-lg border bg-card p-6">
              <WrongQuestionForm
                initialData={{
                  id: wrongQuestion.id,
                  title: wrongQuestion.title,
                  subject_id: wrongQuestion.subject.id,
                  tag_ids: tagIds,
                  image_base64: wrongQuestion.image_base64,
                  analysis_status: wrongQuestion.analysis_status,
                  analysis_result: wrongQuestion.analysis_result,
                  analysis_error: wrongQuestion.analysis_error,
                }}
                subjects={subjects}
                tags={tags}
                isEditing={true}
                readOnly={true}
              />
            </div>
          </div>
        </main>
      </div>
    </ProtectedRoute>
  )
}
