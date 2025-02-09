from autogen import AssistantAgent

# Create an assistant agent
assistant = AssistantAgent(name="chatgpt")

# Prompt the assistant and get a response
response = assistant.generate_reply("What is the capital of France?")
print(response)
