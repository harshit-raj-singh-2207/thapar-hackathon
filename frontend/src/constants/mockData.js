/**
 * MOCK DATA — for UI development only.
 *
 * ⚠️  This file exists ONLY to enable visual development without backend APIs.
 * ⚠️  DO NOT import this from production store/hook code.
 * ⚠️  Replace all usages with real API data (communityApi, chatStore, communityStore).
 *
 * When the backend is ready:
 *  1. Delete this file (or keep for Storybook / tests).
 *  2. Remove all imports of this file from screens.
 *  3. Wire screens to real hooks: useChat, useCommunity, etc.
 */

// ── Current user (the logged-in caregiver) ──────────────────────────────────
export const MOCK_CURRENT_USER = {
  id: 'user-me',
  name: 'Jordan Patel',
  avatarUri: null,
  isVerified: true,
  bio: 'Parent caregiver for my son with autism. Passionate about inclusive education and sensory tools.',
  groups: ['group-1', 'group-3'],
};

// ── Caregivers ──────────────────────────────────────────────────────────────
export const MOCK_CAREGIVERS = [
  {
    id: 'user-1',
    name: 'Sarah Mitchell',
    avatarUri: null,
    isVerified: true,
    isOnline: true,
    lastSeen: null,
    bio: 'ABA therapist and parent advocate. 8 years experience supporting children on the spectrum.',
    groups: ['group-1', 'group-2'],
  },
  {
    id: 'user-2',
    name: 'David Nguyen',
    avatarUri: null,
    isVerified: true,
    isOnline: false,
    lastSeen: '2026-08-12T09:00:00Z',
    bio: 'Special education teacher. Focused on communication strategies and visual supports.',
    groups: ['group-2', 'group-3'],
  },
  {
    id: 'user-3',
    name: 'Amara Okafor',
    avatarUri: null,
    isVerified: true,
    isOnline: true,
    lastSeen: null,
    bio: 'Occupational therapist specializing in sensory integration for autistic children.',
    groups: ['group-1'],
  },
  {
    id: 'user-4',
    name: 'Lisa Chen',
    avatarUri: null,
    isVerified: false,
    isOnline: false,
    lastSeen: '2026-08-11T18:30:00Z',
    bio: 'Parent of two, navigating the joys and challenges of raising neurodivergent kids.',
    groups: ['group-2'],
  },
  {
    id: 'user-5',
    name: 'Marcus Williams',
    avatarUri: null,
    isVerified: true,
    isOnline: true,
    lastSeen: null,
    bio: 'Speech-language pathologist. Love sharing resources and practical tips for AAC users.',
    groups: ['group-3'],
  },
];

// ── Conversations (chat list) ────────────────────────────────────────────────
export const MOCK_CONVERSATIONS = [
  {
    id: 'chat-1',
    name: 'Sarah Mitchell',
    avatarUri: null,
    lastMessage: 'That sensory kit idea is brilliant! 🌟',
    timestamp: '2026-08-12T20:00:00Z',
    unreadCount: 3,
    isOnline: true,
    isGroup: false,
    userId: 'user-1',
  },
  {
    id: 'chat-2',
    name: 'David Nguyen',
    avatarUri: null,
    lastMessage: 'I shared the visual schedule template.',
    timestamp: '2026-08-12T14:30:00Z',
    unreadCount: 0,
    isOnline: false,
    isGroup: false,
    userId: 'user-2',
  },
  {
    id: 'chat-3',
    name: 'Amara Okafor',
    avatarUri: null,
    lastMessage: 'Thanks for the recommendation!',
    timestamp: '2026-08-11T18:00:00Z',
    unreadCount: 0,
    isOnline: true,
    isGroup: false,
    userId: 'user-3',
  },
  {
    id: 'chat-4',
    name: 'Marcus Williams',
    avatarUri: null,
    lastMessage: 'See you at the meetup 👋',
    timestamp: '2026-08-11T09:15:00Z',
    unreadCount: 1,
    isOnline: true,
    isGroup: false,
    userId: 'user-5',
  },
];

