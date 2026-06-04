import tiktoken
import json
from rapidfuzz import process, fuzz
import logging



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
    text = input("Enter the text to analyze: ").strip()
    if not text:
        print("Error: Text cannot be empty.")
        return
    
    try:
        tokens, token_count = count_tokens(text, model, pricings)
        cost = calculate_cost(model, token_count, pricings) 
    except ValueError as e:
        print(f"Error: {e}")
        return
    print("\n--- Results ---")
    print(f"Tokens: {tokens}")
    print(f"Token count: {token_count}")
    print(f"Estimated cost: ${cost:.6f}")

if __name__ == "__main__":
    main()

