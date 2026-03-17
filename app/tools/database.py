from typing import Optional
from .base import Tool, ToolType


class DataBaseTool(Tool):
    """Database query tool"""

    def __init__(self):
        super().__init__(
            name="dataBaseTool",
            description="一个用于执行数据库查询操作的工具，主要用于从PostgreSQL中读取数据。",
            tool_type=ToolType.OPTIONAL,
            func=self._query
        )

    def _query(self, sql: str) -> str:
        """Execute SQL query (SELECT only)"""
        try:
            sql = sql.strip()
            if not sql.upper().startswith("SELECT"):
                return "错误：仅支持SELECT查询语句。提供的SQL: " + sql

            from sqlalchemy import text
            from app.database import engine

            with engine.connect() as conn:
                result = conn.execute(text(sql))
                rows = result.fetchall()
                columns = result.keys()

                if not rows:
                    return "查询结果为空"

                # Format output
                col_widths = [
                    max(len(str(col)), max(len(str(row[i])) for row in rows) if rows else 0)
                    for i, col in enumerate(columns)
                ]

                output = []
                # Header
                header = "| " + " | ".join(
                    f"{str(col):<{width}}" for col, width in zip(columns, col_widths)
                ) + " |"
                output.append(header)

                # Separator
                separator = "|" + "|".join("-" * width for width in col_widths) + "|"
                output.append(separator)

                # Data rows
                for row in rows:
                    row_str = "| " + " | ".join(
                        f"{str(val):<{width}}" for val, width in zip(row, col_widths)
                    ) + " |"
                    output.append(row_str)

                return "\n".join(output)
        except Exception as e:
            return f"错误：操作失败 - {str(e)}\nSQL: {sql}"
