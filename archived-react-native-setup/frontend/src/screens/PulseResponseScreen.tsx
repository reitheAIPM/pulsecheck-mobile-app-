import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { PulseResponse, JournalEntry } from '../types';
import apiService from '../services/api';
import { AIFeedbackComponent } from '../components/AIFeedbackComponent';

interface PulseResponseScreenProps {
  navigation: any;
  route: {
    params: {
      entryId: string;
    };
  };
}

const PulseResponseScreen: React.FC<PulseResponseScreenProps> = ({ navigation, route }) => {
  const { entryId } = route.params;
  const [pulseResponse, setPulseResponse] = useState<PulseResponse | null>(null);
  const [journalEntry, setJournalEntry] = useState<JournalEntry | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadPulseResponse();
  }, []);

  const loadPulseResponse = async () => {
    try {
      setLoading(true);
      setError(null);

      // Load both the journal entry and Pulse response
      const [entryData, responseData] = await Promise.all([
        apiService.getJournalEntry(entryId),
        apiService.getPulseResponse(entryId)
      ]);

      setJournalEntry(entryData);
      setPulseResponse(responseData);
    } catch (err) {
      console.error('Error loading Pulse response:', err);
      setError('Failed to load Pulse response. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleGetFullAnalysis = async () => {
    try {
      navigation.navigate('AIAnalysis', { entryId });
    } catch (error) {
      Alert.alert('Error', 'Failed to load detailed analysis');
    }
  };

  const handleFeedbackSubmitted = (feedbackType: string) => {
    console.log('Feedback submitted:', feedbackType);
    // Optionally show a toast or update UI
  };

  const getMoodEmoji = (mood: number): string => {
    if (mood >= 9) return '😄';
    if (mood >= 7) return '😊';
    if (mood >= 5) return '😐';
    if (mood >= 3) return '😟';
    return '😢';
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#FF6B6B" />
        <Text style={styles.loadingText}>Pulse is thinking...</Text>
        <Text style={styles.loadingSubtext}>Analyzing your wellness check-in</Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.errorContainer}>
        <Ionicons name="alert-circle" size={48} color="#E74C3C" />
        <Text style={styles.errorText}>{error}</Text>
        <TouchableOpacity style={styles.retryButton} onPress={loadPulseResponse}>
          <Text style={styles.retryButtonText}>Try Again</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()}>
          <Ionicons name="arrow-back" size={24} color="#2C3E50" />
        </TouchableOpacity>
        <View style={styles.headerContent}>
          <Ionicons name="heart" size={24} color="#FF6B6B" />
          <Text style={styles.headerTitle}>Pulse</Text>
        </View>
        <View style={{ width: 24 }} />
      </View>

      {/* Your Check-in Summary */}
      {journalEntry && (
        <View style={styles.summaryCard}>
          <Text style={styles.summaryTitle}>Your Check-in</Text>
          <View style={styles.summaryMetrics}>
            <View style={styles.metric}>
              <Text style={styles.metricEmoji}>{getMoodEmoji(journalEntry.mood_level)}</Text>
              <Text style={styles.metricLabel}>Mood</Text>
              <Text style={styles.metricValue}>{journalEntry.mood_level}/10</Text>
            </View>
            <View style={styles.metric}>
              <Text style={styles.metricEmoji}>⚡</Text>
              <Text style={styles.metricLabel}>Energy</Text>
              <Text style={styles.metricValue}>{journalEntry.energy_level}/10</Text>
            </View>
            <View style={styles.metric}>
              <Text style={styles.metricEmoji}>😰</Text>
              <Text style={styles.metricLabel}>Stress</Text>
              <Text style={styles.metricValue}>{journalEntry.stress_level}/10</Text>
            </View>
          </View>
          <Text style={styles.summaryContent} numberOfLines={2}>
            {journalEntry.content}
          </Text>
        </View>
      )}

      {/* Pulse Response */}
      {pulseResponse && (
        <View style={styles.pulseCard}>
          <View style={styles.pulseHeader}>
            <View style={styles.pulseAvatar}>
              <Ionicons name="heart" size={20} color="white" />
            </View>
            <View style={styles.pulseInfo}>
              <Text style={styles.pulseName}>Pulse</Text>
              <Text style={styles.pulseRole}>Your Wellness Companion</Text>
            </View>
            <View style={styles.confidenceIndicator}>
              <Text style={styles.confidenceText}>
                {Math.round(pulseResponse.confidence_score * 100)}%
              </Text>
            </View>
          </View>

          <View style={styles.pulseMessage}>
            <Text style={styles.pulseMessageText}>{pulseResponse.message}</Text>
          </View>

          {/* Suggested Actions */}
          {pulseResponse.suggested_actions && pulseResponse.suggested_actions.length > 0 && (
            <View style={styles.actionsSection}>
              <Text style={styles.actionsSectionTitle}>💡 Suggestions</Text>
              {pulseResponse.suggested_actions.map((action, index) => (
                <View key={index} style={styles.actionItem}>
                  <Ionicons name="checkmark-circle-outline" size={16} color="#27AE60" />
                  <Text style={styles.actionText}>{action}</Text>
                </View>
              ))}
            </View>
          )}

          {/* Follow-up Question */}
          {pulseResponse.follow_up_question && (
            <View style={styles.questionSection}>
              <Text style={styles.questionTitle}>🤔 Reflection</Text>
              <Text style={styles.questionText}>{pulseResponse.follow_up_question}</Text>
            </View>
          )}

          {/* Response Time */}
          {pulseResponse.response_time_ms && (
            <Text style={styles.responseTime}>
              Responded in {pulseResponse.response_time_ms}ms
            </Text>
          )}
        </View>
      )}

      {/* Action Buttons */}
      <View style={styles.actionButtons}>
        <TouchableOpacity 
          style={styles.primaryActionButton}
          onPress={handleGetFullAnalysis}
        >
          <Ionicons name="analytics" size={20} color="white" />
          <Text style={styles.primaryActionText}>Get Full Analysis</Text>
        </TouchableOpacity>

        <View style={styles.secondaryActions}>
          <TouchableOpacity 
            style={styles.secondaryButton}
            onPress={() => navigation.navigate('JournalEntry')}
          >
            <Ionicons name="add" size={16} color="#4A90E2" />
            <Text style={styles.secondaryButtonText}>New Check-in</Text>
          </TouchableOpacity>

          <TouchableOpacity 
            style={styles.secondaryButton}
            onPress={() => navigation.navigate('Journal')}
          >
            <Ionicons name="book" size={16} color="#4A90E2" />
            <Text style={styles.secondaryButtonText}>View History</Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Beta Feedback Component */}
      {pulseResponse && (
                 <View style={styles.betaFeedbackContainer}>
          <AIFeedbackComponent
            aiResponse={pulseResponse}
            journalEntryId={entryId}
            onFeedbackSubmitted={handleFeedbackSubmitted}
          />
        </View>
      )}

      <View style={{ height: 50 }} />
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8F9FA',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#F8F9FA',
  },
  loadingText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#2C3E50',
    marginTop: 15,
  },
  loadingSubtext: {
    fontSize: 14,
    color: '#7F8C8D',
    marginTop: 5,
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#F8F9FA',
    padding: 20,
  },
  errorText: {
    fontSize: 16,
    color: '#E74C3C',
    textAlign: 'center',
    marginVertical: 20,
  },
  retryButton: {
    backgroundColor: '#4A90E2',
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 8,
  },
  retryButtonText: {
    color: 'white',
    fontWeight: '600',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 20,
    paddingTop: 60,
  },
  headerContent: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#2C3E50',
    marginLeft: 8,
  },
  summaryCard: {
    backgroundColor: 'white',
    margin: 20,
    marginTop: 0,
    padding: 15,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  summaryTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#2C3E50',
    marginBottom: 10,
  },
  summaryMetrics: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: 15,
  },
  metric: {
    alignItems: 'center',
  },
  metricEmoji: {
    fontSize: 24,
    marginBottom: 4,
  },
  metricLabel: {
    fontSize: 12,
    color: '#7F8C8D',
  },
  metricValue: {
    fontSize: 14,
    fontWeight: '600',
    color: '#2C3E50',
  },
  summaryContent: {
    fontSize: 14,
    color: '#7F8C8D',
    lineHeight: 20,
  },
  pulseCard: {
    backgroundColor: 'white',
    margin: 20,
    marginTop: 0,
    padding: 20,
    borderRadius: 12,
    borderLeftWidth: 4,
    borderLeftColor: '#FF6B6B',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  pulseHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 15,
  },
  pulseAvatar: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#FF6B6B',
    justifyContent: 'center',
    alignItems: 'center',
  },
  pulseInfo: {
    flex: 1,
    marginLeft: 12,
  },
  pulseName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#2C3E50',
  },
  pulseRole: {
    fontSize: 12,
    color: '#7F8C8D',
  },
  confidenceIndicator: {
    backgroundColor: '#E8F5E8',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  confidenceText: {
    fontSize: 12,
    color: '#27AE60',
    fontWeight: '600',
  },
  pulseMessage: {
    marginBottom: 15,
  },
  pulseMessageText: {
    fontSize: 16,
    lineHeight: 24,
    color: '#2C3E50',
  },
  actionsSection: {
    marginBottom: 15,
  },
  actionsSectionTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#2C3E50',
    marginBottom: 8,
  },
  actionItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 6,
  },
  actionText: {
    flex: 1,
    fontSize: 14,
    color: '#2C3E50',
    marginLeft: 8,
    lineHeight: 20,
  },
  questionSection: {
    backgroundColor: '#FFF9E6',
    padding: 12,
    borderRadius: 8,
    marginBottom: 10,
  },
  questionTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#2C3E50',
    marginBottom: 5,
  },
  questionText: {
    fontSize: 14,
    color: '#2C3E50',
    lineHeight: 20,
  },
  responseTime: {
    fontSize: 10,
    color: '#BDC3C7',
    textAlign: 'right',
  },
  actionButtons: {
    margin: 20,
    marginTop: 0,
  },
  primaryActionButton: {
    backgroundColor: '#4A90E2',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 15,
    borderRadius: 10,
    marginBottom: 15,
  },
  primaryActionText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
    marginLeft: 8,
  },
  secondaryActions: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  secondaryButton: {
    flex: 1,
    backgroundColor: 'white',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 12,
    borderRadius: 8,
    marginHorizontal: 5,
    borderWidth: 1,
    borderColor: '#E0E0E0',
  },
  secondaryButtonText: {
    color: '#4A90E2',
    fontSize: 14,
    fontWeight: '500',
    marginLeft: 5,
  },
  betaFeedbackContainer: {
    margin: 20,
    marginTop: 0,
  },
});

export default PulseResponseScreen; 