// ── Direct messages ─────────────────────────────────────────────────────────
export const MOCK_MESSAGES = {
  'chat-1': [
    {
      id: 'msg-1',
      text: 'Hi Sarah! I saw your post about sensory rooms.',
      sentAt: '9:20 AM',
      status: 'read',
      isOwn: true,
      imageUri: null,
    },
    {
      id: 'msg-2',
      text: 'Yes! We just set one up at the center. It made such a difference for the kids.',
      sentAt: '9:22 AM',
      status: null,
      isOwn: false,
      imageUri: null,
    },
    {
      id: 'msg-3',
      text: 'That sensory kit idea is brilliant! 🌟',
      sentAt: '9:45 AM',
      status: null,
      isOwn: false,
      imageUri: null,
    },
  ],
};

// ── Groups ──────────────────────────────────────────────────────────────────
export const MOCK_MY_GROUPS = [
  {
    id: 'group-1',
    name: 'Sensory Support Circle',
    description: 'A safe space for caregivers to share sensory tools, strategies, and support for children with sensory processing differences.',
    avatarUri: null,
    memberCount: 142,
    isJoined: true,
    category: 'Sensory',
    unreadCount: 5,
    lastActivity: 'Sarah shared a new resource',
  },
  {
    id: 'group-3',
    name: 'AAC & Communication',
    description: 'Supporting non-verbal and minimally verbal children through augmentative and alternative communication.',
    avatarUri: null,
    memberCount: 89,
    isJoined: true,
    category: 'Communication',
    unreadCount: 0,
    lastActivity: '3 new messages',
  },
];

export const MOCK_DISCOVER_GROUPS = [
  {
    id: 'group-2',
    name: 'Visual Schedules & Routines',
    description: 'Share visual schedule templates and routine strategies that work for your family.',
    avatarUri: null,
    memberCount: 203,
    isJoined: false,
    category: 'Routines',
    unreadCount: 0,
    lastActivity: null,
  },
  {
    id: 'group-4',
    name: 'IEP Advocacy Network',
    description: 'Navigate IEP meetings, school placements, and educational rights together.',
    avatarUri: null,
    memberCount: 317,
    isJoined: false,
    category: 'Education',
    unreadCount: 0,
    lastActivity: null,
  },
  {
    id: 'group-5',
    name: 'Parent Self-Care Corner',
    description: 'Because you can\'t pour from an empty cup. A supportive space for caregiver wellbeing.',
    avatarUri: null,
    memberCount: 78,
    isJoined: false,
    category: 'Wellbeing',
    unreadCount: 0,
    lastActivity: null,
  },
  {
    id: 'group-6',
    name: 'Autism & Siblings',
    description: 'Supporting the neurotypical and neurodivergent siblings of autistic children.',
    avatarUri: null,
    memberCount: 95,
    isJoined: false,
    category: 'Family',
    unreadCount: 0,
    lastActivity: null,
  },
];

// ── Group messages ───────────────────────────────────────────────────────────
export const MOCK_GROUP_MESSAGES = {
  'group-1': [
    {
      id: 'gm-1',
      text: 'We started using weighted blankets and it helped so much with bedtime transitions!',
      sentAt: '9:00 AM',
      isOwn: false,
      senderId: 'user-1',
      senderName: 'Sarah',
      senderAvatar: null,
      status: null,
      imageUri: null,
    },
    {
      id: 'gm-2',
      text: 'That\'s amazing Sarah! Which brand do you recommend?',
      sentAt: '9:05 AM',
      isOwn: false,
      senderId: 'user-3',
      senderName: 'Amara',
      senderAvatar: null,
      status: null,
      imageUri: null,
    },
    {
      id: 'gm-3',
      text: 'We use SensaCalm. The 5lb one worked well for my 7 year old.',
      sentAt: '9:10 AM',
      isOwn: true,
      senderId: 'user-me',
      senderName: 'Jordan',
      senderAvatar: null,
      status: 'read',
      imageUri: null,
    },
  ],
};

