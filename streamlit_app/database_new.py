# Simplified generate_graphical_password function

def generate_graphical_password(length: int = 1) -> str:
    """Generate a random graphical password using a single emoji.

    Returns one random emoji that students can easily remember.
    Examples: 🌟, 🎮, 🍎, 🐱
    """
    import random

    # Define emojis for students to choose from
    emojis = [
        # Fun & Colorful
        '🌟', '🌙', '⭐', '☀️', '🌈', '☁️', '⚡', '❄️', '🔥',
        # Colors
        '🔴', '🟠', '🟡', '🟢', '🔵', '🟣', '🟤', '⚫', '⚪',
        # Animals
        '🐶', '🐱', '🐭', '🐹', '🐰', '🦊', '🐻', '🐼', '🐨',
        # Food
        '🍎', '🍊', '🍋', '🍌', '🍇', '🍓', '🍒', '🍑', '🥝',
        # Sports & Games
        '⚽', '🏀', '🏈', '⚾', '🎾', '🏐', '🏉', '🎱', '🏓',
        # Activities
        '🎮', '🎯', '🎲', '🎪', '🎨', '🎭', '🎵', '🎸', '🎹',
        # Objects
        '📚', '✏️', '🖊️', '🖍️', '📏', '📐', '🎒', '🔑', '🖱️',
        # Vehicles
        '🚗', '🚕', '🚙', '🚌', '🚎', '🚓', '🚲', '🛴', '🚃',
        # Nature
        '🌸', '🌺', '🌻', '🌼', '🌷', '🌹', '🍀', '🌲', '🌴',
        # Faces (simple ones)
        '😊', '😃', '😄', '🙂', '😎', '🤗', '🤩', '😇', '🥰',
    ]

    return random.choice(emojis)
