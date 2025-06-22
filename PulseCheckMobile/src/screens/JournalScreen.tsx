import React, { useState } from 'react';
import { View, Text, StyleSheet, TextInput, TouchableOpacity, Alert } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { mobileSyncService } from '../services/syncService';

export default function JournalScreen({ navigation }: any) {
  const [content, setContent] = useState('');
  const [moodLevel, setMoodLevel] = useState(5);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (content.trim().length < 10) {
      Alert.alert('Error', 'Please write at least 10 characters');
      return;
    }

    try {
      setLoading(true);
      const result = await mobileSyncService.createJournalEntry({
        content: content.trim(),
        mood_level: moodLevel,
        energy_level: 5,
        stress_level: 5,
      });
      
      if (result.success) {
        if (result.isOffline) {
          Alert.alert('Saved Offline! 📱', 'Your check-in has been saved and will sync when online');
        } else {
          Alert.alert('Success! 🎉', 'Your check-in has been saved');
        }
        setContent('');
        setMoodLevel(5);
      } else {
        Alert.alert('Error', 'Failed to save entry');
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to save entry');
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>How are you feeling today?</Text>
      
      <TextInput
        style={styles.textInput}
        placeholder="What's on your mind today?"
        value={content}
        onChangeText={setContent}
        multiline
        numberOfLines={6}
      />

      <View style={styles.moodContainer}>
        <Text style={styles.moodLabel}>Mood Level: {moodLevel}</Text>
        <View style={styles.moodButtons}>
          {[1,2,3,4,5,6,7,8,9,10].map(num => (
            <TouchableOpacity
              key={num}
              style={[styles.moodButton, moodLevel === num && styles.moodButtonActive]}
              onPress={() => setMoodLevel(num)}
            >
              <Text style={[styles.moodButtonText, moodLevel === num && styles.moodButtonTextActive]}>
                {num}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      <TouchableOpacity 
        style={[styles.submitButton, loading && styles.submitButtonDisabled]}
        onPress={handleSubmit}
        disabled={loading}
      >
        <Text style={styles.submitButtonText}>
          {loading ? 'Saving...' : 'Save Check-in'}
        </Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20, backgroundColor: '#F8FAFC' },
  title: { fontSize: 24, fontWeight: 'bold', marginBottom: 20, color: '#1E293B' },
  textInput: { backgroundColor: 'white', borderRadius: 12, padding: 15, fontSize: 16, minHeight: 120, marginBottom: 20 },
  moodContainer: { marginBottom: 20 },
  moodLabel: { fontSize: 16, fontWeight: '600', marginBottom: 10, color: '#1E293B' },
  moodButtons: { flexDirection: 'row', flexWrap: 'wrap', justifyContent: 'space-between' },
  moodButton: { width: 40, height: 40, borderRadius: 20, backgroundColor: '#E2E8F0', justifyContent: 'center', alignItems: 'center', marginBottom: 10 },
  moodButtonActive: { backgroundColor: '#8B5CF6' },
  moodButtonText: { color: '#64748B', fontWeight: '600' },
  moodButtonTextActive: { color: 'white' },
  submitButton: { backgroundColor: '#8B5CF6', paddingVertical: 15, borderRadius: 12, alignItems: 'center' },
  submitButtonDisabled: { backgroundColor: '#9CA3AF' },
  submitButtonText: { color: 'white', fontSize: 16, fontWeight: '600' },
}); 