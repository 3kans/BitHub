import hashlib
import os
import requests
import time
import locale
import sys
from datetime import datetime
import yfinance as yf
from mnemonic import Mnemonic

# Display titles for the combined program
def display_titles():
    print("\n------------------------------------------------")
    print("         \033[1m##### Welcome to BitHub #####\033[0m\n")
    print("                \033[1mv1.0 - by snak3 \033[0m")
    print("------------------------------------------------\n")
    print("*Press Ctrl+C at any time to exit the program.")

def generate_sha256_hash(input_string):
    """Generates a SHA-256 hash from an input string."""
    return hashlib.sha256(input_string.encode()).hexdigest()

def validate_hash(hash_string):
    """Validates that the provided hash is 64 characters long."""
    return len(hash_string) == 64

def generate_seed_from_hash(hash_string, language="english", words=12):
    """Generates a BIP39 seed from a provided SHA-256 hash with the specified number of words."""
    mnemo = Mnemonic(language)
    entropy_length = 128 if words == 12 else 256  # 128 bits for 12 words, 256 bits for 24 words
    entropy = hash_string[:entropy_length // 4]  # Convert bits to hexadecimal characters
    return mnemo.to_mnemonic(bytes.fromhex(entropy))

def format_seed(seed_phrase, enumerate_words=False, words_per_line=12):
    """Formats the seed with or without enumeration, one word per line."""
    seed_words = seed_phrase.split()
    if enumerate_words:
        formatted_seed = "\n".join([f"{i + 1}. {word}" for i, word in enumerate(seed_words)])
    else:
        formatted_seed = "\n".join(seed_words)
    return formatted_seed

def get_exchange_rates():
    """
    Fetches the current Bitcoin exchange rate in BRL and USD, the BRL to USD exchange rate,
    the Bovespa index (IBOV), the S&P 500, and Nasdaq in real-time.
    """
    url_btc_brl = "https://www.mercadobitcoin.net/api/BTC/ticker/"
    url_btc_usd = "https://api.coindesk.com/v1/bpi/currentprice.json"
    url_usd_brl = "https://economia.awesomeapi.com.br/json/last/USD-BRL"

    try:
        # Requesting data from Bitcoin and USD APIs
        response_btc_brl = requests.get(url_btc_brl)
        response_btc_usd = requests.get(url_btc_usd)
        response_usd_brl = requests.get(url_usd_brl)

        data_btc_brl = response_btc_brl.json()
        data_btc_usd = response_btc_usd.json()
        data_usd_brl = response_usd_brl.json()

        last_btc_brl = float(data_btc_brl["ticker"]["last"])
        last_btc_usd = float(data_btc_usd["bpi"]["USD"]["rate_float"])
        last_usd_brl = float(data_usd_brl["USDBRL"]["bid"])

        # Fetching the IBOV index using Yahoo Finance
        ibov = yf.Ticker("^BVSP")
        last_ibov = ibov.history(period="1d")["Close"].iloc[-1]

        # Fetching the S&P 500 index
        sp500 = yf.Ticker("^GSPC")
        last_sp500 = sp500.history(period="1d")["Close"].iloc[-1]

        # Fetching the Nasdaq index
        nasdaq = yf.Ticker("^IXIC")
        last_nasdaq = nasdaq.history(period="1d")["Close"].iloc[-1]

        return last_btc_brl, last_btc_usd, last_usd_brl, last_ibov, last_sp500, last_nasdaq

    except Exception as e:
        print(f"Error fetching data: {e}")
        return None, None, None, None, None, None

def seed_program():
    """Handles the seed generation functionality."""
    try:
        while True:
            # Step 1: Get input method (hash, string, or file)
            choice = input("\n1) Provide a SHA-256 HASH, a STRING, or a TEXT FILE to generate the hash?\n(Press Enter for 'string', or type 'hash' or type 'file'[.txt]): ").strip().lower()

            if choice == "string" or choice == "":
                while True:
                    input_string = input("\n2) Enter the string to generate the SHA-256 hash: ").strip()
                    if input_string:
                        hash_poem = generate_sha256_hash(input_string)
                        print(f"\n\033[1m=> Generated SHA-256 hash: {hash_poem}\033[0m\n")
                        break
                    else:
                        print("**Error: You must provide a non-empty string.")
            elif choice == "hash":
                while True:
                    hash_poem = input("2) Enter the SHA-256 hash of your poem (64 characters): ").strip()
                    if validate_hash(hash_poem):
                        break
                    else:
                        print("**Error: The provided hash must be exactly 64 characters long. Please enter a valid SHA-256 hash.")
            elif choice == "file":
                while True:
                    file_path = input("2) Enter the path to the text file (.txt): ").strip()
                    if os.path.isfile(file_path) and file_path.endswith(".txt"):
                        with open(file_path, "r", encoding="utf-8") as file:
                            input_string = file.read().strip()
                            hash_poem = generate_sha256_hash(input_string)
                            print(f"\n\033[1m=> Generated SHA-256 hash from file: {hash_poem}\033[0m\n")
                        break
                    else:
                        print("**Error: Invalid file path or file format. Please enter a valid .txt file path.")
            else:
                print("**Error: Invalid choice. Please type 'string', 'hash', or 'file'.")
                continue

            # Step 2: Get the desired language
            valid_languages = ["english", "japanese", "korean", "spanish", "chinese", "french", "italian", "czech", "portuguese"]
            while True:
                language = input("3) Enter the desired language for the seed\n(Press Enter for 'english' or type japanese, korean, spanish, chinese, french, italian, czech or portuguese): ").strip().lower()
                if language == "":
                    language = "english"  # Default language
                    print("")
                if language in valid_languages:
                    break
                else:
                    print("**Error: Invalid language. Please enter a valid language from the list.\n")

            # Step 3: Choose the number of words for the seed (12 or 24)
            while True:
                try:
                    num_words = int(input("\033[1m4) How many words would you like for the seed? (12 or 24): \033[0m").strip())
                    if num_words in [12, 24]:
                        break
                    else:
                        print("**Error: Please enter '12' or '24'.")
                except ValueError:
                    print("**Error: Please enter a valid number (12 or 24).\n")

            # Generate and format the seed
            seed_phrase = generate_seed_from_hash(hash_poem, language, num_words)
            formatted_seed = format_seed(seed_phrase, enumerate_words=True)

            # Display the formatted BIP39 seed
            print("\n\033[1m=> Formatted BIP39 poetic seed:\033[0m\n", formatted_seed, "\n")

            # Step 4: Ask the user if they want to save the seed to a file
            save_option = input("Would you like to save the seed to a file? (y/n): ").strip().lower()
            if save_option == "y" or save_option == "yes":
                try:
                    # Use the user's Documents directory
                    documents_path = os.path.join(os.path.expanduser("~"), "Documents")
                    file_path = os.path.join(documents_path, "seed_bip39.txt")
                    # Save the seed without enumeration
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(format_seed(seed_phrase, enumerate_words=False))
                    print(f"\033[1m*Seed successfully saved to '{file_path}'\n\033[0m")
                except Exception as e:
                    print(f"**Error: Failed to save the seed to a file.\n {str(e)}")
            else:
                print("\033[1m*Seed not saved.\n\033[0m")
            
            # Step 5: Ask the user if they want to generate another seed
            another = input("Would you like to generate another seed? (y/n): ").strip().lower()
            if another != "y" and another != "yes":
                print("\nExiting the seed generation program...\n")
                break

    except KeyboardInterrupt:
        print("\n\nExiting the seed generation program...\n")

def quotation_program():
    """Handles the real-time quotations functionality."""
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

    try:
        while True:
            price_btc_brl, price_btc_usd, price_usd_brl, price_ibov, price_sp500, price_nasdaq = get_exchange_rates()

            if price_btc_brl is not None and price_btc_usd is not None and price_usd_brl is not None and price_ibov is not None and price_sp500 is not None and price_nasdaq is not None:
                # Formatting values according to the US standard
                price_btc_brl_formatted = locale.format_string('%.2f', price_btc_brl, grouping=True)
                price_btc_usd_formatted = locale.format_string('%.2f', price_btc_usd, grouping=True)
                price_usd_brl_formatted = locale.format_string('%.2f', price_usd_brl, grouping=True)
                price_ibov_formatted = locale.format_string('%.0f', price_ibov, grouping=True)
                price_sp500_formatted = locale.format_string('%.0f', price_sp500, grouping=True)
                price_nasdaq_formatted = locale.format_string('%.0f', price_nasdaq, grouping=True)

                # Getting the current time
                current_time = datetime.now().strftime("%H:%M:%S")

                print(f"\n[{current_time}]")
                print(f"Bitcoin price: BRL {price_btc_brl_formatted} | USD {price_btc_usd_formatted}")
                print(f"BRL to USD exchange rate: BRL 1.00 = USD {price_usd_brl_formatted}")
                print(f"Bovespa index (IBOV): {price_ibov_formatted} points")
                print(f"S&P 500: {price_sp500_formatted} points")
                print(f"Nasdaq: {price_nasdaq_formatted} points")
                print(f"--------------------------------------------------")

            time.sleep(15)  # Updates every 15 seconds

    except KeyboardInterrupt:
        print("\nExiting the real-time quotations program...\n")

def main():
    display_titles()

    try:
        while True:
            print("\n\033[1m1. Seed Phrase Generator\033[0m")
            print("\033[1m2. Real-time Quotation\033[0m")
            choice = input("\nChoose an option (1 or 2): ").strip()
            
            if choice == "1":
                print("\n\033[1m*Seed Phrase Generator\033[0m")
                seed_program()
            elif choice == "2":
                print("\n\033[1m*Real-time Quotation\033[0m")
                quotation_program()
            else:
                print("**Error: Invalid choice. Please enter '1' or '2'.")
                continue

            # Ask the user if they want to return to the main menu
            another = input("Would you like to return to the main menu? (y/n): ").strip().lower()
            if another != "y" and another != "yes":
                print("\nExiting the program...\n")
                break

    except KeyboardInterrupt:
        print("\n\nExiting the program...\n")

if __name__ == "__main__":
    main()
