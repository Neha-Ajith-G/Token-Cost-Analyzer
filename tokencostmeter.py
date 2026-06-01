import tiktoken
import json

with open("pricings.json", "r") as f:
    pricings = json.load(f) 

models = list(pricings.keys()) 
print("Available models:")
for i,model in enumerate(models):
    print(f"{i+1}. {model}")
model = input("Select a model: ")

enc = tiktoken.encoding_for_model(model)
print(f"Using encoding: {enc.name}")

text = input("Enter the text to calculate token cost: ")

tokens = enc.encode(text)
tkcount = len(tokens)
print(f"Tokens : {tokens}")
print(f"Token count: {tkcount}")

if model in pricings:
    input_cost = pricings[model]["input"]
    cost = tkcount * input_cost / 1000
    print(f"Cost for {tkcount} tokens: ${cost:.6f}")
