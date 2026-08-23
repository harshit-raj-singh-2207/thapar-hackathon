from typing import List, Dict, Any

SEED_GAMES: List[Dict[str, Any]] = [
    # 1. Communication
    {
        "id": "game-comm-1",
        "title": "AAC Picture Word Match",
        "category": "Communication",
        "description": "Match everyday picture cards with their words to build vocabulary and express needs.",
        "icon": "🗣️",
        "color": "#2563EB",
        "difficulty": "easy",
        "min_age": 4,
        "max_age": 12,
        "is_emergency_recommended": True,
        "skill_tags": ["AAC Vocabulary", "Visual Matching", "Expressive Communication"],
        "instructions": "Look at the picture card and choose the matching word or action.",
        "tasks_data": [
            {
                "id": "t1",
                "prompt": "When you are thirsty, which picture do you tap?",
                "aac_token": "WATER",
                "task_type": "matching",
                "options": [
                    {"id": "o1", "label": "WATER", "icon": "💧", "is_correct": True},
                    {"id": "o2", "label": "BED", "icon": "🛏️", "is_correct": False},
                    {"id": "o3", "label": "SHOE", "icon": "👟", "is_correct": False},
                ],
            },
            {
                "id": "t2",
                "prompt": "When you want to eat something, which card helps you say it?",
                "aac_token": "FOOD",
                "task_type": "matching",
                "options": [
                    {"id": "o1", "label": "PLAY", "icon": "⚽", "is_correct": False},
                    {"id": "o2", "label": "FOOD", "icon": "🍎", "is_correct": True},
                    {"id": "o3", "label": "BOOK", "icon": "📖", "is_correct": False},
                ],
            },
            {
                "id": "t3",
                "prompt": "If something is tricky and you need a grown-up, what do you ask?",
                "aac_token": "HELP",
                "task_type": "matching",
                "options": [
                    {"id": "o1", "label": "HELP", "icon": "🤝", "is_correct": True},
                    {"id": "o2", "label": "SLEEP", "icon": "🌙", "is_correct": False},
                    {"id": "o3", "label": "JUMP", "icon": "🦘", "is_correct": False},
                ],
            },
        ],
    },

    # 2. Emotion
    {
        "id": "game-emotion-1",
        "title": "Emotion Detective",
        "category": "Emotion",
        "description": "Recognize feeling expressions and match them with safe self-regulation tools.",
        "icon": "😊",
        "color": "#EC4899",
        "difficulty": "easy",
        "min_age": 5,
        "max_age": 14,
        "is_emergency_recommended": True,
        "skill_tags": ["Emotion Recognition", "Sensory Grounding", "Self-Regulation"],
        "instructions": "Identify the emotion shown and find what can help you feel better.",
        "tasks_data": [
            {
                "id": "t1",
                "prompt": "Leo's heart is beating fast and the room is too loud. How is Leo feeling?",
                "emotion_target": "anxious",
                "task_type": "emotion_select",
                "options": [
                    {"id": "o1", "label": "Anxious / Overwhelmed", "icon": "😰", "is_correct": True},
                    {"id": "o2", "label": "Sleepy", "icon": "😴", "is_correct": False},
                    {"id": "o3", "label": "Excited", "icon": "🤩", "is_correct": False},
                ],
            },
            {
                "id": "t2",
                "prompt": "What is a great calming strategy when feeling overwhelmed?",
                "task_type": "matching",
                "options": [
                    {"id": "o1", "label": "Yell loudly", "icon": "📢", "is_correct": False},
                    {"id": "o2", "label": "Put on headphones & take 5 slow breaths", "icon": "🎧", "is_correct": True},
                    {"id": "o3", "label": "Run away", "icon": "🏃", "is_correct": False},
                ],
            },
            {
                "id": "t3",
                "prompt": "You finished your favorite puzzle! Which feeling matches your smile?",
                "emotion_target": "happy",
                "task_type": "emotion_select",
                "options": [
                    {"id": "o1", "label": "Angry", "icon": "😡", "is_correct": False},
                    {"id": "o2", "label": "Happy & Proud", "icon": "😊", "is_correct": True},
                    {"id": "o3", "label": "Scared", "icon": "😨", "is_correct": False},
                ],
            },
        ],
    },

    # 3. Memory
    {
        "id": "game-memory-1",
        "title": "Visual Pattern & Memory Quest",
        "category": "Memory",
        "description": "Remember sensory object sequences and recall them to build cognitive working memory.",
        "icon": "🧠",
        "color": "#8B5CF6",
        "difficulty": "medium",
        "min_age": 5,
        "max_age": 14,
        "is_emergency_recommended": True,
        "skill_tags": ["Working Memory", "Pattern Recognition", "Visual Sequencing"],
        "instructions": "Look at the 3 items in order and tap the matching sequence.",
        "tasks_data": [
            {
                "id": "t1",
                "prompt": "Remember this sequence: 🌟 Star -> 🍎 Apple -> 💧 Water",
                "task_type": "sequence",
                "options": [
                    {"id": "o1", "label": "Star -> Apple -> Water", "icon": "🌟🍎💧", "is_correct": True},
                    {"id": "o2", "label": "Water -> Apple -> Star", "icon": "💧🍎🌟", "is_correct": False},
                    {"id": "o3", "label": "Apple -> Star -> Water", "icon": "🍎🌟💧", "is_correct": False},
                ],
            },
            {
                "id": "t2",
                "prompt": "Which item came SECOND in the sequence: 🐱 Cat -> 🚗 Car -> 🎈 Balloon?",
                "task_type": "matching",
                "options": [
                    {"id": "o1", "label": "Cat", "icon": "🐱", "is_correct": False},
                    {"id": "o2", "label": "Car", "icon": "🚗", "is_correct": True},
                    {"id": "o3", "label": "Balloon", "icon": "🎈", "is_correct": False},
                ],
            },
        ],
    },

    # 4. Matching
    {
        "id": "game-matching-1",
        "title": "Sensory Shape & Color Sorter",
        "category": "Matching",
        "description": "Sort shapes, colors, and sensory textures to strengthen categorization skills.",
        "icon": "🔷",
        "color": "#F59E0B",
        "difficulty": "easy",
        "min_age": 4,
        "max_age": 10,
        "is_emergency_recommended": True,
        "skill_tags": ["Categorization", "Color Recognition", "Sensory Discrimination"],
        "instructions": "Select the item that belongs to the matching color or shape group.",
        "tasks_data": [
            {
                "id": "t1",
                "prompt": "Which object is BLUE and used for drinking?",
                "task_type": "matching",
                "options": [
                    {"id": "o1", "label": "Blue Cup", "icon": "🥛", "is_correct": True},
                    {"id": "o2", "label": "Yellow Banana", "icon": "🍌", "is_correct": False},
                    {"id": "o3", "label": "Red Apple", "icon": "🍎", "is_correct": False},
                ],
            },
            {
                "id": "t2",
                "prompt": "Find the SOFT sensory item among these objects:",
                "task_type": "matching",
                "options": [
                    {"id": "o1", "label": "Soft Plush Teddy", "icon": "🧸", "is_correct": True},
                    {"id": "o2", "label": "Hard Wooden Block", "icon": "🪵", "is_correct": False},
                    {"id": "o3", "label": "Metal Key", "icon": "🔑", "is_correct": False},
                ],
            },
        ],
    },

    # 5. Focus
    {
        "id": "game-focus-1",
        "title": "Quiet Focus Target Finder",
        "category": "Focus",
        "description": "Find specific hidden details in a calm visual space to boost sustained attention.",
        "icon": "🎯",
        "color": "#10B981",
        "difficulty": "medium",
        "min_age": 5,
        "max_age": 14,
        "is_emergency_recommended": True,
        "skill_tags": ["Sustained Attention", "Visual Search", "Focus"],
        "instructions": "Locate the designated quiet object without getting distracted.",
        "tasks_data": [
            {
                "id": "t1",
                "prompt": "Find the soothing sensory item hidden in the quiet room:",
                "task_type": "visual_find",
                "options": [
                    {"id": "o1", "label": "Glitter Sensory Bottle", "icon": "🫧", "is_correct": True},
                    {"id": "o2", "label": "Noisy Horn", "icon": "📯", "is_correct": False},
                    {"id": "o3", "label": "Flashing Siren", "icon": "🚨", "is_correct": False},
                ],
            },
            {
                "id": "t2",
                "prompt": "Tap the calming nature icon:",
                "task_type": "visual_find",
                "options": [
                    {"id": "o1", "label": "Green Leaf", "icon": "🍃", "is_correct": True},
                    {"id": "o2", "label": "Loud Drum", "icon": "🥁", "is_correct": False},
                    {"id": "o3", "label": "Jackhammer", "icon": "🔨", "is_correct": False},
                ],
            },
        ],
    },

    # 6. Learning
    {
        "id": "game-learning-1",
        "title": "Daily Routine Step Sorter",
        "category": "Learning",
        "description": "Arrange daily visual routine micro-steps in the right sequence for independence.",
        "icon": "📖",
        "color": "#3B82F6",
        "difficulty": "easy",
        "min_age": 4,
        "max_age": 14,
        "is_emergency_recommended": True,
        "skill_tags": ["Daily Routines", "Sequential Planning", "Home Independence"],
        "instructions": "Put the steps in the right chronological order.",
        "tasks_data": [
            {
                "id": "t1",
                "prompt": "What is the FIRST step when brushing your teeth in the morning?",
                "task_type": "sequence",
                "options": [
                    {"id": "o1", "label": "Put toothpaste on brush", "icon": "🪥", "is_correct": True},
                    {"id": "o2", "label": "Rinse mouth with water", "icon": "🚰", "is_correct": False},
                    {"id": "o3", "label": "Put toothbrush away in cup", "icon": "🥤", "is_correct": False},
                ],
            },
            {
                "id": "t2",
                "prompt": "What do you do right before eating lunch?",
                "task_type": "sequence",
                "options": [
                    {"id": "o1", "label": "Wash hands with soap", "icon": "🧼", "is_correct": True},
                    {"id": "o2", "label": "Go to sleep", "icon": "😴", "is_correct": False},
                    {"id": "o3", "label": "Put on winter coat", "icon": "🧥", "is_correct": False},
                ],
            },
        ],
    },

    # 7. Social Skills
    {
        "id": "game-social-1",
        "title": "Turn-Taking & Friendship Adventure",
        "category": "Social Skills",
        "description": "Learn gentle turn-taking, asking to join games, and respectful social boundaries.",
        "icon": "🤝",
        "color": "#6366F1",
        "difficulty": "medium",
        "min_age": 5,
        "max_age": 14,
        "is_emergency_recommended": True,
        "skill_tags": ["Turn Taking", "Social Problem Solving", "Empathy"],
        "instructions": "Pick the kindest and clearest way to share and play.",
        "tasks_data": [
            {
                "id": "t1",
                "prompt": "Your brother is playing with a toy you want. What is the best choice?",
                "task_type": "multiple_choice",
                "options": [
                    {"id": "o1", "label": "Ask: 'Can I have a turn in 2 minutes?'", "icon": "⏳", "is_correct": True},
                    {"id": "o2", "label": "Grab it away immediately", "icon": "🚫", "is_correct": False},
                    {"id": "o3", "label": "Scream loudly", "icon": "🗣️", "is_correct": False},
                ],
            },
            {
                "id": "t2",
                "prompt": "When a friend does a great job, what can you say?",
                "task_type": "multiple_choice",
                "options": [
                    {"id": "o1", "label": "'Great job, well done!'", "icon": "👏", "is_correct": True},
                    {"id": "o2", "label": "'I am better than you'", "icon": "❌", "is_correct": False},
                    {"id": "o3", "label": "Walk away in silence", "icon": "🚶", "is_correct": False},
                ],
            },
        ],
    },

    # 8. Daily Life Skills
    {
        "id": "game-daily-1",
        "title": "Desk & Room Clean-Up Champion",
        "category": "Daily Life Skills",
        "description": "Practice organizing indoor home spaces, sensory toys, and school items.",
        "icon": "🧹",
        "color": "#14B8A6",
        "difficulty": "easy",
        "min_age": 4,
        "max_age": 14,
        "is_emergency_recommended": True,
        "skill_tags": ["Organization", "Task Completion", "Self-Care"],
        "instructions": "Sort items to their proper storage bin or station.",
        "tasks_data": [
            {
                "id": "t1",
                "prompt": "Where do colored markers go after drawing?",
                "task_type": "matching",
                "options": [
                    {"id": "o1", "label": "Pencil Case / Pen Holder", "icon": "✏️", "is_correct": True},
                    {"id": "o2", "label": "Under the bed floor", "icon": "🛏️", "is_correct": False},
                    {"id": "o3", "label": "Inside the refrigerator", "icon": "🧊", "is_correct": False},
                ],
            },
            {
                "id": "t2",
                "prompt": "Where do dirty clothes belong at bedtime?",
                "task_type": "matching",
                "options": [
                    {"id": "o1", "label": "Laundry Hamper", "icon": "🧺", "is_correct": True},
                    {"id": "o2", "label": "On the desk", "icon": "💻", "is_correct": False},
                    {"id": "o3", "label": "On the dinner table", "icon": "🍽️", "is_correct": False},
                ],
            },
        ],
    },
]
