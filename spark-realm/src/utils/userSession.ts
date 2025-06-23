/**
 * User Session Management for Beta Testing
 * 
 * Provides persistent user identity across browser sessions without requiring authentication.
 * Each browser gets a unique user ID that persists in localStorage.
 */

export interface UserSession {
  userId: string;
  createdAt: string;
  displayName: string;
  isBetaTester: boolean;
}

const STORAGE_KEY = 'pulsecheck_user_session';

/**
 * Generate a unique user ID for beta testing
 */
function generateUserId(): string {
  const timestamp = Date.now();
  const randomPart = Math.random().toString(36).substr(2, 9);
  return `user_${timestamp}_${randomPart}`;
}

/**
 * Generate a friendly display name for the user
 */
function generateDisplayName(): string {
  const adjectives = ['Thoughtful', 'Mindful', 'Reflective', 'Curious', 'Balanced', 'Focused', 'Calm', 'Inspired'];
  const nouns = ['Writer', 'Thinker', 'Explorer', 'Dreamer', 'Creator', 'Learner', 'Seeker', 'Builder'];
  
  const adjective = adjectives[Math.floor(Math.random() * adjectives.length)];
  const noun = nouns[Math.floor(Math.random() * nouns.length)];
  
  return `${adjective} ${noun}`;
}

/**
 * Get or create user session
 */
export function getUserSession(): UserSession {
  try {
    // Try to get existing session
    const existingSession = localStorage.getItem(STORAGE_KEY);
    if (existingSession) {
      const session = JSON.parse(existingSession) as UserSession;
      // Validate session structure
      if (session.userId && session.createdAt) {
        return session;
      }
    }
  } catch (error) {
    console.warn('Failed to parse existing user session:', error);
  }

  // Create new session
  const newSession: UserSession = {
    userId: generateUserId(),
    createdAt: new Date().toISOString(),
    displayName: generateDisplayName(),
    isBetaTester: true, // All browser sessions are beta testers
  };

  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(newSession));
  } catch (error) {
    console.error('Failed to save user session:', error);
  }

  return newSession;
}

/**
 * Get current user ID (simplified interface)
 */
export function getCurrentUserId(): string {
  return getUserSession().userId;
}

/**
 * Get current user display name
 */
export function getCurrentUserDisplayName(): string {
  return getUserSession().displayName;
}

/**
 * Check if user is a beta tester (always true for browser sessions)
 */
export function isBetaTester(): boolean {
  return getUserSession().isBetaTester;
}

/**
 * Reset user session (for testing purposes)
 */
export function resetUserSession(): UserSession {
  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch (error) {
    console.error('Failed to reset user session:', error);
  }
  return getUserSession(); // This will create a new session
}

/**
 * Get session info for debugging
 */
export function getSessionInfo(): {
  userId: string;
  displayName: string;
  createdAt: string;
  daysSinceCreated: number;
  isBetaTester: boolean;
} {
  const session = getUserSession();
  const createdDate = new Date(session.createdAt);
  const daysSinceCreated = Math.floor((Date.now() - createdDate.getTime()) / (1000 * 60 * 60 * 24));

  return {
    userId: session.userId,
    displayName: session.displayName,
    createdAt: session.createdAt,
    daysSinceCreated,
    isBetaTester: session.isBetaTester,
  };
} 