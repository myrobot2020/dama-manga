import random

def get_embedding(text):
    """Returns a random vector for UI demonstration."""
    return [random.uniform(-1, 1) for _ in range(384)]

def cosine_similarity(v1, v2):
    """Returns a mock similarity score."""
    return random.uniform(0.7, 0.99)
