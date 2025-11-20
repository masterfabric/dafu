'use client';

import { useEffect, useRef, useState } from 'react';

interface HoverCardProps {
  children: React.ReactNode;
  content: React.ReactNode;
  delay?: number;
}

export function GitHubHoverCard({ children, content, delay = 300 }: HoverCardProps) {
  const [isVisible, setIsVisible] = useState(false);
  const [position, setPosition] = useState({ top: 0, left: 0 });
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);
  const cardRef = useRef<HTMLDivElement>(null);
  const triggerRef = useRef<HTMLDivElement>(null);

  const handleMouseEnter = () => {
    timeoutRef.current = setTimeout(() => {
      setIsVisible(true);
    }, delay);
  };

  const handleMouseLeave = () => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    setIsVisible(false);
  };

  useEffect(() => {
    if (isVisible && triggerRef.current && cardRef.current) {
      const triggerRect = triggerRef.current.getBoundingClientRect();
      const cardRect = cardRef.current.getBoundingClientRect();
      const viewportWidth = window.innerWidth;
      const viewportHeight = window.innerHeight;

      let top = triggerRect.bottom + 8;
      let left = triggerRect.left;

      // Adjust if card goes off right edge
      if (left + cardRect.width > viewportWidth) {
        left = viewportWidth - cardRect.width - 16;
      }

      // Adjust if card goes off bottom edge
      if (top + cardRect.height > viewportHeight) {
        top = triggerRect.top - cardRect.height - 8;
      }

      // Ensure card doesn't go off left edge
      if (left < 16) {
        left = 16;
      }

      setPosition({ top, left });
    }
  }, [isVisible]);

  return (
    <>
      <div
        ref={triggerRef}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
        style={{ position: 'relative', display: 'inline-block' }}
      >
        {children}
      </div>
      {isVisible && (
        <div
          ref={cardRef}
          className="github-hover-card"
          style={{
            position: 'fixed',
            top: `${position.top}px`,
            left: `${position.left}px`,
            zIndex: 1000,
            pointerEvents: 'none',
          }}
          onMouseEnter={handleMouseEnter}
          onMouseLeave={handleMouseLeave}
        >
          {content}
        </div>
      )}
    </>
  );
}

