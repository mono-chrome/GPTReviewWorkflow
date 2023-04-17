from review import call_gpt

system = {"role": "system", "content": "Create a ARM Template JSON file from a Bicep template for the user."}
response = call_gpt(prompt, temperature=0.00, max_tokens=1200, system=system)
print(response)
