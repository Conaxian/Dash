import http.client as http
from ssl import create_default_context
from requestor.url import Url
from requestor.http import Connection as HttpConnection

TIMEOUT = 5

class Connection(HttpConnection):
    """
    Represents an HTTPS connection.
    """
    def __init__(self, conn: http.HTTPSConnection, url: Url) -> None:
        super().__init__(conn, url)

class Client:
    """
    Provides an interface for establishing HTTPS connections.
    """
    def __init__(self) -> None:
        self.ssl = create_default_context()
        self.user_agent = None

    def connect(self, url: Url) -> Connection:
        """
        Connects to the `url`.
        """
        url.validate()
        url.https_complete()

        conn = http.HTTPSConnection(
            url.domain,
            url.port,
            timeout=TIMEOUT,
            context=self.ssl
        )
        connection = Connection(conn, url)
        if self.user_agent:
            connection.user_agent = self.user_agent
        return connection
