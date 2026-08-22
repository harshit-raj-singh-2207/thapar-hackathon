import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import inspect
from app.core.database import Base, engine, SessionLocal, sync_database_schema
from app.core.security import get_password_hash
from app.api.router import api_router
from app.domains.users.models import User
from app.domains.caregivers.models import Caregiver
from app.domains.community.models import Group, GroupMember, Post, Comment, Resource, Event, SavedPost
from app.domains.communication.models import AACCategory, AACCard, SavedPhrase, EmotionRecord, CommunicationLog
from app.domains.learning.models import Routine, RoutineStep, Task, Reminder, LearningTopic, TutorChatSession

app = FastAPI(title="NIVARA Caregiver Community API", version="1.0.0")

# Enable CORS for frontend web and mobile clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure static upload directory exists and mount static files
UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../uploads"))
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/static/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

from app.api.v1.community.sound_routes import router as sound_router
from app.api.v1.community.social_routes import router as social_router

# Include master API router
app.include_router(api_router, prefix="/api")

# Top-level alias routers for social interactions and sounds
app.include_router(social_router)
app.include_router(sound_router, prefix="/api")
app.include_router(sound_router)

@app.get("/")
def root():
    return {"message": "NIVARA Caregiver Community API", "status": "ok", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

def startup_event():
    Base.metadata.create_all(bind=engine)
    sync_database_schema(engine)
    db = SessionLocal()
    try:
        # Seed test users if not present
        sarah = db.query(User).filter((User.email == "sarah@nivara.app") | (User.id == "user-verified-sarah")).first()
        if not sarah:
            try:
                sarah = User(
                    id="user-verified-sarah",
                    email="sarah@nivara.app",
                    hashed_password=get_password_hash("password123"),
                    full_name="Sarah Mitchell",
                    role="caregiver",
                )
                db.add(sarah)
                db.commit()
                db.refresh(sarah)
            except Exception:
                db.rollback()
                sarah = db.query(User).filter(User.email == "sarah@nivara.app").first()

        if sarah:
            sarah_cg = db.query(Caregiver).filter(Caregiver.user_id == sarah.id).first()
            if not sarah_cg:
                try:
                    sarah_cg = Caregiver(
                        user_id=sarah.id,
                        bio="ABA therapist & caregiver",
                        is_verified=True,
                        verification_status="verified",
                        is_online=True,
                    )
                    db.add(sarah_cg)
                    db.commit()
                except Exception:
                    db.rollback()

        david = db.query(User).filter((User.email == "david@nivara.app") | (User.id == "user-verified-david")).first()
        if not david:
            try:
                david = User(
                    id="user-verified-david",
                    email="david@nivara.app",
                    hashed_password=get_password_hash("password123"),
                    full_name="David Nguyen",
                    role="caregiver",
                )
                db.add(david)
                db.commit()
                db.refresh(david)
            except Exception:
                db.rollback()
                david = db.query(User).filter(User.email == "david@nivara.app").first()

        if david:
            david_cg = db.query(Caregiver).filter(Caregiver.user_id == david.id).first()
            if not david_cg:
                try:
                    david_cg = Caregiver(
                        user_id=david.id,
                        bio="Special education teacher & caregiver",
                        is_verified=True,
                        verification_status="verified",
                        is_online=False,
                    )
                    db.add(david_cg)
                    db.commit()
                except Exception:
                    db.rollback()

        lisa = db.query(User).filter((User.email == "lisa@nivara.app") | (User.id == "user-unverified-lisa")).first()
        if not lisa:
            try:
                lisa = User(
                    id="user-unverified-lisa",
                    email="lisa@nivara.app",
                    hashed_password=get_password_hash("password123"),
                    full_name="Lisa Chen",
                    role="caregiver",
                )
                db.add(lisa)
                db.commit()
                db.refresh(lisa)
            except Exception:
                db.rollback()
                lisa = db.query(User).filter(User.email == "lisa@nivara.app").first()

        if lisa:
            lisa_cg = db.query(Caregiver).filter(Caregiver.user_id == lisa.id).first()
            if not lisa_cg:
                try:
                    lisa_cg = Caregiver(
                        user_id=lisa.id,
                        bio="Parent caregiver",
                        is_verified=False,
                        verification_status="pending",
                        is_online=False,
                    )
                    db.add(lisa_cg)
                    db.commit()
                except Exception:
                    db.rollback()

        # Seed group-sensory-1 for Phase 5 tests if not present
        group = db.query(Group).filter(Group.id == "group-sensory-1").first()
        if not group:
            group = Group(
                id="group-sensory-1",
                name="Sensory Support Circle",
                description="Share sensory tools and strategies",
                category="Sensory",
                creator_id="user-verified-sarah",
            )
            db.add(group)
            db.commit()

            sarah_gm = GroupMember(
                group_id="group-sensory-1",
                user_id="user-verified-sarah",
                role="admin",
            )
            db.add(sarah_gm)
            db.commit()

        # Seed group-newly-diagnosed-1 if not present
        group_nd = db.query(Group).filter(Group.id == "group-newly-diagnosed-1").first()
        if not group_nd:
            group_nd = Group(
                id="group-newly-diagnosed-1",
                name="Parents of Newly Diagnosed",
                description="A supportive space for parents and guardians navigating recent diagnoses. Share experiences, resources, and find comfort in a community that understands your journey.",
                category="Parents of Newly Diagnosed",
                creator_id="user-verified-sarah",
            )
            db.add(group_nd)
            db.commit()

            sarah_nd_gm = GroupMember(
                group_id="group-newly-diagnosed-1",
                user_id="user-verified-sarah",
                role="admin",
            )
            db.add(sarah_nd_gm)
            db.commit()

        # Seed initial posts for Parents of Newly Diagnosed
        post_nd_1 = db.query(Post).filter(Post.id == "post-nd-1").first()
        if not post_nd_1:
            post_nd_1 = Post(
                id="post-nd-1",
                author_id="user-verified-sarah",
                content="Hi everyone, we just received our diagnosis last week. It feels overwhelming to process all the medical paperwork and sensory schedules, but reading your posts has given us so much hope.",
                category="Parents of Newly Diagnosed",
                like_count=12,
                comment_count=5,
            )
            db.add(post_nd_1)

            post_nd_2 = Post(
                id="post-nd-2",
                author_id="user-verified-david",
                content="Does anyone have recommendations for noise-canceling headphones or quiet spaces for kids aged 4-6? We are planning our first family park trip after speech therapy.",
                category="Parents of Newly Diagnosed",
                like_count=24,
                comment_count=9,
            )
            db.add(post_nd_2)
            db.commit()

        # Seed initial post for feed tests
        post = db.query(Post).filter(Post.id == "post-welcome-1").first()
        if not post:
            post = Post(
                id="post-welcome-1",
                author_id="user-verified-sarah",
                content="Welcome caregivers to the NIVARA private community! Feel free to share resources and ask questions.",
                category="Resources",
                comment_count=1,
            )
            db.add(post)
            db.commit()

            # Seed initial comment on welcome post
            comment = Comment(
                id="comment-welcome-1",
                post_id="post-welcome-1",
                author_id="user-verified-david",
                content="Thank you Sarah! Excited to connect with other caregivers and share tools.",
            )
            db.add(comment)
            db.commit()

        post_emily = db.query(Post).filter(Post.id == "post-emily-1").first()
        if not post_emily:
            post_emily = Post(
                id="post-emily-1",
                author_id="user-verified-sarah",
                content="Today was a big win! My son tried a new sensory activity and loved it. Small steps, big progress 💙",
                category="Sensory Support",
                like_count=24,
                comment_count=8,
            )
            db.add(post_emily)
            db.commit()

        post_michael = db.query(Post).filter(Post.id == "post-michael-1").first()
        if not post_michael:
            post_michael = Post(
                id="post-michael-1",
                author_id="user-verified-david",
                content="Does anyone have tips for helping with school transitions? We're struggling with morning routines.",
                category="School Life",
                like_count=18,
                comment_count=12,
            )
            db.add(post_michael)
            db.commit()

        # Seed initial resources
        res1 = db.query(Resource).filter(Resource.id == "res-visual-schedule").first()
        if not res1:
            res1 = Resource(
                id="res-visual-schedule",
                title="Daily Visual Schedule Printable Template",
                description="Step-by-step visual routine cards with morning, school, and bedtime icons for children on the spectrum.",
                category="Education",
                file_type="template",
                url="https://nivara.app/resources/visual-schedule.pdf",
                author_id="user-verified-sarah",
            )
            db.add(res1)

            res2 = Resource(
                id="res-sensory-diet",
                title="Sensory Diet & Calming Tools Guide",
                description="Practical sensory diet strategies, proprioceptive activities, and deep-pressure techniques for emotional regulation.",
                category="Sensory",
                file_type="guide",
                url="https://nivara.app/resources/sensory-guide.pdf",
                author_id="user-verified-david",
            )
            db.add(res2)

            res3 = Resource(
                id="res-iep-checklist",
                title="Caregiver IEP Meeting Preparation Checklist",
                description="Essential questions, accommodation requests, and behavioral goal templates for annual school IEP meetings.",
                category="Advocacy",
                file_type="checklist",
                url="https://nivara.app/resources/iep-checklist.pdf",
                author_id="user-verified-sarah",
            )
            db.add(res3)
            db.commit()

        # Seed initial events
        event1 = db.query(Event).filter(Event.id == "event-1").first()
        if not event1:
            event1 = Event(
                id="event-1",
                title="Parent Support Circle",
                description="Monthly virtual circle for autism parent caregivers.",
                month_str="MAY",
                day_str="24",
                time_str="Sat, 10:00 AM",
                location="Online",
                event_type="Virtual Circle",
            )
            db.add(event1)

            event2 = Event(
                id="event-2",
                title="Mindful Caregiving",
                description="Stress regulation and mindfulness strategies for caregivers.",
                month_str="MAY",
                day_str="27",
                time_str="Tue, 07:00 PM",
                location="Online",
                event_type="Wellness Webinar",
            )
            db.add(event2)

            event3 = Event(
                id="event-3",
                title="Autism & Communication Workshop",
                description="Practical AAC and non-verbal communication strategies.",
                month_str="JUN",
                day_str="02",
                time_str="Sun, 11:00 AM",
                location="Community Center",
                event_type="In-Person Workshop",
            )
            db.add(event3)
            db.commit()

        # Seed Safety demo data: Child, Device, SafeZone, Emergency Contact
        from app.models.child import Child
        from app.models.device import Device
        from app.models.safe_zone import SafeZone
        from app.models.emergency_contact import EmergencyContact
        from app.models.location import Location

        leo = db.query(Child).filter(Child.id == "child-leo-1").first()
        if not leo:
            leo = Child(
                id="child-leo-1",
                caregiver_id="user-verified-sarah",
                name="Leo Mitchell",
                age=7,
                gender="Male",
                autism_level="Level 2",
                medical_notes="Sensitive to loud sirens. Non-verbal under acute distress.",
                tracking_enabled=True,
                current_status="safe",
            )
            db.add(leo)
            db.commit()

            band = Device(
                id="dev-band-leo-1",
                child_id="child-leo-1",
                device_name="NIVARA Smart SafeBand",
                device_type="gps_band",
                serial_number="NIVARA-BAND-LEO-001",
                battery_level=92,
                is_active=True,
                is_online=True,
            )
            db.add(band)

            home_zone = SafeZone(
                id="sz-home-1",
                child_id="child-leo-1",
                name="Home (Safe Haven)",
                zone_type="circle",
                center_latitude=37.7749,
                center_longitude=-122.4194,
                radius_meters=200.0,
                address="123 Serenity Way, San Francisco, CA",
                is_active=True,
                alert_on_exit=True,
            )
            db.add(home_zone)

            contact = EmergencyContact(
                id="contact-emily-1",
                user_id="user-verified-sarah",
                child_id="child-leo-1",
                name="Dr. Emily Watson",
                relationship_type="Behavioral Specialist",
                phone_number="+1-555-0199",
                priority_order=1,
                notify_via_sms=True,
                notify_via_call=True,
            )
            db.add(contact)

            loc = Location(
                id="loc-init-1",
                child_id="child-leo-1",
                device_id="dev-band-leo-1",
                latitude=37.7750,
                longitude=-122.4195,
                accuracy=4.2,
                speed=0.0,
                heading=90.0,
                battery_level=92.0,
                address="123 Serenity Way, San Francisco, CA",
            )
            db.add(loc)
            db.commit()

            # Seed AAC Categories and Cards if not present
            if db.query(AACCategory).count() == 0:
                cat_quick = AACCategory(id="cat-quick", name="Quick Needs", icon="⭐", color="#2563EB", order=1)
                cat_food = AACCategory(id="cat-food", name="Food", icon="🍴", color="#F59E0B", order=2)
                cat_drink = AACCategory(id="cat-drink", name="Drink", icon="🥤", color="#3B82F6", order=3)
                cat_feelings = AACCategory(id="cat-feelings", name="Feelings", icon="❤️", color="#EF4444", order=4)
                cat_actions = AACCategory(id="cat-actions", name="Actions", icon="🏃", color="#10B981", order=5)
                cat_play = AACCategory(id="cat-play", name="Play", icon="🧸", color="#8B5CF6", order=6)
                db.add_all([cat_quick, cat_food, cat_drink, cat_feelings, cat_actions, cat_play])
                db.commit()

                cards = [
                    # Quick Needs
                    AACCard(id="card-water", category_id="cat-quick", label="Water", spoken_text="I want water, please.", icon="💧", part_of_speech="noun", is_quick_need=True, usage_count=45),
                    AACCard(id="card-food", category_id="cat-quick", label="Food", spoken_text="I want food, please.", icon="🍴", part_of_speech="noun", is_quick_need=True, usage_count=42),
                    AACCard(id="card-toilet", category_id="cat-quick", label="Toilet", spoken_text="I need to use the bathroom, please.", icon="🚻", part_of_speech="noun", is_quick_need=True, usage_count=38),
                    AACCard(id="card-help", category_id="cat-quick", label="Help", spoken_text="Please help me.", icon="🛟", part_of_speech="verb", is_quick_need=True, usage_count=36),
                    AACCard(id="card-sleep", category_id="cat-quick", label="Sleep", spoken_text="I am tired and want to rest.", icon="🛏️", part_of_speech="noun", is_quick_need=True, usage_count=29),
                    AACCard(id="card-play", category_id="cat-quick", label="Play", spoken_text="I want to play.", icon="🚗", part_of_speech="verb", is_quick_need=True, usage_count=31),
                    AACCard(id="card-quiet", category_id="cat-quick", label="Quiet", spoken_text="It is too loud. I need quiet.", icon="🤫", part_of_speech="adjective", is_quick_need=True, usage_count=20),
                    AACCard(id="card-hug", category_id="cat-quick", label="Hug", spoken_text="Can I have a hug, please?", icon="🫂", part_of_speech="noun", is_quick_need=True, usage_count=24),

                    # Common Pronouns & Action Connectors
                    AACCard(id="card-i", category_id="cat-actions", label="I", spoken_text="I", icon="👤", part_of_speech="pronoun", usage_count=80),
                    AACCard(id="card-want", category_id="cat-actions", label="WANT", spoken_text="want", icon="👋", part_of_speech="verb", usage_count=75),
                    AACCard(id="card-need", category_id="cat-actions", label="NEED", spoken_text="need", icon="✋", part_of_speech="verb", usage_count=60),
                    AACCard(id="card-feel", category_id="cat-actions", label="FEEL", spoken_text="feel", icon="❤️", part_of_speech="verb", usage_count=50),
                    AACCard(id="card-stop", category_id="cat-actions", label="STOP", spoken_text="please stop", icon="🛑", part_of_speech="verb", is_quick_need=True, usage_count=35),
                    AACCard(id="card-yes", category_id="cat-actions", label="YES", spoken_text="yes", icon="✅", part_of_speech="adverb", is_quick_need=True, usage_count=40),
                    AACCard(id="card-no", category_id="cat-actions", label="NO", spoken_text="no", icon="❌", part_of_speech="adverb", is_quick_need=True, usage_count=40),

                    # Food & Drink
                    AACCard(id="card-apple", category_id="cat-food", label="Apple", spoken_text="apple", icon="🍎", part_of_speech="noun", usage_count=12),
                    AACCard(id="card-bread", category_id="cat-food", label="Bread", spoken_text="bread", icon="🍞", part_of_speech="noun", usage_count=10),
                    AACCard(id="card-juice", category_id="cat-drink", label="Juice", spoken_text="juice", icon="🧃", part_of_speech="noun", usage_count=18),
                    AACCard(id="card-milk", category_id="cat-drink", label="Milk", spoken_text="milk", icon="🥛", part_of_speech="noun", usage_count=15),

                    # Feelings
                    AACCard(id="card-happy", category_id="cat-feelings", label="Happy", spoken_text="happy", icon="😊", part_of_speech="adjective", usage_count=22),
                    AACCard(id="card-sad", category_id="cat-feelings", label="Sad", spoken_text="sad", icon="😢", part_of_speech="adjective", usage_count=14),
                    AACCard(id="card-angry", category_id="cat-feelings", label="Angry", spoken_text="angry", icon="😡", part_of_speech="adjective", usage_count=9),
                    AACCard(id="card-anxious", category_id="cat-feelings", label="Anxious", spoken_text="worried", icon="😰", part_of_speech="adjective", usage_count=11),
                ]
                db.add_all(cards)
                db.commit()

            # Seed Default Common Communication Phrases
            if db.query(SavedPhrase).count() == 0:
                common_phrases = [
                    SavedPhrase(id="phrase-help", text="I need help", category="Emergency & Help", icon="🆘", is_favorite=False, usage_count=50, use_count=50),
                    SavedPhrase(id="phrase-hungry", text="I am hungry", category="Food & Drink", icon="🍽️", is_favorite=False, usage_count=45, use_count=45),
                    SavedPhrase(id="phrase-thirsty", text="I am thirsty", category="Food & Drink", icon="🥤", is_favorite=False, usage_count=40, use_count=40),
                    SavedPhrase(id="phrase-break", text="I need a break", category="Comfort & Calm", icon="⏸️", is_favorite=False, usage_count=35, use_count=35),
                    SavedPhrase(id="phrase-play", text="I want to play", category="Activities", icon="🧸", is_favorite=False, usage_count=30, use_count=30),
                    SavedPhrase(id="phrase-toilet", text="I need the toilet", category="Daily Needs", icon="🚻", is_favorite=False, usage_count=38, use_count=38),
                    SavedPhrase(id="phrase-uncomfortable", text="I feel uncomfortable", category="Feelings", icon="😣", is_favorite=False, usage_count=20, use_count=20),
                    SavedPhrase(id="phrase-please-help", text="Please help me", category="Emergency & Help", icon="🙏", is_favorite=False, usage_count=28, use_count=28),
                    SavedPhrase(id="phrase-yes", text="Yes, please", category="Quick Responses", icon="👍", is_favorite=False, usage_count=60, use_count=60),
                    SavedPhrase(id="phrase-no", text="No, thank you", category="Quick Responses", icon="✋", is_favorite=False, usage_count=55, use_count=55),
                ]
                db.add_all(common_phrases)
                db.commit()

            # Seed Default Routines & Steps
            if db.query(Routine).count() == 0:
                morning_routine = Routine(
                    id="routine-morning-1",
                    title="Morning Sunshine Routine",
                    time_of_day="morning",
                    icon="🌅",
                    color="#3B82F6",
                    streak_days=4,
                )
                db.add(morning_routine)
                db.commit()

                steps = [
                    RoutineStep(routine_id=morning_routine.id, step_number=1, title="Wake up & stretch", instruction="Gentle stretches and open curtains.", icon="🧘", duration_sec=60, is_completed=True),
                    RoutineStep(routine_id=morning_routine.id, step_number=2, title="Brush teeth", instruction="Scrub circles on top and bottom.", icon="🪥", duration_sec=120, is_completed=True),
                    RoutineStep(routine_id=morning_routine.id, step_number=3, title="Wash face & hands", instruction="Warm water and dry with soft towel.", icon="🧼", duration_sec=60, is_completed=False),
                    RoutineStep(routine_id=morning_routine.id, step_number=4, title="Put on clothes", instruction="Shirt, pants, and cozy socks.", icon="👕", duration_sec=180, is_completed=False),
                    RoutineStep(routine_id=morning_routine.id, step_number=5, title="Healthy breakfast", instruction="Eat breakfast and drink a glass of water.", icon="🥣", duration_sec=600, is_completed=False),
                ]
                db.add_all(steps)

                bedtime_routine = Routine(
                    id="routine-bedtime-1",
                    title="Calm Bedtime Wind-Down",
                    time_of_day="bedtime",
                    icon="🌙",
                    color="#8B5CF6",
                    streak_days=6,
                )
                db.add(bedtime_routine)
                db.commit()

                bed_steps = [
                    RoutineStep(routine_id=bedtime_routine.id, step_number=1, title="Put on pajamas", instruction="Cozy nightwear.", icon="🧸", duration_sec=120, is_completed=False),
                    RoutineStep(routine_id=bedtime_routine.id, step_number=2, title="Night tooth brushing", instruction="2 minutes clean teeth.", icon="🪥", duration_sec=120, is_completed=False),
                    RoutineStep(routine_id=bedtime_routine.id, step_number=3, title="Bedtime social story", instruction="Read 1 story together in dim light.", icon="📖", duration_sec=300, is_completed=False),
                    RoutineStep(routine_id=bedtime_routine.id, step_number=4, title="White noise & lights off", instruction="Cozy blanket and sweet dreams.", icon="🌌", duration_sec=60, is_completed=False),
                ]
                db.add_all(bed_steps)
                db.commit()

            # Seed Reminders
            if db.query(Reminder).count() == 0:
                rems = [
                    Reminder(id="rem-water-1", title="Drink Water (Hydration Break)", time_str="10:00 AM", frequency="Daily", category="Hydration", icon="💧", is_active=True),
                    Reminder(id="rem-sensory-1", title="5-Minute Sensory Calming Break", time_str="02:30 PM", frequency="Weekdays", category="Sensory Break", icon="🎧", is_active=True),
                    Reminder(id="rem-homework-1", title="Visual Learning & Puzzle Time", time_str="04:30 PM", frequency="Weekdays", category="Routine", icon="🧩", is_active=True),
                ]
                db.add_all(rems)
                db.commit()

            # Seed Learning Topics
            if db.query(LearningTopic).count() == 0:
                topics = [
                    LearningTopic(
                        id="topic-social-1",
                        title="Taking Turns on the Playground",
                        category="Social Stories",
                        description="Learn how to share swings and ask friends to play together politely.",
                        icon="🛝",
                        color="#10B981",
                        progress_pct=60,
                        modules=[
                            {"title": "When the swing is busy", "text": "We wait on the bench and count to 20.", "icon": "⏳"},
                            {"title": "Magic words", "text": "'May I have a turn next, please?'", "icon": "✨"},
                        ]
                    ),
                    LearningTopic(
                        id="topic-emotion-1",
                        title="When Noises Get Too Loud",
                        category="Emotion Regulation",
                        description="Steps to handle loud sirens, blenders, or crowded rooms peacefully.",
                        icon="🎧",
                        color="#3B82F6",
                        progress_pct=85,
                        modules=[
                            {"title": "Recognizing the feeling", "text": "Ears hurt or body feels tense.", "icon": "👂"},
                            {"title": "Put on headphones", "text": "Reach into backpack for your quiet headphones.", "icon": "🎧"},
                            {"title": "Ask for quiet space", "text": "Show the 'Too Loud' card to adult.", "icon": "💬"},
                        ]
                    ),
                    LearningTopic(
                        id="topic-skills-1",
                        title="Tying Shoes Step-by-Step",
                        category="Daily Life Skills",
                        description="Bunny ears method made simple with visual colors.",
                        icon="👟",
                        color="#F59E0B",
                        progress_pct=40,
                    ),
                    LearningTopic(
                        id="topic-science-1",
                        title="Secrets of the Solar System",
                        category="Science & Nature",
                        description="Meet the 8 planets and their moons with fun analogies.",
                        icon="🪐",
                        color="#8B5CF6",
                        progress_pct=100,
                        is_completed=True,
                    ),
                ]
                db.add_all(topics)
                db.commit()

    finally:
        db.close()

@app.on_event("startup")
def on_startup():
    startup_event()
