#!/usr/bin/env python3
#
# Copyright 2023 Angus Gratton
#
# SPDX-License-Identifier: MIT
import argparse
from asyncio import run, sleep, wait_for
import configparser
import logging
import telnetlib3
import json
import re
import amqtt.client as amqtt
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class BroadcomTelnet:
    def __init__(self, host, port, username, password):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.r = None
        self.w = None

    async def connect(self):
        logger.info(f"Connecting to {self.host}:{self.port}...")
        r, w = await telnetlib3.open_connection(self.host, self.port)
        self.r = r
        self.w = w
        logger.info("Socket connected")

        banner = await self.read_to_prompt("Login:")
        self.banner = banner.strip()
        logger.info(f"Server banner: {self.banner}")
        self.writeline(self.username)

        await self.read_to_prompt("Password:")
        self.writeline(self.password)
        await self.read_to_prompt()
        logger.info(f"Logged in as {self.username}")

    def writeline(self, line):
        logger.debug(">>> " + repr(line))
        self.w.write(line)
        self.w.write("\r\n")

    async def read_to_prompt(self, prompt="> "):
        """Similar to self.r.read_until(prompt) but don't include 'prompt' in the
        result, and discards anything read after 'prompt' in the same read
        call.

        Can be used to detect when a telnet command has finished and the command
        line has prompted for the next command.

        (Doesn't use read_until because telnetlb3 doesn't seem to
        work that well with it!)

        """

        res = ""
        while prompt not in res:
            if self.r.connection_closed:
                raise RuntimeError("Telnet connection closed")
            new = await self.r.read(80)
            logger.debug("<<< " + repr(new))
            res += new
        res = res[: res.index(prompt)]
        return res.replace("\r\n", "\n")

    async def command(self, cmd):
        """Write a telnet command, read and return the output."""
        self.writeline(cmd)
        resp = await self.read_to_prompt()
        resp = resp[len(cmd) :]  # Strip the echoed command
        return resp.strip()

    async def xdsl_stats(self):
        """Write the xslctl info --stats command, parse the output."""
        raw = await self.command("xdslctl info --stats")
        p = OutputParser(raw)

        p.add_str("profile", "Profile:")
        p.add_str("line_status", "Line Status:")
        p.add_str("training_status", "Training Status:")

        # These two are probably enum values of some kind, but I don't know what
        # each number corresponds to
        p.add_str("last_retrain_reason", "Last Retrain Reason:")
        p.add_str("last_init_status", "Last initialization procedure status:")

        p.add_downup("snr_db", "SNR (dB):", float)
        p.add_downup("atten_db", "Attn(dB):", float)
        p.add_downup("power_dbm", "Pwr(dBm):", float)

        # Current upstream/downstream rate, as Bearer 0
        p.add_rate("rate", "Bearer: 0,")

        # Max upstream/downstream rates, a one-off format
        p.add_rate("max_rate", "Max:")

        errc = p.parsed["error_counters"] = {}
        # Explanation of acronyms: https://kitz.co.uk/adsl/linestats_errors.htm
        #
        # The stats command outputs multiple sets of these for different time windows,
        # but the first window is "Totals" so it'll match these.
        for counter in ("FEC", "CRC", "ES", "SES", "UAS", "LOS", "LOF", "LOM"):
            p.add_downup(counter, counter + ":", int, errc)

        # G.INP, "impulse noise" protection
        ginp = p.parsed["ginp"] = {}
        # Seconds when one or more Low Error-Free Throughput Defect was logged
        p.add_downup("LEFTRS", "LEFTRS:", int, ginp)
        # minimum Error-Free Throughput
        p.add_downup("min_EFTR", "minEFTR:", int, ginp)

        return p.parsed

    async def ifconfig(self, ifname="ptm0.1"):
        """Write the ifconfig command, parse the output."""
        raw = await self.command(f"ifconfig {ifname}")
        p = OutputParser(raw)

        p.parsed["up"] = " UP " in raw

        packets = p.parsed["packets"] = {}
        p.add_int("rx", "RX packets:", packets)
        p.add_int("tx", "TX packets:", packets)

        ibytes = p.parsed["bytes"] = {}
        p.add_int("rx", "RX bytes:", ibytes)
        p.add_int("tx", "TX bytes:", ibytes)

        return p.parsed


class OutputParser:
    """Wrapper around regex parsing of fields in a chunk of raw command output.

    Accumulates each result in the dict field self.parsed, unless a different
    dict is supplied via the "dest" kwarg on each function.

    """

    def __init__(self, raw):
        """Initialize the parser with the raw command output."""
        self.raw = raw
        self.parsed = {}

    def add_str(self, key, prefix, dest=None):
        """Extract a simple string value of the form "<prefix label>:    VALUE"
        and add it to 'dest' (or self.parsed by default) if found.
        """
        if dest is None:
            dest = self.parsed
        m = re.search(r"{}\s*(.+)".format(re.escape(prefix)), self.raw)
        if m:
            dest[key] = m.group(1)

    def add_int(self, key, prefix, dest=None):
        """Extract an integer value of the form "<prefix label>:    INTVALUE"
        and add it to 'dest' (or self.parsed by default) if found.
        """
        if dest is None:
            dest = self.parsed
        m = re.search(r"{}\s*(\d+)".format(re.escape(prefix)), self.raw)
        if m:
            dest[key] = int(m.group(1))

    def add_rate(self, key, prefix, dest=None):
        """Extract a pair of rates with the given prefix, followed by
        "Upstream rate = XXX Kbps, Downstream rate = XXX Kbps" and add
        the up/down values as integers to dest[key].
        """
        if dest is None:
            dest = self.parsed
        expr = r"{}\s*Upstream rate = (\d+) Kbps, Downstream rate = (\d+) Kbps".format(
            prefix
        )
        m = re.search(expr, self.raw)
        if m:
            dest[key] = {"down": int(m.group(2)), "up": int(m.group(1))}

    def add_downup(self, key, prefix, ntype, dest=None):
        """Extract a pair of values of the form "<prefix label>: XXX YYY" where
        "XXX" column corresponds to "Down" and "YYY" column corresponds to "Up".

        Pass to the ntype function to convert to a numeric value of that type,
        then store in dest[key]["down"] and dest[key]["up"].
        """
        if dest is None:
            dest = self.parsed
        expr = r"{}\s+([^\s]+)\s+([^\s]+)".format(re.escape(prefix))
        m = re.search(expr, self.raw)
        if m:
            down = ntype(m.group(1))
            up = ntype(m.group(2))
            dest[key] = {"down": down, "up": up}


