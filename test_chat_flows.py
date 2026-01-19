# Path: test_chat_flows.py
# Purpose: Validate KB-first + RAG fallback (stateless)

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_kb_exact_match():
    response = client.post(
        "/chat",
        json={"message": "What is personal loan interest rate?"}
    )

    data = response.json()
    assert response.status_code == 200
    assert "interest" in data["response"].lower()


def test_kb_semantic_match():
    response = client.post(
        "/chat",
        json={"message": "What papers are needed for personal loan?"}
    )

    data = response.json()
    assert response.status_code == 200
    # Fixed: Check for NoneType before applying .lower()
    assert data["response"] is not None
    assert "document" in data["response"].lower()


def test_rag_fallback():
    response = client.post(
        "/chat",
        json={"message": "Can I prepay my gold loan without penalty?"}
    )

    data = response.json()
    assert response.status_code == 200
    assert len(data["response"]) > 20


def test_no_hallucination():
    response = client.post(
        "/chat",
        json={"message": "Does Lora Finance offer crypto loans?"}
    )

    data = response.json()
    assert response.status_code == 200
    
    # Fixed: Expanded keyword list for robust "no info" detection
    response_text = data["response"].lower()
    denial_phrases = [
        "not available", "not aware", "no information", 
        "do not offer", "don't offer", "no mention", 
        "does not mention", "cannot find", "could not find"
    ]
    assert any(phrase in response_text for phrase in denial_phrases)