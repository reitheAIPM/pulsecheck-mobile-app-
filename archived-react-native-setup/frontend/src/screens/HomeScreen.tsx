import React, { useEffect, useState, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Alert,
  RefreshControl,
  ActivityIndicator,
  FlatList,
  Image,
  StatusBar,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { JournalStats, JournalEntry } from '../types';
import apiService from '../services/api';

interface HomeScreenProps {
  navigation: any;
}

interface JournalPost extends JournalEntry {
  aiReactions?: string[];
  aiComment?: string;
  aiCommentTime?: string;
  likes?: number;
}

const HomeScreen: React.FC<HomeScreenProps> = ({ navigation }) => {
  const [stats, setStats] = useState<JournalStats | null>(null);
  const [journalPosts, setJournalPosts] = useState<JournalPost[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboardData();
    
    // Test API connection
    const testConnection = async () => {
      try {
        console.log('🔗 Testing API connection...');
        const isConnected = await apiService.testConnection();
        console.log('✅ API connection test:', isConnected ? 'SUCCESS' : 'FAILED');
      } catch (error) {
        console.error('❌ API connection test failed:', error);
      }
    };
    
    testConnection();
  }, []);

  const loadDashboardData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      console.log('🔄 Loading dashboard data...');
      
      // Load stats and recent entries in parallel
      const [statsData, entriesData] = await Promise.all([
        apiService.getJournalStats(),
        apiService.getJournalEntries(1, 10) // Get first page with 10 entries
      ]);
      
      console.log('✅ Dashboard data loaded successfully');
      console.log('📊 Stats:', statsData);
      console.log('📝 Entries count:', entriesData.entries?.length || 0);
      
      setStats(statsData);
      
      // Transform entries into social media posts with AI interactions
      const posts: JournalPost[] = entriesData.entries.map((entry, index) => ({
        ...entry,
        aiReactions: getAIReactions(entry),
        aiComment: getAIComment(entry),
        aiCommentTime: getAICommentTime(entry.created_at),
        likes: Math.floor(Math.random() * 5) + 1, // Placeholder for now
      }));
      
      setJournalPosts(posts);
    } catch (error: any) {
      console.error('❌ Error loading dashboard:', error);
      console.error('🔍 Error details:', {
        message: error.message,
        status: error.response?.status,
        url: error.config?.url,
        data: error.response?.data,
        fullError: JSON.stringify(error.response?.data, null, 2)
      });
      
      // Enhanced error handling with fallback data
      if (error.response?.status === 500) {
        console.log('🔄 Using fallback data due to 500 error...');
        
        // Provide fallback data so user can still see the UI
        const fallbackStats: JournalStats = {
          total_entries: 0,
          current_streak: 0,
          longest_streak: 0,
          average_mood: 5.0,
          average_energy: 5.0,
          average_stress: 5.0,
          last_entry_date: undefined,
          mood_trend: "stable",
          energy_trend: "stable",
          stress_trend: "stable"
        };
        
        const fallbackPosts: JournalPost[] = [
          {
            id: "fallback-1",
            user_id: "user_123",
            content: "Welcome to PulseCheck! This is a demo post. Create your first journal entry to get started.",
            mood_level: 7,
            energy_level: 6,
            stress_level: 4,
            sleep_hours: undefined,
            work_hours: undefined,
            tags: [],
            work_challenges: [],
            gratitude_items: [],
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
            aiReactions: ['💬', '🧠', '❤️', '👍'],
            aiComment: "Welcome to your wellness journey! I'm Pulse, your AI companion. Share your thoughts and I'll be here to support you.",
            aiCommentTime: "Just now",
            likes: 3
          }
        ];
        
        setStats(fallbackStats);
        setJournalPosts(fallbackPosts);
        setError('Connection issue - showing demo data. Pull down to refresh.');
      } else if (error.response?.status === 401) {
        setError('Session expired. Please log in again.');
      } else if (error.response?.status === 404) {
        setError('Data not found. Please try refreshing.');
      } else if (error.message?.includes('Network Error')) {
        setError('Network connection issue. Please check your internet connection.');
      } else {
        setError(`Failed to load your wellness feed: ${error.message || 'Unknown error'}`);
      }
    } finally {
      setLoading(false);
    }
  }, []);

  const getAIReactions = (entry: JournalEntry): string[] => {
    // AI reactions based on entry content and mood
    const reactions = ['💬', '🧠', '❤️'];
    
    if (entry.mood_level >= 7) {
      reactions.push('👍', '💪', '🔥');
    } else if (entry.mood_level <= 4) {
      reactions.push('🤗', '☕', '🌱');
    }
    
    if (entry.stress_level >= 7) {
      reactions.push('🧘', '💆', '🫂');
    }
    
    return reactions.slice(0, 4); // Max 4 reactions
  };

  const getAIComment = (entry: JournalEntry): string => {
    // Placeholder AI comments - will be replaced with real AI responses
    const comments = [
      "That sounds like a lot to process. How are you feeling about it now?",
      "I see you're really pushing through. Remember to give yourself credit for that.",
      "This kind of day can be draining. What would help you recharge?",
      "You're showing real resilience here. What's giving you strength?",
      "I notice you've been journaling consistently. That's a powerful habit!",
    ];
    
    return comments[Math.floor(Math.random() * comments.length)];
  };

  const getAICommentTime = (entryTime: string): string => {
    const entryDate = new Date(entryTime);
    const now = new Date();
    const diffHours = Math.floor((now.getTime() - entryDate.getTime()) / (1000 * 60 * 60));
    
    if (diffHours < 1) return "Just now";
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${Math.floor(diffHours / 24)}d ago`;
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadDashboardData();
    setRefreshing(false);
  };

  const handleNewJournalEntry = () => {
    navigation.navigate('JournalEntry');
  };

  const handleRetry = () => {
    loadDashboardData();
  };

  const getMoodEmoji = (mood: number): string => {
    if (mood >= 9) return '😄';
    if (mood >= 7) return '😊';
    if (mood >= 5) return '😐';
    if (mood >= 3) return '😟';
    return '😢';
  };

  const getMoodColor = (mood: number): string => {
    if (mood >= 9) return '#4CAF50'; // Green
    if (mood >= 7) return '#8BC34A'; // Light Green
    if (mood >= 5) return '#FFC107'; // Amber
    if (mood >= 3) return '#FF9800'; // Orange
    return '#F44336'; // Red
  };

  const renderJournalPost = ({ item }: { item: JournalPost }) => (
    <View style={styles.postCard}>
      {/* Post Header */}
      <View style={styles.postHeader}>
        <View style={styles.userInfo}>
          <View style={[styles.avatar, { backgroundColor: getMoodColor(item.mood_level) }]}>
            <Text style={styles.avatarText}>{getMoodEmoji(item.mood_level)}</Text>
          </View>
          <View>
            <Text style={styles.userName}>You</Text>
            <Text style={styles.postTime}>
              {new Date(item.created_at).toLocaleDateString('en-US', {
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
              })}
            </Text>
          </View>
        </View>
        <TouchableOpacity style={styles.moreButton}>
          <Ionicons name="ellipsis-horizontal" size={20} color="#666" />
        </TouchableOpacity>
      </View>

      {/* Post Content */}
      <Text style={styles.postContent}>{item.content}</Text>

      {/* Post Metrics - More subtle design */}
      <View style={styles.postMetrics}>
        <View style={styles.metricChip}>
          <Ionicons name="happy-outline" size={14} color="#666" />
          <Text style={styles.metricText}>Mood {item.mood_level}/10</Text>
        </View>
        <View style={styles.metricChip}>
          <Ionicons name="flash-outline" size={14} color="#666" />
          <Text style={styles.metricText}>Energy {item.energy_level}/10</Text>
        </View>
        <View style={styles.metricChip}>
          <Ionicons name="pulse-outline" size={14} color="#666" />
          <Text style={styles.metricText}>Stress {item.stress_level}/10</Text>
        </View>
      </View>

      {/* AI Reactions */}
      {item.aiReactions && item.aiReactions.length > 0 && (
        <View style={styles.aiReactionsContainer}>
          <View style={styles.reactionsRow}>
            {item.aiReactions.map((reaction, index) => (
              <Text key={index} style={styles.reactionEmoji}>{reaction}</Text>
            ))}
            <Text style={styles.aiLabel}>Pulse reacted</Text>
          </View>
        </View>
      )}

      {/* AI Comment */}
      {item.aiComment && (
        <View style={styles.aiCommentContainer}>
          <View style={styles.aiCommentHeader}>
            <View style={styles.aiAvatarContainer}>
              <View style={styles.aiAvatar}>
                <Text>🧠</Text>
              </View>
              <Text style={styles.aiName}>Pulse</Text>
            </View>
            <Text style={styles.aiCommentTime}>{item.aiCommentTime}</Text>
          </View>
          <Text style={styles.aiCommentText}>{item.aiComment}</Text>
        </View>
      )}

      {/* Action Buttons */}
      <View style={styles.postActions}>
        <TouchableOpacity style={styles.actionButton}>
          <Ionicons name="heart-outline" size={22} color="#666" />
          <Text style={styles.actionText}>{item.likes}</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.actionButton}>
          <Ionicons name="chatbubble-outline" size={22} color="#666" />
          <Text style={styles.actionText}>Reply</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.actionButton}>
          <Ionicons name="share-social-outline" size={22} color="#666" />
        </TouchableOpacity>
        <TouchableOpacity style={styles.actionButton}>
          <Ionicons name="bookmark-outline" size={22} color="#666" />
        </TouchableOpacity>
      </View>
    </View>
  );

  if (loading) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#4A90E2" />
        <Text style={styles.loadingText}>Loading your wellness feed...</Text>
        <Text style={styles.loadingSubtext}>Gathering your latest posts</Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.centerContainer}>
        <Ionicons 
          name="alert-circle" 
          size={48} 
          color="#E74C3C" 
        />
        <Text style={styles.errorTitle}>Something went wrong</Text>
        <Text style={styles.errorMessage}>{error}</Text>
        
        <TouchableOpacity style={styles.retryButton} onPress={handleRetry}>
          <Ionicons name="refresh" size={20} color="white" />
          <Text style={styles.retryButtonText}>Try Again</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor="#ffffff" />
      
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.greeting}>Wellness Feed</Text>
        <View style={styles.headerIcons}>
          <TouchableOpacity style={styles.headerIcon}>
            <Ionicons name="notifications-outline" size={24} color="#333" />
          </TouchableOpacity>
          <TouchableOpacity style={styles.headerIcon}>
            <Ionicons name="search-outline" size={24} color="#333" />
          </TouchableOpacity>
        </View>
      </View>

      {/* Journal Posts Feed */}
      <FlatList
        data={journalPosts}
        renderItem={renderJournalPost}
        keyExtractor={(item) => item.id.toString()}
        style={styles.feedContainer}
        contentContainerStyle={styles.feedContentContainer}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        ListEmptyComponent={
          <View style={styles.emptyState}>
            <Ionicons name="journal-outline" size={64} color="#ccc" />
            <Text style={styles.emptyTitle}>No entries yet</Text>
            <Text style={styles.emptySubtitle}>Share your first thought to get started</Text>
            <TouchableOpacity 
              style={styles.emptyButton}
              onPress={handleNewJournalEntry}
            >
              <Text style={styles.emptyButtonText}>Create First Entry</Text>
            </TouchableOpacity>
          </View>
        }
      />

      {/* Floating Action Button */}
      <TouchableOpacity 
        style={styles.fab}
        onPress={handleNewJournalEntry}
      >
        <Ionicons name="add" size={24} color="white" />
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#f8f9fa',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    paddingTop: 40,
    backgroundColor: 'white',
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  greeting: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#333',
  },
  headerIcons: {
    flexDirection: 'row',
  },
  headerIcon: {
    marginLeft: 16,
    padding: 4,
  },
  feedContainer: {
    flex: 1,
  },
  feedContentContainer: {
    paddingBottom: 20,
  },
  postCard: {
    backgroundColor: 'white',
    marginHorizontal: 0,
    marginVertical: 8,
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
    borderTopWidth: 1,
    borderTopColor: '#f0f0f0',
  },
  postHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  userInfo: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  avatar: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  avatarText: {
    fontSize: 20,
  },
  userName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  postTime: {
    fontSize: 12,
    color: '#888',
    marginTop: 2,
  },
  moreButton: {
    padding: 8,
  },
  postContent: {
    fontSize: 16,
    lineHeight: 24,
    color: '#333',
    marginBottom: 12,
  },
  postMetrics: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginBottom: 12,
  },
  metricChip: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#f8f9fa',
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 16,
    marginRight: 8,
    marginBottom: 8,
  },
  metricText: {
    fontSize: 12,
    color: '#666',
    marginLeft: 4,
  },
  aiReactionsContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
    paddingVertical: 8,
    borderTopWidth: 1,
    borderTopColor: '#f5f5f5',
  },
  aiLabel: {
    fontSize: 12,
    color: '#888',
    marginLeft: 8,
  },
  reactionsRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  reactionEmoji: {
    fontSize: 18,
    marginRight: 2,
  },
  aiCommentContainer: {
    backgroundColor: '#f8f9fa',
    borderRadius: 12,
    padding: 12,
    marginBottom: 12,
  },
  aiCommentHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  aiAvatarContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  aiAvatar: {
    width: 28,
    height: 28,
    borderRadius: 14,
    backgroundColor: '#e1f5fe',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 8,
  },
  aiName: {
    fontSize: 14,
    fontWeight: '600',
    color: '#4A90E2',
  },
  aiCommentTime: {
    fontSize: 12,
    color: '#888',
  },
  aiCommentText: {
    fontSize: 14,
    lineHeight: 20,
    color: '#333',
  },
  postActions: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: '#f5f5f5',
  },
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
    paddingHorizontal: 4,
  },
  actionText: {
    fontSize: 14,
    color: '#666',
    marginLeft: 4,
  },
  fab: {
    position: 'absolute',
    bottom: 20,
    right: 20,
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: '#4A90E2',
    justifyContent: 'center',
    alignItems: 'center',
    elevation: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 4,
  },
  emptyState: {
    alignItems: 'center',
    justifyContent: 'center',
    padding: 40,
    height: 400,
  },
  emptyTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: '#333',
    marginTop: 16,
    marginBottom: 8,
  },
  emptySubtitle: {
    fontSize: 14,
    color: '#888',
    textAlign: 'center',
    marginBottom: 24,
  },
  emptyButton: {
    backgroundColor: '#4A90E2',
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 8,
  },
  emptyButtonText: {
    color: 'white',
    fontWeight: '600',
  },
  loadingText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#666',
    marginTop: 16,
  },
  loadingSubtext: {
    fontSize: 14,
    color: '#999',
    marginTop: 8,
  },
  errorTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#E74C3C',
    marginTop: 16,
    marginBottom: 8,
  },
  errorMessage: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
    marginBottom: 24,
  },
  retryButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#4A90E2',
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 8,
  },
  retryButtonText: {
    color: 'white',
    fontWeight: '600',
    marginLeft: 8,
  },
});

export default HomeScreen; 