import tiktoken
import json

pricing_data_path = "pricings.json"
def load_pricings(path: str = pricing_data_path) -> dict:
    try:
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Pricing file not found: '{path}'")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format in pricing file: {e}")
    except Exception as e:
        return (f"Error loading pricing file: {e}")

pricings = load_pricings()

def get_models(pricings: dict) -> list[str]:
    models = list(pricings.keys()) 
    return models

FALLBACK_ENCODING= tiktoken.get_encoding("cl100k_base")
def get_encoding_for_model(model: str, pricings: dict) -> tiktoken.Encoding:
    if model not in pricings:
        raise ValueError(f"Model '{model}' not found in pricing data."
                         f" Available models: {', '.join(pricings.keys())}")
        # print( f"ValueError: "
        #     f"Model '{model}' not found in pricing data."
        #                  f" Available models: {', '.join(pricings.keys())}")
    tiktoken_model = model
    try:
        return tiktoken.encoding_for_model(tiktoken_model)
    except KeyError:
        print(f"Error getting encoding for model '{model}'. Using fallback encoding 'cl100k_base'.")
        return FALLBACK_ENCODING #cl100k_base

def count_tokens(text: str, model: str) -> tuple [list[int], int]:
    enc = get_encoding_for_model(model, pricings)
    tokens = enc.encode(text)
    return tokens, len(tokens)

def calculate_cost(model: str, token_count: int, pricings: dict) -> float:
    if model not in pricings:
        raise ValueError(f"Model '{model}' not found in pricing data."
                         f" Available models: {', '.join(pricings.keys())}")
    cost = pricings[model]["input"] # Only taking input cost for now. cost per million tokens
    return token_count * cost / 1000000

def main():
    # pricings = load_pricings()
    models = get_models(pricings)

    print("Available models:")
    for i,model in enumerate(models, 1):
        print(f"{i}. {model}")

    model = input("Enter the model: ").lower().strip()
    text = input("Enter the text to analyze: ")
    tokens, token_count = count_tokens(text, model)
    cost = calculate_cost(model, token_count, pricings)
    print(f"Tokens: {tokens}")
    print(f"Token count: {token_count}")
    print(f"Estimated cost: ${cost:.6f}")

if __name__ == "__main__":
    main()

