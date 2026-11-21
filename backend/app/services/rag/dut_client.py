"""DUT AI HTTP client. Standard library only; credentials never enter reports."""
import json
import math
import os
import shlex
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, build_opener, HTTPRedirectHandler

MODEL = "BAAI/bge-m3"
DIMENSIONS = 1024
ROOT = Path(__file__).resolve().parents[4]


def normalize(vector):
    if (not isinstance(vector, list) or len(vector) != DIMENSIONS
            or not all(type(v) in (int, float) and math.isfinite(v) for v in vector)):
        raise ValueError("Vector phải có 1024 giá trị hữu hạn.")
    norm = math.hypot(*vector)
    if not math.isfinite(norm) or norm == 0:
        raise ValueError("Độ dài vector không hợp lệ.")
    return [v / norm for v in vector]


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None  # Do not forward credentials to another host.


class DUTClient:
    def __init__(self, api_key, base_url="https://textembedding.dutai.io.vn", timeout=120):
        parsed = urlparse(base_url)
        if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ValueError("DUT_AI_BASE_URL phải là HTTPS URL hợp lệ.")
        if not api_key:
            raise ValueError("Thiếu DUT_AI_API_KEY.")
        self.api_key = api_key
        # This client uses native TEI endpoints /embed and /rerank.
        # Accept the OpenAI-compatible base URL supplied in DUT documentation.
        self.base_url = base_url.rstrip("/")
        if self.base_url.endswith("/v1"):
            self.base_url = self.base_url[:-3]
        self.timeout = timeout

    @classmethod
    def from_env(cls, env_file=None):
        values = {}
        path = Path(env_file) if env_file else ROOT / ".env"
        if path.exists():
            for line in path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line.startswith("export "):
                    line = line[7:].strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                name, value = line.split("=", 1)
                if name.strip() not in {"DUT_AI_API_KEY", "DUT_AI_BASE_URL"}:
                    continue
                parts = shlex.split(value, comments=True)
                values[name.strip()] = " ".join(parts)
        for name in ("DUT_AI_API_KEY", "DUT_AI_BASE_URL"):
            if name in os.environ:
                values[name] = os.environ[name]
        return cls(values.get("DUT_AI_API_KEY", ""),
                   values.get("DUT_AI_BASE_URL", "https://textembedding.dutai.io.vn"))

    def _post(self, endpoint, payload):
        request = Request(self.base_url + endpoint,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={"Authorization": f"Bearer {self.api_key}",
                     "Content-Type": "application/json", "Accept": "application/json",
                     "User-Agent": "museum-assistant/0.1"}, method="POST")
        try:
            with build_opener(NoRedirect()).open(request, timeout=self.timeout) as response:
                return json.load(response)
        except HTTPError as error:
            if error.code == 404:
                raise RuntimeError(
                    f"DUT AI HTTP 404 tại endpoint {endpoint}; kiểm tra DUT_AI_BASE_URL và đường dẫn API."
                ) from None
            raise RuntimeError(f"DUT AI HTTP {error.code}; kiểm tra key/quyền truy cập hoặc trạng thái dịch vụ.") from None
        except (URLError, TimeoutError, OSError):
            raise RuntimeError("Không kết nối được DUT AI hoặc hết thời gian chờ.") from None
        except ValueError:
            raise ValueError("DUT AI trả JSON không hợp lệ.") from None

    def embed(self, texts):
        if not texts:
            return []
        if any(not isinstance(t, str) or not t.strip() for t in texts):
            raise ValueError("Nội dung embedding không được trống.")
        data = self._post("/embed", {"inputs": texts, "normalize": True, "truncate": False})
        if not isinstance(data, list) or len(data) != len(texts):
            raise ValueError("Số vector trả về không khớp.")
        return [normalize(v) for v in data]

    def rerank(self, question, texts):
        if not texts:
            return []
        data = self._post("/rerank", {"query": question, "texts": texts,
                                     "return_text": False, "truncate": False})
        if not isinstance(data, list):
            raise ValueError("Reranking phải trả danh sách.")
        seen = set()
        for row in data:
            if not isinstance(row, dict):
                raise ValueError("Kết quả reranking không hợp lệ.")
            i, score = row.get("index"), row.get("score")
            if (type(i) is not int or not 0 <= i < len(texts) or i in seen
                    or type(score) not in (int, float) or not math.isfinite(score)):
                raise ValueError("Index/score reranking không hợp lệ.")
            seen.add(i)
        if len(seen) != len(texts):
            raise ValueError("Reranking không trả đủ ứng viên.")
        return sorted(data, key=lambda row: (-row["score"], row["index"]))
