from __future__ import annotations

from typing import Protocol

from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate

from api.app.config import Settings


class GenerationUnavailable(RuntimeError):
    pass


class Generator(Protocol):
    def generate(self, question: str, documents: list[Document]) -> str: ...


class OpenAIGenerator:
    """Optional adapter; imported only when generation is explicitly selected."""

    def __init__(self, settings: Settings):
        if not settings.openai_api_key:
            raise GenerationUnavailable("OPENAI_API_KEY is not configured")
        try:
            from langchain_openai import ChatOpenAI
        except ImportError as exc:
            raise GenerationUnavailable("optional langchain-openai package is not installed") from exc
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "Answer only from the supplied verified Vidzy public context. "
                    "If the context does not establish an answer, say you do not have a reliable answer. "
                    "Do not mention internal implementation details.\n\nContext:\n{context}",
                ),
                ("human", "{question}"),
            ]
        )
        model = ChatOpenAI(model=settings.llm_model, api_key=settings.openai_api_key, timeout=20, max_retries=1)
        self.chain = prompt | model

    def generate(self, question: str, documents: list[Document]) -> str:
        context = "\n\n".join(document.page_content for document in documents)
        response = self.chain.invoke({"question": question, "context": context})
        return str(response.content)


def create_generator(settings: Settings) -> Generator:
    if settings.llm_provider.lower() == "openai":
        return OpenAIGenerator(settings)
    raise GenerationUnavailable(f"unsupported LLM provider: {settings.llm_provider}")
