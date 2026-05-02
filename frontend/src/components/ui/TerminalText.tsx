"use client";

import { useState, useEffect, useRef } from "react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

interface TerminalTextProps {
  text: string;
  speed?: number;
  className?: string;
}

export function TerminalText({ text, speed = 15, className }: TerminalTextProps) {
  const [displayedText, setDisplayedText] = useState("");
  const [currentIndex, setCurrentIndex] = useState(0);
  const textRef = useRef(text);

  useEffect(() => {
    if (textRef.current !== text) {
      setDisplayedText("");
      setCurrentIndex(0);
      textRef.current = text;
    }
  }, [text]);

  useEffect(() => {
    if (currentIndex < text.length && textRef.current === text) {
      const timeout = setTimeout(() => {
        setDisplayedText((prev) => prev + text[currentIndex]);
        setCurrentIndex((prev) => prev + 1);
      }, speed);
      return () => clearTimeout(timeout);
    }
  }, [currentIndex, text, speed]);

  return (
    <div className={cn("font-mono whitespace-pre-wrap leading-relaxed", className)}>
      {displayedText}
      {currentIndex < text.length && (
        <motion.span
          animate={{ opacity: [1, 0] }}
          transition={{ repeat: Infinity, duration: 0.8 }}
          className="inline-block w-2 h-4 bg-brand-primary ml-1 align-middle"
        />
      )}
    </div>
  );
}
