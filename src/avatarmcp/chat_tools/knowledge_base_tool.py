"""
Knowledge base tool for the Avatar MCP chatbot.

This tool allows the chatbot to query a knowledge base for information.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional

from .base_tool import (
    ChatTool,
    ToolResult,
    ToolParameter,
    ToolParameterType,
    ToolExecutionStatus,
)

logger = logging.getLogger(__name__)

class KnowledgeBaseTool(ChatTool):
    """Tool for querying a knowledge base."""
    
    @property
    def name(self) -> str:
        return "query_knowledge_base"
    
    @property
    def description(self) -> str:
        return "Search the knowledge base for information. Useful for finding specific details about the system, APIs, or domain-specific information."
    
    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="query",
                type=ToolParameterType.STRING,
                description="The search query or question",
                required=True
            ),
            ToolParameter(
                name="context",
                type=ToolParameterType.STRING,
                description="Additional context to help with the search",
                required=False
            ),
            ToolParameter(
                name="max_results",
                type=ToolParameterType.INTEGER,
                description="Maximum number of results to return (1-10)",
                required=False,
                default=3,
                min_value=1,
                max_value=10
            )
        ]
    
    async def execute(self, query: str, context: str = "", max_results: int = 3, **kwargs) -> ToolResult:
        """
        Query the knowledge base.
        
        Args:
            query: The search query or question
            context: Additional context to help with the search
            max_results: Maximum number of results to return (1-10)
            
        Returns:
            ToolResult with knowledge base results
        """
        try:
            logger.info(f"Querying knowledge base: {query}")
            if context:
                logger.debug(f"Additional context: {context}")
            
            # Simulate API call delay
            await asyncio.sleep(0.5)
            
            # Mock knowledge base results
            mock_results = [
                {
                    "id": f"kb_{i+1}",
                    "title": f"Knowledge Base Entry {i+1} about '{query}'",
                    "content": f"This is a sample knowledge base entry about '{query}'. It contains detailed information that might be relevant to the query.",
                    "relevance": 0.9 - (i * 0.1),
                    "source": "internal_knowledge_base"
                }
                for i in range(min(max_results, 5))  # Cap at 5 mock results
            ]
            
            # Sort by relevance (highest first)
            mock_results.sort(key=lambda x: x["relevance"], reverse=True)
            
            return ToolResult.success(
                content={
                    "query": query,
                    "context": context,
                    "results": mock_results
                },
                metadata={
                    "result_count": len(mock_results),
                    "sources": list({r["source"] for r in mock_results})
                }
            )
            
        except Exception as e:
            logger.error(f"Error querying knowledge base: {e}", exc_info=True)
            return ToolResult.error(f"Failed to query knowledge base: {str(e)}")

# Example usage:
# tool = KnowledgeBaseTool()
# result = await tool.execute(
#     query="How do I configure the MCP server?",
#     context="I'm trying to set up the server for the first time",
#     max_results=2
# )
# print(json.dumps(result.to_dict(), indent=2))
