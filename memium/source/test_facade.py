from collections.abc import Sequence

from .document import Document
from .document_source import BaseDocumentSource
from .extractors.extractor_qa import QAPromptExtractor
from .prompt_source import DocumentPromptSource


def test_document_prompt_source():
    source = DocumentPromptSource(
        document_ingester=FakeDocumentIngester(
            [
                Document.fake(
                    """Q. What is a test even?
A. Nothing"""
                )
            ]
        ),
        prompt_extractors=[QAPromptExtractor(question_prefix="Q.", answer_prefix="A.")],
    )
    prompts = source.get_prompts()
    assert len(prompts) == 1


class FakeDocumentIngester(BaseDocumentSource):
    def __init__(self, documents: Sequence[Document]):
        self.documents = documents

    def get_documents(self) -> Sequence[Document]:
        return self.documents
