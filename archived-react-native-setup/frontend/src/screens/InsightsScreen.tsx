import React, { useEffect, useState, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  RefreshControl,
  ActivityIndicator,
  StatusBar,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { JournalStats } from '../types';
import apiService from '../services/api';

interface InsightsScreenProps {
  navigation: any;
}

const InsightsScreen: React.FC<InsightsScreenProps> = ({ navigation }) => {
  const [stats, setStats] = useState<JournalStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadInsightsData();
  }, []);

  const loadInsightsData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      console.log('🔄 Loading insights data...');
      
      // Load stats
      const statsData = await apiService.getJournalStats();
      
      console.log('✅ Insights data loaded successfully');
      console.log('📊 Stats:', statsData);
      
      setStats(statsData);
    } catch (error: any) {
      console.error('❌ Error loading insights:', error);
      
      // Enhanced error handling with fallback data
      if (error.response?.status === 500) {
        console.log('🔄 Using fallback data due to 500 error...');
        
        // Provide fallback data so user can still see the UI
        const fallbackStats: JournalStats = {
          total_entries: 12,
          current_streak: 3,
          longest_streak: 7,
          average_mood: 6.8,
          average_energy: 6.2,
          average_stress: 4.5,
          last_entry_date: new Date().toISOString(),
          mood_trend: "improving",
          energy_trend: "stable",
          stress_trend: "improving"
        };
        
        setStats(fallbackStats);
        setError('Connection issue - showing demo data. Pull down to refresh.');
      } else {
        setError(`Failed to load insights: ${error.message || 'Unknown error'}`);
      }
    } finally {
      setLoading(false);
    }
  }, []);

  const onRefresh = async () => {
    setRefreshing(true);
    await loadInsightsData();
    setRefreshing(false);
  };

  const handleRetry = () => {
    loadInsightsData();
  };

  const getMoodEmoji = (mood: number): string => {
    if (mood >= 9) return '😄';
    if (mood >= 7) return '😊';
    if (mood >= 5) return '😐';
    if (mood >= 3) return '😟';
    return '😢';
  };

  const getEnergyEmoji = (energy: number): string => {
    if (energy >= 9) return '⚡⚡';
    if (energy >= 7) return '⚡';
    if (energy >= 5) return '💡';
    if (energy >= 3) return '🔋';
    return '🪫';
  };

  const getStressEmoji = (stress: number): string => {
    if (stress >= 9) return '😰';
    if (stress >= 7) return '😓';
    if (stress >= 5) return '😐';
    if (stress >= 3) return '😌';
    return '😊';
  };

  const getTrendIcon = (trend: string | undefined): string => {
    if (trend === 'improving') return '↗️';
    if (trend === 'declining') return '↘️';
    return '→';
  };

  const getTrendColor = (trend: string | undefined): string => {
    if (trend === 'improving') return '#4CAF50';
    if (trend === 'declining') return '#F44336';
    return '#FFC107';
  };

  if (loading) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#4A90E2" />
        <Text style={styles.loadingText}>Loading your insights...</Text>
        <Text style={styles.loadingSubtext}>Analyzing your wellness data</Text>
      </View>
    );
  }

  if (error && !stats) {
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

  // Safe values for rendering
  const averageMood = stats?.average_mood || 5;
  const averageEnergy = stats?.average_energy || 5;
  const averageStress = stats?.average_stress || 5;
  const moodBarWidth = `${averageMood * 10}%`;
  const energyBarWidth = `${averageEnergy * 10}%`;
  const stressBarWidth = `${averageStress * 10}%`;

  return (
    <View style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor="#ffffff" />
      
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.greeting}>Your Insights</Text>
        <TouchableOpacity style={styles.headerIcon}>
          <Ionicons name="calendar" size={24} color="#333" />
        </TouchableOpacity>
      </View>

      <ScrollView 
        style={styles.scrollContainer}
        contentContainerStyle={styles.contentContainer}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        {/* Main Stats Card */}
        <View style={styles.mainStatsCard}>
          <Text style={styles.cardTitle}>Wellness Overview</Text>
          
          <View style={styles.statsGrid}>
            <View style={styles.statItem}>
              <Text style={styles.statValue}>{stats?.total_entries || 0}</Text>
              <Text style={styles.statLabel}>Total Entries</Text>
            </View>
            
            <View style={styles.statItem}>
              <Text style={styles.statValue}>{stats?.current_streak || 0}</Text>
              <Text style={styles.statLabel}>Day Streak 🔥</Text>
            </View>
            
            <View style={styles.statItem}>
              <Text style={styles.statValue}>{stats?.longest_streak || 0}</Text>
              <Text style={styles.statLabel}>Longest Streak</Text>
            </View>
          </View>
        </View>

        {/* Mood Card */}
        <View style={styles.insightCard}>
          <View style={styles.cardHeader}>
            <Text style={styles.cardTitle}>Mood</Text>
            <View style={[styles.trendBadge, { backgroundColor: getTrendColor(stats?.mood_trend) }]}>
              <Text style={styles.trendText}>{getTrendIcon(stats?.mood_trend)} {stats?.mood_trend || 'stable'}</Text>
            </View>
          </View>
          
          <View style={styles.moodDisplay}>
            <Text style={styles.moodEmoji}>{getMoodEmoji(averageMood)}</Text>
            <View style={styles.moodStats}>
              <Text style={styles.moodValue}>{averageMood.toFixed(1)}/10</Text>
              <Text style={styles.moodLabel}>Average Mood</Text>
            </View>
          </View>
          
          <View style={styles.moodBar}>
            <View 
              style={[
                styles.moodBarFill, 
                { width: moodBarWidth }
              ]} 
            />
          </View>
        </View>

        {/* Energy Card */}
        <View style={styles.insightCard}>
          <View style={styles.cardHeader}>
            <Text style={styles.cardTitle}>Energy</Text>
            <View style={[styles.trendBadge, { backgroundColor: getTrendColor(stats?.energy_trend) }]}>
              <Text style={styles.trendText}>{getTrendIcon(stats?.energy_trend)} {stats?.energy_trend || 'stable'}</Text>
            </View>
          </View>
          
          <View style={styles.moodDisplay}>
            <Text style={styles.moodEmoji}>{getEnergyEmoji(averageEnergy)}</Text>
            <View style={styles.moodStats}>
              <Text style={styles.moodValue}>{averageEnergy.toFixed(1)}/10</Text>
              <Text style={styles.moodLabel}>Average Energy</Text>
            </View>
          </View>
          
          <View style={styles.energyBar}>
            <View 
              style={[
                styles.energyBarFill, 
                { width: energyBarWidth }
              ]} 
            />
          </View>
        </View>

        {/* Stress Card */}
        <View style={styles.insightCard}>
          <View style={styles.cardHeader}>
            <Text style={styles.cardTitle}>Stress</Text>
            <View style={[styles.trendBadge, { backgroundColor: getTrendColor(stats?.stress_trend) }]}>
              <Text style={styles.trendText}>{getTrendIcon(stats?.stress_trend)} {stats?.stress_trend || 'stable'}</Text>
            </View>
          </View>
          
          <View style={styles.moodDisplay}>
            <Text style={styles.moodEmoji}>{getStressEmoji(averageStress)}</Text>
            <View style={styles.moodStats}>
              <Text style={styles.moodValue}>{averageStress.toFixed(1)}/10</Text>
              <Text style={styles.moodLabel}>Average Stress</Text>
            </View>
          </View>
          
          <View style={styles.stressBar}>
            <View 
              style={[
                styles.stressBarFill, 
                { width: stressBarWidth }
              ]} 
            />
          </View>
        </View>

        {/* Last Entry Card */}
        <View style={styles.insightCard}>
          <Text style={styles.cardTitle}>Last Entry</Text>
          
          {stats?.last_entry_date ? (
            <View style={styles.lastEntryInfo}>
              <Ionicons name="time-outline" size={20} color="#666" style={styles.lastEntryIcon} />
              <Text style={styles.lastEntryText}>
                {new Date(stats.last_entry_date).toLocaleDateString('en-US', {
                  weekday: 'long',
                  month: 'short',
                  day: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit'
                })}
              </Text>
            </View>
          ) : (
            <Text style={styles.noEntryText}>No entries yet</Text>
          )}
        </View>

        {/* Tips Card */}
        <View style={styles.insightCard}>
          <Text style={styles.cardTitle}>Wellness Tips</Text>
          
          <View style={styles.tipItem}>
            <Ionicons name="bulb-outline" size={24} color="#FFC107" style={styles.tipIcon} />
            <Text style={styles.tipText}>
              {averageMood < 5 
                ? "Try taking short breaks throughout your day to reset your mind and improve your mood."
                : "You're maintaining a positive mood! Keep up activities that bring you joy."}
            </Text>
          </View>
          
          <View style={styles.tipItem}>
            <Ionicons name="battery-charging-outline" size={24} color="#4CAF50" style={styles.tipIcon} />
            <Text style={styles.tipText}>
              {averageEnergy < 5 
                ? "Consider adjusting your sleep schedule or adding short power naps to boost energy."
                : "Your energy levels are good! Remember to maintain a consistent sleep schedule."}
            </Text>
          </View>
          
          <View style={styles.tipItem}>
            <Ionicons name="water-outline" size={24} color="#2196F3" style={styles.tipIcon} />
            <Text style={styles.tipText}>
              {averageStress > 6 
                ? "High stress detected. Try mindfulness exercises or short meditation sessions."
                : "You're managing stress well! Continue your current stress management techniques."}
            </Text>
          </View>
        </View>

        {/* Error message if any */}
        {error && (
          <View style={styles.errorContainer}>
            <Ionicons name="information-circle-outline" size={20} color="#E74C3C" />
            <Text style={styles.errorText}>{error}</Text>
          </View>
        )}
        
        {/* Bottom padding */}
        <View style={styles.bottomPadding} />
      </ScrollView>
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
  headerIcon: {
    padding: 8,
  },
  scrollContainer: {
    flex: 1,
  },
  contentContainer: {
    padding: 16,
  },
  mainStatsCard: {
    backgroundColor: 'white',
    borderRadius: 16,
    padding: 20,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  insightCard: {
    backgroundColor: 'white',
    borderRadius: 16,
    padding: 20,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
    marginBottom: 16,
  },
  statsGrid: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  statItem: {
    alignItems: 'center',
    flex: 1,
  },
  statValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#4A90E2',
  },
  statLabel: {
    fontSize: 14,
    color: '#666',
    marginTop: 4,
  },
  moodDisplay: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  moodEmoji: {
    fontSize: 40,
    marginRight: 16,
  },
  moodStats: {
    flex: 1,
  },
  moodValue: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
  },
  moodLabel: {
    fontSize: 14,
    color: '#666',
  },
  moodBar: {
    height: 8,
    backgroundColor: '#f0f0f0',
    borderRadius: 4,
    overflow: 'hidden',
  },
  moodBarFill: {
    height: '100%',
    backgroundColor: '#4CAF50',
    borderRadius: 4,
  },
  energyBar: {
    height: 8,
    backgroundColor: '#f0f0f0',
    borderRadius: 4,
    overflow: 'hidden',
  },
  energyBarFill: {
    height: '100%',
    backgroundColor: '#FF9800',
    borderRadius: 4,
  },
  stressBar: {
    height: 8,
    backgroundColor: '#f0f0f0',
    borderRadius: 4,
    overflow: 'hidden',
  },
  stressBarFill: {
    height: '100%',
    backgroundColor: '#F44336',
    borderRadius: 4,
  },
  trendBadge: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
  },
  trendText: {
    color: 'white',
    fontSize: 12,
    fontWeight: '500',
  },
  lastEntryInfo: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  lastEntryIcon: {
    marginRight: 8,
  },
  lastEntryText: {
    fontSize: 16,
    color: '#333',
  },
  noEntryText: {
    fontSize: 16,
    color: '#888',
    fontStyle: 'italic',
  },
  tipItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 16,
  },
  tipIcon: {
    marginRight: 12,
    marginTop: 2,
  },
  tipText: {
    flex: 1,
    fontSize: 14,
    lineHeight: 20,
    color: '#333',
  },
  errorContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFEBEE',
    padding: 12,
    borderRadius: 8,
    marginBottom: 16,
  },
  errorText: {
    flex: 1,
    fontSize: 14,
    color: '#E74C3C',
    marginLeft: 8,
  },
  bottomPadding: {
    height: 40,
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

export default InsightsScreen; 