# CCEN356 Project — HTTP/HTTPS Performance & Visibility

Compare HTTP vs HTTPS performance using physical Cisco networking equipment, Python automation, Wireshark analysis, and data visualization.

## Team

- 2 members
- Spring 2026

## Network Topology

```
[Client 1: 192.168.1.10] ──┐
[Client 2: 192.168.1.11] ──┤── [SW1 (2960)] ── [R1 (2901)] ── [R2 (2901)] ── [Server: 192.168.2.10]
[Monitor:  192.168.1.20] ──┘       │
                              (SPAN to Gi0/10)
```

## Setup

### 1. Install Python dependencies (on client PCs)

```bash
pip install -r requirements.txt
```

### 2. Generate SSL certificates (on server PC)

```bash
cd server/
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout key.pem -out cert.pem \
  -subj "/CN=192.168.2.10/O=CCEN356Lab"
```

### 3. Start servers (on server PC — 192.168.2.10)

```bash
# Terminal 1: HTTP server
sudo python3 server/http_server.py

# Terminal 2: HTTPS server
python3 server/secured_server.py

# Also ensure Apache is running for ports 80/443
sudo systemctl start apache2
```

### 4. Verify connectivity (from client PCs)

```bash
ping 192.168.2.10
curl http://192.168.2.10
curl -k https://192.168.2.10
```

## Running the Scripts

Execute from client PCs in order:

```bash
# 1. SSH to router and collect show commands
python3 scripts/ssh_connect.py

# 2. Capture traffic (requires sudo, run on Client 1)
sudo python3 scripts/capture_traffic.py

# 3. Performance benchmark (run on Client 2 while capture is active)
python3 scripts/performance_metrics.py

# 4. Generate charts (after capture completes)
python3 scripts/visualize_traffic.py

# 5. Live dashboard
python3 scripts/dashboard.py
# Then visit http://localhost:5000
```

## Project Structure

```
├── scripts/
│   ├── ssh_connect.py            # Netmiko SSH to routers
│   ├── capture_traffic.py        # Scapy packet capture
│   ├── performance_metrics.py    # HTTP vs HTTPS benchmarking
│   ├── visualize_traffic.py      # Matplotlib charts
│   └── dashboard.py              # Flask live dashboard
├── server/
│   ├── http_server.py            # Flask HTTP (port 80)
│   ├── secured_server.py         # Flask HTTPS (port 8443)
│   └── templates/
│       ├── index.html
│       └── show.html
├── configs/                      # Router config exports
├── data/                         # Generated CSV data
├── charts/                       # Generated PNG charts
├── requirements.txt
├── REFERENCE_PROMPT.md           # Full project reference
└── project_description.md        # Original project guide
```

## Outputs

| File | Source |
|---|---|
| `data/traffic_log.csv` | `capture_traffic.py` |
| `data/performance_results.csv` | `performance_metrics.py` |
| `charts/performance_comparison.png` | `visualize_traffic.py` |
| `charts/traffic_analysis.png` | `visualize_traffic.py` |
| `configs/R1_config.txt` | `show running-config` from R1 |
| `configs/R2_config.txt` | `show running-config` from R2 |
