import json
import os
from typing import Dict, Any, List
import aiohttp
from .tools import TOOLS

class FederalRegisterAgent:
    def __init__(self, model_name="qwen2.5-0.5b"):
        self.model_name = model_name
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.system_prompt = """You are a helpful assistant that provides information about Federal Register documents.
You have access to a database of Federal Register documents and can search through them using various tools.
When a user asks a question, you should:
1. Determine which tool(s) would be most appropriate to answer their question
2. Use the tool(s) to gather relevant information
3. Provide a clear and concise response based on the information gathered

Available tools:
{tools}

Remember to:
- Be specific and accurate in your responses
- Cite document numbers when referencing specific documents
- Provide dates when discussing time-sensitive information
- Summarize information when there are multiple relevant documents
"""

    async def _call_llm(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Call the LLM API."""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model_name,
                    "messages": messages,
                    "stream": False
                }
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"LLM API call failed: {response.status}")

    async def _execute_tool(self, tool_name: str, tool_args: Dict[str, Any]) -> Any:
        """Execute a tool call."""
        # Import the tool function dynamically
        from .tools import globals()[tool_name]
        tool_func = globals()[tool_name]
        
        # Execute the tool
        return await tool_func(**tool_args)

    async def process_query(self, user_query: str) -> str:
        """Process a user query and return a response."""
        # Prepare the system message with available tools
        system_message = self.system_prompt.format(
            tools=json.dumps(TOOLS, indent=2)
        )
        
        # Initial messages
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_query}
        ]
        
        while True:
            # Get LLM response
            response = await self._call_llm(messages)
            assistant_message = response["message"]["content"]
            
            # Check if the response contains a tool call
            try:
                tool_call = json.loads(assistant_message)
                if isinstance(tool_call, dict) and "name" in tool_call and "arguments" in tool_call:
                    # Execute the tool
                    tool_result = await self._execute_tool(
                        tool_call["name"],
                        tool_call["arguments"]
                    )
                    
                    # Add the tool result to the conversation
                    messages.append({
                        "role": "assistant",
                        "content": assistant_message
                    })
                    messages.append({
                        "role": "user",
                        "content": f"Tool result: {json.dumps(tool_result)}"
                    })
                    continue
            except json.JSONDecodeError:
                # Not a tool call, return the response
                return assistant_message
            
            return assistant_message

if __name__ == "__main__":
    # Test the agent
    import asyncio
    
    async def test_agent():
        agent = FederalRegisterAgent()
        response = await agent.process_query(
            "What are the latest documents from the Environmental Protection Agency?"
        )
        print(response)
    
    asyncio.run(test_agent()) 