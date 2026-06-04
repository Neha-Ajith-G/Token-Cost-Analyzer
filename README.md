# Token-Cost-Analyzer
**ALLIANZ Internship Week 1 Hands On Project** 
A Python Command Line Interface (CLI) for analyzing text token usage using tiktoken library, estimating USD costs

## Features
- **Token Counting**: Uses OpenAI's `tiktoken` library for for accurate tokenization and token counting.
- **Estimate API costs**: Calculates estimated input token costs based on token usage and model pricing defined in a custom configuration file.
-**Matching Model Suggestion**: Uses 'rapidfuzz' library to suggest the closest matching model name using fuzzy string matching if you make a typo in model name input prompt.

## Prerequisites
- **Python**: Version 3.8 or higher
- Install the required dependencies

## Configuration Setup
Before running the application, create a configuration file named `pricings.json`, make changes accordingly. 

>**Data Source**: Pricing information can be obtained from the OpenAI pricing documentation: [OpenAI Pricing Documentation](https://developers.openai.com/api/docs/pricing).

Populate it with your target models and their respective **input token pricing per one million tokens**.

### Example `pricings.json`
```json
{
  "gpt-4o": {
    "input": 5.00
  },
  "gpt-3.5-turbo": {
    "input": 0.50
  }
}
```
## Usage
Run the application:

```bash
python3 token_cost_analyzer.py
```
## How It Works

### Token Encoding

```python
import tiktoken
enc = tiktoken.encoding_for_model("gpt-4o")
tokens = enc.encode("Hello, Nice to meet you!!")
```
### Example

```text
Available models:
1. gpt-5.5
2. gpt-5.4
3. gpt-5.4-mini
4. gpt-5.4-nano
5. gpt-5
6. gpt-5-mini
7. gpt-5-nano
8. gpt-4.1
9. gpt-4o
10. gpt-4o-mini
Enter the model: gpt-4o
Enter the text to analyze: Hello, Nice to meet you!!

--- Results ---
Tokens: [13225, 11, 35669, 316, 4158, 481, 2618]
Token count: 7
Estimated cost: $0.000017
```
### Invalid Model Example

```text
Enter the model: Claude
Model 'claude' not found and no close matches available. Exiting.
```
### Typo in Model Name Prompt Example

```text
Enter the model: gpt40 MINI
Model 'gpt40 mini' not found. Did you mean 'gpt-4o-mini'? (y/n): Y
Enter the text to analyze: Have a nice day

--- Results ---
Tokens: [15334, 261, 7403, 2163]
Token count: 4
Estimated cost: $0.000001
```
## Notes
- Costs are estimated using the pricing values stored in `pricings.json`.
- Only input token costs are calculated.
- Token counts may vary across models because different models can use different tokenization schemes.
- Model name suggestions are generated using fuzzy string matching from the `rapidfuzz` library.