import tiktoken
import json
from rapidfuzz import process, fuzz
import logging
import re
import sys


logger = logging.getLogger(__name__)
#GLOBAL VARIABLES
PRICING_DATA_PATH = "pricings.json"
FALLBACK_ENCODING= tiktoken.get_encoding("cl100k_base")

def load_pricings(path: str = PRICING_DATA_PATH) -> dict:
    try:
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error("Pricing configuration file not found at path: '%s'", path)
        raise FileNotFoundError(f"Pricing file not found: '{path}'")
    except json.JSONDecodeError as e:
        logger.error("Invalid JSON format in pricing file: %s", e)
        raise ValueError(f"Invalid JSON format in pricing file: {e}")

def get_models(pricings: dict) -> list[str]:
    return list(pricings.keys()) 
    
def validate_model(model: str, pricings: dict) -> None:
    if model not in pricings:
        available = ", ".join(pricings.keys())
        raise ValueError(
            f"Model '{model}' not found. Available models: {available}"
        )
    
def get_encoding_for_model(model: str, pricings: dict) -> tiktoken.Encoding:
    validate_model(model,pricings)
    try:
        logger.info("Loaded tiktoken encoding for model '%s'.", model)
        return tiktoken.encoding_for_model(model)
    except KeyError:
        logger.warning("No tiktoken encoding for model '%s'. Using fallback 'cl100k_base'.", model)
        return FALLBACK_ENCODING #cl100k_base

def count_tokens(text: str, model: str, pricings: dict) -> tuple [list[int], int]:
    enc = get_encoding_for_model(model, pricings)
    tokens = enc.encode(text)
    return tokens, len(tokens)

def calculate_cost(model: str, token_count: int, pricings: dict) -> float:
    model_pricing = pricings[model]
    if "input" not in model_pricing:
        raise ValueError(
            f"Configuration Error: Missing 'input' token price for model '{model}'."
        )#Only taking input cost for now. cost per million tokens
    return token_count * model_pricing["input"] / 1000000

def get_closest_model_name(userinput: str, pricings: dict) -> str | None:
    available_models = get_models(pricings)
    result = process.extractOne(
        userinput,
        available_models,
        scorer=fuzz.WRatio,
        score_cutoff=65,
    )
    return result[0] if result else None 

def compress_text(text: str) -> str:
    
    #CONTEXT TRIMMING 
    # Strip signatures
    sig_markers = ['best regards', 'kind regards', 'thanks,', 'thank you,', 'cheers,']
    lines = text.splitlines()
    core_lines = []
    for line in lines:
        if any(line.lower().strip().startswith(m) for m in sig_markers):
            break
        core_lines.append(line)
    text = '\n'.join(core_lines).strip()

    #RULE-BASED COMPRESSION
    # Normalise whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    # Remove filler phrases
    fillers = [
        r'\bplease note that\b',
        r'\bPlease\b',
        r'\bThank You\b',
        r'\bit is worth mentioning that\b',
        r'\bas you can see\b',
        r'\bI wanted to let you know that\b',
        r'\bjust to let you know\b',
        r'\bhope you are doing well\b',
        r'\bI am writing to\b',
        r'\bI would like to\b',
        r'\bkind regards\b',
        r'\bbest regards\b',
    ]
    for filler in fillers:
        text = re.sub(filler, '', text, flags=re.IGNORECASE)

    # Collapse repeated punctuation
    text = re.sub(r'[!]{2,}', '!', text)
    text = re.sub(r'[.]{2,}', '...', text)

    # Number formatting
    number_words = {
        'zero':'0', 'one':'1', 'two':'2', 'three':'3', 'four':'4',
        'five':'5', 'six':'6', 'seven':'7', 'eight':'8', 'nine':'9',
        'ten':'10', 'eleven':'11', 'twelve':'12', 'thirteen':'13',
        'fourteen':'14', 'fifteen':'15', 'sixteen':'16',
        'seventeen':'17', 'eighteen':'18', 'nineteen':'19',
        'twenty':'20', 'thirty':'30', 'forty':'40', 'fifty':'50',
        'sixty':'60', 'seventy':'70', 'eighty':'80', 'ninety':'90',
        'hundred':'100', 'thousand':'1000', 'million':'1000000',
    }
    for word, digit in number_words.items():
        text = re.sub(rf'\b{word}\b', digit, text, flags=re.IGNORECASE)

    text = re.sub(r'\s+', ' ', text).strip()

    return text

def get_multiline_input() -> str:
    print("Enter text (Ctrl+D to finish, Ctrl+Z on Windows):")
    return sys.stdin.read().strip()

def main():

    logging.basicConfig(
        level=logging.WARNING,
        format="%(levelname)s [%(name)s]: %(message)s",
    ) 
    pricings = load_pricings()
    models = get_models(pricings)

    print("Available models:")
    for i,model in enumerate(models, 1):
        print(f"{i}. {model}")

#MATCH USERINPUT
    model_prompt= input("Enter the model: ").lower().strip()
    if not model_prompt:
        print("Error: Model cannot be empty.")
        return
    model = model_prompt
    if model_prompt not in models:
        closest_model = get_closest_model_name(model_prompt, pricings)
        if closest_model:
            confirm = (input(f"Model '{model_prompt}' not found. Did you mean '{closest_model}'? (y/n): ").lower().strip())            
            if confirm == 'y':
                model = closest_model
            else:
                print("Exiting.")
                return
        else:
            print(f"Model '{model_prompt}' not found and no close matches available. Exiting.")
            return

    
#TEXT  
    text = get_multiline_input()
    if not text:
        print("Error: Text cannot be empty.")
        return
    compressed = compress_text(text)
    try:
        tokens, token_count = count_tokens(text, model, pricings)
        compressed_tokens, compressed_token_count = count_tokens(compressed, model, pricings)
        original_cost = calculate_cost(model, token_count, pricings) 
        compressed_cost = calculate_cost(model, compressed_token_count, pricings)
    except ValueError as e:
        print(f"Error: {e}")
        return
    
    print("\n--- Results ---")
    print(f"\nOriginal text:")
    # print(f"Tokens: {tokens}")
    print(f"Token count: {token_count}")
    print(f"Estimated cost: ${original_cost:.6f}")
    print("\nCompressed text:")
    # print(f"Tokens: {compressed_tokens}")
    print(f"Token count: {compressed_token_count}")
    print(f"Estimated cost: ${compressed_cost:.6f}")
    print("\nSavings:")
    print(f"Tokens saved: {token_count - compressed_token_count}  ({(1 - compressed_token_count/token_count)*100:.1f}%)")
    print(f"Cost saved: ${original_cost - compressed_cost:.6f}")

if __name__ == "__main__":
    main()

