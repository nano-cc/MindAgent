import frontmatter
import markdown
from typing import List, Tuple


class MarkdownParserService:
    """Markdown parser service for parsing markdown files"""

    @staticmethod
    def parse_file(file_path: str) -> Tuple[dict, str]:
        """Parse markdown file and return metadata and content"""
        post = frontmatter.load(file_path)
        return post.metadata, post.content

    @staticmethod
    def parse_text(text: str) -> Tuple[dict, str]:
        """Parse markdown text and return metadata and content"""
        post = frontmatter.loads(text)
        return post.metadata, post.content

    @staticmethod
    def to_html(markdown_text: str) -> str:
        """Convert markdown to HTML"""
        return markdown.markdown(
            markdown_text,
            extensions=[
                'markdown.extensions.tables',
                'markdown.extensions.fenced_code',
                'markdown.extensions.codehilite',
            ]
        )

    @staticmethod
    def chunk_text(
        text: str,
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ) -> List[str]:
        """Split text into chunks

        Args:
            text: Text to chunk
            chunk_size: Maximum size of each chunk
            chunk_overlap: Overlap between chunks

        Returns:
            List of text chunks
        """
        if not text:
            return []

        chunks = []
        start = 0
        text_len = len(text)

        while start < text_len:
            end = min(start + chunk_size, text_len)

            # Try to break at paragraph or sentence boundary
            if end < text_len:
                # Look for paragraph break
                next_para = text.find('\n\n', end - 200, end + 200)
                if next_para != -1:
                    end = next_para + 2
                else:
                    # Look for sentence break
                    next_period = text.rfind('. ', end - 100, end)
                    if next_period != -1:
                        end = next_period + 2

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            start = end - chunk_overlap if chunk_overlap > 0 else end

            # Prevent infinite loop
            if start >= end:
                break

        return chunks
