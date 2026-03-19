# Mid-Plan Nuance Audit

Date: 2026-03-10

Scope:
- Step 10 grouping/threading/topic routing/operator UX
- Step 11 role-aware UI split
- Step 12 favorites/profile-like acceleration
- Step 14-16 digest/topic/admin/hosts nuances
- Step 17-19 read-only operational/admin nuances

Implemented in this pass:
- Narrow Step 11 slice only: admins now get a home-level `Admin view` shortcut into the existing read-only admin surface, while operators keep the existing uncluttered home menu.
  - Evidence: `scripts/axxon_tg_ui.py:1233-1288`, `scripts/axxon_tg_bot.py:1372-1378`, `scripts/axxon_tg_bot.py:2238-2425`, `tests/test_ui_payloads.py`

Remaining gaps

1. Step 10 command/menu grouping is still largely flat.
   - The plan calls for grouped operator/subscription/operations/utility surfaces, including `digest`, `hosts`, and `profile`: `support/docs/IMPLEMENTATION_PLAN_NEXT.md:195-204`.
   - The registered Telegram command set is still a single flat list and does not expose `digest`, `hosts`, `host`, `acfa`, or `profile`: `scripts/axxon_tg_bot.py:1329-1351`.
   - Help text is also still a flat command dump rather than grouped role-aware navigation: `scripts/axxon_tg_bot.py:1390-1431`.

2. Step 11 role-aware UI split is only partial.
   - The plan expects operator vs admin UI capability split: `support/docs/IMPLEMENTATION_PLAN_NEXT.md:206-213`.
   - Current admin visibility exists, but only as `/admin` plus `adm:*` callbacks: `scripts/axxon_tg_bot.py:1705-1719`, `scripts/tg_admin_ui.py:15-20`.
   - Macro/PTZ remain admin-only slash commands outside the home/menu model, so the split is not yet a complete UI capability separation: `scripts/axxon_tg_bot.py:1580-1629`, `scripts/axxon_tg_bot.py:1632-1693`.

3. Step 12 favorites / pinned detectors / saved quick views are not implemented.
   - The plan explicitly calls for favorite cameras, pinned detectors, default host/domain, and saved quick views in secure profile storage: `support/docs/IMPLEMENTATION_PLAN_NEXT.md:215-224`.
   - Secure profile persistence currently stores subscription metadata and timezone only: `scripts/axxon_tg_bot.py:172-185`, `scripts/axxon_tg_bot.py:852-904`.
   - No runtime command/UI surface exists for favorites or quick views; repo search found no implementation hits for `favorite`, `pinned`, or `quick view` outside roadmap/test text.

4. Step 14 digest-capable notifications are still absent.
   - The plan expects bundling, grouping, daily/shift summaries, and quiet-hours behavior: `support/docs/IMPLEMENTATION_PLAN_NEXT.md:244-252`.
   - Subscription runtime tracks only per-user rate limits, duplicate windows, and per-event delivery accounting; there is no digest window, batch model, quiet-hours policy, or summary artifact: `axxon_telegram_vms/services/subscriptions.py:40-51`, `axxon_telegram_vms/services/subscriptions.py:54-219`.
   - No `/digest` command or digest callback surface exists in the Telegram command set: `scripts/axxon_tg_bot.py:1329-1351`.

5. Step 15 topic/thread-aware routing is not implemented.
   - The plan expects per-topic routing and digest broadcast support: `support/docs/IMPLEMENTATION_PLAN_NEXT.md:254-263`.
   - Current subscription records do not carry topic/thread identifiers or routing rules: `axxon_telegram_vms/services/subscriptions.py:54-80`.
   - The bot callback/runtime path does not reference Telegram topic/thread fields such as `message_thread_id`; delivery is only chat/user scoped in the current runtime.

6. Step 16 host/domain visibility is only partially covered through the admin view.
   - The plan expects `/hosts`, `/host <name>`, host status cards, and domain/platform summaries: `support/docs/IMPLEMENTATION_PLAN_NEXT.md:269-278`.
   - Current backend/UI support is bundled inside `admin-view` and `adm:hosts`, not direct host commands: `scripts/axxon_web_api.py:1413-1417`, `scripts/axxon_web_api.py:2286-2363`, `scripts/tg_admin_ui.py:87-131`.
   - Telegram command registration has `/admin` but no `/hosts` or `/host`: `scripts/axxon_tg_bot.py:1329-1351`, `scripts/axxon_tg_bot.py:2437-2459`.

7. Step 17 macro read-only inventory is not realized; only guarded execution preview exists.
   - The plan expects list/search/details inventory before execution: `support/docs/IMPLEMENTATION_PLAN_NEXT.md:280-289`.
   - Current macro UX is explicitly execution-oriented and admin-only: `scripts/axxon_tg_ui.py:729-832`, `scripts/axxon_tg_bot.py:1580-1629`.
   - No `/macros` list/search/detail command exists in the registered bot surface: `scripts/axxon_tg_bot.py:1329-1351`.

8. Step 18 PTZ read-only visibility is only partially realized and still tied to control preview.
   - The plan expects read-only capability/preset/tour/position visibility as a confidence-building step: `support/docs/IMPLEMENTATION_PLAN_NEXT.md:291-298`.
   - Current PTZ UX is an admin-only control preview flow that "only exposes preset jumps in this MVP": `scripts/axxon_tg_ui.py:844-858`, `scripts/axxon_tg_bot.py:1632-1693`.
   - Capability and preset details are visible only after entering the control preview, not through a distinct read-only PTZ inventory surface: `scripts/axxon_tg_ui.py:861-939`.

9. Step 19 ACFA read-only visibility is still missing.
   - The plan expects ACFA unit inventory, event/action metadata, and host/domain linkage: `support/docs/IMPLEMENTATION_PLAN_NEXT.md:300-305`.
   - The current Telegram command list and API parser surfaces expose no ACFA command/view: `scripts/axxon_tg_bot.py:1329-1351`, `scripts/axxon_web_api.py:1407-1417`.

Priority recommendation

1. Add direct read-only entrypoints for already-shaped data before adding more write-like admin flows.
   - Highest-value next slices: `/hosts`, macro inventory list/details, PTZ read-only list/details.
2. Add a lightweight profile/favorites layer on top of the existing secure profile store.
   - Start with favorite cameras + saved default host/domain.
3. Add digest/topic data model changes only after command/UI grouping is cleaned up.
   - Otherwise delivery behavior will outrun discoverability and configuration clarity.
