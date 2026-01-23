"use client"

import * as React from "react"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { X, Plus } from "lucide-react"

import { cn } from "@/lib/utils"

interface Tag {
  id: number
  name: string
  is_preset: boolean
}

interface TagSelectorProps {
  availableTags: Tag[]
  selectedTagIds: number[]
  onChange: (tagIds: number[]) => void
  onCreateTag?: (name: string) => Promise<Tag>
  disabled?: boolean
  className?: string
}

export function TagSelector({
  availableTags,
  selectedTagIds,
  onChange,
  onCreateTag,
  disabled = false,
  className,
}: TagSelectorProps) {
  const [newTagName, setNewTagName] = React.useState("")
  const [isCreating, setIsCreating] = React.useState(false)
  const [showCreateInput, setShowCreateInput] = React.useState(false)

  const selectedTags = availableTags.filter((tag) =>
    selectedTagIds.includes(tag.id)
  )

  const handleToggleTag = (tagId: number) => {
    if (selectedTagIds.includes(tagId)) {
      onChange(selectedTagIds.filter((id) => id !== tagId))
    } else {
      onChange([...selectedTagIds, tagId])
    }
  }

  const handleCreateTag = async () => {
    if (!newTagName.trim() || !onCreateTag) return

    setIsCreating(true)
    try {
      // Check if tag already exists
      const existingTag = availableTags.find(
        (t) => t.name.toLowerCase() === newTagName.toLowerCase().trim()
      )

      if (existingTag) {
        // Just select the existing tag
        if (!selectedTagIds.includes(existingTag.id)) {
          onChange([...selectedTagIds, existingTag.id])
        }
        setNewTagName("")
        setShowCreateInput(false)
        return
      }

      const newTag = await onCreateTag(newTagName.trim())
      onChange([...selectedTagIds, newTag.id])
      setNewTagName("")
      setShowCreateInput(false)
    } catch (error) {
      console.error("Failed to create tag:", error)
    } finally {
      setIsCreating(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      e.preventDefault()
      handleCreateTag()
    }
  }

  const availablePresetTags = availableTags.filter((t) => t.is_preset)
  const availableCustomTags = availableTags.filter((t) => !t.is_preset)

  return (
    <div className={cn("space-y-3", className)}>
      {/* Selected Tags */}
      {selectedTags.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {selectedTags.map((tag) => (
            <Badge
              key={tag.id}
              variant="secondary"
              className="gap-1 pr-1"
            >
              {tag.name}
              {!disabled && (
                <button
                  type="button"
                  onClick={() => handleToggleTag(tag.id)}
                  className="ml-1 rounded-full hover:bg-muted-foreground/20 p-0.5"
                >
                  <X className="h-3 w-3" />
                </button>
              )}
            </Badge>
          ))}
        </div>
      )}

      {/* Preset Tags */}
      {availablePresetTags.length > 0 && (
        <div className="space-y-2">
          <p className="text-sm text-muted-foreground">预设标签</p>
          <div className="flex flex-wrap gap-2">
            {availablePresetTags.map((tag) => {
              const isSelected = selectedTagIds.includes(tag.id)
              return (
                <Badge
                  key={tag.id}
                  variant={isSelected ? "default" : "outline"}
                  className="cursor-pointer"
                  onClick={() => !disabled && handleToggleTag(tag.id)}
                >
                  {tag.name}
                </Badge>
              )
            })}
          </div>
        </div>
      )}

      {/* Custom Tags */}
      {availableCustomTags.length > 0 && (
        <div className="space-y-2">
          <p className="text-sm text-muted-foreground">自定义标签</p>
          <div className="flex flex-wrap gap-2">
            {availableCustomTags.map((tag) => {
              const isSelected = selectedTagIds.includes(tag.id)
              return (
                <Badge
                  key={tag.id}
                  variant={isSelected ? "default" : "outline"}
                  className="cursor-pointer"
                  onClick={() => !disabled && handleToggleTag(tag.id)}
                >
                  {tag.name}
                </Badge>
              )
            })}
          </div>
        </div>
      )}

      {/* Create New Tag */}
      {onCreateTag && !disabled && (
        <div className="space-y-2">
          {!showCreateInput ? (
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() => setShowCreateInput(true)}
              className="w-full"
            >
              <Plus className="h-4 w-4 mr-1" />
              新建标签
            </Button>
          ) : (
            <div className="flex gap-2">
              <Input
                placeholder="输入新标签名称"
                value={newTagName}
                onChange={(e) => setNewTagName(e.target.value)}
                onKeyPress={handleKeyPress}
                disabled={isCreating}
                autoFocus
              />
              <Button
                type="button"
                size="sm"
                onClick={handleCreateTag}
                disabled={isCreating || !newTagName.trim()}
              >
                添加
              </Button>
              <Button
                type="button"
                size="sm"
                variant="outline"
                onClick={() => {
                  setShowCreateInput(false)
                  setNewTagName("")
                }}
              >
                取消
              </Button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
