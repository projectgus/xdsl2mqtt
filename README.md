# xdsl2mqtt

A bridge to read the "xDSL" statistics from the telnet interface of a Broadcom-based xDSL modem and publish the output to MQTT where it can be ingested into a database like InfluxDB for analysis, graphing, etc.

This might be useful if, for example, your crummy Australian NBN FTTN connection keeps developing issues on the exact days NBNCo contractors are working in your street, and you need to convince them to escalate the fault each time it happens... Or maybe it'll just make you feel self-righteous about knowing the exact moment it went bad or came good. Who can say?

Disclaimer: I'm not an ADSL or VDSL expert, just a frustrated NBN customer.

## Alternative Programs

* [DSLStats](http://dslstats.me.uk/index.html) looks to have an impressive amount of modem support, although it doesn't integrate with MQTT so I didn't try it out. It is apparently free software under GPL, but you have to [contact the author to get the source](http://dslstats.me.uk/licence.html).

## Modem Support

Currently:

* D-Link DSL-G225, with a Broadcom BCM963381 VDSL2 chipset.

This will probably work on other Broadcom chipset modems, but may need some tweaking.

To tell if a modem if supported, try to connect to your modem's IP address via telnet:

```
❯ telnet 192.168.1.1
Trying 192.168.1.1...
Connected to 192.168.1.1.
Escape character is '^]'.
BCM963381 Broadband Router
Login: admin
Password: 
 > 
```

Default admin password is `admin`, at least it was for my modem.

(Note: if your modem is in "bridge mode" then your router will need to have a static route added on the router WAN interface, routing to the modem's IP address. If you can access the web interface of the modem, then you have all the routes you need.)

## Adding New Modem Support

If your modem's telnet interface says something other than `BCM963381 Broadband Router` then this program may or may not work unmodified.

If this program doesn't work with your modem and you'd like support added, run two commands in the telnet interface - `xdslctl info --stats` and `ifconfig`. Then open an issue here with the output from them, and I'll see what I can do.

If your xDSL modem doesn't have a Broadcom chipset, doesn't have a Telnet interface available, or doesn't support the `xdslctl info --stats` command then it won't be very easy to add support, sorry. Pull Requests to add more support would still be welcome, though, provided they are maintainable!

<details>
<summary>Sample output from these two commands on DSL-G225</summary>

```
 > xdslctl info --stats
xdslctl: ADSL driver and PHY status
Status: Showtime
Last Retrain Reason:    0
Last initialization procedure status:   0
Max:    Upstream rate = 5517 Kbps, Downstream rate = 33960 Kbps
Bearer: 0, Upstream rate = 5517 Kbps, Downstream rate = 31829 Kbps
Bearer: 1, Upstream rate = 0 Kbps, Downstream rate = 0 Kbps
Link Power State:       L0
Mode:                   VDSL2 Annex B
VDSL2 Profile:          Profile 17a
TPS-TC:                 PTM Mode(0x0)
Trellis:                U:ON /D:ON
Line Status:            No Defect
Training Status:        Showtime
                Down            Up
SNR (dB):        6.9             4.9
Attn(dB):        31.0            0.0
Pwr(dBm):        14.5            6.3

                        VDSL2 framing
                        Bearer 0
MSGc:           -6              -6
B:              235             162
M:              1               1
T:              0               0
R:              12              10
S:              0.2360          0.9389
L:              8408            1474
D:              8               4
I:              248             173
N:              248             173
Q:              8               4
V:              1               0
RxQueue:                24              12
TxQueue:                8               6
G.INP Framing:          18              18
G.INP lookback:         8               6
RRC bits:               24              24
                        Bearer 1
MSGc:           90              58
B:              0               0
M:              2               2
T:              2               2
R:              16              16
S:              10.6667         16.0000
L:              24              16
D:              1               1
I:              32              32
N:              32              32
Q:              0               0
V:              0               0
RxQueue:                0               0
TxQueue:                0               0
G.INP Framing:          0               0
G.INP lookback:         0               0
RRC bits:               0               0

                        Counters
                        Bearer 0
OHF:            0               0
OHFErr:         0               0
RS:             2957066272              3097964
RSCorr:         1253366         20211
RSUnCorr:       0               0
                        Bearer 1
OHF:            10902661                460943
OHFErr:         10              0
RS:             65415596                837140
RSCorr:         11175           131
RSUnCorr:       10              0

                        Retransmit Counters
rtx_tx:         24512155                830
rtx_c:          1844            527121
rtx_uc:         0               1442420

                        G.INP Counters
LEFTRS:         0               1196
minEFTR:        31831           5516
errFreeBits:    84935001                2463247937

                        Bearer 0
HEC:            0               0
OCD:            0               0
LCD:            0               0
Total Cells:    2129435049              0
Data Cells:     390808005               0
Drop Cells:     0
Bit Errors:     0               0

                        Bearer 1
HEC:            0               0
OCD:            0               0
LCD:            0               0
Total Cells:    0               0
Data Cells:     0               0
Drop Cells:     0
Bit Errors:     0               0

ES:             0               0
SES:            0               0
UAS:            162             162
AS:             175147

                        Bearer 0
INP:            43.00           41.00
INPRein:        0.00            0.00
delay:          0               0
PER:            0.00            0.00
OR:             0.01            0.01
AgR:            31880.11        5533.57

                        Bearer 1
INP:            2.50            4.00
INPRein:        2.50            4.00
delay:          0               0
PER:            16.06           16.06
OR:             47.81           31.87
AgR:            47.81   31.87

Bitswap:        3817/12067              1253/1257

Total time = 2 days 41 min 49 sec
FEC:            1253366         20211
CRC:            0               0
ES:             0               0
SES:            0               0
UAS:            162             162
LOS:            0               0
LOF:            0               0
LOM:            0               0
Latest 15 minutes time = 11 min 49 sec
FEC:            12604           2
CRC:            0               0
ES:             0               0
SES:            0               0
UAS:            0               0
LOS:            0               0
LOF:            0               0
LOM:            0               0
Previous 15 minutes time = 15 min 0 sec
FEC:            4140            15
CRC:            0               0
ES:             0               0
SES:            0               0
UAS:            0               0
LOS:            0               0
LOF:            0               0
LOM:            0               0
Latest 1 day time = 41 min 49 sec
FEC:            20810           23
CRC:            0               0
ES:             0               0
SES:            0               0
UAS:            0               0
LOS:            0               0
LOF:            0               0
LOM:            0               0
Previous 1 day time = 24 hours 0 sec
FEC:            530985          1839
CRC:            0               0
ES:             0               0
SES:            0               0
UAS:            0               0
LOS:            0               0
LOF:            0               0
LOM:            0               0
Since Link time = 2 days 39 min 7 sec
FEC:            1253366         20211
CRC:            0               0
ES:             0               0
SES:            0               0
UAS:            0               0
LOS:            0               0
LOF:            0               0
LOM:            0               0
NTR: mipsCntAtNtr=0 ncoCntAtNtr=0
 > ifconfig
bcmsw     Link encap:Ethernet  HWaddr (snipped)  
          UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
          RX packets:10945915 multicast:0 unicast:10945915 broadcast:0
          RX errors:0 dropped:0 overruns:0 frame:0
          TX packets:20717184 multicast:0 unicast:20717184 broadcast:0
          TX errors:0 dropped:0 overruns:0 carrier:0 collisions:0
          txqueuelen:1000
          RX bytes:2371136848 (2.2 GiB) TX bytes:3309911575 (3.0 GiB)
          RX multicast bytes:0 (0.0 B) TX multicast bytes:0 (0.0 B)
          Base address:0x8200 

br0       Link encap:Ethernet  HWaddr (snipped) 
          inet addr:192.168.1.1  Bcast:192.168.254.255  Mask:255.255.255.0
          inet6 addr: fe80::76da:daff:fe56:7990/64 Scope:Link
          UP BROADCAST RUNNING ALLMULTI MULTICAST  MTU:1500  Metric:1
          RX packets:60974 multicast:846 unicast:59721 broadcast:407
          RX errors:0 dropped:0 overruns:0 frame:0
          TX packets:59241 multicast:0 unicast:59241 broadcast:0
          TX errors:0 dropped:0 overruns:0 carrier:0 collisions:0
          txqueuelen:0
          RX bytes:3414643 (3.2 MiB) TX bytes:18624039 (17.7 MiB)
          RX multicast bytes:131155 (128.0 KiB) TX multicast bytes:0 (0.0 B)

eth0      Link encap:Ethernet  HWaddr (snipped)
          UP BROADCAST MULTICAST  MTU:1500  Metric:1
          RX packets:0 multicast:0 unicast:0 broadcast:0
          RX errors:0 dropped:0 overruns:0 frame:0
          TX packets:0 multicast:0 unicast:0 broadcast:0
          TX errors:0 dropped:0 overruns:0 carrier:0 collisions:0
          txqueuelen:1000
          RX bytes:0 (0.0 B) TX bytes:0 (0.0 B)
          RX multicast bytes:0 (0.0 B) TX multicast bytes:0 (0.0 B)

eth1      Link encap:Ethernet  HWaddr (snipped)
          UP BROADCAST MULTICAST  MTU:1500  Metric:1
          RX packets:0 multicast:0 unicast:0 broadcast:0
          RX errors:0 dropped:0 overruns:0 frame:0
          TX packets:0 multicast:0 unicast:0 broadcast:0
          TX errors:0 dropped:0 overruns:0 carrier:0 collisions:0
          txqueuelen:1000
          RX bytes:0 (0.0 B) TX bytes:0 (0.0 B)
          RX multicast bytes:0 (0.0 B) TX multicast bytes:0 (0.0 B)
          

eth2      Link encap:Ethernet  HWaddr (snipped)
          UP BROADCAST MULTICAST  MTU:1500  Metric:1
          RX packets:0 multicast:0 unicast:0 broadcast:0
          RX errors:0 dropped:0 overruns:0 frame:0
          TX packets:0 multicast:0 unicast:0 broadcast:0
          TX errors:0 dropped:0 overruns:0 carrier:0 collisions:0
          txqueuelen:1000
          RX bytes:0 (0.0 B) TX bytes:0 (0.0 B)
          RX multicast bytes:0 (0.0 B) TX multicast bytes:0 (0.0 B)
          

eth3      Link encap:Ethernet  HWaddr (snipped)
          inet6 addr: fe80::snipped/64 Scope:Link
          UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
          RX packets:10945919 multicast:855 unicast:10944650 broadcast:414
          RX errors:0 dropped:0 overruns:0 frame:0
          TX packets:20717184 multicast:787 unicast:20716380 broadcast:17
          TX errors:0 dropped:0 overruns:0 carrier:0 collisions:0
          txqueuelen:1000
          RX bytes:2371137334 (2.2 GiB) TX bytes:3309911575 (3.0 GiB)
          RX multicast bytes:0 (0.0 B) TX multicast bytes:0 (0.0 B)
          

eth4      Link encap:Ethernet  HWaddr (snipped)
          UP BROADCAST MULTICAST  MTU:1500  Metric:1
          RX packets:0 multicast:0 unicast:0 broadcast:0
          RX errors:0 dropped:0 overruns:0 frame:0
          TX packets:0 multicast:0 unicast:0 broadcast:0
          TX errors:0 dropped:0 overruns:0 carrier:0 collisions:0
          txqueuelen:1000
          RX bytes:0 (0.0 B) TX bytes:0 (0.0 B)
          RX multicast bytes:0 (0.0 B) TX multicast bytes:0 (0.0 B)
          

lo        Link encap:Local Loopback  
          inet addr:127.0.0.1  Mask:255.0.0.0
          inet6 addr: ::1/128 Scope:Host
          UP LOOPBACK RUNNING  MTU:16436  Metric:1
          RX packets:30060 errors:0 dropped:0 overruns:0 frame:0
          TX packets:30060 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0           txqueuelen:0 
          RX bytes:1683360 (1.6 MiB) TX bytes:1683360 (1.6 MiB)

ptm0      Link encap:Ethernet  HWaddr (snipped)
          inet6 addr: fe80::snipped/64 Scope:Link
          UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
          RX packets:20657945 multicast:10 unicast:20657744 broadcast:191
          RX errors:0 dropped:0 overruns:0 frame:0
          TX packets:11184578 multicast:41 unicast:11184537 broadcast:0
          TX errors:0 dropped:84564 overruns:0 carrier:0 collisions:0
          txqueuelen:1000
          RX bytes:3208414092 (2.9 GiB) TX bytes:2538074010 (2.3 GiB)
          RX multicast bytes:4776 (4.6 KiB) TX multicast bytes:6539 (6.3 KiB)

ptm0.1    Link encap:Ethernet  HWaddr (snipped)
          inet6 addr: fe80::snipped/64 Scope:Link
          UP BROADCAST RUNNING ALLMULTI MULTICAST  MTU:1500  Metric:1
          RX packets:20657946 multicast:0 unicast:20657938 broadcast:8
          RX errors:0 dropped:0 overruns:0 frame:0
          TX packets:10886405 multicast:834 unicast:10885385 broadcast:186
          TX errors:0 dropped:0 overruns:0 carrier:0 collisions:0
          txqueuelen:0
          RX bytes:4250434713 (3.9 GiB) TX bytes:2857102205 (2.6 GiB)
          RX multicast bytes:0 (0.0 B) TX multicast bytes:141429 (138.1 KiB)

```

Note: In this example, `ptm0.1` is the xDSL modem interface. Most of the other interfaces are unused, as the modem is in bridge mode.

</details>

## Configuring

Create a `config.ini` file with contents such as the following:

```
[general]
# debug=False

[mqtt]
uri=mqtt://mqtt_url_here/
# topic_prefix = xdsl2

[xdsl2]
host=192.168.1.1
# user=admin
# password=admin
# connect_timeout=8
# poll_delay=30
```

(Commented lines are optional and show the default values.)

`[general]`

* `debug` can be set to `True` to see a lot of debug-level log output.

`[mqtt]`

* `uri` is the URI of your MQTT broker, as per the [MQTT URI scheme](https://github.com/mqtt/mqtt.org/wiki/URI-Scheme) as [implemented by aMQTT](https://amqtt.readthedocs.io/en/latest/quickstart.html#url-scheme). Username and password for the broker are encoded here.
* `topic_prefix` is optional. MQTT messages are published to `<topic_prefix>/stats` and `<topic_prefix>/interface`.

`[xdsl2]`

* `host` is the IP address or hostname of the modem, used to connect to the telnet interface.
* `username` and `password` are for the telnet login of the modem, default values are `admin:admin`.
* `connect_timeout` is timeout (in seconds) before failing to connect to the modem. Currently the program exits if connection fails, and expects some service host to restart it.
* `poll_delay` is the interval (in seconds) between running the telnet commands to poll status of the modem. The telnet interface remains connected the whole time.

## Installing and running

### Locally

To install and run locally, first get a recent-ish Python install and/or Python virtualenv and then:

```sh
pip install -r requirements.txt
python xdsl2mqtt.py
```

Can optionally pass `python xdsl2mqtt.py -c /path/to/config.ini` if needed.

### Docker

There's a Dockerfile here so if you're container-oriented then you can run something like:

```sh
docker build -t xdsl2mqtt .
docker run -v ./config.ini:/etc/xdsl2mqtt/config.ini xdsl2mqtt-dev
```

## MQTT Output

For as long as the telnet connection to the modem stays up, the script periodically runs two commands and parses the output into JSON objects. Values in the JSON objects only appear if the relevant output is found in the Telnet interface, if you don't see something then either the output format is different or that value is not there.

### Stats

Telnet command `xdslctl info --stats` is run and publishes to MQTT topic `xdsl2/stats` (prefix configurable):

```json
{
  "profile": "Profile 17a",
  "line_status": "No Defect",
  "training_status": "Showtime",
  "last_retrain_reason": "0",
  "last_init_status": "0",
  "snr_db": {
    "down": 7.1,
    "up": 4.9
  },
  "atten_db": {
    "down": 31,
    "up": 0
  },
  "power_dbm": {
    "down": 14.4,
    "up": 6.3
  },
  "max_rate": {
    "down": 34239,
    "up": 5517
  },
  "error_counters": {
    "FEC": {
      "down": 1284284,
      "up": 20226
    },
    "CRC": {
      "down": 0,
      "up": 0
    },
    "ES": {
      "down": 0,
      "up": 0
    },
    "SES": {
      "down": 0,
      "up": 0
    },
    "UAS": {
      "down": 162,
      "up": 162
    },
    "LOS": {
      "down": 0,
      "up": 0
    },
    "LOF": {
      "down": 0,
      "up": 0
    },
    "LOM": {
      "down": 0,
      "up": 0
    }
  },
  "g.inp": {
    "LEFTRS": {
      "down": 0,
      "up": 1196
    },
    "min_EFTR": {
      "down": 31816,
      "up": 5516
    }
  },
  "banner": "BCM963381 Broadband Router"
}}
```

Deciphering this output requires DSL knowledge that I don't really have. Most of what I know is cribbed from [this page](https://kitz.co.uk/adsl/linestats_errors.htm), and [this forum thread](https://forum.kitz.co.uk/index.php?topic=10289.0).

However, the fields (as I understand them) are:

* `profile`: [VDSL Profile](https://en.wikipedia.org/wiki/VDSL#Profiles) in use.
* `line_status`: Is `"No defect"` if the line is happy, something else otherwise.
* `training_status`: Is `"Showtime"` when the line is synced, other values during initialization and line training phases.
* `last_retrain_reason`/`last_init_status`: These are (I think) internal enumerated values in the Broadcam firmware. They obviously stand for something, I don't know what.

The remaining fields all have separate values for upstream and downstream directions:

* `max_rate`: Maximum achievable rate in Kbps, often informally called "sync speed". This is the thing most people care about.
* `snr_db`: Signal to noise ratio of the line (in dB).
* `atten_db`: Signal attenuation (in dB).
* `power_dbm`: Power output in dBm. (I don't know, and someone can maybe explain, how the downstream value is calculated here - does the other end report it?)

The `error_counters` object contains some global (since boot) counters for different types of error events:

* `FEC`: Total Forward Error Correction events, where packet errors existed but were successfully corrected without needing retransmission. (As above, maybe someone can tell me - for upstream does the other end report this number back?)
* `CRC`: Total Cyclic Redundancy Check errors, meaning a packet was corrupt and needed retransmission.
* `ES`: Error Seconds, meaning the total number of seconds during which at least one "error" occurred. Comparing these counters to absolute error counts like `CRC` count can help determine if a large number of errors happened very suddenly in a short total number of seconds, or if errors are happening intermittently over a long period of time.
* `SES`: Severe Error Seconds, meaning the total number of seconds during which a high number of "errors" occurred.
* `UAS`: Unavailable Seconds, meaning the total number of seconds during which the link was unavailable (for example, it was retraining).
* `LOS`: Number of "loss of signal" events, during which the modem totally lost its signal and (probably) had to retrain and reestablish the link.
* `LOF`: Number of "loss of frame" events, during which the modem received an Out of Frame condition that didn't resolve immediately.
* `LOM`: Number of "loss of margin" events, during which the modem lost its acceptable "noise margin" and had to increase transmit power.

The `g.inp` object contains some values relevant to the [G.INP Retranmission](https://kitz.co.uk/adsl/retransmission.htm) xDSL feature, if it is enabled:

* `min_EFTR` - is the Minimum Error-Free Throughput Rate (in Kbps) according to the current line conditions. Expect this will map more closely to real maximum transfer speeds than the `max_rate` value.
* `LEFTRS` - Total number of seconds where at least one "Low EFTR" (LEFTR) defect occurred. I assume this means the EFTR value dipped below some acceptable threshold as configured in the modem, although I don't know exactly how this is calculated.

* `banner` - This is whatever text the modem outputs when you log in via Telnet.

### Network Interface

Telnet command `ifconfig ptm0.1` is run and published to MQTT topic `xdsl2/interface` (prefix configurable):

```json
{
  "up": true,
  "packets": {
    "rx": 20685211,
    "tx": 10908548
  },
  "bytes": {
    "rx": 4276196848,
    "tx": 2861475864
  }
}
```

* `up` is a boolean for whether the IP-level interface is "up".
* `packets` is the number of packets sent and received over the link.
* `bytes` is the number of bytes sent and received over the link.

## Telegraf Configuration

TBD
