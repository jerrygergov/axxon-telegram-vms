# systemd units

Install:

```bash
APP_DIR="$HOME/axxon-telegram-vms"
sudo cp "$APP_DIR/deploy/systemd/axxon-archive-relay.service" /etc/systemd/system/
sudo cp "$APP_DIR/deploy/systemd/axxon-tg-bot.service" /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable axxon-archive-relay.service axxon-tg-bot.service
sudo systemctl restart axxon-tg-bot.service
```

Status:

```bash
sudo systemctl status axxon-tg-bot.service
sudo systemctl status axxon-archive-relay.service
```

Logs:

```bash
journalctl -u axxon-tg-bot.service -f
journalctl -u axxon-archive-relay.service -f
```
