"use client"

import * as React from "react"
import { X } from "lucide-react"
import {
  Dialog,
  DialogContent,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog"
import { VisuallyHidden } from "@/components/ui/visually-hidden"

interface ImageLightboxProps {
  src: string
  alt?: string
  children: React.ReactElement
  disabled?: boolean
}

export function ImageLightbox({
  src,
  alt = "Image",
  children,
  disabled = false,
}: ImageLightboxProps) {
  const [open, setOpen] = React.useState(false)

  const handleClick = () => {
    if (!disabled) {
      setOpen(true)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault()
      handleClick()
    }
  }

  return (
    <>
      <div
        onClick={handleClick}
        onKeyDown={handleKeyDown}
        role="button"
        tabIndex={0}
        className={disabled ? "" : "cursor-pointer"}
        aria-label={`查看${alt}大图`}
      >
        {children}
      </div>
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="max-w-5xl w-full p-0 bg-black/95 border-none">
          <VisuallyHidden>
            <DialogTitle>查看大图</DialogTitle>
            <DialogDescription>查看完整尺寸的图片</DialogDescription>
          </VisuallyHidden>
          <button
            onClick={() => setOpen(false)}
            className="absolute top-4 right-4 z-10 rounded-full bg-black/50 p-2 text-white hover:bg-black/70 transition-colors"
            aria-label="关闭"
          >
            <X className="h-5 w-5" />
          </button>
          <div className="flex items-center justify-center min-h-[50vh] max-h-[85vh] p-4">
            <img
              src={src}
              alt={alt}
              className="max-w-full max-h-[85vh] object-contain"
            />
          </div>
        </DialogContent>
      </Dialog>
    </>
  )
}
