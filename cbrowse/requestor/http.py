import http.client as http
from requestor.url import Url
from requestor.response import Response

TIMEOUT = 5

class Connection:
    """
    Represents a HTTP connection.
    """
    def __init__(self, conn: http.HTTPConnection, url: Url) -> None:
        self._conn = conn
        self.url = url
        self.user_agent = None

    def get(self, path: str, body: str=None, headers: dict[str, str]=None):
        """
        Sends a GET request to the given URL `path`.
        """
        headers = headers or {}
        if self.user_agent:
            headers.setdefault("User-Agent", self.user_agent)
        self._conn.request("GET", path, body, headers)
        resp = self._conn.getresponse()
        return Response(resp)

    def close(self) -> None:
        """
        Closes the connection.
        """
        self._conn.close()

class Client:
    """
    Provides an interface for establishing HTTP connections.
    """
    def __init__(self) -> None:
        self.user_agent = None

    def connect(self, url: Url) -> Connection:
        """
        Connects to the `url`.
        """
        url.validate()
        url.http_complete()

        conn = http.HTTPConnection(
            url.domain, url.port, TIMEOUT
        )
        connection = Connection(conn, url)
        if self.user_agent:
            connection.user_agent = self.user_agent
        return connection
