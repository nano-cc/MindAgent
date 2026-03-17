import os
import shutil
from pathlib import Path
from typing import Optional
from .base import Tool, ToolType


class FileSystemTool(Tool):
    """File system operations tool"""

    def __init__(self, base_directory: Optional[str] = None):
        self.base_directory = base_directory or os.getcwd()
        super().__init__(
            name="fileSystemTool",
            description="提供文件系统操作的工具，包括读取文件、写入文件、列出目录等功能",
            tool_type=ToolType.OPTIONAL,
            func=self._execute
        )

    def _validate_path(self, file_path: str) -> Path:
        """Validate and resolve path to prevent directory traversal"""
        base_path = Path(self.base_directory).resolve()
        resolved_path = (base_path / file_path).resolve()

        if not str(resolved_path).startswith(str(base_path)):
            raise SecurityException(f"路径遍历攻击被阻止: {file_path}")

        return resolved_path

    def _read_file(self, file_path: str) -> str:
        """Read file content"""
        try:
            path = self._validate_path(file_path)

            if not path.exists():
                return f"错误：文件不存在 - {file_path}"
            if not path.is_file():
                return f"错误：路径不是文件 - {file_path_path}"

            content = path.read_text(encoding='utf-8')
            return f"文件内容:\n{content}"
        except Exception as e:
            return f"错误：读取文件失败 - {str(e)}"

    def _write_file(self, file: str, content: str) -> str:
        """Write content to file"""
        try:
            path = self._validate_path(file)

            # Ensure parent directory exists
            path.parent.mkdir(parents=True, exist_ok=True)

            path.write_text(content, encoding='utf-8')
            return f"成功写入文件: {file}"
        except Exception as e:
            return f"错误：写入文件失败 - {str(e)}"

    def _append_file(self, file: str, content: str) -> str:
        """Append content to file"""
        try:
            path = self._validate_path(file)

            # Ensure parent directory exists
            path.parent.mkdir(parents=True, exist_ok=True)

            with open(path, 'a', encoding='utf-8') as f:
                f.write(content)
            return f"成功追加内容到文件: {file}"
        except Exception as e:
            return f"错误：追加内容失败 - {str(e)}"

    def _list_files(self, directory: str = "") -> str:
        """List directory contents"""
        try:
            if not directory or not directory.strip():
                path = Path(self.base_directory)
            else:
                path = self._validate_path(directory)

            if not path.exists():
                return f"错误：目录不存在 - {directory}"
            if not path.is_dir():
                return f"错误：路径不是目录 - {directory}"

            items = []
            for item in sorted(path.iterdir()):
                name = item.name
                if item.is_dir():
                    items.append(f"[DIR] {name}")
                else:
                    size = item.stat().st_size
                    size_str = self._format_file_size(size)
                    items.append(f"[FILE] {name} ({size_str})")

            if not items:
                return f"目录为空: {directory}"

            return f"目录内容 ({directory}):\n" + "\n".join(items)
        except Exception as e:
            return f"错误：列出目录失败 - {str(e)}"

    def _delete_file(self, path: str) -> str:
        """Delete file or directory"""
        try:
            file_path = self._validate_path(path)

            if not file_path.exists():
                return f"错误：文件或目录不存在 - {path}"

            if file_path.is_dir():
                shutil.rmtree(file_path)
                return f"成功删除目录: {path}"
            else:
                file_path.unlink()
                return f"成功删除文件: {path}"
        except Exception as e:
            return f"错误：删除失败 - {str(e)}"

    def _create_directory(self, directory: str) -> str:
        """Create directory"""
        try:
            path = self._validate_path(directory)

            if path.exists():
                if path.is_dir():
                    return f"目录已存在: {directory}"
                else:
                    return f"错误：路径已存在但不是目录 - {directory}"

            path.mkdir(parents=True, exist_ok=True)
            return f"成功创建目录: {directory}"
        except Exception as e:
            return f"错误：创建目录失败 - {str(e)}"

    def _format_file_size(self, size: int) -> str:
        """Format file size"""
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.2f} KB"
        elif size < 1024 * 1024 * 1024:
            return f"{size / (1024 * 1024):.2f} MB"
        else:
            return f"{size / (1024 * 1024 * 1024):.2f} GB"

    def _execute(self, action: str, **kwargs) -> str:
        """Execute file system operation"""
        actions = {
            "readFile": lambda: self._read_file(kwargs.get("filePath")),
            "writeFile": lambda: self._write_file(kwargs.get("filePath"), kwargs.get("content")),
            "appendToFile": lambda: self._append_file(kwargs.get("filePath"), kwargs.get("content")),
            "listFiles": lambda: self._list_files(kwargs.get("directoryPath")),
            "deleteFile": lambda: self._delete_file(kwargs.get("path")),
            "createDirectory": lambda: self._create_directory(kwargs.get("directoryPath")),
        }

        return actions.get(action, lambda: f"未知操作: {action}")()
