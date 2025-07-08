"use server"

import { generateText } from "ai"
import { openai } from "@ai-sdk/openai"

export async function processWithLLM(transcript: string) {
  try {
    const { text } = await generateText({
      model: openai("gpt-4"),
      prompt: `Please enhance and improve the following speech transcript. Make it more coherent, fix any grammar issues, and structure it better while maintaining the original meaning and intent:

"${transcript}"

Please provide a clean, well-structured version that sounds natural and professional.`,
    })

    return text
  } catch (error) {
    console.error("Error processing with LLM:", error)
    throw new Error("Failed to process with AI")
  }
}
