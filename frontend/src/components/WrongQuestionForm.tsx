"use client"

import * as React from "react"
import { useRouter } from "next/navigation"
import { Loader2, Edit } from "lucide-react"
import { useSWRConfig } from "swr"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { ImageUpload } from "@/components/ImageUpload"
import { TagSelector } from "@/components/TagSelector"
import { useToast } from "@/components/ui/use-toast"
import { api } from "@/lib/api"
import { cn } from "@/lib/utils"

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

interface WrongQuestionFormProps {
  initialData?: {
    id?: number
    title?: string
    subject_id?: number
    tag_ids?: number[]
    image_base64?: string
  }
  subjects: Subject[]
  tags: Tag[]
  isEditing?: boolean
  readOnly?: boolean
  className?: string
}

export function WrongQuestionForm({
  initialData,
  subjects,
  tags,
  isEditing = false,
  readOnly = false,
  className,
}: WrongQuestionFormProps) {
  const router = useRouter()
  const { mutate } = useSWRConfig()
  const { toast } = useToast()

  const [title, setTitle] = React.useState(initialData?.title ?? "")
  const [subjectId, setSubjectId] = React.useState<number | undefined>(
    initialData?.subject_id
  )
  const [tagIds, setTagIds] = React.useState<number[]>(initialData?.tag_ids ?? [])
  const [imageBase64, setImageBase64] = React.useState<string | undefined>(
    initialData?.image_base64
  )
  const [isSubmitting, setIsSubmitting] = React.useState(false)
  const [errors, setErrors] = React.useState<
    Record<string, string | undefined>
  >({})

  const validate = () => {
    const newErrors: Record<string, string | undefined> = {}

    if (!title.trim()) {
      newErrors.title = "请输入标题"
    }

    if (!subjectId) {
      newErrors.subject_id = "请选择学科"
    }

    if (!imageBase64) {
      newErrors.image = "请上传错题截图"
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!validate()) return
    if (!subjectId) return

    setIsSubmitting(true)

    try {
      const data = {
        title: title.trim(),
        subject_id: subjectId,
        tag_ids: tagIds,
        image_base64: imageBase64!,
      }

      if (isEditing && initialData?.id) {
        await api.updateWrongQuestion(initialData.id, data)
        toast({
          title: "更新成功",
          description: "错题已更新",
        })
      } else {
        await api.createWrongQuestion(data)
        toast({
          title: "创建成功",
          description: "错题已添加",
        })
      }

      // Invalidate cache
      mutate("/wrong-questions")

      router.push("/wrong-questions")
    } catch (error) {
      console.error("Failed to save wrong question:", error)
      toast({
        title: "操作失败",
        description: "保存错题时出错，请重试",
        variant: "destructive",
      })
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleCreateTag = async (name: string): Promise<Tag> => {
    const response = await api.createTag({ name })
    return response.data
  }

  const isDisabled = isSubmitting || readOnly

  return (
    <form onSubmit={handleSubmit} className={cn("space-y-6", className)}>
      {/* Title */}
      <div className="space-y-2">
        <Label htmlFor="title">
          标题 <span className="text-destructive">*</span>
        </Label>
        <Input
          id="title"
          placeholder="例如：二次函数求最值问题"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          disabled={isDisabled}
          className={errors.title ? "border-destructive" : ""}
        />
        {errors.title && (
          <p className="text-sm text-destructive">{errors.title}</p>
        )}
      </div>

      {/* Subject */}
      <div className="space-y-2">
        <Label htmlFor="subject">
          学科 <span className="text-destructive">*</span>
        </Label>
        <Select
          value={subjectId?.toString() || ""}
          onValueChange={(value) => setSubjectId(parseInt(value))}
          disabled={isDisabled}
        >
          <SelectTrigger
            id="subject"
            className={errors.subject_id ? "border-destructive" : ""}
          >
            <SelectValue placeholder="请选择学科" />
          </SelectTrigger>
          <SelectContent>
            {subjects.map((subject) => (
              <SelectItem key={subject.id} value={subject.id.toString()}>
                {subject.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        {errors.subject_id && (
          <p className="text-sm text-destructive">{errors.subject_id}</p>
        )}
      </div>

      {/* Tags */}
      <div className="space-y-2">
        <Label>标签</Label>
        <TagSelector
          availableTags={tags}
          selectedTagIds={tagIds}
          onChange={setTagIds}
          onCreateTag={handleCreateTag}
          disabled={isDisabled}
        />
      </div>

      {/* Image Upload */}
      <div className="space-y-2">
        <Label>
          错题截图 <span className="text-destructive">*</span>
        </Label>
        <ImageUpload
          value={imageBase64}
          onChange={setImageBase64}
          onRemove={() => setImageBase64(undefined)}
          disabled={isDisabled}
          className={errors.image ? "border-destructive" : ""}
        />
        {errors.image && (
          <p className="text-sm text-destructive">{errors.image}</p>
        )}
      </div>

      {/* Submit/Action Buttons */}
      {readOnly ? (
        <div className="flex gap-3">
          <Button
            type="button"
            onClick={() => router.push(`/wrong-questions/${initialData?.id}/edit`)}
          >
            <Edit className="mr-2 h-4 w-4" />
            编辑
          </Button>
          <Button
            type="button"
            variant="outline"
            onClick={() => router.back()}
          >
            返回
          </Button>
        </div>
      ) : (
        <div className="flex gap-3">
          <Button type="submit" disabled={isDisabled}>
            {isSubmitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            {isEditing ? "更新" : "创建"}
          </Button>
          <Button
            type="button"
            variant="outline"
            onClick={() => router.back()}
            disabled={isDisabled}
          >
            取消
          </Button>
        </div>
      )}
    </form>
  )
}
