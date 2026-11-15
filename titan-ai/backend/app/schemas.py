from pydantic import BaseModel, Field
from typing import Literal

class ModelCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    provider: Literal["ollama"] = "ollama"
    model_id: str = Field(min_length=2, max_length=160)
    description: str = ""

class InferenceRequest(BaseModel):
    model_name: str
    prompt: str = Field(min_length=1, max_length=20000)

class AgentCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    instructions: str = Field(min_length=1, max_length=10000)
    model_name: str

class AgentRunRequest(BaseModel):
    task: str = Field(min_length=1, max_length=20000)

class EvaluationCase(BaseModel):
    prompt: str = Field(min_length=1, max_length=10000)
    expected_contains: str = Field(min_length=1, max_length=500)

class EvaluationCreate(BaseModel):
    title: str = Field(min_length=2, max_length=160)
    model_name: str
    cases: list[EvaluationCase] = Field(min_length=1, max_length=20)

class DatasetCreate(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    description: str = Field(default="", max_length=2000)
    samples: list[EvaluationCase] = Field(min_length=1, max_length=200)
