import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';

type MarkdownTone = 'light' | 'dark' | 'inherit';

interface MarkdownContentProps {
  content: string;
  className?: string;
  tone?: MarkdownTone;
  /** When true, wrap raw LaTeX (no $ delimiters) as a display math block. */
  asDisplayMath?: boolean;
}

function normalizeContent(content: string, asDisplayMath?: boolean): string {
  if (!content) return '';
  if (asDisplayMath) {
    const trimmed = content.trim();
    if (trimmed.startsWith('$$') || trimmed.startsWith('$')) return trimmed;
    return `$$\n${trimmed}\n$$`;
  }
  return content;
}

const toneClasses: Record<MarkdownTone, string> = {
  light:
    'prose prose-slate max-w-none prose-headings:font-extrabold prose-headings:text-slate-900 prose-p:text-slate-700 prose-strong:text-slate-900 prose-code:text-indigo-700 prose-pre:bg-slate-950 prose-pre:text-slate-100 prose-table:text-xs',
  dark:
    'prose prose-invert max-w-none prose-headings:font-extrabold prose-p:text-slate-200 prose-strong:text-white prose-code:text-indigo-300 prose-pre:bg-black/60 prose-a:text-indigo-300',
  inherit: 'max-w-none [&_p]:my-2 [&_ul]:my-2 [&_ol]:my-2 [&_pre]:overflow-x-auto'
};

export const MarkdownContent: React.FC<MarkdownContentProps> = ({
  content,
  className = '',
  tone = 'light',
  asDisplayMath = false
}) => {
  const source = normalizeContent(content, asDisplayMath);

  return (
    <div className={`${toneClasses[tone]} text-xs md:text-sm leading-relaxed ${className}`}>
      <ReactMarkdown remarkPlugins={[remarkGfm, remarkMath]} rehypePlugins={[rehypeKatex]}>
        {source}
      </ReactMarkdown>
    </div>
  );
};
