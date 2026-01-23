"use client"

import * as React from "react"
import { useRouter } from "next/navigation"
import { Plus, Loader2, Edit } from "lucide-react"
import useSWR from "swr"

import { ProtectedRoute } from "@/components/ProtectedRoute"
import { Header } from "@/components/Header"
import { Button } from "@/components/ui/button"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { api } from "@/lib/api"
import { useToast } from "@/components/ui/use-toast"

interface Subject {
  id: number
  name: string
}

interface Tag {
  id: number
  name: string
}

interface WrongQuestion {
  id: number
  title: string
  subject: Subject
  tags: Tag[]
  created_at: string
  updated_at: string
}

export default function WrongQuestionsPage() {
  const router = useRouter()
  const { toast } = useToast()

  const { data: wrongQuestions, isLoading, error } = useSWR<WrongQuestion[]>(
    "/wrong-questions",
    async () => {
      const response = await api.getWrongQuestions()
      return response.data
    }
  )

  const formatDate = (dateString: string) => {
    // 确保字符串被正确解析为 UTC 时间
    const date = new Date(dateString + (dateString.endsWith("Z") ? "" : "Z"))
    return date.toLocaleString("zh-CN", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
    })
  }

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-background">
        <Header />
        <main className="p-6">
          <div className="mx-auto max-w-6xl">
            <div className="mb-6 flex items-center justify-between">
              <h1 className="text-2xl font-semibold">错题本</h1>
              <Button onClick={() => router.push("/dashboard/wrong-questions/new")}>
                <Plus className="mr-2 h-4 w-4" />
                新增错题
              </Button>
            </div>

            <div className="rounded-lg border bg-card">
              {isLoading ? (
                <div className="flex h-64 items-center justify-center">
                  <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
                </div>
              ) : error ? (
                <div className="flex h-64 items-center justify-center">
                  <p className="text-muted-foreground">
                    加载失败，请刷新页面重试
                  </p>
                </div>
              ) : !wrongQuestions || wrongQuestions.length === 0 ? (
                <div className="flex h-64 flex-col items-center justify-center">
                  <p className="mb-4 text-muted-foreground">
                    还没有错题记录，点击上方按钮添加第一道错题吧！
                  </p>
                  <Button
                    variant="outline"
                    onClick={() => router.push("/dashboard/wrong-questions/new")}
                  >
                    <Plus className="mr-2 h-4 w-4" />
                    添加错题
                  </Button>
                </div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>标题</TableHead>
                      <TableHead>学科</TableHead>
                      <TableHead>标签</TableHead>
                      <TableHead>创建时间</TableHead>
                      <TableHead className="text-right">操作</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {wrongQuestions.map((wq) => (
                      <TableRow key={wq.id}>
                        <TableCell className="font-medium">{wq.title}</TableCell>
                        <TableCell>{wq.subject.name}</TableCell>
                        <TableCell>
                          <div className="flex flex-wrap gap-1">
                            {wq.tags.map((tag) => (
                              <Badge key={tag.id} variant="secondary">
                                {tag.name}
                              </Badge>
                            ))}
                          </div>
                        </TableCell>
                        <TableCell>{formatDate(wq.created_at)}</TableCell>
                        <TableCell className="text-right">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() =>
                              router.push(`/dashboard/wrong-questions/${wq.id}/edit`)
                            }
                          >
                            <Edit className="h-4 w-4" />
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </div>
          </div>
        </main>
      </div>
    </ProtectedRoute>
  )
}
