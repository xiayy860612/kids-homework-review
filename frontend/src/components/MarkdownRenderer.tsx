"use client"

import * as React from "react"
import ReactMarkdown from "react-markdown"

// TypeScript declarations for MathJax
declare global {
  interface Window {
    MathJax: any
  }
}

// MathJax configuration
const MATHJAX_CONFIG = {
  tex: {
    inlineMath: [["$", "$"]],
    displayMath: [["$$", "$$"]],
    processEscapes: true,
    packages: { "[+]": ["text-macros"] },
  },
  options: {
    skipHtmlTags: ["script", "noscript", "style", "textarea", "pre", "code"],
    ignoreHtmlClass: "tex2jax_ignore",
    processHtmlClass: "tex2jax_process",
  },
  startup: {
    typeset: false,
  },
  ready: () => {
    return (window as any).MathJax.startup.defaultReady()
  },
}

interface MarkdownRendererProps {
  content: string
  className?: string
}

// MathJax context for dynamic loading
let mathjaxPromise: Promise<typeof window.MathJax> | null = null
let isMathJaxLoaded = false
let isMathJaxLoading = false

const loadMathJax = (): Promise<typeof window.MathJax> => {
  if (isMathJaxLoaded && window.MathJax) {
    return Promise.resolve(window.MathJax)
  }

  if (mathjaxPromise) {
    return mathjaxPromise
  }

  if (isMathJaxLoading) {
    // Return a promise that resolves when loading completes
    return new Promise((resolve) => {
      const checkLoaded = setInterval(() => {
        if (isMathJaxLoaded && window.MathJax) {
          clearInterval(checkLoaded)
          resolve(window.MathJax)
        }
      }, 100)
    })
  }

  isMathJaxLoading = true

  mathjaxPromise = new Promise((resolve, reject) => {
    if (window.MathJax) {
      isMathJaxLoaded = true
      isMathJaxLoading = false
      resolve(window.MathJax)
      return
    }

    // Configure MathJax before loading
    window.MathJax = MATHJAX_CONFIG as any

    const script = document.createElement("script")
    script.src = "https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"
    script.async = true
    script.id = "MathJax-script"

    script.onload = () => {
      isMathJaxLoaded = true
      isMathJaxLoading = false
      if (window.MathJax) {
        resolve(window.MathJax)
      } else {
        reject(new Error("MathJax failed to load"))
      }
    }

    script.onerror = () => {
      isMathJaxLoading = false
      reject(new Error("Failed to load MathJax script"))
    }

    document.head.appendChild(script)
  })

  return mathjaxPromise
}

// Component that triggers MathJax rendering on its children
const MathJaxRenderer: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const containerRef = React.useRef<HTMLDivElement>(null)

  React.useEffect(() => {
    const renderMath = async () => {
      try {
        await loadMathJax()
        if (containerRef.current && window.MathJax?.typesetPromise) {
          await window.MathJax.typesetPromise([containerRef.current])
        }
      } catch (error) {
        console.error("MathJax rendering error:", error)
      }
    }

    // Small delay to ensure DOM is ready
    const timer = setTimeout(() => {
      renderMath()
    }, 10)

    return () => clearTimeout(timer)
  }, [children])

  return <div ref={containerRef}>{children}</div>
}

export function MarkdownRenderer({
  content,
  className,
}: MarkdownRendererProps) {
  return (
    <div className={className}>
      <MathJaxRenderer>
        <ReactMarkdown
          components={{
            h1: ({ children }) => (
              <h1 className="text-2xl font-bold mt-6 mb-4">{children}</h1>
            ),
            h2: ({ children }) => (
              <h2 className="text-xl font-semibold mt-5 mb-3">{children}</h2>
            ),
            h3: ({ children }) => (
              <h3 className="text-lg font-medium mt-4 mb-2">{children}</h3>
            ),
            h4: ({ children }) => (
              <h4 className="text-base font-medium mt-3 mb-2">{children}</h4>
            ),
            h5: ({ children }) => (
              <h5 className="text-sm font-medium mt-2 mb-2">{children}</h5>
            ),
            h6: ({ children }) => (
              <h6 className="text-xs font-medium mt-2 mb-2">{children}</h6>
            ),
            p: ({ children }) => (
              <p className="my-2 leading-relaxed">{children}</p>
            ),
            ul: ({ children }) => (
              <ul className="list-disc list-inside my-2 space-y-1">{children}</ul>
            ),
            ol: ({ children }) => (
              <ol className="list-decimal list-inside my-2 space-y-1">
                {children}
              </ol>
            ),
            li: ({ children }) => <li className="ml-4">{children}</li>,
            code: ({ children, className }) => {
              if (!className) {
                return (
                  <code className="bg-muted px-1.5 py-0.5 rounded text-sm font-mono">
                    {children}
                  </code>
                )
              }
              return <code className={className}>{children}</code>
            },
            pre: ({ children }) => (
              <pre className="bg-muted p-4 rounded-lg overflow-x-auto my-3">
                {children}
              </pre>
            ),
            strong: ({ children }) => (
              <strong className="font-semibold">{children}</strong>
            ),
            em: ({ children }) => <em className="italic">{children}</em>,
            blockquote: ({ children }) => (
              <blockquote className="border-l-4 border-muted-foreground pl-4 italic my-2">
                {children}
              </blockquote>
            ),
            a: ({ href, children }) => (
              <a
                href={href}
                className="text-blue-600 hover:text-blue-800 underline"
                target="_blank"
                rel="noopener noreferrer"
              >
                {children}
              </a>
            ),
          }}
        >
          {content}
        </ReactMarkdown>
      </MathJaxRenderer>
    </div>
  )
}
