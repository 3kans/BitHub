import hashlib
import os
import locale
import math
from datetime import datetime
import asyncio
import aiohttp

def import_conditional_modules():
    from mnemonic import Mnemonic
    return Mnemonic

def display_titles():
    print("\n------------------------------------------------")
    print("         \033[1m##### Welcome to BitHub #####\033[0m\n")
    print("                \033[1mv1.0 - by snak3 \033[0m")
    print("------------------------------------------------\n")
    print("*Press Ctrl+C at any time to exit the program.")

def generate_sha256_hash(input_string):
    return hashlib.sha256(input_string.encode()).hexdigest()

def validate_hash(hash_string):
    return len(hash_string) == 64

def calculate_entropy(input_string):
    probability_distribution = {char: input_string.count(char) / len(input_string) for char in set(input_string)}
    entropy = -sum(prob * math.log2(prob) for prob in probability_distribution.values())
    return entropy

def grade_entropy(entropy_value):
    if entropy_value < 3.0:
        return "Low"
    elif 3.0 <= entropy_value < 4.0:
        return "Medium"
    else:
        return "High"

def generate_seed_from_hash(hash_string, language="english", words=12):
    Mnemonic = import_conditional_modules()
    mnemo = Mnemonic(language)
    entropy_length = 128 if words == 12 else 256
    entropy = hash_string[:entropy_length // 4]
    return mnemo.to_mnemonic(bytes.fromhex(entropy))

def format_seed(seed_phrase, enumerate_words=False):
    seed_words = seed_phrase.split()
    if enumerate_words:
        formatted_seed = "\n".join([f"{i + 1}. {word}" for i, word in enumerate(seed_words)])
    else:
        formatted_seed = "\n".join(seed_words)
    return formatted_seed

def seed_program():
    try:
        while True:
            hash_poem = None  
            choice = input("\n1) Provide a SHA-256 HASH, a STRING or a TEXT FILE to generate the hash?\n(Press Enter for 'string', or type 'hash' or type 'file'[.txt]): ").strip().lower()
            
            if choice == "string" or choice == "":
                input_string = input("\n2) Enter the string to generate the SHA-256 hash: ").strip()
                if input_string:
                    hash_poem = generate_sha256_hash(input_string)
                    entropy = calculate_entropy(input_string)
                    entropy_grade = grade_entropy(entropy)
                    print(f"\n\033[1m=> Generated SHA-256 hash: {hash_poem}\033[0m")
                    print(f"\n\033[1m=> Entropy of input: {entropy:.2f} ({entropy_grade})\033[0m\n")
                else:
                    print("**Error: You must provide a non-empty string.")
            elif choice == "hash":
                hash_input = input("2) Enter the SHA-256 hash of your poem (64 characters): ").strip()
                if validate_hash(hash_input):
                    hash_poem = hash_input
                    entropy = calculate_entropy(hash_poem)
                    entropy_grade = grade_entropy(entropy)
                    print(f"\n\033[1m=> Entropy of hash: {entropy:.2f} ({entropy_grade})\033[0m\n")
                else:
                    print("**Error: The provided hash must be exactly 64 characters long. Please enter a valid SHA-256 hash.")
            elif choice == "file":
                file_path = input("\n2) Enter the path to the text file (.txt): ").strip()
                if os.path.isfile(file_path) and file_path.endswith(".txt"):
                    with open(file_path, "r", encoding="utf-8") as file:
                        input_string = file.read().strip()
                        hash_poem = generate_sha256_hash(input_string)
                        entropy = calculate_entropy(input_string)
                        entropy_grade = grade_entropy(entropy)
                        print(f"\n\033[1m=> Generated SHA-256 hash from file: {hash_poem}\033[0m")
                        print(f"\n\033[1m=> Entropy of text / Hash: {entropy:.2f} ({entropy_grade})\033[0m\n")
                else:
                    print("**Error: Invalid file path or file format. Please enter a valid .txt file path.")
            else:
                print("**Error: Invalid choice. Please type 'string', 'hash', or 'file'.")
                continue

            if hash_poem is None:
                print("*Hash not generated. Please try again.")
                continue

            valid_languages = ["english", "japanese", "korean", "spanish", "chinese", "french", "italian", "czech", "portuguese"]
            language = input("3) Enter the desired language for the seed\n(Press Enter for 'english' or type japanese, korean, spanish, chinese, french, italian, czech or portuguese): ").strip().lower()
            if language == "":
                language = "english"
            if language not in valid_languages:
                print("**Error: Invalid language. Please enter a valid language from the list.\n")
                continue

            while True:
                try:
                    num_words = int(input("\n\033[1m4) How many words would you like for the seed? (12 or 24): \033[0m").strip())
                    if num_words in [12, 24]:
                        break
                    else:
                        print("**Error: Please enter a valid number (12 or 24).")
                except ValueError:
                    print("**Error: Please enter a valid number (12 ou 24).")
            
            seed_phrase = generate_seed_from_hash(hash_poem, language, num_words)
            formatted_seed = format_seed(seed_phrase, enumerate_words=True)

            print("\n\033[1m------ BACKUP Bitcoin Seed Phrase! ------\033[0m")
            print("\033[1m------ BACKUP Bitcoin Seed Phrase! ------\033[0m\n")
            print(formatted_seed, "\n")

            save_option = input("Would you like to save the seed to a file? (y/n): ").strip().lower()
            if save_option in ["y", "yes"]:
                try:
                    documents_path = os.path.join(os.path.expanduser("~"), "Documents")
                    file_path = os.path.join(documents_path, "seed_bip39.txt")
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(format_seed(seed_phrase, enumerate_words=False))
                    print(f"\033[1m*Seed successfully saved to '{file_path}'\n\033[0m")
                except Exception as e:
                    print(f"**Error: Failed to save the seed to a file.\n {str(e)}")
            else:
                print("\033[1m*Seed not saved.\n\033[0m")
            
            another = input("Would you like to generate another seed? (y/n): ").strip().lower()
            if another not in ["y", "yes"]:
                print("\nExiting the seed generation program...\n")
                break

    except KeyboardInterrupt:
        print("\n\nExiting the seed generation program...\n")

async def fetch_data(session, url):
    try:
        async with session.get(url) as response:
            return await response.json()
    except Exception as e:
        print(f"Error fetching data from {url}: {e}")
        return None

async def get_exchange_rates_async():
    url_btc_brl = "https://www.mercadobitcoin.net/api/BTC/ticker/"
    url_btc_usd = "https://api.coindesk.com/v1/bpi/currentprice.json"
    url_usd_brl = "https://economia.awesomeapi.com.br/json/last/USD-BRL"

    async with aiohttp.ClientSession() as session:
        tasks = [
            fetch_data(session, url_btc_brl),
            fetch_data(session, url_btc_usd),
            fetch_data(session, url_usd_brl),
        ]
        results = await asyncio.gather(*tasks)

    if any(result is None for result in results):
        return None, None, None, None, None, None
    
    data_btc_brl, data_btc_usd, data_usd_brl = results

    last_btc_brl = float(data_btc_brl["ticker"]["last"])
    last_btc_usd = float(data_btc_usd["bpi"]["USD"]["rate_float"])
    last_usd_brl = float(data_usd_brl["USDBRL"]["bid"])

    from yfinance import Ticker
    ibov = Ticker("^BVSP")
    sp500 = Ticker("^GSPC")
    nasdaq = Ticker("^IXIC")

    last_ibov = ibov.history(period="1d")["Close"].iloc[-1]
    last_sp500 = sp500.history(period="1d")["Close"].iloc[-1]
    last_nasdaq = nasdaq.history(period="1d")["Close"].iloc[-1]

    return last_btc_brl, last_btc_usd, last_usd_brl, last_ibov, last_sp500, last_nasdaq

async def quotation_program_async():
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    try:
        while True:
            rates = await get_exchange_rates_async()
            if rates:
                price_btc_brl, price_btc_usd, price_usd_brl, price_ibov, price_sp500, price_nasdaq = rates

                current_time = datetime.now().strftime("%H:%M:%S")
                print(f"\n[{current_time}]")
                print(f"Bitcoin price: BRL {price_btc_brl:.2f} | USD {price_btc_usd:.2f}")
                print(f"BRL to USD exchange rate: BRL 1.00 = USD {price_usd_brl:.2f}")
                print(f"Bovespa index (IBOV): {price_ibov:.0f} points")
                print(f"S&P 500: {price_sp500:.0f} points")
                print(f"Nasdaq: {price_nasdaq:.0f} points")
                print(f"--------------------------------------------------")

            await asyncio.sleep(15)  # Atualiza a cada 15 segundos
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
                asyncio.run(quotation_program_async())
            else:
                print("**Error: Invalid choice. Please enter '1' or '2'.")
                continue

            another = input("Would you like to return to the main menu? (y/n): ").strip().lower()
            if another not in ["y", "yes"]:
                print("\nExiting the program...\n")
                break

    except KeyboardInterrupt:
        print("\n\nExiting the program...\n")

if __name__ == "__main__":
    main()