async def main(config):
    mqtt_config = config["mqtt"]
    mqtt_uri = mqtt_config["uri"]
    mqtt_topic_prefix = mqtt_config.get("topic_prefix", "xdsl")

    xdsl_config = config["xdsl"]
    xdsl_host = xdsl_config["host"]
    xdsl_user = xdsl_config.get("user", "admin")
    xdsl_password = xdsl_config.get("password", "admin")
    xdsl_port = int(xdsl_config.get("port", 23))
    xdsl_connect_timeout = int(xdsl_config.get("connect_timeout", 8))
    xdsl_timeout = int(xdsl_config.get("command_timeout", 20))
    xdsl_poll_delay = int(xdsl_config.get("poll_delay", 30))

    try:
        # (config.get() is a weird function in configparser...)
        restart_config = config["restart"]
    except KeyError:
        restart_config = None

    if restart_config:
        restart_at = restart_config["at"]
        m = re.match(r"(\d+):(\d+)$", restart_at)
        if m:
            restart_h, restart_m = (
                int(d) for d in m.groups()
            )  # hour and minute to check for restart conditions
        if not (m and 0 <= restart_h <= 23 and 0 <= restart_m <= 59):
            raise RuntimeError(
                f"Config [restart] value {restart_at} must be a valid 24-hour time formatted as HH:MM"
            )
        restart_min_up = int(restart_config["min_up"])
        restart_min_down = int(restart_config["min_down"])
        logger.info(
            f"Daily at {restart_at} will check max_rate exceeds upstream {restart_min_up}kbps and downstream {restart_min_down}kbps"
        )

    def get_next_restart_check():
        if not restart_config:
            return None
        now = datetime.now()
        next_restart = now.replace(
            hour=restart_h, minute=restart_m, second=0, microsecond=0
        )
        if next_restart < now:
            next_restart += timedelta(days=1)
        logger.debug(f"Next restart check at {next_restart}")
        return next_restart

    t = None
    next_restart = get_next_restart_check()

    m = amqtt.MQTTClient("xdsl2mqtt")
    await wait_for(m.connect(mqtt_uri), xdsl_connect_timeout)

    while True:
        if not t:  # connect to Telnet interface
            t = BroadcomTelnet(xdsl_host, xdsl_port, xdsl_user, xdsl_password)
            await wait_for(t.connect(), xdsl_connect_timeout)

        stats = await wait_for(t.xdsl_stats(), xdsl_timeout)
        stats["banner"] = t.banner
        interface = await t.ifconfig()
        stats_topic = f"{mqtt_topic_prefix}/stats"
        stats_payload = json.dumps(stats)
        interface_topic = f"{mqtt_topic_prefix}/interface"
        interface_payload = json.dumps(interface)

        logger.debug(f"Publish {stats_topic} {stats_payload}")
        logger.debug(f"Publish {interface_topic} {interface_payload}")

        await wait_for(m.publish(stats_topic, stats_payload.encode()), xdsl_timeout)
        await wait_for(
            m.publish(interface_topic, interface_payload.encode()), xdsl_timeout
        )

        if next_restart and datetime.now() > next_restart:
            next_restart = get_next_restart_check()

            try:
                up = stats["max_rate"]["up"]
                down = stats["max_rate"]["down"]
                logger.info(
                    f"Checking restart conditions. Up {up} vs min "
                    f"{restart_min_up}. Down {down} vs min "
                    f"{restart_min_down}."
                )
            except KeyError:
                up = 0
                down = 0
                logger.info(
                    "Checking restart conditions while interface appears down..."
                )

            if up < restart_min_up or down < restart_min_down:
                logger.warning("Restarting modem...")
                t.writeline("reboot")
                t = None  # allow garbage collection to clean old socket up
                logger.info("Waiting for reboot to complete...")
                await sleep(60)
                continue

        await sleep(xdsl_poll_delay)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", "-c", default="config.ini", help="Config file")
    args = parser.parse_args()

    config = configparser.ConfigParser()
    if not config.read(args.config):
        raise SystemExit(f"ERROR: Config file not found: {args.config}")

    debug = config.getboolean("general", "debug", fallback=False)

    logging.basicConfig(level=logging.DEBUG if debug else logging.INFO,
                        format='%(asctime)s %(levelname)-8s %(message)s')

    run(main(config), debug=debug)
