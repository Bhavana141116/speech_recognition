"use client"

import { useState, useRef, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Mic, MicOff, Square, Volume2, Loader2 } from "lucide-react"
import { processWithLLM } from "./actions"

interface SpeechRecognitionEvent extends Event {
  results: SpeechRecognitionResultList
  resultIndex: number
}

interface SpeechRecognitionErrorEvent extends Event {
  error: string
  message: string
}

interface SpeechRecognition extends EventTarget {
  continuous: boolean
  interimResults: boolean
  lang: string
  start(): void
  stop(): void
  abort(): void
  onstart: ((this: SpeechRecognition, ev: Event) => any) | null
  onend: ((this: SpeechRecognition, ev: Event) => any) | null
  onresult: ((this: SpeechRecognition, ev: SpeechRecognitionEvent) => any) | null
  onerror: ((this: SpeechRecognition, ev: SpeechRecognitionErrorEvent) => any) | null
}

declare global {
  interface Window {
    SpeechRecognition: new () => SpeechRecognition
    webkitSpeechRecognition: new () => SpeechRecognition
  }
}

export default function SpeechRecognitionApp() {
  const [isListening, setIsListening] = useState(false)
  const [transcript, setTranscript] = useState("")
  const [finalTranscript, setFinalTranscript] = useState("")
  const [llmResponse, setLlmResponse] = useState("")
  const [isProcessing, setIsProcessing] = useState(false)
  const [error, setError] = useState("")
  const [isSupported, setIsSupported] = useState(true)

  const recognitionRef = useRef<SpeechRecognition | null>(null)

  useEffect(() => {
    if (typeof window !== "undefined") {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
      if (!SpeechRecognition) {
        setIsSupported(false)
        setError("Speech recognition is not supported in this browser. Please use Chrome, Edge, or Safari.")
        return
      }

      const recognition = new SpeechRecognition()
      recognition.continuous = true
      recognition.interimResults = true
      recognition.lang = "en-US"

      recognition.onstart = () => {
        setIsListening(true)
        setError("")
      }

      recognition.onend = () => {
        setIsListening(false)
      }

      recognition.onresult = (event: SpeechRecognitionEvent) => {
        let interimTranscript = ""
        let finalTranscriptText = ""

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const result = event.results[i]
          if (result.isFinal) {
            finalTranscriptText += result[0].transcript
          } else {
            interimTranscript += result[0].transcript
          }
        }

        setTranscript(interimTranscript)
        if (finalTranscriptText) {
          setFinalTranscript((prev) => prev + finalTranscriptText)
        }
      }

      recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
        setError(`Speech recognition error: ${event.error}`)
        setIsListening(false)
      }

      recognitionRef.current = recognition
    }
  }, [])

  const startListening = () => {
    if (recognitionRef.current && !isListening) {
      setTranscript("")
      setError("")
      recognitionRef.current.start()
    }
  }

  const stopListening = () => {
    if (recognitionRef.current && isListening) {
      recognitionRef.current.stop()
    }
  }

  const processWithAI = async () => {
    if (!finalTranscript.trim()) return

    setIsProcessing(true)
    try {
      const response = await processWithLLM(finalTranscript)
      setLlmResponse(response)
    } catch (err) {
      setError("Failed to process with AI. Please try again.")
    } finally {
      setIsProcessing(false)
    }
  }

  const clearAll = () => {
    setTranscript("")
    setFinalTranscript("")
    setLlmResponse("")
    setError("")
  }

  const speakText = (text: string) => {
    if ("speechSynthesis" in window) {
      const utterance = new SpeechSynthesisUtterance(text)
      utterance.rate = 0.8
      utterance.pitch = 1
      speechSynthesis.speak(utterance)
    }
  }

  if (!isSupported) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <Card className="w-full max-w-md">
          <CardHeader>
            <CardTitle className="text-red-600">Not Supported</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground">{error}</p>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-4xl mx-auto space-y-6">
        <div className="text-center space-y-2">
          <h1 className="text-4xl font-bold text-gray-900">AI Speech Recognition</h1>
          <p className="text-lg text-muted-foreground">Speak naturally and let AI enhance your words</p>
        </div>

        {/* Recording Controls */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Mic className="w-5 h-5" />
              Voice Recording
            </CardTitle>
            <CardDescription>Click the microphone to start recording your voice</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-center gap-4">
              <Button
                onClick={isListening ? stopListening : startListening}
                size="lg"
                variant={isListening ? "destructive" : "default"}
                className="w-32"
              >
                {isListening ? (
                  <>
                    <MicOff className="w-4 h-4 mr-2" />
                    Stop
                  </>
                ) : (
                  <>
                    <Mic className="w-4 h-4 mr-2" />
                    Start
                  </>
                )}
              </Button>

              <Button onClick={clearAll} variant="outline">
                <Square className="w-4 h-4 mr-2" />
                Clear All
              </Button>
            </div>

            {isListening && (
              <div className="flex items-center justify-center gap-2">
                <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
                <Badge variant="destructive">Recording...</Badge>
              </div>
            )}

            {error && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-md">
                <p className="text-red-700 text-sm">{error}</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Live Transcript */}
        {(transcript || finalTranscript) && (
          <Card>
            <CardHeader>
              <CardTitle>Live Transcript</CardTitle>
              <CardDescription>Real-time speech-to-text conversion</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {finalTranscript && (
                  <div className="p-3 bg-green-50 border border-green-200 rounded-md">
                    <p className="text-green-800">{finalTranscript}</p>
                  </div>
                )}
                {transcript && (
                  <div className="p-3 bg-blue-50 border border-blue-200 rounded-md">
                    <p className="text-blue-700 italic">{transcript}</p>
                    <Badge variant="secondary" className="mt-2">
                      Interim
                    </Badge>
                  </div>
                )}
              </div>

              {finalTranscript && (
                <div className="flex gap-2 mt-4">
                  <Button onClick={processWithAI} disabled={isProcessing}>
                    {isProcessing ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Processing...
                      </>
                    ) : (
                      "Enhance with AI"
                    )}
                  </Button>
                  <Button variant="outline" onClick={() => speakText(finalTranscript)}>
                    <Volume2 className="w-4 h-4 mr-2" />
                    Speak
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* AI Enhanced Response */}
        {llmResponse && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                AI Enhanced Response
              </CardTitle>
              <CardDescription>Your speech processed and enhanced by AI</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="p-4 bg-purple-50 border border-purple-200 rounded-md">
                <p className="text-purple-900 whitespace-pre-wrap">{llmResponse}</p>
              </div>
              <Button variant="outline" onClick={() => speakText(llmResponse)} className="mt-4">
                <Volume2 className="w-4 h-4 mr-2" />
                Speak AI Response
              </Button>
            </CardContent>
          </Card>
        )}

        {/* Instructions */}
        <Card>
          <CardHeader>
            <CardTitle>How to Use</CardTitle>
          </CardHeader>
          <CardContent>
            <ol className="list-decimal list-inside space-y-2 text-sm text-muted-foreground">
              <li>Click "Start" to begin voice recording</li>
              <li>Speak clearly into your microphone</li>
              <li>Watch the real-time transcript appear</li>
              <li>Click "Stop" when finished speaking</li>
              <li>Use "Enhance with AI" to process your speech with LLM</li>
              <li>Use the speaker buttons to hear the text read aloud</li>
            </ol>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
