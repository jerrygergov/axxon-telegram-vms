# Axxon Streaming Options (Telegram-Focused)

This note summarizes practical Axxon streaming and event-delivery paths found in local references, with focus on what can be delivered in Telegram bots immediately.

Primary references reviewed:
- `http_server_http_api.md`
- `http_servers.md`
- `http_cameras.md`
- `http_archives.md`
- `http_get_camera_events_using_websocket.md`

## Practical Matrix

| Method | Protocol / Format | Typical latency | Telegram suitability | Pros | Cons | Exact endpoint pattern(s) |
|---|---|---:|---|---|---|---|
| Live HTTP stream (`/live/media`) | HTTP MJPEG (default); MP4/HLS options | Low for MJPEG; medium for HLS | Medium | Easy URL playback in browser/ffplay; can scale via `w/h` | Continuous stream is not native in Telegram chat bubbles; MJPEG can add server load | `GET http://{host}:{port}/{prefix}/live/media/{VIDEOSOURCEID}`; MJPEG sample: `...?w=1600&h=0` |
| Live RTSP | RTSP native video | Low | Low (direct in Telegram) / High (as external player link) | Best real-time quality, native stream | Requires RTSP-capable client | `rtsp://{user}:{pass}@{host}:554/hosts/{VIDEOSOURCEID}` |
| RTSP over HTTP tunnel | RTSP over HTTP (`rtspproxy`) | Low-Medium | Low (direct in Telegram) / High (external link) | Works where raw RTSP is blocked | Extra transport overhead | `rtsp://{user}:{pass}@{host}:{http_port}/rtspproxy/hosts/{VIDEOSOURCEID}` |
| Live HLS | HTTP HLS (`m3u8`) | About 20s startup delay | Medium (open in browser/player) | Web-friendly, broadly supported | Startup delay and segment buffering | Init: `GET http://{host}:{port}/{prefix}/live/media/{VIDEOSOURCEID}?format=hls&keep_alive=60`; response has `stream_url` like `/hls/{stream_id}/playout.m3u8`, `keep_alive_url`, `stop_url` |
| Live snapshot | HTTP JPEG frame | Snapshot cadence; default refresh behavior ~30s | High | Best fit for Telegram `send_photo`; cheap, simple | Not continuous video | `GET http://{host}:{port}/{prefix}/live/media/snapshot/{VIDEOSOURCEID}` with optional `w`,`h`,`crop_x`,`crop_y`,`crop_width`,`crop_height` |
| Archive stream bootstrap | HTTP endpoint returning RTSP/HTTP paths | Depends on chosen playback speed and transport | Medium | Plays historical video with speed control, rewind | More parameters and timestamp handling | `GET http://{host}:{port}/{prefix}/archive/media/{VIDEOSOURCEID}/{STARTTIME}?format={rtsp|mjpeg|mp4|hls}&speed={n}&w={w}&h={h}&id={stream_id}` |
| Archive RTSP direct | RTSP | Low-Medium | Low (direct in Telegram) / High (external link) | Efficient archive playback with `speed` | External player required | `rtsp://{user}:{pass}@{host}:554/archive/hosts/{VIDEOSOURCEID}/{STARTTIME}?speed={n}` |
| Archive RTSP over HTTP tunnel | RTSP over HTTP | Medium | Low (direct in Telegram) / High (external link) | Works through HTTP-friendly paths | External player required | `rtsp://{user}:{pass}@{host}:{proxy_port}/rtspproxy/archive/hosts/{VIDEOSOURCEID}/{STARTTIME}` |
| Archive HTTP video | HTTP MJPEG/other by format negotiation | Medium | Medium | URL-based historical playback | Heavier than snapshots; player-dependent behavior | `http://{user}:{pass}@{host}:{port}/{prefix}/archive/media/{VIDEOSOURCEID}/{STARTTIME}?w={w}&h={h}&speed={n}` |
| Events over WebSocket | WS / WSS event feed | Near real-time | High (as trigger path, not media playback) | Push delivery for detector/alert/state events | Not media itself; needs bot logic to fetch frame/clip | Connect: `ws://{user}:{pass}@{host}:{port}/{prefix}/events` (detailed payload: `?schema=proto`) |

Notes:
- `{VIDEOSOURCEID}` in HTTP live/snapshot/archive routes is documented as three-component source endpoint id like `SERVER1/DeviceIpint.23/SourceEndpoint.video:0:0`.
- RTSP paths in docs are shown under `/hosts/...` for live and `/archive/hosts/...` for archive.
- WebSocket supports include/exclude subscription JSON and camera configuration `track`/`untrack` commands.

## Telegram-Compatible Delivery Paths

Best immediate patterns for Telegram bots:

1. Live snapshots as photos:
- Pull `GET /live/media/snapshot/{VIDEOSOURCEID}` and send via `send_photo`.
- Strong match for anti-spam throttling and callback-based UX.

2. Event-driven frame/clip from archive/media:
- Use event id/timestamp to build single frame or short clip and send as photo/video.
- Already fits callback actions and avoids long-running streams in chat.

3. External stream links:
- Provide RTSP/HLS/HTTP URLs in camera cards so operators can open VLC/browser when needed.
- Keep Telegram as control plane and notification plane.

## Practical Recommendation

For this bot architecture, the most reliable default is:
- Telegram message/photo/video for snapshots and short clips.
- Optional external links for RTSP/HLS/HTTP playback.
- WebSocket or notifier/polling for fast event triggers, not for direct media rendering in Telegram.
