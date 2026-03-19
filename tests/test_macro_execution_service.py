import unittest

from axxon_telegram_vms.services import (
    build_macro_execution_policy,
    evaluate_macro_execution_guardrails,
    macro_execution_request_to_api_args,
    parse_macro_execution_terms,
    select_macro_inventory_record,
    shape_macro_execution_result,
)


MACROS = [
    {
        "guid": "11111111-1111-1111-1111-111111111111",
        "name": "Manual Alert Test",
        "mode": {
            "enabled": True,
            "is_add_to_menu": True,
            "user_role": "",
            "common": {},
        },
        "conditions": {},
        "rules": {
            "0": {
                "path": "/E:0",
                "action": {
                    "action": {
                        "raise_alert": {
                            "priority": "AP_LOW",
                        }
                    }
                },
            }
        },
    },
    {
        "guid": "22222222-2222-2222-2222-222222222222",
        "name": "Webhook Trigger",
        "mode": {
            "enabled": True,
            "is_add_to_menu": True,
            "user_role": "",
            "common": {},
        },
        "conditions": {},
        "rules": {
            "0": {
                "path": "/E:0",
                "action": {
                    "action": {
                        "web_query": {
                            "path": "/danger",
                        }
                    }
                },
            }
        },
    },
]


class MacroExecutionServiceTests(unittest.TestCase):
    def test_parse_terms_accepts_multi_token_name(self):
        request = parse_macro_execution_terms(["name=Manual", "Alert", "Test"])

        self.assertEqual(request.macro_name, "Manual Alert Test")
        self.assertEqual(
            macro_execution_request_to_api_args(request),
            ["--macro-name", "Manual Alert Test"],
        )

    def test_guardrails_allow_manual_allowlisted_macro(self):
        request = parse_macro_execution_terms(["id=11111111-1111-1111-1111-111111111111"])
        record = select_macro_inventory_record(request, MACROS)
        policy = build_macro_execution_policy(
            execution_enabled=True,
            admin=True,
            allowed_macro_ids=[record.macro_id],
        )

        decision = evaluate_macro_execution_guardrails(record, policy)

        self.assertTrue(decision.allowed)
        self.assertIn("Guardrails are re-checked immediately before execution.", decision.warnings)

    def test_guardrails_block_denied_action_families(self):
        request = parse_macro_execution_terms(["name=Webhook", "Trigger"])
        record = select_macro_inventory_record(request, MACROS)
        policy = build_macro_execution_policy(
            execution_enabled=True,
            admin=True,
            allowed_macro_names=[record.name],
        )

        decision = evaluate_macro_execution_guardrails(record, policy)

        self.assertFalse(decision.allowed)
        self.assertTrue(any("web_query" in item for item in decision.reasons))

    def test_shape_result_keeps_guardrail_and_execution_state(self):
        request = parse_macro_execution_terms(["id=11111111-1111-1111-1111-111111111111"])
        record = select_macro_inventory_record(request, MACROS)
        policy = build_macro_execution_policy(
            execution_enabled=False,
            admin=True,
            allowed_macro_ids=[record.macro_id],
        )
        decision = evaluate_macro_execution_guardrails(record, policy)

        result = shape_macro_execution_result(
            request,
            record,
            decision,
            policy=policy,
            attempted=False,
            ok=False,
            error=None,
        )

        self.assertEqual(result["request"]["selector"]["kind"], "id")
        self.assertEqual(result["macro"]["name"], "Manual Alert Test")
        self.assertFalse(result["guardrails"]["allowed"])
        self.assertFalse(result["execution"]["attempted"])
        self.assertTrue(result["execution"]["blocked"])


if __name__ == "__main__":
    unittest.main()
