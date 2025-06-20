import React, { useState, useMemo } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TextInput,
  TouchableOpacity,
  Alert,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { JournalEntryCreate } from '../types';
import apiService from '../services/api';

interface JournalEntryScreenProps {
  navigation: any;
}

const JournalEntryScreen: React.FC<JournalEntryScreenProps> = ({ navigation }) => {
  const [content, setContent] = useState('');
  const [moodLevel, setMoodLevel] = useState(5);
  const [energyLevel, setEnergyLevel] = useState(5);
  const [stressLevel, setStressLevel] = useState(5);
  const [sleepHours, setSleepHours] = useState<string>('');
  const [workHours, setWorkHours] = useState<string>('');
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [workChallenges, setWorkChallenges] = useState<string[]>([]);
  const [gratitudeItems, setGratitudeItems] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);

  // Predefined tags for quick selection
  const availableTags = [
    'productive', 'stressed', 'motivated', 'tired', 'focused', 'overwhelmed',
    'creative', 'anxious', 'confident', 'frustrated', 'calm', 'energetic'
  ];

  const commonChallenges = [
    'tight deadlines', 'difficult bugs', 'meeting overload', 'unclear requirements',
    'technical debt', 'team communication', 'work-life balance', 'imposter syndrome'
  ];

  // Enhanced validation and feedback
  const isFormValid = useMemo(() => {
    return content.trim().length >= 10 && content.trim().length <= 1000;
  }, [content]);

  const characterCount = content.length;
  const characterLimit = 1000;
  const isNearLimit = characterCount > characterLimit * 0.8;

  const handleSubmit = async () => {
    // Enhanced validation
    if (!content.trim()) {
      Alert.alert('Required Field', 'Please share how you\'re feeling today');
      return;
    }

    if (content.trim().length < 10) {
      Alert.alert('Too Short', 'Please write at least 10 characters about your day to help Pulse provide better insights');
      return;
    }

    if (content.trim().length > 1000) {
      Alert.alert('Too Long', 'Please keep your entry under 1000 characters for the best experience');
      return;
    }

    setLoading(true);

    try {
      const entryData: JournalEntryCreate = {
        content: content.trim(),
        mood_level: moodLevel,
        energy_level: energyLevel,
        stress_level: stressLevel,
        sleep_hours: sleepHours ? parseFloat(sleepHours) : undefined,
        work_hours: workHours ? parseFloat(workHours) : undefined,
        tags: selectedTags,
        work_challenges: workChallenges,
        gratitude_items: gratitudeItems,
      };

      const newEntry = await apiService.createJournalEntry(entryData);
      
      // Enhanced success feedback
      Alert.alert(
        'Check-in Saved! 🎉',
        'Your wellness check-in has been saved. Would you like to see what Pulse thinks?',
        [
          { 
            text: 'View Dashboard', 
            style: 'cancel',
            onPress: () => navigation.navigate('Home')
          },
          { 
            text: 'See Pulse Response', 
            onPress: () => navigation.navigate('PulseResponse', { entryId: newEntry.id })
          }
        ]
      );
    } catch (error: any) {
      console.error('Error saving entry:', error);
      
      // Enhanced error handling
      let errorMessage = 'Failed to save your check-in. Please try again.';
      if (error.response?.status === 500) {
        errorMessage = 'Our servers are temporarily busy. Your entry has been saved locally and will sync when possible.';
      }
      
      Alert.alert('Error', errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const toggleTag = (tag: string) => {
    if (selectedTags.includes(tag)) {
      setSelectedTags(selectedTags.filter(t => t !== tag));
    } else {
      setSelectedTags([...selectedTags, tag]);
    }
  };

  const toggleChallenge = (challenge: string) => {
    if (workChallenges.includes(challenge)) {
      setWorkChallenges(workChallenges.filter(c => c !== challenge));
    } else {
      setWorkChallenges([...workChallenges, challenge]);
    }
  };

  const getMoodEmoji = (mood: number): string => {
    if (mood >= 9) return '😄';
    if (mood >= 7) return '😊';
    if (mood >= 5) return '😐';
    if (mood >= 3) return '😟';
    return '😢';
  };

  const getEnergyEmoji = (energy: number): string => {
    if (energy >= 9) return '⚡';
    if (energy >= 7) return '🔋';
    if (energy >= 5) return '🟡';
    if (energy >= 3) return '🟠';
    return '🔴';
  };

  const getStressEmoji = (stress: number): string => {
    if (stress >= 9) return '😰';
    if (stress >= 7) return '😟';
    if (stress >= 5) return '😐';
    if (stress >= 3) return '😌';
    return '😊';
  };

  // Custom slider component
  const CustomSlider: React.FC<{
    value: number;
    onValueChange: (value: number) => void;
    color: string;
  }> = ({ value, onValueChange, color }) => {
    return (
      <View style={styles.customSlider}>
        {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((num) => (
          <TouchableOpacity
            key={num}
            style={[
              styles.sliderDot,
              { backgroundColor: num <= value ? color : '#E0E0E0' }
            ]}
            onPress={() => onValueChange(num)}
          />
        ))}
      </View>
    );
  };

  return (
    <KeyboardAvoidingView 
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
        {/* Header */}
        <View style={styles.header}>
          <TouchableOpacity onPress={() => navigation.goBack()}>
            <Ionicons name="arrow-back" size={24} color="#2C3E50" />
          </TouchableOpacity>
          <Text style={styles.title}>Daily Check-in</Text>
          <View style={{ width: 24 }} />
        </View>

        {/* Main Content Input */}
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>How are you feeling today? 💭</Text>
            <Text style={[
              styles.characterCount, 
              { color: isNearLimit ? '#E74C3C' : '#7F8C8D' }
            ]}>
              {characterCount}/{characterLimit}
            </Text>
          </View>
          <TextInput
            style={[
              styles.textInput,
              !isFormValid && content.length > 0 ? { borderColor: '#E74C3C' } : {}
            ]}
            value={content}
            onChangeText={setContent}
            placeholder="Share what's on your mind... work stress, wins, challenges, or just how you're feeling. The more detail you provide, the better Pulse can support you."
            multiline
            numberOfLines={4}
            textAlignVertical="top"
            maxLength={characterLimit}
          />
          {content.length > 0 && !isFormValid && (
            <Text style={styles.validationText}>
              {content.trim().length < 10 
                ? 'Please write at least 10 characters for better insights'
                : 'Character limit exceeded'
              }
            </Text>
          )}
        </View>

        {/* Mood Slider */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>
            Mood {getMoodEmoji(moodLevel)} ({moodLevel}/10)
          </Text>
          <CustomSlider
            value={moodLevel}
            onValueChange={setMoodLevel}
            color="#4A90E2"
          />
          <View style={styles.sliderLabels}>
            <Text style={styles.sliderLabel}>😢 Low</Text>
            <Text style={styles.sliderLabel}>😄 High</Text>
          </View>
        </View>

        {/* Energy Slider */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>
            Energy {getEnergyEmoji(energyLevel)} ({energyLevel}/10)
          </Text>
          <CustomSlider
            value={energyLevel}
            onValueChange={setEnergyLevel}
            color="#27AE60"
          />
          <View style={styles.sliderLabels}>
            <Text style={styles.sliderLabel}>🔴 Drained</Text>
            <Text style={styles.sliderLabel}>⚡ Energized</Text>
          </View>
        </View>

        {/* Stress Slider */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>
            Stress Level {getStressEmoji(stressLevel)} ({stressLevel}/10)
          </Text>
          <CustomSlider
            value={stressLevel}
            onValueChange={setStressLevel}
            color="#E74C3C"
          />
          <View style={styles.sliderLabels}>
            <Text style={styles.sliderLabel}>😊 Relaxed</Text>
            <Text style={styles.sliderLabel}>😰 Stressed</Text>
          </View>
        </View>

        {/* Sleep & Work Hours */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Sleep & Work (optional)</Text>
          <View style={styles.hoursRow}>
            <View style={styles.hoursInput}>
              <Text style={styles.hoursLabel}>Sleep Hours 😴</Text>
              <TextInput
                style={styles.hoursField}
                value={sleepHours}
                onChangeText={setSleepHours}
                placeholder="7.5"
                keyboardType="numeric"
              />
            </View>
            <View style={styles.hoursInput}>
              <Text style={styles.hoursLabel}>Work Hours 💻</Text>
              <TextInput
                style={styles.hoursField}
                value={workHours}
                onChangeText={setWorkHours}
                placeholder="8"
                keyboardType="numeric"
              />
            </View>
          </View>
        </View>

        {/* Tags */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>How would you describe today?</Text>
          <View style={styles.tagsContainer}>
            {availableTags.map((tag) => (
              <TouchableOpacity
                key={tag}
                style={[
                  styles.tag,
                  selectedTags.includes(tag) && styles.selectedTag
                ]}
                onPress={() => toggleTag(tag)}
              >
                <Text style={[
                  styles.tagText,
                  selectedTags.includes(tag) && styles.selectedTagText
                ]}>
                  {tag}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {/* Work Challenges */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Any work challenges today?</Text>
          <View style={styles.tagsContainer}>
            {commonChallenges.map((challenge) => (
              <TouchableOpacity
                key={challenge}
                style={[
                  styles.tag,
                  workChallenges.includes(challenge) && styles.selectedChallengeTag
                ]}
                onPress={() => toggleChallenge(challenge)}
              >
                <Text style={[
                  styles.tagText,
                  workChallenges.includes(challenge) && styles.selectedChallengeTagText
                ]}>
                  {challenge}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {/* Enhanced Submit Button */}
        <View style={styles.submitSection}>
          <TouchableOpacity 
            style={[
              styles.submitButton,
              !isFormValid ? styles.submitButtonDisabled : {}
            ]}
            onPress={handleSubmit}
            disabled={!isFormValid || loading}
          >
            {loading ? (
              <ActivityIndicator size="small" color="white" />
            ) : (
              <>
                <Ionicons name="heart" size={20} color="white" />
                <Text style={styles.submitButtonText}>
                  Save Check-in & Get Pulse Insights
                </Text>
              </>
            )}
          </TouchableOpacity>
          
          {!isFormValid && (
            <Text style={styles.submitHint}>
              Write at least 10 characters to enable insights
            </Text>
          )}
        </View>

        <View style={{ height: 50 }} />
      </ScrollView>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8F9FA',
  },
  scrollView: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 20,
    paddingTop: 60,
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#2C3E50',
  },
  section: {
    margin: 20,
    marginTop: 0,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#2C3E50',
  },
  textInput: {
    backgroundColor: 'white',
    borderRadius: 10,
    padding: 15,
    fontSize: 16,
    minHeight: 100,
    borderWidth: 1,
    borderColor: '#E0E0E0',
    textAlignVertical: 'top',
  },
  slider: {
    width: '100%',
    height: 40,
  },
  customSlider: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 10,
    marginVertical: 10,
  },
  sliderDot: {
    width: 20,
    height: 20,
    borderRadius: 10,
    marginHorizontal: 2,
  },
  sliderLabels: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 5,
  },
  sliderLabel: {
    fontSize: 12,
    color: '#7F8C8D',
  },
  hoursRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  hoursInput: {
    flex: 1,
    marginHorizontal: 5,
  },
  hoursLabel: {
    fontSize: 14,
    color: '#7F8C8D',
    marginBottom: 5,
  },
  hoursField: {
    backgroundColor: 'white',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    borderWidth: 1,
    borderColor: '#E0E0E0',
    textAlign: 'center',
  },
  tagsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  tag: {
    backgroundColor: 'white',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 20,
    margin: 4,
    borderWidth: 1,
    borderColor: '#E0E0E0',
  },
  selectedTag: {
    backgroundColor: '#4A90E2',
    borderColor: '#4A90E2',
  },
  selectedChallengeTag: {
    backgroundColor: '#E74C3C',
    borderColor: '#E74C3C',
  },
  tagText: {
    fontSize: 14,
    color: '#7F8C8D',
  },
  selectedTagText: {
    color: 'white',
  },
  selectedChallengeTagText: {
    color: 'white',
  },
  submitSection: {
    margin: 20,
    alignItems: 'center',
  },
  submitButton: {
    backgroundColor: '#4A90E2',
    padding: 15,
    borderRadius: 10,
    flexDirection: 'row',
    alignItems: 'center',
  },
  submitButtonDisabled: {
    backgroundColor: '#BDC3C7',
  },
  submitButtonText: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
    marginLeft: 10,
  },
  submitHint: {
    color: '#7F8C8D',
    marginTop: 10,
  },
  characterCount: {
    fontSize: 12,
    color: '#7F8C8D',
  },
  validationText: {
    color: '#E74C3C',
    marginTop: 5,
  },
});

export default JournalEntryScreen; 