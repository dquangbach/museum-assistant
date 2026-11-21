import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.services.rag.dut_client import DUTClient, normalize
from app.services.rag.vector_retrieval import VectorRetriever
from scripts.build_embeddings import build_index
from scripts.evaluate_vector_retrieval import evaluate


class FakeClient:
    def embed(self, texts):
        return [[1.0] + [0.0]*1023 for text in texts]

    def rerank(self, question, texts):
        return [{"index": i, "score": float(i)} for i in reversed(range(len(texts)))]


class VectorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.source = Path(self.temp.name)/"chunks.json"
        self.output = Path(self.temp.name)/"index.json"
        self.rows = [
            {"chunk_id": "A", "text": "alpha", "review_status": "verified", "topic_id": "T1"},
            {"chunk_id": "B", "text": "beta", "review_status": "verified", "topic_id": "T2"},
            {"chunk_id": "C", "text": "draft", "review_status": "needs_review", "topic_id": "T1"},
        ]
        self.source.write_text(json.dumps(self.rows))
        self.client = FakeClient()
        build_index(self.source, self.output, self.client)

    def retriever(self):
        return VectorRetriever(self.source, self.output, self.client)

    def test_verified_only_topic_filter_and_mapping(self):
        r = self.retriever()
        candidates = r.retrieve("question")
        self.assertEqual([x["chunk"]["chunk_id"] for x in candidates], ["A", "B"])
        self.assertEqual(r.rerank("question", candidates)[0]["chunk"]["chunk_id"], "B")
        self.assertEqual(r.retrieve("question", "T1")[0]["chunk"]["chunk_id"], "A")
        with patch.object(self.client, "embed", side_effect=AssertionError("unexpected API")):
            self.assertEqual(r.retrieve("question", "unknown"), [])

    def test_review_index_requires_explicit_opt_in(self):
        output = Path(self.temp.name)/"review.json"
        build_index(self.source, output, self.client, review=True)
        with self.assertRaises(ValueError):
            VectorRetriever(self.source, output, self.client)
        r = VectorRetriever(self.source, output, self.client, review=True)
        self.assertEqual(len(r.chunks), 3)
        self.assertEqual(len(self.retriever().chunks), 2)

    def test_resume_after_partial_failure(self):
        output = Path(self.temp.name)/"resume.json"
        calls = []
        def interrupted(texts):
            calls.extend(texts)
            if texts == ["beta"]:
                raise RuntimeError("offline")
            return FakeClient().embed(texts)
        with patch.object(self.client, "embed", side_effect=interrupted):
            with self.assertRaises(RuntimeError):
                build_index(self.source, output, self.client, batch_size=1)
        self.assertFalse(output.exists())
        calls.clear()
        def resumed(texts):
            calls.extend(texts)
            return FakeClient().embed(texts)
        with patch.object(self.client, "embed", side_effect=resumed):
            build_index(self.source, output, self.client, batch_size=1)
        self.assertEqual(calls, ["beta"])

    def test_cached_vectors_reused(self):
        with patch.object(self.client, "embed", side_effect=AssertionError("network")):
            build_index(self.source, self.output, self.client, force=True)

    def test_stale_source_rejected(self):
        self.source.write_text(self.source.read_text() + " ")
        with self.assertRaises(ValueError):
            self.retriever()

    def test_duplicate_or_missing_record_rejected(self):
        data = json.loads(self.output.read_text())
        data["records"][1] = data["records"][0]
        self.output.write_text(json.dumps(data))
        with self.assertRaises(ValueError):
            self.retriever()

    def test_build_refuses_overwrite_and_failure_preserves_index(self):
        original = self.output.read_bytes()
        with self.assertRaises(ValueError):
            build_index(self.source, self.output, self.client)
        self.output.with_suffix(".cache.json").unlink()
        with patch.object(self.client, "embed", side_effect=RuntimeError("offline")):
            with self.assertRaises(RuntimeError):
                build_index(self.source, self.output, self.client, force=True)
        self.assertEqual(self.output.read_bytes(), original)

    def test_invalid_vectors(self):
        for vector in ([0]*1024, [1]*3, [float("nan")]*1024):
            with self.assertRaises(ValueError):
                normalize(vector)

    def test_client_response_validation(self):
        client = DUTClient("test")
        with patch.object(client, "_post", return_value=[]):
            with self.assertRaises(ValueError):
                client.embed(["text"])
        for response in ([{"index": 0, "score": 1}, {"index": 0, "score": 2}],
                         [{"index": 3, "score": 1}],
                         [{"index": 0, "score": float("nan")}]):
            with patch.object(client, "_post", return_value=response):
                with self.assertRaises(ValueError):
                    client.rerank("q", ["a", "b"])

    def test_evaluation_denominator_excludes_unanswerable(self):
        questions = [
            {"id": "Q1", "question": "alpha", "answerable": True, "expected_chunk_ids": ["B"]},
            {"id": "Q2", "question": "unknown", "answerable": False, "expected_chunk_ids": []},
        ]
        report = evaluate(self.retriever(), questions)
        self.assertEqual(report["answerable_count"], 1)
        self.assertEqual(report["stats"]["reranking"]["hit_at_1"], 1)
        self.assertEqual(report["stats"]["embedding"]["hit_at_1"], 0)

    def test_native_endpoints_accept_openai_base_url(self):
        for base in ("https://textembedding.dutai.io.vn",
                     "https://textembedding.dutai.io.vn/",
                     "https://textembedding.dutai.io.vn/v1",
                     "https://textembedding.dutai.io.vn/v1/"):
            client = DUTClient("test", base)
            self.assertEqual(client.base_url + "/embed",
                             "https://textembedding.dutai.io.vn/embed")
            self.assertEqual(client.base_url + "/rerank",
                             "https://textembedding.dutai.io.vn/rerank")

    def test_environment_overrides_file(self):
        env = Path(self.temp.name)/".env"
        env.write_text('DUT_AI_API_KEY="file-key" # comment\n')
        with patch.dict("os.environ", {"DUT_AI_API_KEY": "env-key"}):
            self.assertEqual(DUTClient.from_env(env).api_key, "env-key")


if __name__ == "__main__":
    unittest.main()
