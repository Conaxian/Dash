import http.client as http
from re import compile as regex

DEFAULT_CHARSET = "utf-8"

headers_regex = regex(r"^[ \t]*(?P<name>[a-zA-Z0-9-]+):[ \t]*(?P<value>.+)$")
charset_regex = regex(r"charset=([a-zA-Z0-9-_]+)")

class Response:
    """
    Represents a server response.
    """
    def __init__(self, resp: http.HTTPResponse) -> None:
        self._resp = resp
        self.version = resp.version
        self.code = resp.status
        self.reason = resp.reason
        self.status = f"{resp.status} {resp.reason}"
        self.closed = resp.closed
        self.headers = self.parse_headers(str(resp.headers))
        self.body = resp.read()

    def __repr__(self) -> str:
        version = round(self.version / 10, 1)
        return f"""{self.status}\nHTTP {version}
{self.headers}\n{self.body}"""

    def type(self) -> str:
        """
        Returns the response body's MIME type.
        """
        return self.headers["Content-Type"].split(";")[0]

    def charset(self) -> str:
        """
        Returns the response body's charset.
        """
        match = charset_regex.search(self.headers["Content-Type"])
        return match.group(1) if match else None

    def location(self) -> str:
        """
        Returns the redirect location of the response.
        """
        return self.headers["Location"]

    def decoded(self) -> str:
        """
        Decodes and returns the response body.
        """
        return self.body.decode(self.charset() or \
        DEFAULT_CHARSET, "ignore")

    @staticmethod
    def parse_headers(headers: str="") -> dict[str, str]:
        """
        Parses the response headers into a dictionary.
        """
        header_dict = {}
        for header in headers.split("\n"):
            match = headers_regex.match(header)
            if not match: continue
            header_dict[match["name"]] = match["value"]
        return header_dict
