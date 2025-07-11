// Mobile Storage Service for PulseCheck React Native App
// Provides offline storage and sync capabilities

import AsyncStorage from '@react-native-async-storage/async-storage';
import { JournalEntry, JournalEntryCreate } from './api';

const STORAGE_KEYS = {
  DRAFT_ENTRIES: 'pulsecheck_draft_entries',
  CACHED_ENTRIES: 'pulsecheck_cached_entries',
  USER_PREFERENCES: 'pulsecheck_user_preferences',
  LAST_SYNC: 'pulsecheck_last_sync',
};

export interface DraftEntry extends JournalEntryCreate {
  id: string;
  created_at: string;
  is_draft: true;
}

export interface UserPreferences {
  notifications_enabled: boolean;
  reminder_time: string; // HH:MM format
  preferred_persona: string;
  theme: 'light' | 'dark' | 'auto';
}

class MobileStorageService {
  // Draft Entries Management (for offline mode)
  async saveDraftEntry(entry: JournalEntryCreate): Promise<string> {
    try {
      const draftId = `draft_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      const draftEntry: DraftEntry = {
        ...entry,
        id: draftId,
        created_at: new Date().toISOString(),
        is_draft: true,
      };

      const existingDrafts = await this.getDraftEntries();
      const updatedDrafts = [...existingDrafts, draftEntry];
      
      await AsyncStorage.setItem(
        STORAGE_KEYS.DRAFT_ENTRIES,
        JSON.stringify(updatedDrafts)
      );
      
      console.log('📝 Draft entry saved:', draftId);
      return draftId;
    } catch (error) {
      console.error('Failed to save draft entry:', error);
      throw error;
    }
  }

  async getDraftEntries(): Promise<DraftEntry[]> {
    try {
      const draftsJson = await AsyncStorage.getItem(STORAGE_KEYS.DRAFT_ENTRIES);
      return draftsJson ? JSON.parse(draftsJson) : [];
    } catch (error) {
      console.error('Failed to get draft entries:', error);
      return [];
    }
  }

  async deleteDraftEntry(draftId: string): Promise<void> {
    try {
      const existingDrafts = await this.getDraftEntries();
      const updatedDrafts = existingDrafts.filter(draft => draft.id !== draftId);
      
      await AsyncStorage.setItem(
        STORAGE_KEYS.DRAFT_ENTRIES,
        JSON.stringify(updatedDrafts)
      );
      
      console.log('🗑️ Draft entry deleted:', draftId);
    } catch (error) {
      console.error('Failed to delete draft entry:', error);
      throw error;
    }
  }

  // Cached Entries Management (for offline viewing)
  async cacheEntries(entries: JournalEntry[]): Promise<void> {
    try {
      await AsyncStorage.setItem(
        STORAGE_KEYS.CACHED_ENTRIES,
        JSON.stringify(entries)
      );
      
      await AsyncStorage.setItem(
        STORAGE_KEYS.LAST_SYNC,
        new Date().toISOString()
      );
      
      console.log('💾 Cached', entries.length, 'entries');
    } catch (error) {
      console.error('Failed to cache entries:', error);
    }
  }

  async getCachedEntries(): Promise<JournalEntry[]> {
    try {
      const cachedJson = await AsyncStorage.getItem(STORAGE_KEYS.CACHED_ENTRIES);
      return cachedJson ? JSON.parse(cachedJson) : [];
    } catch (error) {
      console.error('Failed to get cached entries:', error);
      return [];
    }
  }

  async getLastSyncTime(): Promise<Date | null> {
    try {
      const lastSyncStr = await AsyncStorage.getItem(STORAGE_KEYS.LAST_SYNC);
      return lastSyncStr ? new Date(lastSyncStr) : null;
    } catch (error) {
      console.error('Failed to get last sync time:', error);
      return null;
    }
  }

  // User Preferences Management
  async saveUserPreferences(preferences: UserPreferences): Promise<void> {
    try {
      await AsyncStorage.setItem(
        STORAGE_KEYS.USER_PREFERENCES,
        JSON.stringify(preferences)
      );
      console.log('⚙️ User preferences saved');
    } catch (error) {
      console.error('Failed to save user preferences:', error);
      throw error;
    }
  }

  async getUserPreferences(): Promise<UserPreferences> {
    try {
      const preferencesJson = await AsyncStorage.getItem(STORAGE_KEYS.USER_PREFERENCES);
      
      if (preferencesJson) {
        return JSON.parse(preferencesJson);
      }
      
      // Default preferences
      const defaultPreferences: UserPreferences = {
        notifications_enabled: true,
        reminder_time: '20:00', // 8 PM default
        preferred_persona: 'auto',
        theme: 'auto',
      };
      
      await this.saveUserPreferences(defaultPreferences);
      return defaultPreferences;
    } catch (error) {
      console.error('Failed to get user preferences:', error);
      // Return defaults on error
      return {
        notifications_enabled: true,
        reminder_time: '20:00',
        preferred_persona: 'auto',
        theme: 'auto',
      };
    }
  }

  // Utility Methods
  async clearAllData(): Promise<void> {
    try {
      await Promise.all([
        AsyncStorage.removeItem(STORAGE_KEYS.DRAFT_ENTRIES),
        AsyncStorage.removeItem(STORAGE_KEYS.CACHED_ENTRIES),
        AsyncStorage.removeItem(STORAGE_KEYS.USER_PREFERENCES),
        AsyncStorage.removeItem(STORAGE_KEYS.LAST_SYNC),
      ]);
      console.log('🧹 All local data cleared');
    } catch (error) {
      console.error('Failed to clear all data:', error);
      throw error;
    }
  }

  async getStorageInfo(): Promise<{
    draftCount: number;
    cachedCount: number;
    lastSync: Date | null;
    totalSize: string;
  }> {
    try {
      const [drafts, cached, lastSync] = await Promise.all([
        this.getDraftEntries(),
        this.getCachedEntries(),
        this.getLastSyncTime(),
      ]);

      // Estimate storage size
      const draftSize = JSON.stringify(drafts).length;
      const cachedSize = JSON.stringify(cached).length;
      const totalBytes = draftSize + cachedSize;
      const totalSize = totalBytes > 1024 
        ? `${(totalBytes / 1024).toFixed(1)} KB`
        : `${totalBytes} bytes`;

      return {
        draftCount: drafts.length,
        cachedCount: cached.length,
        lastSync,
        totalSize,
      };
    } catch (error) {
      console.error('Failed to get storage info:', error);
      return {
        draftCount: 0,
        cachedCount: 0,
        lastSync: null,
        totalSize: '0 bytes',
      };
    }
  }

  // Network Status Helper
  async isOnline(): Promise<boolean> {
    try {
      // Simple connectivity check - try to fetch from our API
      const response = await fetch('https://pulsecheck-mobile-app-production.up.railway.app/health', {
        method: 'HEAD',
        cache: 'no-cache',
      });
      return response.ok;
    } catch {
      return false;
    }
  }
}

// Export singleton instance
export const mobileStorageService = new MobileStorageService(); 