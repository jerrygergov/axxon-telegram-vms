import unittest

from axxon_telegram_vms.models import (
    EventQuery,
    EventScopeFilter,
    EventTaxonomyFilter,
    EventTextFilter,
    EventTimeRange,
    format_query_datetime,
    parse_query_datetime,
    query_card_matches,
)


class QueryFilterModelTests(unittest.TestCase):
    def test_time_range_normalizes_to_utc_and_formats_compact_values(self):
        time_range = EventTimeRange(
            begin="2026-03-10T12:00:00+02:00",
            end="20260310T110000",
        )

        self.assertEqual(format_query_datetime(time_range.begin), "20260310T100000")
        self.assertEqual(format_query_datetime(time_range.end), "20260310T110000")
        self.assertTrue(time_range.is_bounded())
        self.assertTrue(time_range.contains("20260310T103000"))
        self.assertFalse(time_range.contains("20260310T113001"))
        self.assertEqual(
            time_range.as_axxon_range(),
            {
                "begin_time": "20260310T100000",
                "end_time": "20260310T110000",
            },
        )
        self.assertEqual(
            parse_query_datetime("2026-03-10T10:00:00Z").isoformat(),
            "2026-03-10T10:00:00+00:00",
        )

    def test_event_query_from_legacy_filters_round_trips_shared_fields(self):
        legacy_filters = {
            "range": {
                "begin_time": "20260310T100000",
                "end_time": "20260310T110000",
            },
            "host": "ServerA",
            "domains": ["DomainA"],
            "subject": "hosts/ServerA/DeviceIpint.7",
            "camera_names": ["Gate"],
            "camera_access_points": ["hosts/ServerA/DeviceIpint.7/SourceEndpoint.video:0:0"],
            "detector_access_points": ["hosts/ServerA/AVDetector.2/EventSupplier"],
            "detector_names": ["2.LPR"],
            "detector_types": ["LicensePlateRecognition"],
            "categories": ["LPR", "lpr"],
            "event_type": "ET_DetectorEvent",
            "states": ["happened"],
            "priority": "ap_high",
            "severity": "sv_warning",
            "contains": "YZ45246",
            "mask": "*5246",
            "limit": "50",
            "offset": "10",
            "descending": "false",
        }

        query = EventQuery.from_legacy_filters(legacy_filters)

        self.assertEqual(query.scope.hosts, ("ServerA",))
        self.assertEqual(query.scope.domains, ("DomainA",))
        self.assertEqual(query.scope.subjects, ("hosts/ServerA/DeviceIpint.7",))
        self.assertEqual(query.scope.camera_names, ("Gate",))
        self.assertEqual(query.scope.camera_access_points, ("hosts/ServerA/DeviceIpint.7/SourceEndpoint.video:0:0",))
        self.assertEqual(query.scope.detector_access_points, ("hosts/ServerA/AVDetector.2/EventSupplier",))
        self.assertEqual(query.scope.detector_names, ("2.LPR",))
        self.assertEqual(query.scope.detector_types, ("LicensePlateRecognition",))
        self.assertEqual(query.taxonomy.categories, ("lpr",))
        self.assertEqual(query.taxonomy.event_types, ("ET_DetectorEvent",))
        self.assertEqual(query.taxonomy.states, ("HAPPENED",))
        self.assertEqual(query.taxonomy.priorities, ("AP_HIGH",))
        self.assertEqual(query.taxonomy.severities, ("SV_WARNING",))
        self.assertEqual(query.text.contains, "YZ45246")
        self.assertEqual(query.text.mask, "*5246")
        self.assertEqual(query.limit, 50)
        self.assertEqual(query.offset, 10)
        self.assertFalse(query.descending)
        self.assertEqual(
            query.to_legacy_filters(),
            {
                "range": {
                    "begin_time": "20260310T100000",
                    "end_time": "20260310T110000",
                },
                "hosts": ["ServerA"],
                "domains": ["DomainA"],
                "subject": "hosts/ServerA/DeviceIpint.7",
                "camera_names": ["Gate"],
                "camera_access_points": ["hosts/ServerA/DeviceIpint.7/SourceEndpoint.video:0:0"],
                "detector_access_points": ["hosts/ServerA/AVDetector.2/EventSupplier"],
                "detector_names": ["2.LPR"],
                "detector_types": ["LicensePlateRecognition"],
                "categories": ["lpr"],
                "event_type": "ET_DetectorEvent",
                "states": ["HAPPENED"],
                "severities": ["SV_WARNING"],
                "priorities": ["AP_HIGH"],
                "contains": "YZ45246",
                "mask": "*5246",
                "limit": 50,
                "offset": 10,
                "descending": False,
            },
        )

    def test_event_query_matches_card_across_time_scope_taxonomy_and_text(self):
        card = {
            "timestamp": "20260310T101500",
            "event_type": "listed_lpr_detected",
            "category": "lpr",
            "state": "HAPPENED",
            "priority": "AP_HIGH",
            "camera_access_point": "hosts/ServerA/DeviceIpint.7/SourceEndpoint.video:0:0",
            "detector_access_point": "hosts/ServerA/AVDetector.2/EventSupplier",
            "detector": "2.LPR",
            "camera": "Gate",
            "text": "LP recognized from list Not listed · YZ45246",
            "localization_text": "LP recognized from list Not listed · YZ45246",
            "plate": "YZ45246",
            "server": "ServerA",
        }
        query = EventQuery(
            time_range=EventTimeRange(begin="20260310T100000", end="20260310T103000"),
            scope=EventScopeFilter(
                hosts=("ServerA",),
                subjects=("hosts/ServerA/DeviceIpint.7",),
                camera_names=("Gate",),
                camera_access_points=("hosts/ServerA/DeviceIpint.7/SourceEndpoint.video:0:0",),
                detector_access_points=("hosts/ServerA/AVDetector.2/EventSupplier",),
                detector_names=("LPR",),
            ),
            taxonomy=EventTaxonomyFilter(
                categories=("lpr",),
                event_types=("ET_DetectorEvent",),
                states=("HAPPENED",),
                priorities=("AP_HIGH",),
            ),
            text=EventTextFilter(contains="YZ45246"),
        )

        self.assertTrue(query.matches_card(card))
        self.assertTrue(query_card_matches(card, query))
        self.assertFalse(query.matches_card({**card, "timestamp": "20260310T104501"}))
        self.assertFalse(query.matches_card({**card, "priority": "AP_LOW"}))
        self.assertFalse(
            query.matches_card(
                {
                    **card,
                    "server": "ServerB",
                    "camera_access_point": "hosts/ServerB/DeviceIpint.7/SourceEndpoint.video:0:0",
                    "detector_access_point": "hosts/ServerB/AVDetector.2/EventSupplier",
                }
            )
        )

    def test_event_text_mask_matches_plate_values(self):
        card = {
            "timestamp": "20260310T101500",
            "event_type": "ET_DetectorEvent",
            "category": "lpr",
            "plate": "YZ45246",
            "text": "license plate",
        }
        query = EventQuery(text=EventTextFilter(mask="*5246"))

        self.assertTrue(query.matches_card(card))
        self.assertFalse(EventQuery(text=EventTextFilter(mask="AB*")).matches_card(card))


if __name__ == "__main__":
    unittest.main()
