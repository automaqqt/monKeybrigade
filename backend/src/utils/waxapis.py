
import concurrent.futures,inspect, requests

class apiException(Exception):
    pass

def get_resp(url: str) -> requests.models.Response:
    
    resp = requests.get(url,timeout=5)
    resp.raise_for_status()
    if resp.json().get("error"):
        raise apiException(resp.json().get("error"))
    return resp

def build_query(args: dict) -> str:
        args.pop("endpoint")
        args.pop("url")
        args.pop("self")
        query = None
        for arg in args:
            if args.get(arg) is not None:
                if query is None:
                    query = f"{arg}={args.get(arg)}"
                else:
                    query += f"&{arg}={args.get(arg)}"
        return query

class WAXMonitor:
    def __init__(
        self,
        server="waxmonitor.cmstats.net",
    ):
        self.limit = 100
        self.server = server
        self.url_base = f"http://{self.server}/api"
        
        self.session = requests.Session()
    
    def endpoints(
        self,
        type: int = None,
    ) -> requests.models.Response:
        endpoint = "endpoints"
        url = f"{self.url_base}/{endpoint}"
        args = locals()
        query = build_query(args)
        if query is None:
            raise Exception("Must provide at least one query parameter")
        return self.session.get(f"{url}?{query}")


class AH:
    def __init__(
        self,
        api_version="v1",
        server="wax.api.atomicassets.io",
    ):
        self.limit = 100
        self.api_version = api_version  # use v2 apis unless explicitely overriden
        self.server = server
        self.url_base = f"https://{self.server}/atomicassets/{self.api_version}"
        self.session = requests.Session()
    
    def get_resp_ah(self,url: str) -> requests.models.Response:
    
        resp = self.session.get(url,timeout=15)
        resp.raise_for_status()
        return resp

    
    def templates(
        self,
        collection_name: str = None,
        schema_name: str = "crptomonkeys",
        page: int = None,
        limit: str = None,
    ) -> requests.models.Response:
        endpoint = inspect.currentframe().f_code.co_name
        url = f"{self.url_base}/{endpoint}"
        args = locals()
        query = build_query(args)
        if query is None:
            raise Exception("Must provide at least one query parameter")
        return self.get_resp_ah(f"{url}?{query}")

    def assets(
        self,
        collection_name: str = "crptomonkeys",
        schema_name: str = None,
        owner: str = None,
        page: int = 1,
        ids: str = None,
        limit: int = 1000,
        sort: str = "minted",
        order: str = "desc",
    ) -> requests.models.Response:
        endpoint = inspect.currentframe().f_code.co_name
        url = f"{self.url_base}/{endpoint}"
        args = locals()
        query = build_query(args)
        if query is None:
            raise Exception("Must provide at least one query parameter")
        return self.get_resp_ah(f"{url}?{query}")


