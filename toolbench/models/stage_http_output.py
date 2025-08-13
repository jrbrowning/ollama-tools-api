# File: toolbench/models/stage_http_outputs.py

from models.llm_response import TextStageOutput, ToolStageOutput
from models.stage_common import StageInfo
from typing import Any, Literal
from pydantic import BaseModel

# Alias for FSM/pipeline orchestration logic
class StageHttpTextOutput(TextStageOutput):
    status: StageInfo

class StageHttpToolCallOutput(ToolStageOutput):
    status: StageInfo

class StageHTTPStreamOutput(BaseModel):
    status: StageInfo
    stage_id: str
    type: Literal["events"]
    events: Any

'''
Future vision output stage orchestration example
'''
# class StageHttpVisionOutput(StageIdValidatorMixin, BaseModel):
#     stage_id: str
#     status: StageInfo
#     image_url: Optional[str] = None
#     caption: Optional[str] = None
#     embeddings: Optional[List[float]] = None
#     metadata: Optional[dict] = None

