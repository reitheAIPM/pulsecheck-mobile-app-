import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

export default function InsightsScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Insights & Analytics</Text>
      <Text style={styles.subtitle}>Coming soon! 📊</Text>
      <Text style={styles.description}>
        We're working on personalized insights based on your journal entries.
        This will include mood trends, pattern analysis, and AI-powered recommendations.
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20, backgroundColor: '#F8FAFC', justifyContent: 'center', alignItems: 'center' },
  title: { fontSize: 24, fontWeight: 'bold', color: '#1E293B', marginBottom: 10 },
  subtitle: { fontSize: 18, color: '#8B5CF6', marginBottom: 20 },
  description: { fontSize: 16, color: '#64748B', textAlign: 'center', lineHeight: 24 },
}); 