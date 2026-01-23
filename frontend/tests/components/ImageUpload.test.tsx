import { render, screen, fireEvent, waitFor } from "@testing-library/react"
import { ImageUpload } from "@/components/ImageUpload"

describe("ImageUpload", () => {
  it("renders upload placeholder when no image", () => {
    const onChange = jest.fn()
    const onRemove = jest.fn()

    render(<ImageUpload onChange={onChange} onRemove={onRemove} />)

    expect(screen.getByText(/点击上传错题截图/)).toBeInTheDocument()
    expect(
      screen.getByText(/支持 JPG、PNG 格式，最大 5MB/)
    ).toBeInTheDocument()
  })

  it("renders preview when image is provided", () => {
    const onChange = jest.fn()
    const onRemove = jest.fn()
    const base64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="

    render(
      <ImageUpload
        value={base64}
        onChange={onChange}
        onRemove={onRemove}
      />
    )

    const img = screen.getByAltText("预览")
    expect(img).toBeInTheDocument()
    expect(img).toHaveAttribute("src", base64)
  })

  it("calls onChange when valid file is selected", async () => {
    const onChange = jest.fn()
    const onRemove = jest.fn()

    render(<ImageUpload onChange={onChange} onRemove={onRemove} />)

    const file = new File(["dummy"], "test.png", { type: "image/png" })
    const input = document.querySelector("input[type='file']") as HTMLInputElement

    fireEvent.change(input, { target: { files: [file] } })

    await waitFor(() => {
      expect(onChange).toHaveBeenCalled()
    })
  })

  it("shows error for invalid file type", async () => {
    const onChange = jest.fn()
    const onRemove = jest.fn()

    render(<ImageUpload onChange={onChange} onRemove={onRemove} />)

    const file = new File(["dummy"], "test.gif", { type: "image/gif" })
    const input = document.querySelector("input[type='file']") as HTMLInputElement

    fireEvent.change(input, { target: { files: [file] } })

    await waitFor(() => {
      expect(screen.getByText(/仅支持 JPG 和 PNG 格式的图片/)).toBeInTheDocument()
    })
  })

  it("calls onRemove when remove button is clicked", () => {
    const onChange = jest.fn()
    const onRemove = jest.fn()
    const base64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="

    render(
      <ImageUpload
        value={base64}
        onChange={onChange}
        onRemove={onRemove}
      />
    )

    const removeButton = screen.getByRole("button")
    fireEvent.click(removeButton)

    expect(onRemove).toHaveBeenCalled()
  })

  it("is disabled when disabled prop is true", () => {
    const onChange = jest.fn()
    const onRemove = jest.fn()

    render(<ImageUpload onChange={onChange} onRemove={onRemove} disabled />)

    const input = document.querySelector("input[type='file']") as HTMLInputElement
    expect(input).toBeDisabled()
  })
})
