import pytest
from app.orchestration import safe_calculate, WorkflowRequest
from app.benchmark import BenchmarkCase, score

def test_calculator():
    assert safe_calculate("(4+6)*2") == 20
    assert safe_calculate("-3 + 8 / 2") == 1

@pytest.mark.parametrize("expression", ["__import__('os')", "2**100", "1/0", "[1,2]", "(1+2)*'a'"])
def test_calculator_rejects_unsafe(expression):
    with pytest.raises(ValueError): safe_calculate(expression)

def test_benchmark():
    cases = [BenchmarkCase(predicted="hello world", reference="hello world", latency_ms=10, retrieved_ids=[1,2], relevant_ids=[2])]
    result = score(cases, 2)
    assert result["exact_match"] == 1 and result["token_f1"] == 1
    assert result["retrieval_recall_at_k"] == 1

def test_workflow_step_validation():
    with pytest.raises(Exception): WorkflowRequest(task="task", model_name="m", steps=["shell"])
