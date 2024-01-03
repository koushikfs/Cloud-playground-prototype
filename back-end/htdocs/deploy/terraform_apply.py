import subprocess
import time
from datetime import datetime
import sys

def run_terraform_apply(log_file_path,timeout=420):
    with open(log_file_path, 'a') as log_file:
        def log_entry(message):
            timestamp = datetime.now().strftime("%d %b %Y / %I:%M %p")
            log_file.write(f"{timestamp}:            {message}\n")

        start_time = time.time()
        process = subprocess.Popen(['terraform', 'apply', '-auto-approve'],
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                    text=True, bufsize=1)
        count = 0

        while True:
            output_line = process.stdout.readline()
            current_time = time.time()
            elapsed_time = current_time - start_time

            if elapsed_time > timeout:
                process.kill()
                log_entry("[-] Terraform apply timeout.\n")
                log_entry("[-] Unable to deploy, no response from servers .. check your internet\n")
                break

            elif "Error" in output_line:
                log_entry("[-] Something went wrong\n")
                log_entry("[-] Try running manually for debugging\n")
                break

            elif "Apply complete!" in output_line:
                log_entry("[+] Terraform apply completed successfully.")
                log_entry("[+] Your infrastructure Design Got Deployed <3 <3 <3\n")
                break

        
        
    return True

if __name__ == "__main__":
    log_file_path = 'D:/xampp/htdocs/status.log'
    run_terraform_apply(log_file_path)