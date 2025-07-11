import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { mobileApiService, JournalStats } from '../services/api';
import { mobileSyncService } from '../services/syncService';
import { mobileStorageService } from '../services/storage';

export default function HomeScreen({ navigation }: any) {
  const [stats, setStats] = useState<JournalStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [syncStatus, setSyncStatus] = useState<{
    isOnline: boolean;
    draftCount: number;
    needsSync: boolean;
  } | null>(null);

  useEffect(() => {
    loadStats();
    loadSyncStatus();
    
    // Auto-sync when component mounts
    mobileSyncService.autoSync();
  }, []);

  const loadSyncStatus = async () => {
    try {
      const status = await mobileSyncService.getSyncStatus();
      setSyncStatus(status);
    } catch (error) {
      console.error('Failed to load sync status:', error);
    }
  };

  const loadStats = async () => {
    try {
      setLoading(true);
      const statsData = await mobileApiService.getJournalStats();
      setStats(statsData);
    } catch (error) {
      console.error('Failed to load stats:', error);
      Alert.alert('Error', 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const handleQuickEntry = () => {
    navigation.navigate('Journal');
  };

  const handleSync = async () => {
    try {
      const result = await mobileSyncService.syncDraftEntries();
      if (result.success) {
        Alert.alert('Sync Complete! ✅', `Synced ${result.syncedEntries} entries`);
        loadSyncStatus(); // Refresh sync status
      } else {
        Alert.alert('Sync Failed', result.errors.join('\n'));
      }
    } catch (error) {
      Alert.alert('Sync Error', 'Failed to sync entries');
    }
  };

  if (loading) {
    return (
      <View style={[styles.container, styles.centered]}>
        <Text style={styles.loadingText}>Loading...</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.welcomeText}>Welcome back! 👋</Text>
        <Text style={styles.subtitleText}>How are you feeling today?</Text>
      </View>

      {/* Sync Status */}
      {syncStatus && (
        <View style={styles.syncStatusContainer}>
          <View style={styles.syncStatus}>
            <Ionicons 
              name={syncStatus.isOnline ? "cloud-done" : "cloud-offline"} 
              size={16} 
              color={syncStatus.isOnline ? "#10B981" : "#64748B"} 
            />
            <Text style={styles.syncStatusText}>
              {syncStatus.isOnline ? "Online" : "Offline"}
            </Text>
            {syncStatus.draftCount > 0 && (
              <TouchableOpacity style={styles.syncButton} onPress={handleSync}>
                <Text style={styles.syncButtonText}>
                  Sync {syncStatus.draftCount} drafts
                </Text>
              </TouchableOpacity>
            )}
          </View>
        </View>
      )}

      {/* Quick Entry Button */}
      <TouchableOpacity style={styles.quickEntryButton} onPress={handleQuickEntry}>
        <Ionicons name="create" size={24} color="white" />
        <Text style={styles.quickEntryText}>Quick Check-in</Text>
      </TouchableOpacity>

      {/* Stats Cards */}
      {stats && (
        <View style={styles.statsContainer}>
          <View style={styles.statsRow}>
            <View style={styles.statCard}>
              <Text style={styles.statNumber}>{stats.total_entries}</Text>
              <Text style={styles.statLabel}>Total Entries</Text>
            </View>
            <View style={styles.statCard}>
              <Text style={styles.statNumber}>{stats.current_streak}</Text>
              <Text style={styles.statLabel}>Current Streak</Text>
            </View>
          </View>

          <View style={styles.statsRow}>
            <View style={styles.statCard}>
              <Text style={styles.statNumber}>{stats.average_mood.toFixed(1)}</Text>
              <Text style={styles.statLabel}>Avg Mood</Text>
            </View>
            <View style={styles.statCard}>
              <Text style={styles.statNumber}>{stats.average_energy.toFixed(1)}</Text>
              <Text style={styles.statLabel}>Avg Energy</Text>
            </View>
          </View>
        </View>
      )}

      {/* Quick Actions */}
      <View style={styles.actionsContainer}>
        <TouchableOpacity 
          style={styles.actionButton}
          onPress={() => navigation.navigate('History')}
        >
          <Ionicons name="calendar" size={20} color="#8B5CF6" />
          <Text style={styles.actionText}>View History</Text>
        </TouchableOpacity>

        <TouchableOpacity 
          style={styles.actionButton}
          onPress={() => navigation.navigate('Insights')}
        >
          <Ionicons name="analytics" size={20} color="#8B5CF6" />
          <Text style={styles.actionText}>View Insights</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8FAFC',
  },
  centered: {
    justifyContent: 'center',
    alignItems: 'center',
  },
  header: {
    padding: 20,
    paddingTop: 10,
  },
  welcomeText: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1E293B',
    marginBottom: 5,
  },
  subtitleText: {
    fontSize: 16,
    color: '#64748B',
  },
  syncStatusContainer: {
    paddingHorizontal: 20,
    paddingBottom: 10,
  },
  syncStatus: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'white',
    borderRadius: 8,
    padding: 12,
    gap: 8,
  },
  syncStatusText: {
    fontSize: 14,
    color: '#64748B',
    flex: 1,
  },
  syncButton: {
    backgroundColor: '#8B5CF6',
    borderRadius: 6,
    paddingHorizontal: 12,
    paddingVertical: 6,
  },
  syncButtonText: {
    color: 'white',
    fontSize: 12,
    fontWeight: '600',
  },
  loadingText: {
    fontSize: 16,
    color: '#64748B',
  },
  quickEntryButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#8B5CF6',
    marginHorizontal: 20,
    paddingVertical: 15,
    borderRadius: 12,
    marginBottom: 20,
  },
  quickEntryText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
    marginLeft: 8,
  },
  statsContainer: {
    paddingHorizontal: 20,
    marginBottom: 20,
  },
  statsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 15,
  },
  statCard: {
    backgroundColor: 'white',
    padding: 20,
    borderRadius: 12,
    flex: 0.48,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  statNumber: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#8B5CF6',
    marginBottom: 5,
  },
  statLabel: {
    fontSize: 12,
    color: '#64748B',
    textAlign: 'center',
  },
  actionsContainer: {
    paddingHorizontal: 20,
    paddingBottom: 20,
  },
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'white',
    padding: 15,
    borderRadius: 12,
    marginBottom: 10,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  actionText: {
    fontSize: 16,
    color: '#1E293B',
    marginLeft: 10,
    fontWeight: '500',
  },
}); 