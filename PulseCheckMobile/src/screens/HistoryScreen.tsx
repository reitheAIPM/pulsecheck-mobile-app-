import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, FlatList, TouchableOpacity, RefreshControl } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { JournalEntry } from '../services/api';
import { mobileSyncService } from '../services/syncService';

export default function HistoryScreen() {
  const [entries, setEntries] = useState<JournalEntry[]>([]);
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
      setEntries(result.entries);
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

  const renderEntry = ({ item }: { item: JournalEntry }) => (
    <TouchableOpacity style={styles.entryCard}>
      <Text style={styles.entryDate}>
        {new Date(item.created_at).toLocaleDateString()}
      </Text>
      <Text style={styles.entryContent} numberOfLines={2}>
        {item.content}
      </Text>
      <View style={styles.entryMoods}>
        <Text style={styles.moodText}>Mood: {item.mood_level}</Text>
        <Text style={styles.moodText}>Energy: {item.energy_level}</Text>
        <Text style={styles.moodText}>Stress: {item.stress_level}</Text>
      </View>
    </TouchableOpacity>
  );

  if (loading) {
    return (
      <View style={[styles.container, styles.centered]}>
        <Text>Loading...</Text>
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
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F8FAFC' },
  centered: { justifyContent: 'center', alignItems: 'center' },
  cacheIndicator: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', padding: 8, backgroundColor: '#F1F5F9' },
  cacheText: { fontSize: 12, color: '#64748B', marginLeft: 4 },
  listContainer: { padding: 20 },
  entryCard: { backgroundColor: 'white', borderRadius: 12, padding: 15, marginBottom: 15 },
  entryDate: { fontSize: 14, color: '#64748B', marginBottom: 8 },
  entryContent: { fontSize: 16, color: '#1E293B', marginBottom: 10 },
  entryMoods: { flexDirection: 'row', justifyContent: 'space-between' },
  moodText: { fontSize: 12, color: '#8B5CF6', fontWeight: '600' },
}); 