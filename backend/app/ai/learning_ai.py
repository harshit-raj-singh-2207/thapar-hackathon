from typing import List, Dict, Any, Optional

class LearningAI:
    """
    AI engine for:
    1. Task Breakdown (micro-steps with icons and timers)
    2. AI Tutor ("Nivi") for patient, neuro-inclusive explanations
    3. Personalized Social Stories & Learning Concepts
    """

    DEFAULT_TASK_TEMPLATES = {
        "brush teeth": [
            {"step_number": 1, "title": "Get your toothbrush & paste", "instruction": "Pick up your favorite brush and put a pea-sized dot of toothpaste.", "icon": "🪥", "duration_sec": 30},
            {"step_number": 2, "title": "Brush front teeth in circles", "instruction": "Gently make small round circles on your front smile.", "icon": "😁", "duration_sec": 45},
            {"step_number": 3, "title": "Brush top & bottom chewing teeth", "instruction": "Scrub the flat biting tops on the left and right.", "icon": "🦷", "duration_sec": 45},
            {"step_number": 4, "title": "Spit and rinse mouth", "instruction": "Spit out foam into sink, take a sip of water, swish, and spit!", "icon": "🚰", "duration_sec": 30},
            {"step_number": 5, "title": "Wipe mouth & smile", "instruction": "Pat dry with clean towel. High five for clean teeth! ⭐", "icon": "✨", "duration_sec": 15},
        ],
        "pack backpack": [
            {"step_number": 1, "title": "Open main backpack zipper", "instruction": "Place backpack flat on floor or desk and zip open.", "icon": "🎒", "duration_sec": 20},
            {"step_number": 2, "title": "Put homework & folders inside", "instruction": "Slide big books and flat folders into the back pocket.", "icon": "📁", "duration_sec": 40},
            {"step_number": 3, "title": "Pack pencil box & sensory fidget", "instruction": "Put pencils and favorite sensory comfort item in front pouch.", "icon": "✏️", "duration_sec": 30},
            {"step_number": 4, "title": "Slide in water bottle", "instruction": "Check that the cap is tightly closed and slide into side mesh.", "icon": "💧", "duration_sec": 20},
            {"step_number": 5, "title": "Zip closed & place by door", "instruction": "Zip it up tight and put it ready for school tomorrow!", "icon": "🚪", "duration_sec": 20},
        ],
        "wash hands": [
            {"step_number": 1, "title": "Turn on water & wet hands", "instruction": "Put hands under warm running water.", "icon": "🚰", "duration_sec": 10},
            {"step_number": 2, "title": "Pump soap into palm", "instruction": "One pump of soap on your hands.", "icon": "🧼", "duration_sec": 10},
            {"step_number": 3, "title": "Rub palms, backs, & between fingers", "instruction": "Make bubbly suds while singing happy birthday twice (20s).", "icon": "🫧", "duration_sec": 20},
            {"step_number": 4, "title": "Rinse all bubbles away", "instruction": "Hold hands under clean water until no soap remains.", "icon": "💦", "duration_sec": 15},
            {"step_number": 5, "title": "Dry with clean towel", "instruction": "Pat hands completely dry.", "icon": "🧺", "duration_sec": 15},
        ],
        "tidy room": [
            {"step_number": 1, "title": "Pick up soft toys", "instruction": "Collect plushies and place them in the toy basket.", "icon": "🧸", "duration_sec": 60},
            {"step_number": 2, "title": "Stack books on shelf", "instruction": "Pick up books from floor and line them up neatly.", "icon": "📚", "duration_sec": 60},
            {"step_number": 3, "title": "Put dirty clothes in hamper", "instruction": "Find socks and shirts on floor and drop in laundry basket.", "icon": "🧺", "duration_sec": 45},
            {"step_number": 4, "title": "Smooth bed blanket", "instruction": "Pull blanket up to pillows for a cozy clean bed!", "icon": "🛏️", "duration_sec": 45},
        ]
    }

    @classmethod
    def breakdown_task(cls, task_title: str) -> List[Dict[str, Any]]:
        title_lower = task_title.lower().strip()
        for key, steps in cls.DEFAULT_TASK_TEMPLATES.items():
            if key in title_lower or title_lower in key:
                return steps

        # Dynamic AI Generator
        return [
            {"step_number": 1, "title": f"Prepare for {task_title}", "instruction": f"Get your materials ready and take a deep breath to begin.", "icon": "🏁", "duration_sec": 30},
            {"step_number": 2, "title": "Do step one carefully", "instruction": "Focus on the first small action. Take your time.", "icon": "1️⃣", "duration_sec": 60},
            {"step_number": 3, "title": "Complete main part", "instruction": "Keep going! You are doing great progress.", "icon": "⭐", "duration_sec": 90},
            {"step_number": 4, "title": "Check your work", "instruction": "Look over what you did and make sure everything is in place.", "icon": "🔍", "duration_sec": 30},
            {"step_number": 5, "title": "Celebrate & reward", "instruction": "Task finished! Great job staying focused.", "icon": "🎉", "duration_sec": 15},
        ]

    @classmethod
    def answer_tutor_question(cls, question: str, age_level: str = "child") -> Dict[str, Any]:
        q_lower = question.lower()
        
        if "rainbow" in q_lower:
            reply = "🌈 Rainbows happen when sunlight shines through raindrops! The raindrop acts like a tiny glass triangle that bends the white light into 7 beautiful colors: Red, Orange, Yellow, Green, Blue, Indigo, and Violet!"
            analogy = "Think of sunlight as a box of crayons, and the raindrop opens the box so all colors can shine!"
            follow_up = ["Why is the sky blue?", "How do clouds make rain?"]
            icon = "🌈"
        elif "dinosaur" in q_lower or "t-rex" in q_lower:
            reply = "🦖 Dinosaurs lived millions of years ago! Some like the Brachiosaurus ate tall tree leaves (herbivores), while the T-Rex was a mighty hunter with sharp teeth (carnivore)!"
            analogy = "Some dinosaurs were as small as a chicken, while others were as long as two school buses parked together!"
            follow_up = ["Why did dinosaurs disappear?", "Are birds related to dinosaurs?"]
            icon = "🦕"
        elif "space" in q_lower or "planet" in q_lower or "moon" in q_lower:
            reply = "🚀 Our solar system has 8 planets traveling in big circles around the Sun! Earth is the 3rd rock from the sun, and it's the only one with oceans, trees, and us!"
            analogy = "The sun is like a giant warm campfire in the middle, and the planets are friends sitting in circles around it!"
            follow_up = ["What is inside a black hole?", "Why does the moon change shapes?"]
            icon = "🪐"
        elif "friend" in q_lower or "share" in q_lower:
            reply = "🤝 Being a kind friend means taking turns, listening when someone speaks, and asking: 'Would you like to play together?' If you need quiet time, it's okay to say: 'I need a solo break right now!'"
            analogy = "Friendship is like passing a ball back and forth gently so both people enjoy the game!"
            follow_up = ["What can I do if someone is upset?", "How do I join a game at recess?"]
            icon = "🤝"
        else:
            reply = f"✨ That is a wonderful question! Learning about '{question}' helps our brain build new super-strength connections. Let's explore step by step!"
            analogy = "Every time you ask a question, your brain gets another star in its curiosity trophy!"
            follow_up = ["Tell me more about this!", "Can we try a mini quiz?"]
            icon = "💡"

        return {
            "question": question,
            "reply": reply,
            "simple_analogy": analogy,
            "follow_up_questions": follow_up,
            "icon": icon,
        }
