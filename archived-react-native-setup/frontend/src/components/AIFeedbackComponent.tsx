import React, { useState } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Modal,
  TextInput,
  Alert,
  Animated,
} from 'react-native';
import { PulseResponse } from '../types';
import { submitFeedback } from '../services/api';

interface AIFeedbackComponentProps {
  aiResponse: PulseResponse;
  journalEntryId: string;
  onFeedbackSubmitted?: (feedbackType: string) => void;
}

export const AIFeedbackComponent: React.FC<AIFeedbackComponentProps> = ({
  aiResponse,
  journalEntryId,
  onFeedbackSubmitted,
}) => {
  const [feedbackGiven, setFeedbackGiven] = useState(false);
  const [showDetailedModal, setShowDetailedModal] = useState(false);
  const [detailedFeedback, setDetailedFeedback] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [fadeAnim] = useState(new Animated.Value(1));

  const handleQuickFeedback = async (type: 'thumbs_up' | 'thumbs_down') => {
    try {
      setIsSubmitting(true);
      
      await submitFeedback({
        entryId: journalEntryId,
        feedbackType: type,
      });
      
      setFeedbackGiven(true);
      onFeedbackSubmitted?.(type);
      
      // Fade out animation
      Animated.timing(fadeAnim, {
        toValue: 0.3,
        duration: 1000,
        useNativeDriver: true,
      }).start();
      
      // Show thank you message
      const message = type === 'thumbs_up' 
        ? "Thanks! Your positive feedback helps Pulse learn 🌟"
        : "Thanks for the feedback! This helps Pulse improve 🔧";
      
      Alert.alert('Feedback Received', message);
      
    } catch (error) {
      console.error('Error submitting feedback:', error);
      Alert.alert('Error', 'Failed to submit feedback. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDetailedFeedback = async () => {
    if (!detailedFeedback.trim()) {
      Alert.alert('Empty Feedback', 'Please enter some feedback before submitting.');
      return;
    }

    try {
      setIsSubmitting(true);
      
      await submitFeedback({
        entryId: journalEntryId,
        feedbackType: 'detailed',
        feedbackText: detailedFeedback,
      });
      
      setShowDetailedModal(false);
      setFeedbackGiven(true);
      onFeedbackSubmitted?.('detailed');
      
      Alert.alert(
        'Detailed Feedback Received', 
        'Thank you for taking the time to provide detailed feedback! This really helps improve Pulse.'
      );
      
    } catch (error) {
      console.error('Error submitting detailed feedback:', error);
      Alert.alert('Error', 'Failed to submit feedback. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (feedbackGiven) {
    return (
      <Animated.View style={[styles.feedbackContainer, { opacity: fadeAnim }]}>
        <View style={styles.thankYouContainer}>
          <Text style={styles.thankYouText}>✅ Feedback received</Text>
          <Text style={styles.thankYouSubtext}>Thank you for helping Pulse improve!</Text>
        </View>
      </Animated.View>
    );
  }

  return (
    <View style={styles.feedbackContainer}>
      <Text style={styles.feedbackPrompt}>Was this response helpful?</Text>
      
      <View style={styles.buttonContainer}>
        <TouchableOpacity 
          style={[styles.feedbackButton, styles.thumbsUpButton]}
          onPress={() => handleQuickFeedback('thumbs_up')}
          disabled={isSubmitting}
        >
          <Text style={styles.thumbsIcon}>👍</Text>
          <Text style={styles.buttonText}>Helpful</Text>
        </TouchableOpacity>
        
        <TouchableOpacity 
          style={[styles.feedbackButton, styles.thumbsDownButton]}
          onPress={() => handleQuickFeedback('thumbs_down')}
          disabled={isSubmitting}
        >
          <Text style={styles.thumbsIcon}>👎</Text>
          <Text style={styles.buttonText}>Not helpful</Text>
        </TouchableOpacity>
      </View>
      
      <TouchableOpacity 
        style={styles.detailedFeedbackButton}
        onPress={() => setShowDetailedModal(true)}
        disabled={isSubmitting}
      >
        <Text style={styles.detailedFeedbackText}>💬 Give detailed feedback</Text>
      </TouchableOpacity>

      {/* Detailed Feedback Modal */}
      <Modal
        visible={showDetailedModal}
        animationType="slide"
        presentationStyle="pageSheet"
        onRequestClose={() => setShowDetailedModal(false)}
      >
        <View style={styles.modalContainer}>
          <View style={styles.modalHeader}>
            <Text style={styles.modalTitle}>Detailed Feedback</Text>
            <TouchableOpacity 
              onPress={() => setShowDetailedModal(false)}
              style={styles.closeButton}
            >
              <Text style={styles.closeButtonText}>✕</Text>
            </TouchableOpacity>
          </View>
          
          <View style={styles.modalContent}>
            <Text style={styles.modalPrompt}>
              Help us improve Pulse by sharing your thoughts on this response:
            </Text>
            
            <View style={styles.responsePreview}>
              <Text style={styles.responsePreviewText} numberOfLines={3}>
                "{aiResponse.message}"
              </Text>
            </View>
            
            <TextInput
              style={styles.feedbackInput}
              multiline
              numberOfLines={6}
              placeholder="What could be improved? Was the response relevant? Any suggestions?"
              placeholderTextColor="#666"
              value={detailedFeedback}
              onChangeText={setDetailedFeedback}
              maxLength={500}
            />
            
            <Text style={styles.characterCount}>
              {detailedFeedback.length}/500 characters
            </Text>
            
            <View style={styles.modalButtonContainer}>
              <TouchableOpacity 
                style={styles.cancelButton}
                onPress={() => setShowDetailedModal(false)}
              >
                <Text style={styles.cancelButtonText}>Cancel</Text>
              </TouchableOpacity>
              
              <TouchableOpacity 
                style={[
                  styles.submitButton, 
                  (!detailedFeedback.trim() || isSubmitting) && styles.submitButtonDisabled
                ]}
                onPress={handleDetailedFeedback}
                disabled={!detailedFeedback.trim() || isSubmitting}
              >
                <Text style={[
                  styles.submitButtonText,
                  (!detailedFeedback.trim() || isSubmitting) && styles.submitButtonTextDisabled
                ]}>
                  {isSubmitting ? 'Submitting...' : 'Submit Feedback'}
                </Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>
    </View>
  );
};

const styles = StyleSheet.create({
  feedbackContainer: {
    backgroundColor: '#f8f9fa',
    borderRadius: 12,
    padding: 16,
    marginTop: 16,
    borderWidth: 1,
    borderColor: '#e9ecef',
  },
  feedbackPrompt: {
    fontSize: 16,
    fontWeight: '600',
    color: '#2c3e50',
    textAlign: 'center',
    marginBottom: 12,
  },
  buttonContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: 12,
  },
  feedbackButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    paddingHorizontal: 20,
    borderRadius: 25,
    minWidth: 120,
    justifyContent: 'center',
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  thumbsUpButton: {
    backgroundColor: '#27ae60',
  },
  thumbsDownButton: {
    backgroundColor: '#e74c3c',
  },
  thumbsIcon: {
    fontSize: 18,
    marginRight: 8,
  },
  buttonText: {
    color: 'white',
    fontWeight: '600',
    fontSize: 14,
  },
  detailedFeedbackButton: {
    alignSelf: 'center',
    paddingVertical: 8,
    paddingHorizontal: 16,
  },
  detailedFeedbackText: {
    color: '#3498db',
    fontSize: 14,
    fontWeight: '500',
    textDecorationLine: 'underline',
  },
  thankYouContainer: {
    alignItems: 'center',
    paddingVertical: 8,
  },
  thankYouText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#27ae60',
    marginBottom: 4,
  },
  thankYouSubtext: {
    fontSize: 14,
    color: '#7f8c8d',
  },
  
  // Modal styles
  modalContainer: {
    flex: 1,
    backgroundColor: 'white',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#e9ecef',
    paddingTop: 60, // Account for status bar
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#2c3e50',
  },
  closeButton: {
    width: 30,
    height: 30,
    borderRadius: 15,
    backgroundColor: '#ecf0f1',
    justifyContent: 'center',
    alignItems: 'center',
  },
  closeButtonText: {
    fontSize: 18,
    color: '#7f8c8d',
    fontWeight: 'bold',
  },
  modalContent: {
    flex: 1,
    padding: 20,
  },
  modalPrompt: {
    fontSize: 16,
    color: '#2c3e50',
    marginBottom: 16,
    lineHeight: 24,
  },
  responsePreview: {
    backgroundColor: '#f8f9fa',
    borderRadius: 8,
    padding: 12,
    marginBottom: 20,
    borderLeftWidth: 4,
    borderLeftColor: '#3498db',
  },
  responsePreviewText: {
    fontSize: 14,
    color: '#5d6d7e',
    fontStyle: 'italic',
  },
  feedbackInput: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    textAlignVertical: 'top',
    minHeight: 120,
    backgroundColor: 'white',
  },
  characterCount: {
    textAlign: 'right',
    color: '#7f8c8d',
    fontSize: 12,
    marginTop: 8,
    marginBottom: 20,
  },
  modalButtonContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 'auto',
    paddingTop: 20,
  },
  cancelButton: {
    flex: 1,
    paddingVertical: 12,
    marginRight: 10,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#ddd',
    alignItems: 'center',
  },
  cancelButtonText: {
    color: '#7f8c8d',
    fontSize: 16,
    fontWeight: '500',
  },
  submitButton: {
    flex: 1,
    paddingVertical: 12,
    marginLeft: 10,
    borderRadius: 8,
    backgroundColor: '#3498db',
    alignItems: 'center',
  },
  submitButtonDisabled: {
    backgroundColor: '#bdc3c7',
  },
  submitButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
  submitButtonTextDisabled: {
    color: '#ecf0f1',
  },
}); 