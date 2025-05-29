from groq import Groq

client = Groq(api_key="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")

models = client.models.list()
for model in models.data:
    print(model.id)
