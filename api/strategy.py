from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json

from option_strategy_system import OptionStrategySystem


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            qs = parse_qs(urlparse(self.path).query)

            symbol = (qs.get("symbol", ["AAPL"])[0] or "AAPL").upper()
            objective = (qs.get("objective", ["income"])[0] or "income").lower()

            system = OptionStrategySystem()
            result = system.get_best_strategy(symbol, objective)

            body = json.dumps({
                "ok": True,
                "data": result
            }, ensure_ascii=False).encode("utf-8")

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        except Exception as e:
            body = json.dumps({
                "ok": False,
                "error": str(e)
            }, ensure_ascii=False).encode("utf-8")

            self.send_response(500)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(body)