// ── Community feed posts ─────────────────────────────────────────────────────
export const MOCK_POSTS = [
  {
    id: 'post-1',
    author: {
      id: 'user-1',
      name: 'Sarah Mitchell',
      avatarUri: null,
      isVerified: true,
    },
    text: 'We finally finished our sensory corner setup! 🌈 Used a pop-up tent, fairy lights, and textured cushions. My son now voluntarily goes there when he feels overwhelmed. It took 3 months to build the trust but totally worth it.\n\nHappy to share our setup list if anyone is interested!',
    imageUri: null,
    timestamp: '2026-08-12T18:00:00Z',
    commentCount: 12,
    likeCount: 47,
    isLiked: true,
  },
  {
    id: 'post-2',
    author: {
      id: 'user-2',
      name: 'David Nguyen',
      avatarUri: null,
      isVerified: true,
    },
    text: 'Reminder: You are doing an incredible job. Caregiving is one of the hardest and most meaningful things a person can do. Don\'t forget to take a moment for yourself today. 💙',
    imageUri: null,
    timestamp: '2026-08-12T14:30:00Z',
    commentCount: 8,
    likeCount: 93,
    isLiked: false,
  },
  {
    id: 'post-3',
    author: {
      id: 'user-5',
      name: 'Marcus Williams',
      avatarUri: null,
      isVerified: true,
    },
    text: 'Quick tip for AAC users: try modeling at least 100 words a day without expectations. Just model. The research shows this dramatically increases spontaneous communication over time. Any questions? Happy to chat!',
    imageUri: null,
    timestamp: '2026-08-12T10:15:00Z',
    commentCount: 21,
    likeCount: 64,
    isLiked: false,
  },
  {
    id: 'post-4',
    author: {
      id: 'user-3',
      name: 'Amara Okafor',
      avatarUri: null,
      isVerified: true,
    },
    text: 'Sharing our visual schedule template that\'s been a game-changer for our morning routine. The trick is using real photos of YOUR child doing each activity, not generic icons.',
    imageUri: null,
    timestamp: '2026-08-11T20:00:00Z',
    commentCount: 34,
    likeCount: 112,
    isLiked: true,
  },
];

// ── Post comments ────────────────────────────────────────────────────────────
export const MOCK_COMMENTS = {
  'post-1': [
    {
      id: 'comment-1',
      author: { id: 'user-2', name: 'David Nguyen', avatarUri: null, isVerified: true },
      text: 'This is so wonderful! Would love to see the setup list.',
      timestamp: '2026-08-12T18:30:00Z',
    },
    {
      id: 'comment-2',
      author: { id: 'user-3', name: 'Amara Okafor', avatarUri: null, isVerified: true },
      text: 'The pop-up tent is such a great idea. We use something similar but the fairy lights addition sounds perfect.',
      timestamp: '2026-08-12T19:00:00Z',
    },
  ],
};

// ── Group members ────────────────────────────────────────────────────────────
export const MOCK_MEMBERS = {
  'group-1': [
    { id: 'user-1', name: 'Sarah Mitchell', avatarUri: null, role: 'admin', isOnline: true },
    { id: 'user-me', name: 'Jordan Patel', avatarUri: null, role: 'member', isOnline: true },
    { id: 'user-3', name: 'Amara Okafor', avatarUri: null, role: 'member', isOnline: true },
    { id: 'user-2', name: 'David Nguyen', avatarUri: null, role: 'member', isOnline: false },
    { id: 'user-4', name: 'Lisa Chen', avatarUri: null, role: 'member', isOnline: false },
    { id: 'user-5', name: 'Marcus Williams', avatarUri: null, role: 'member', isOnline: true },
  ],
};

// ── Notifications ────────────────────────────────────────────────────────────
export const MOCK_NOTIFICATIONS = [
  {
    id: 'notif-1',
    type: 'message',
    title: 'Sarah Mitchell',
    body: 'That sensory kit idea is brilliant! 🌟',
    timestamp: '2026-08-12T20:00:00Z',
    read: false,
  },
  {
    id: 'notif-2',
    type: 'post_like',
    title: 'Community',
    body: '47 people liked your post about the sensory corner.',
    timestamp: '2026-08-12T19:00:00Z',
    read: false,
  },
  {
    id: 'notif-3',
    type: 'group',
    title: 'Sensory Support Circle',
    body: 'Sarah Mitchell posted a new resource.',
    timestamp: '2026-08-12T17:00:00Z',
    read: true,
  },
  {
    id: 'notif-4',
    type: 'comment',
    title: 'Your post',
    body: 'David Nguyen commented: "This is so wonderful!"',
    timestamp: '2026-08-12T18:30:00Z',
    read: true,
  },
];

// ── Feed filter categories ───────────────────────────────────────────────────
export const FEED_FILTERS = ['All', 'Resources', 'Tips', 'Questions', 'Support', 'Milestones'];

// ── Group categories ─────────────────────────────────────────────────────────
export const GROUP_CATEGORIES = ['All', 'Sensory', 'Communication', 'Routines', 'Education', 'Wellbeing', 'Family'];
