"""Script 1 - SSH Connection & Device Info via Netmiko.

Connects to a Cisco router via SSH, runs show commands, and prints output.
Run from a client PC:
    python scripts/ssh_connect.py --host 192.165.10.37
"""

import argparse
import socket
import sys

from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoAuthenticationException, NetmikoTimeoutException


def _check_tcp_port(host, port, timeout=2):
    """Return (is_open, details) for a TCP socket check."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True, f"TCP {port} is reachable on {host}."
    except OSError as exc:
        return False, str(exc)


def _router_ssh_fix_hint():
    """Provide concise Cisco IOS commands to enable SSH on the router."""
    return (
        "Possible router-side fix (R1):\n"
        "  conf t\n"
        "  ip domain-name lab.local\n"
        "  crypto key generate rsa modulus 2048\n"
        "  ip ssh version 2\n"
        "  username admin privilege 15 secret admin123\n"
        "  line vty 0 4\n"
        "  transport input ssh\n"
        "  login local\n"
        "  end\n"
        "  write memory"
    )


def connect_to_device(host, username='admin', password='admin123', port=22, timeout=8):
    """Connect to a Cisco IOS device and collect show command outputs."""
    is_open, tcp_msg = _check_tcp_port(host, port)
    if not is_open:
        raise ConnectionError(
            f"Cannot reach {host}:{port}. Socket check failed: {tcp_msg}\n"
            f"Verify client-to-router connectivity (ping {host}), ACL/firewall rules, and SSH config.\n"
            f"{_router_ssh_fix_hint()}"
        )

    device = {
        'device_type': 'cisco_ios',
        'host': host,
        'port': port,
        'username': username,
        'password': password,
        'secret': password,
        'conn_timeout': timeout,
        'timeout': timeout,
    }

    print(f"Connecting to {host}:{port}...")
    try:
        connection = ConnectHandler(**device)
        connection.enable()
    except NetmikoAuthenticationException as exc:
        raise ConnectionError(
            f"Authentication failed for {username}@{host}:{port}. "
            "Verify router username/password/enable secret."
        ) from exc
    except NetmikoTimeoutException as exc:
        raise ConnectionError(
            f"Timed out connecting to {host}:{port}. "
            "Host may be reachable but SSH service is not accepting sessions.\n"
            f"{_router_ssh_fix_hint()}"
        ) from exc

    print(f"Connected to {host} - privileged exec mode.\n")

    commands = [
        'show ip interface brief',
        'show ip route',
        'show access-lists',
        'show policy-map interface GigabitEthernet0/0',
    ]

    results = {}
    for cmd in commands:
        output = connection.send_command(cmd)
        results[cmd] = output
        print(f"--- {cmd} ---")
        print(output)
        print()

    connection.disconnect()
    print(f"Disconnected from {host}.")
    return results


def _parse_args():
    parser = argparse.ArgumentParser(description='Connect to Cisco IOS over SSH and run show commands.')
    parser.add_argument('--host', default='192.165.10.37', help='Router IP address (default: 192.165.10.37)')
    parser.add_argument('--port', type=int, default=22, help='SSH TCP port (default: 22)')
    parser.add_argument('--username', default='admin', help='SSH username (default: admin)')
    parser.add_argument('--password', default='admin123', help='SSH password (default: admin123)')
    parser.add_argument('--timeout', type=int, default=8, help='Connection timeout in seconds (default: 8)')
    return parser.parse_args()


if __name__ == '__main__':
    args = _parse_args()
    try:
        connect_to_device(
            host=args.host,
            username=args.username,
            password=args.password,
            port=args.port,
            timeout=args.timeout,
        )
    except Exception as exc:  # Keep CLI output simple for lab usage.
        print(f"ERROR: {exc}")
        sys.exit(1)
