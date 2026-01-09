"""
Quick demo of the chat interface in non-interactive mode.
Shows how the system works without requiring user input.
"""

from chat import ChatInterface
import sys

print("="*60)
print("CHAT INTERFACE DEMO")
print("="*60)

# Create chat interface (dataset-only mode, no model needed)
chat = ChatInterface(
    model_path=None,
    dataset_path="demo_chat_data.json",
    auto_save=True
)

# Setup demo profile
chat.memory_manager.give_consent(True)
chat.memory_manager.set_user_profile(
    name="Demo User",
    age=9,
    favorite_color="blue",
    favorite_subject="Science"
)

print("\n✓ Chat interface initialized")
print(f"  Model: {'Loaded' if chat.engine else 'Dataset-only mode'}")
print(f"  Dataset: {chat.dataset_path}")
print(f"  Memory: Enabled with consent")

# Simulate some conversations
demo_conversations = [
    ("happy", "Why is the sky blue?"),
    ("excited", "Tell me about space!"),
    ("curious", "How do airplanes fly?"),
    ("neutral", "What is photosynthesis?"),
]

print("\n" + "="*60)
print("DEMO CONVERSATIONS")
print("="*60)

for emotion, question in demo_conversations:
    chat.current_emotion = emotion
    response = chat.generate_response(question)
    
    print(f"\n[{emotion}] User: {question}")
    print(f"AI: {response}")
    
    # Add to dataset
    chat.add_to_dataset(emotion, question, response, chat.current_age)
    
    # Add to memory
    chat.memory_manager.add_interaction(emotion, question, response)

# Show stats
print("\n" + "="*60)
print("STATISTICS")
print("="*60)
print(f"Dataset examples: {len(chat.dataset['examples'])}")
print(f"Memory interactions: {chat.memory_manager.get_stats()['total_interactions']}")
print(f"Dataset file: {chat.dataset_path}")

# Save dataset
chat._save_dataset()
print(f"\n✓ Dataset saved: {len(chat.dataset['examples'])} examples")

print("\n" + "="*60)
print("✓ DEMO COMPLETE")
print("="*60)
print("\nTo start interactive chat, run:")
print("  python chat.py")
print("\nYour conversations will be saved to the training dataset!")
