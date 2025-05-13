from typing import Dict, Any, AsyncIterable
from pydantic import BaseModel
from crew import SimpleResearcherCrew

class TaskInput(BaseModel):
    topic: str  # TODO: Replace with the actual input field name

class A2AWrapperAgent:
    def __init__(self):
        self.agent = SimpleResearcherCrew()  # TODO: Replace with the actual agent class

    async def invoke(self, input_data: TaskInput, sessionId: str) -> Dict[str, Any]:
        try:
            inputs = {**input_data.model_dump(), "sessionId": sessionId}
            result = self.agent.crew().kickoff(inputs)

            return {
                "is_task_complete": True,
                "require_user_input": False,
                "content": str(result),
                # optionally, include metadata for downstream artifact retrieval
                "metadata": {
                    "artifact_id": str(result),
                    "session_id": sessionId
                }
            }
        except Exception as e:
            return {
                "is_task_complete": False,
                "require_user_input": True,
                "content": f"Error: {str(e)}"
            }

    async def stream(self, input_data: TaskInput, sessionId: str) -> AsyncIterable[Dict[str, Any]]:
        # CrewAI doesn't support streaming, we yield the final response in one go
        result = await self.invoke(input_data, sessionId)
        yield result

    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]