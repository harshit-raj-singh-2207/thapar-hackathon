import React, { useState, useEffect } from 'react';
import { playLikeSound, playCommentSound, playNotificationSound } from '../../utils/soundEffects';

// Default API Base URL dynamically resolves backend location
const API_BASE_URL = typeof window !== 'undefined' && window.location.origin.includes('localhost')
  ? 'http://localhost:8000/api'
  : 'http://localhost:8000/api';

export default function SocialSection() {
  const [likes, setLikes] = useState(0);
  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // 1. Fetch initial status from FastAPI
  useEffect(() => {
    fetch(`${API_BASE_URL}/post-state`)
      .then((res) => {
        if (!res.ok) throw new Error('Failed to fetch post state');
        return res.json();
      })
      .then((data) => {
        setLikes(data.likes || 0);
        setComments(data.comments || []);
        setLoading(false);
      })
      .catch((err) => {
        console.error('Error loading post data:', err);
        setError('Could not connect to backend.');
        setLoading(false);
      });
  }, []);

  // 2. Handle adding a like with audio sound feedback
  const handleLike = async () => {
    try {
      playLikeSound(); // Audio notification sound
      const response = await fetch(`${API_BASE_URL}/like`, { method: 'POST' });
      if (!response.ok) throw new Error('Like request failed');
      const data = await response.json();
      setLikes(data.likes);
    } catch (err) {
      console.error('Error liking the post:', err);
    }
  };

  // 3. Handle submitting a comment with audio sound feedback
  const handleCommentSubmit = async (e) => {
    e.preventDefault();
    if (!newComment.trim()) return;

    try {
      playCommentSound(); // Audio notification sound
      const response = await fetch(`${API_BASE_URL}/comment`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: newComment.trim() }),
      });

      if (response.ok) {
        const addedComment = await response.json();
        setComments([...comments, addedComment]); // Append comment to UI state
        setNewComment(''); // Clear text input field
      }
    } catch (err) {
      console.error('Error posting comment:', err);
    }
  };

  if (loading) {
    return (
      <div style={{ padding: '24px', textAlign: 'center', color: '#64748B', fontFamily: 'sans-serif' }}>
        ⏳ Loading community interactions...
      </div>
    );
  }

  return (
    <div
      style={{
        maxWidth: '540px',
        margin: '30px auto',
        padding: '24px',
        background: '#FFFFFF',
        border: '1px solid #E2E8F0',
        borderRadius: '16px',
        fontFamily: 'Inter, system-ui, -apple-system, sans-serif',
        boxShadow: '0 4px 16px rgba(15, 23, 42, 0.06)',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
        <h3 style={{ margin: 0, fontSize: '18px', color: '#0F172A', fontWeight: '700' }}>
          💬 Community Post & Live Interactions
        </h3>
        <span style={{ fontSize: '12px', background: '#EEF2FF', color: '#4F46E5', padding: '4px 10px', borderRadius: '12px', fontWeight: '600' }}>
          🔊 Audio Active
        </span>
      </div>

      <p style={{ color: '#64748B', fontSize: '14px', lineHeight: '1.5', marginTop: 0, marginBottom: '20px' }}>
        Interactive social dashboard connecting FastAPI backend directly to React state with real-time audio sound feedback.
      </p>

      {error && (
        <div style={{ background: '#FEF2F2', border: '1px solid #FECACA', color: '#DC2626', padding: '10px 14px', borderRadius: '8px', fontSize: '13px', marginBottom: '16px' }}>
          ⚠️ {error}
        </div>
      )}

      {/* Interaction Buttons Layout */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '15px', marginBottom: '20px' }}>
        <button
          onClick={handleLike}
          style={{
            padding: '10px 20px',
            background: 'linear-gradient(135deg, #4F46E5 0%, #3730A3 100%)',
            color: '#FFFFFF',
            border: 'none',
            borderRadius: '8px',
            cursor: 'pointer',
            fontWeight: '600',
            fontSize: '14px',
            boxShadow: '0 2px 6px rgba(79, 70, 229, 0.3)',
            transition: 'transform 0.1s ease',
          }}
          onMouseDown={(e) => (e.currentTarget.style.transform = 'scale(0.96)')}
          onMouseUp={(e) => (e.currentTarget.style.transform = 'scale(1)')}
        >
          👍 Like
        </button>
        <span style={{ fontWeight: '700', fontSize: '15px', color: '#1E293B' }}>
          {likes} {likes === 1 ? 'Like' : 'Likes'}
        </span>
      </div>

      <hr style={{ border: '0.5px solid #F1F5F9', margin: '20px 0' }} />

      {/* Comments List */}
      <h4 style={{ margin: '0 0 12px 0', color: '#334155', fontSize: '15px' }}>
        Comments ({comments.length})
      </h4>
      <ul style={{ listStyleType: 'none', paddingLeft: 0, maxHeight: '240px', overflowY: 'auto', margin: 0 }}>
        {comments.map((comment) => (
          <li
            key={comment.id}
            style={{
              background: '#F8FAFC',
              border: '1px solid #E2E8F0',
              padding: '10px 14px',
              marginBottom: '10px',
              borderRadius: '8px',
              fontSize: '14px',
              color: '#1E293B',
              lineHeight: '1.4',
            }}
          >
            {comment.text}
          </li>
        ))}
      </ul>

      {/* Comment Input Form */}
      <form onSubmit={handleCommentSubmit} style={{ display: 'flex', gap: '10px', marginTop: '18px' }}>
        <input
          type="text"
          value={newComment}
          onChange={(e) => setNewComment(e.target.value)}
          placeholder="Write a comment..."
          style={{
            flexGrow: 1,
            padding: '10px 14px',
            border: '1px solid #CBD5E1',
            borderRadius: '8px',
            fontSize: '14px',
            outline: 'none',
          }}
        />
        <button
          type="submit"
          style={{
            padding: '10px 18px',
            background: '#0F172A',
            color: '#FFFFFF',
            border: 'none',
            borderRadius: '8px',
            cursor: 'pointer',
            fontWeight: '600',
            fontSize: '14px',
          }}
        >
          Post
        </button>
      </form>
    </div>
  );
}
