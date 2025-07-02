import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, FlatList, TouchableOpacity, RefreshControl } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { JournalEntry, mobileApiService } from '../services/api';
import { mobileSyncService } from '../services/syncService';

// Extended interface to include AI responses
interface JournalEntryWithAI extends JournalEntry {
  ai_response?: {
    response: string;
    persona: string;
    confidence: number;
    created_at: string;
  };
}

export default function HistoryScreen() {
  const [entries, setEntries] = useState<JournalEntryWithAI[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [isFromCache, setIsFromCache] = useState(false);

  useEffect(() => {
    loadEntries();
  }, []);

  const loadEntries = async (forceRefresh = false) => {
    try {
      if (!forceRefresh) setLoading(true);
      
      const result = await mobileSyncService.getJournalEntries(forceRefresh);
      
      // Load AI responses for each entry
      const entriesWithAI = await Promise.all(
        result.entries.map(async (entry) => {
          try {
            // Try to get AI response for this entry
            const pulseResponse = await mobileApiService.getPulseResponse(entry.id);
            return {
              ...entry,
              ai_response: {
                response: pulseResponse.insight || pulseResponse.action || "AI response generated",
                persona: "Pulse",
                confidence: 0.7,
                created_at: new Date().toISOString()
              }
            };
          } catch (error) {
            // If no AI response, return entry without it
            return entry;
          }
        })
      );
      
      setEntries(entriesWithAI);
      setIsFromCache(result.isFromCache);
    } catch (error) {
      console.error('Failed to load entries:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadEntries(true);
  };

  const renderEntry = ({ item }: { item: JournalEntryWithAI }) => (
    <View style={styles.entryCard}>
      {/* User's Journal Entry */}
      <View style={styles.userSection}>
        <View style={styles.userHeader}>
          <Ionicons name="person-circle" size={32} color="#8B5CF6" />
          <View style={styles.userInfo}>
            <Text style={styles.userName}>You</Text>
            <Text style={styles.entryDate}>
              {new Date(item.created_at).toLocaleDateString()} {new Date(item.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </Text>
          </View>
        </View>
        <Text style={styles.entryContent}>
          {item.content}
        </Text>
        <View style={styles.entryMoods}>
          <View style={styles.moodPill}>
            <Text style={styles.moodText}>😊 {item.mood_level}</Text>
          </View>
          <View style={styles.moodPill}>
            <Text style={styles.moodText}>⚡ {item.energy_level}</Text>
          </View>
          <View style={styles.moodPill}>
            <Text style={styles.moodText}>😰 {item.stress_level}</Text>
          </View>
        </View>
      </View>

      {/* AI Response (like a Twitter reply) */}
      {item.ai_response && (
        <View style={styles.aiSection}>
          <View style={styles.aiConnector} />
          <View style={styles.aiResponse}>
            <View style={styles.aiHeader}>
              <Ionicons name="sparkles" size={24} color="#10B981" />
              <View style={styles.aiInfo}>
                <Text style={styles.aiName}>Pulse AI</Text>
                <Text style={styles.aiTime}>
                  {new Date(item.ai_response.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </Text>
              </View>
              <View style={styles.aiBadge}>
                <Text style={styles.aiBadgeText}>AI</Text>
              </View>
            </View>
            <Text style={styles.aiResponseText}>
              {item.ai_response.response}
            </Text>
            <View style={styles.aiActions}>
              <TouchableOpacity style={styles.aiAction}>
                <Ionicons name="heart-outline" size={16} color="#64748B" />
                <Text style={styles.aiActionText}>Helpful</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.aiAction}>
                <Ionicons name="chatbubble-outline" size={16} color="#64748B" />
                <Text style={styles.aiActionText}>Reply</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      )}
    </View>
  );

  if (loading) {
    return (
      <View style={[styles.container, styles.centered]}>
        <Text>Loading your journal...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {isFromCache && (
        <View style={styles.cacheIndicator}>
          <Ionicons name="cloud-offline" size={16} color="#64748B" />
          <Text style={styles.cacheText}>Showing cached entries</Text>
        </View>
      )}
      <FlatList
        data={entries}
        keyExtractor={(item) => item.id}
        renderItem={renderEntry}
        contentContainerStyle={styles.listContainer}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        showsVerticalScrollIndicator={false}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F8FAFC' },
  centered: { justifyContent: 'center', alignItems: 'center' },
  cacheIndicator: { 
    flexDirection: 'row', 
    alignItems: 'center', 
    justifyContent: 'center', 
    padding: 8, 
    backgroundColor: '#F1F5F9' 
  },
  cacheText: { fontSize: 12, color: '#64748B', marginLeft: 4 },
  listContainer: { padding: 16 },
  
  // Entry Card (like a social media post)
  entryCard: { 
    backgroundColor: 'white', 
    borderRadius: 16, 
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 3,
  },
  
  // User's Journal Entry Section
  userSection: {
    padding: 16,
  },
  userHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  userInfo: {
    marginLeft: 12,
    flex: 1,
  },
  userName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1E293B',
  },
  entryDate: { 
    fontSize: 12, 
    color: '#64748B',
    marginTop: 2,
  },
  entryContent: { 
    fontSize: 16, 
    color: '#1E293B', 
    lineHeight: 24,
    marginBottom: 12,
  },
  entryMoods: { 
    flexDirection: 'row', 
    gap: 8,
  },
  moodPill: {
    backgroundColor: '#F1F5F9',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
  },
  moodText: { 
    fontSize: 12, 
    color: '#475569', 
    fontWeight: '500',
  },
  
  // AI Response Section (like a Twitter reply)
  aiSection: {
    position: 'relative',
  },
  aiConnector: {
    position: 'absolute',
    left: 32,
    top: -8,
    width: 2,
    height: 16,
    backgroundColor: '#E2E8F0',
  },
  aiResponse: {
    marginLeft: 48,
    marginRight: 16,
    marginBottom: 16,
    padding: 12,
    backgroundColor: '#F8FAFC',
    borderRadius: 12,
    borderLeftWidth: 3,
    borderLeftColor: '#10B981',
  },
  aiHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  aiInfo: {
    marginLeft: 8,
    flex: 1,
  },
  aiName: {
    fontSize: 14,
    fontWeight: '600',
    color: '#10B981',
  },
  aiTime: {
    fontSize: 11,
    color: '#64748B',
    marginTop: 1,
  },
  aiBadge: {
    backgroundColor: '#10B981',
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 4,
  },
  aiBadgeText: {
    fontSize: 10,
    color: 'white',
    fontWeight: '600',
  },
  aiResponseText: {
    fontSize: 14,
    color: '#374151',
    lineHeight: 20,
    marginBottom: 8,
  },
  aiActions: {
    flexDirection: 'row',
    gap: 16,
  },
  aiAction: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  aiActionText: {
    fontSize: 12,
    color: '#64748B',
  },
}); 