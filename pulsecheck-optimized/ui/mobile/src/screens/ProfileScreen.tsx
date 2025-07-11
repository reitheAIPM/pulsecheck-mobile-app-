import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Alert } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { mobileApiService } from '../services/api';

export default function ProfileScreen() {
  const userId = "user_123"; // Mock user ID

  const handleResetJournal = () => {
    Alert.alert(
      "Reset Journal",
      "This will permanently delete all your journal entries and clear your AI patterns. This action cannot be undone.",
      [
        {
          text: "Cancel",
          style: "cancel"
        },
        {
          text: "Reset",
          style: "destructive",
          onPress: async () => {
            try {
              const result = await mobileApiService.resetJournal(userId);
              Alert.alert("Success", result.message);
            } catch (error: any) {
              Alert.alert(
                "Error", 
                error.response?.data?.detail || error.message || "Failed to reset journal"
              );
            }
          }
        }
      ]
    );
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <View style={styles.avatar}>
          <Ionicons name="person" size={40} color="#8B5CF6" />
        </View>
        <Text style={styles.name}>Demo User</Text>
        <Text style={styles.email}>demo@pulsecheck.app</Text>
      </View>

      <View style={styles.menu}>
        <TouchableOpacity style={styles.menuItem}>
          <Ionicons name="settings" size={20} color="#64748B" />
          <Text style={styles.menuText}>Settings</Text>
        </TouchableOpacity>
        
        <TouchableOpacity style={styles.menuItem}>
          <Ionicons name="help-circle" size={20} color="#64748B" />
          <Text style={styles.menuText}>Help & Support</Text>
        </TouchableOpacity>
        
        <TouchableOpacity style={styles.menuItem}>
          <Ionicons name="information-circle" size={20} color="#64748B" />
          <Text style={styles.menuText}>About PulseCheck</Text>
        </TouchableOpacity>

        {/* Data & Privacy Section */}
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>Data & Privacy</Text>
        </View>
        
        <TouchableOpacity style={styles.menuItem}>
          <Ionicons name="download" size={20} color="#64748B" />
          <Text style={styles.menuText}>Export Data</Text>
        </TouchableOpacity>
        
        <TouchableOpacity style={[styles.menuItem, styles.dangerItem]} onPress={handleResetJournal}>
          <Ionicons name="trash" size={20} color="#EF4444" />
          <Text style={[styles.menuText, styles.dangerText]}>Reset Journal</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F8FAFC' },
  header: { alignItems: 'center', padding: 30 },
  avatar: { width: 80, height: 80, borderRadius: 40, backgroundColor: '#E2E8F0', justifyContent: 'center', alignItems: 'center', marginBottom: 15 },
  name: { fontSize: 20, fontWeight: 'bold', color: '#1E293B', marginBottom: 5 },
  email: { fontSize: 14, color: '#64748B' },
  menu: { paddingHorizontal: 20 },
  menuItem: { flexDirection: 'row', alignItems: 'center', backgroundColor: 'white', padding: 15, borderRadius: 12, marginBottom: 10 },
  menuText: { fontSize: 16, color: '#1E293B', marginLeft: 10 },
  sectionHeader: { padding: 15, borderBottomWidth: 1, borderBottomColor: '#E2E8F0', marginBottom: 10 },
  sectionTitle: { fontSize: 18, fontWeight: 'bold', color: '#1E293B' },
  dangerItem: { backgroundColor: '#FEF2F2' },
  dangerText: { color: '#EF4444' },
}); 