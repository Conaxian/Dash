from re import compile as regex

HTTP_SCHEME = "http"
HTTPS_SCHEME = "https"
HTTP_PORT = 80
HTTPS_PORT = 443
MIN_PORT = 0
MAX_PORT = 65535

url_regex = regex(
    r"^(?:(?P<scheme>[a-zA-Z]+)://)?(?P<domain1>[a-zA-Z0-9-]+)(?P<domain2N>(?:\.[a-zA-Z0-9-]+)*)(?::(?P<port>\d+))?(?P<path>(?:/[a-zA-Z0-9-_\.]+)*)/?$"
)

class UrlError(Exception):
    """
    Raised when the passed URL is invalid.
    """

class SchemeError(UrlError):
    """
    Raised when the scheme of the passed URL is
    neither HTTP nor HTTPS.
    """

class PortError(UrlError):
    """
    Raised when the port of the passed URL is
    out of range (0 - 65535).
    """

class Url:
    """
    Represents a valid URL.
    """
    def __init__(self,
        scheme: str=None,
        domain: str=None,
        port: int=None,
        path: str=None
    ) -> None:
        self.scheme = scheme
        self.domain = domain
        self.port = port
        self.path = path

    def __str__(self) -> str:
        return f"{self.scheme}://{self.domain}:{self.port}{self.path}"

    def validate(self) -> None:
        """
        Validates the URL.
        """
        if self.scheme and self.scheme not in (HTTP_SCHEME, HTTPS_SCHEME):
            raise SchemeError(f"Invalid scheme: '{self.scheme}'")
        if self.port and not MIN_PORT <= self.port <= MAX_PORT:
            raise PortError(f"Port out of range: '{self.port}'")

    def http_complete(self) -> None:
        """
        Fills missing attributes with default values for HTTP.
        """
        self.scheme = self.scheme or HTTP_SCHEME
        self.port = self.port or HTTP_PORT
        self.path = self.path or "/index.html"

    def https_complete(self) -> None:
        """
        Fills missing attributes with default values for HTTPS.
        """
        self.scheme = self.scheme or HTTPS_SCHEME
        self.port = self.port or HTTPS_PORT
        self.path = self.path or "/index.html"

    @classmethod
    def from_str(cls, url_str: str):
        """
        Creates a new `Url` object from a URL string.
        """
        parts = {
            "scheme": None,
            "domain": None,
            "port": None,
            "path": None
        }

        match = url_regex.match(url_str)
        if not match: raise UrlError(f"Invalid URL: '{url_str}'")
        parts["scheme"] = match["scheme"]
        if parts["scheme"]: parts["scheme"] = parts["scheme"].lower()
        parts["domain"] = match["domain1"]
        if match["domain2N"]: parts["domain"] += match["domain2N"]
        parts["port"] = match["port"]
        if parts["port"]: parts["port"] = int(parts["port"])
        parts["path"] = match["path"]

        return cls(**parts)
