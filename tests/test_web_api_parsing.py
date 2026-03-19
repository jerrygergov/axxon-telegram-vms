import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from axxon_web_api import _parse_grpc_response, simplify_event_card


class WebApiParsingTests(unittest.TestCase):
    def test_parse_sse_lines(self):
        raw = "\n".join([
            "event: message",
            'data: {"result": true}',
            "",
            'data: {"items": [1, 2]}',
        ])
        out = _parse_grpc_response(raw)
        self.assertEqual(len(out), 2)
        self.assertEqual(out[0]["result"], True)
        self.assertEqual(out[1]["items"], [1, 2])

    def test_parse_multipart_ngpboundary_packets(self):
        raw = "\r\n".join(
            [
                "--ngpboundary",
                "Content-Type: application/json; charset=utf-8",
                "Content-Length: 16",
                "",
                '{"result": true}',
                "--ngpboundary",
                "Content-Type: application/json; charset=utf-8",
                "Content-Length: 25",
                "",
                '{"items": [{"id": "1"}]}',
                "--ngpboundary--",
            ]
        )
        out = _parse_grpc_response(raw)
        self.assertEqual(out, [{"result": True}, {"items": [{"id": "1"}]}])

    def test_parse_plain_json_object(self):
        out = _parse_grpc_response('{"result": true, "id": "x"}')
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["id"], "x")

    def test_parse_plain_json_list(self):
        out = _parse_grpc_response('[{"a": 1}, {"b": 2}]')
        self.assertEqual(len(out), 2)
        self.assertEqual(out[1]["b"], 2)

    def test_simplify_event_card_prefers_friendly_operator_names(self):
        event = {
            "event_type": "ET_DetectorEvent",
            "body": {
                "guid": "11111111-1111-1111-1111-111111111111",
                "timestamp": "20260308T224316.914000",
                "event_type": "moveInZone",
                "state": "BEGAN",
                "origin_ext": {
                    "access_point": "hosts/AXXON_SERVER/DeviceIpint.1/SourceEndpoint.video:0:0",
                    "friendly_name": "Camera A",
                },
                "detector_ext": {
                    "access_point": "hosts/AXXON_SERVER/AppDataDetector.1/EventSupplier",
                    "friendly_name": "Vehicle Detector",
                },
            },
            "localization": {"text": "Vehicle entered zone"},
        }
        card = simplify_event_card(event)
        self.assertEqual(card["camera"], "Camera A")
        self.assertEqual(card["detector"], "Vehicle Detector")


if __name__ == "__main__":
    unittest.main()
