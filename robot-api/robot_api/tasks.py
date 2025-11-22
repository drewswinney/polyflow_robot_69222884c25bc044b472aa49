import os
import shlex
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any

WIFI_CONF_PATH = Path(os.environ.get("WIFI_CONF_PATH", "/var/lib/polyflow/wifi.conf"))
WIFI_SWITCH_CMD = os.environ.get("WIFI_SWITCH_CMD", "/run/current-system/sw/bin/polyflow-wifi-mode")


def write_wifi_conf(ssid: str, psk: Optional[str]) -> None:
    WIFI_CONF_PATH.parent.mkdir(parents=True, exist_ok=True)
    ssid_q = shlex.quote(ssid)
    psk_q = shlex.quote(psk or "")
    WIFI_CONF_PATH.write_text(f"WIFI_SSID={ssid_q}\nWIFI_PSK={psk_q}\n")


def clear_wifi_conf() -> None:
    if WIFI_CONF_PATH.exists():
        WIFI_CONF_PATH.unlink()


def run_switch() -> None:
    subprocess.run([WIFI_SWITCH_CMD], check=True)


def read_wifi_conf() -> Dict[str, Any]:
    if not WIFI_CONF_PATH.exists():
        return {"configured": False, "ssid": None, "pskSet": False}
    ssid = None
    psk = None
    for line in WIFI_CONF_PATH.read_text().splitlines():
        if line.startswith("WIFI_SSID="):
            ssid = line.split("=", 1)[1].strip().strip('"').strip("'")
        elif line.startswith("WIFI_PSK="):
            psk = line.split("=", 1)[1].strip().strip('"').strip("'")
    return {"configured": True, "ssid": ssid, "pskSet": bool(psk)}
