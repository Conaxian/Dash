from requestor import Url, HttpClient, HttpsClient
from document import Document

USER_AGENT = \
"Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
AppleWebKit/537.36 (KHTML, like Gecko) \
Chrome/92.0.4515.131 Safari/537.36 \
CBrowse/0.1.0"

class UnsupportedContentTypeError(Exception):
    """
    Raised when the content type of the recieved
    document is not supported.
    """

class HttpError(Exception):
    """
    Represents a HTTP error with a response code.
    """
    def __init__(self, code: int, name: str) -> None:
        super().__init__(f"{code} {name}")

class NotFoundError(Exception):
    """
    Represents the HTTP response code 404.
    """
    def __init__(self) -> None:
        super().__init__(f"404 Not Found")

def load(url: str) -> Document:
    url: Url = Url.from_str(url)
    if url.scheme == "http":
        client = HttpClient()
    elif url.scheme == "https" or not url.scheme:
        client = HttpsClient()
    client.user_agent = USER_AGENT
    conn = client.connect(url)
    resp = conn.get(url.path)

    if resp.code == 200:
        if resp.type() == "text/html":
            document = Document(resp.decoded())
        else:
            raise UnsupportedContentTypeError(
                f"Content type '{resp.type()}' not supported"
            )

    elif resp.code in (301, 302):
        document = load(resp.location())

    elif resp.code == 404:
        raise NotFoundError

    else:
        raise HttpError(resp.code, resp.reason)

    conn.close()
    return document
