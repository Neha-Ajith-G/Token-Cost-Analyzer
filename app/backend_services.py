import json
import logging
import tiktoken
import re


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



