print("\033[H\033[J", end="")
print("")
print("Console has been started, please wait.")
print("")
print("")
print("")
print("")
print("Process:")
import sys
import subprocess
import importlib

# ensure stuff is installed using pip3
def ensure_package(pkg):
    try:
        return importlib.import_module(pkg)
    except ImportError:
        print(f"{pkg} not found | installing via pip3...")
        subprocess.check_call(["pip3", "install", pkg])
        return importlib.import_module(pkg)

paramiko = ensure_package("paramiko")
requests = ensure_package("requests")

import os
import termios
import tty
import select

VPS_API_BASE = "https://vps-api.5136.cloud"
VPS_TOKEN = os.getenv("TOKEN")

def call_start():
    print("1 - Starting VPS.")
    headers = {"Authorization": VPS_TOKEN}
    try:
        requests.post(f"{VPS_API_BASE}/manage/start", headers=headers)
    except:
        pass

def get_ssh_info():
    print("2 - Getting SSH Info")
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
    call_start()
    ssh_info = get_ssh_info()
    print("3 - Getting into the server")
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
    print("\033[H\033[J", end="")
    print("")
    print("")
    print("Successfully connected to this server's shell.")
    print("")
    print("")
    print("")
    print("")
    print("To use SSHX instead of this panel, run this command:")
    print("curl -sSf https://sshx.io/get | sh")
    print("")
    print("")
    print("")
    print("")
    print("Also, stopping the server will also stop SSHX If running!")
    print("Please don't use kill unless It's really hung. If it hung but you were in micro, try using 'poweroff -f'.")
    print("")
    print("")
    print("")
    print("")
    print("Have fun with your VPS on 5136.cloud.\n")
    print("/ # ")
    interactive_shell(chan)

if __name__ == "__main__":
    main()
