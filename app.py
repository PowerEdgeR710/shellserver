import paramiko
import sys
import os
import termios
import tty
import select
import requests

VPS_API_BASE = "https://vps-api.5136.cloud"
VPS_TOKEN = os.getenv("TOKEN")  # set this in Pterodactyl env lmao

def get_ssh_info():
    headers = {"Authorization": VPS_TOKEN}
    resp = requests.get(f"{VPS_API_BASE}/manage/sshinfo", headers=headers)
    resp.raise_for_status()
    return resp.json()

def interactive_shell(chan):
    old_tty = termios.tcgetattr(sys.stdin)
    try:
        tty.setraw(sys.stdin.fileno())
        chan.settimeout(0.0)

        while True:
            r, w, e = select.select([chan, sys.stdin], [], [])
            if chan in r:
                try:
                    x = chan.recv(1024)
                    if len(x) == 0:
                        print("\nConnection closed by remote host.")
                        break
                    sys.stdout.write(x.decode())
                    sys.stdout.flush()
                except Exception:
                    break
            if sys.stdin in r:
                x = os.read(sys.stdin.fileno(), 1024)
                if len(x) == 0:
                    break
                chan.send(x)
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_tty)

def main():
    ssh_info = get_ssh_info()
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(
            hostname=ssh_info['ssh_command'].split('@')[-1].split(' ')[0],
            port=ssh_info.get('port', 22),
            username=ssh_info['username'],
            password=ssh_info['password'],
        )
    except Exception as e:
        print("SSH connection failed:", e)
        sys.exit(1)
    chan = client.invoke_shell()
    print("Successfully connected to this VPS(s) shell.")
    interactive_shell(chan)
    chan.close()
    client.close()

if __name__ == "__main__":
    main()
