"use client"

import * as React from "react"
import { Plus, X, Check, Camera, ImageIcon } from "lucide-react"
import type { Crop, PixelCrop } from "react-image-crop"
import ReactCrop from "react-image-crop"
import "react-image-crop/dist/ReactCrop.css"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"

import { cn } from "@/lib/utils"
import { isMobileDevice } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { ImageLightbox } from "@/components/ImageLightbox"

interface ImageUploadProps {
  value?: string
  onChange: (base64: string) => void
  onRemove: () => void
  disabled?: boolean
  className?: string
}

const MAX_FILE_SIZE = 5 * 1024 * 1024 // 5MB
const ACCEPTED_TYPES = ["image/jpeg", "image/png"]

export function ImageUpload({
  value,
  onChange,
  onRemove,
  disabled = false,
  className,
}: ImageUploadProps) {
  const fileInputRef = React.useRef<HTMLInputElement>(null)
  const cameraInputRef = React.useRef<HTMLInputElement>(null)
  const imgRef = React.useRef<HTMLImageElement>(null)
  const [preview, setPreview] = React.useState<string | undefined>(value)
  const [error, setError] = React.useState<string>("")
  const [isMobile, setIsMobile] = React.useState(false)

  // Detect mobile device on mount
  React.useEffect(() => {
    setIsMobile(isMobileDevice())
  }, [])

  // Cropping state
  const [cropModalOpen, setCropModalOpen] = React.useState(false)
  const [imageToCrop, setImageToCrop] = React.useState<string>("")
  const [crop, setCrop] = React.useState<Crop>()
  const [completedCrop, setCompletedCrop] = React.useState<PixelCrop>()

  React.useEffect(() => {
    setPreview(value)
  }, [value])

  const createCroppedImage = async (
    imageSrc: string,
    pixelCrop: PixelCrop
  ): Promise<string> => {
    const image = new Image()
    image.src = imageSrc

    await new Promise((resolve) => {
      image.onload = resolve
    })

    if (!imgRef.current) {
      throw new Error("Image ref not available")
    }

    // Calculate scale ratio between displayed image and natural image
    const scaleX = image.naturalWidth / imgRef.current.width
    const scaleY = image.naturalHeight / imgRef.current.height

    const canvas = document.createElement("canvas")
    const ctx = canvas.getContext("2d")

    if (!ctx) {
      throw new Error("Failed to get canvas context")
    }

    // Scale crop coordinates to match natural image size
    canvas.width = pixelCrop.width * scaleX
    canvas.height = pixelCrop.height * scaleY

    ctx.drawImage(
      image,
      pixelCrop.x * scaleX,
      pixelCrop.y * scaleY,
      pixelCrop.width * scaleX,
      pixelCrop.height * scaleY,
      0,
      0,
      pixelCrop.width * scaleX,
      pixelCrop.height * scaleY
    )

    return new Promise((resolve, reject) => {
      canvas.toBlob(
        (blob) => {
          if (!blob) {
            reject(new Error("Failed to create blob from canvas"))
            return
          }
          const reader = new FileReader()
          reader.onloadend = () => resolve(reader.result as string)
          reader.onerror = reject
          reader.readAsDataURL(blob)
        },
        "image/jpeg",
        0.95
      )
    })
  }

  const handleConfirmCrop = async () => {
    if (!completedCrop || !imageToCrop || !imgRef.current) return

    try {
      const croppedBase64 = await createCroppedImage(
        imageToCrop,
        completedCrop
      )
      setPreview(croppedBase64)
      onChange(croppedBase64)
      setCropModalOpen(false)
      setImageToCrop("")
      setCrop(undefined)
      setCompletedCrop(undefined)
    } catch (error) {
      console.error("Failed to crop image:", error)
      setError("裁剪图片失败，请重试")
    }
  }

  const handleCancelCrop = () => {
    setCropModalOpen(false)
    setImageToCrop("")
    setCrop(undefined)
    setCompletedCrop(undefined)
  }

  const onImageLoad = () => {
    const initialCrop: Crop = {
      unit: "%",
      x: 25,
      y: 25,
      width: 50,
      height: 50,
    }
    setCrop(initialCrop)
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    // Validate file type
    if (!ACCEPTED_TYPES.includes(file.type)) {
      setError("仅支持 JPG 和 PNG 格式的图片")
      return
    }

    // Validate file size
    if (file.size > MAX_FILE_SIZE) {
      setError("图片大小不能超过 5MB")
      return
    }

    setError("")

    // Convert to base64 and open cropper
    const reader = new FileReader()
    reader.onloadend = () => {
      const base64 = reader.result as string
      setImageToCrop(base64)
      setCropModalOpen(true)
    }
    reader.readAsDataURL(file)

    // Reset inputs
    if (fileInputRef.current) {
      fileInputRef.current.value = ""
    }
    if (cameraInputRef.current) {
      cameraInputRef.current.value = ""
    }
  }

  const handleClick = () => {
    if (!disabled) {
      fileInputRef.current?.click()
    }
  }

  const handleCameraClick = () => {
    if (!disabled) {
      cameraInputRef.current?.click()
    }
  }

  const handleGalleryClick = () => {
    if (!disabled) {
      fileInputRef.current?.click()
    }
  }

  const handleRemove = () => {
    setPreview(undefined)
    onRemove()
  }

  return (
    <div className={cn("space-y-2", className)}>
      {/* Gallery file input */}
      <input
        ref={fileInputRef}
        type="file"
        accept="image/jpeg,image/png"
        onChange={handleFileChange}
        className="hidden"
        disabled={disabled}
      />
      {/* Camera file input with capture attribute */}
      <input
        ref={cameraInputRef}
        type="file"
        accept="image/jpeg,image/png"
        capture="environment"
        onChange={handleFileChange}
        className="hidden"
        disabled={disabled}
      />

      {preview ? (
        <div className="relative group">
          {disabled ? (
            <ImageLightbox src={preview} alt="预览">
              <img
                src={preview}
                alt="预览"
                className="w-full max-h-96 object-contain rounded-md border border-input"
              />
            </ImageLightbox>
          ) : (
            <img
              src={preview}
              alt="预览"
              className="w-full max-h-96 object-contain rounded-md border border-input"
            />
          )}
          {!disabled && (
            <Button
              type="button"
              variant="destructive"
              size="icon"
              className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity"
              onClick={handleRemove}
            >
              <X className="h-4 w-4" />
            </Button>
          )}
        </div>
      ) : isMobile ? (
        // Mobile: Show two separate buttons for camera and gallery
        <div className="flex flex-col sm:flex-row gap-3">
          <Button
            type="button"
            variant="outline"
            onClick={handleCameraClick}
            disabled={disabled}
            className="flex-1 h-auto py-4 flex flex-col items-center gap-2"
          >
            <Camera className="h-6 w-6" />
            <span>拍照</span>
          </Button>
          <Button
            type="button"
            variant="outline"
            onClick={handleGalleryClick}
            disabled={disabled}
            className="flex-1 h-auto py-4 flex flex-col items-center gap-2"
          >
            <ImageIcon className="h-6 w-6" />
            <span>从相册选择</span>
          </Button>
        </div>
      ) : (
        // Desktop: Show original dashed border area
        <div
          onClick={handleClick}
          className={cn(
            "border-2 border-dashed rounded-md p-8 flex flex-col items-center justify-center cursor-pointer transition-colors",
            !disabled && "hover:border-primary",
            disabled && "opacity-50 cursor-not-allowed"
          )}
        >
          <Plus className="h-8 w-8 text-muted-foreground mb-2" />
          <p className="text-sm text-muted-foreground">点击上传错题截图</p>
          <p className="text-xs text-muted-foreground mt-1">
            支持 JPG、PNG 格式，最大 5MB
          </p>
        </div>
      )}

      {error && (
        <p className="text-sm text-destructive">{error}</p>
      )}

      {/* Cropping Modal */}
      <Dialog open={cropModalOpen} onOpenChange={setCropModalOpen}>
        <DialogContent className="max-w-4xl max-h-[95vh] flex flex-col p-0 gap-0">
          <DialogHeader className="px-6 pt-6 pb-2">
            <DialogTitle>裁剪图片</DialogTitle>
            <DialogDescription className="sr-only">
              拖动剪裁框的角落和边缘来调整大小和位置，点击确认完成裁剪
            </DialogDescription>
          </DialogHeader>

          {/* Image container - takes available space */}
          <div className="flex-1 relative w-full flex justify-center items-center bg-muted p-2 sm:p-4 overflow-hidden min-h-0">
            {imageToCrop && (
              <ReactCrop
                crop={crop}
                onChange={(c: Crop) => setCrop(c)}
                onComplete={(c: PixelCrop) => setCompletedCrop(c)}
                aspect={undefined}
                keepSelection
              >
                <img
                  ref={imgRef}
                  src={imageToCrop}
                  onLoad={onImageLoad}
                  alt="Crop preview"
                  className="max-w-full max-h-full object-contain"
                />
              </ReactCrop>
            )}
          </div>

          <DialogFooter className="px-6 py-4 border-t">
            <Button
              type="button"
              variant="outline"
              onClick={handleCancelCrop}
            >
              取消
            </Button>
            <Button
              type="button"
              onClick={handleConfirmCrop}
              disabled={!completedCrop}
            >
              <Check className="mr-2 h-4 w-4" />
              确认裁剪
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
