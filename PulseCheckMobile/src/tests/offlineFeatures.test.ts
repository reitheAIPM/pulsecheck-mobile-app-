// Comprehensive Offline Features Test Suite
// Tests all offline functionality as per CONTRIBUTING.md requirements

import AsyncStorage from '@react-native-async-storage/async-storage';
import { mobileStorageService, DraftEntry, UserPreferences } from '../services/storage';
import { mobileSyncService, SyncResult } from '../services/syncService';
import { JournalEntryCreate } from '../services/api';

// Mock AsyncStorage
jest.mock('@react-native-async-storage/async-storage', () => ({
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
}));

// Mock fetch for network tests
global.fetch = jest.fn();

describe('Offline Features Test Suite', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (AsyncStorage.getItem as jest.Mock).mockResolvedValue(null);
    (AsyncStorage.setItem as jest.Mock).mockResolvedValue(undefined);
    (AsyncStorage.removeItem as jest.Mock).mockResolvedValue(undefined);
  });

  describe('Mobile Storage Service', () => {
    describe('Draft Entries Management', () => {
      it('should save draft entry successfully', async () => {
        const mockEntry: JournalEntryCreate = {
          content: 'Test draft entry',
          mood_level: 7,
          energy_level: 6,
          stress_level: 4,
        };

        const draftId = await mobileStorageService.saveDraftEntry(mockEntry);

        expect(draftId).toMatch(/^draft_\d+_[a-z0-9]+$/);
        expect(AsyncStorage.setItem).toHaveBeenCalledWith(
          'pulsecheck_draft_entries',
          expect.stringContaining('"is_draft":true')
        );
      });

      it('should retrieve draft entries', async () => {
        const mockDrafts = [
          {
            id: 'draft_123_abc',
            content: 'Test draft',
            mood_level: 5,
            energy_level: 5,
            stress_level: 5,
            created_at: '2025-01-01T00:00:00.000Z',
            is_draft: true,
          },
        ];

        (AsyncStorage.getItem as jest.Mock).mockResolvedValue(JSON.stringify(mockDrafts));

        const drafts = await mobileStorageService.getDraftEntries();

        expect(drafts).toEqual(mockDrafts);
        expect(AsyncStorage.getItem).toHaveBeenCalledWith('pulsecheck_draft_entries');
      });

      it('should delete draft entry', async () => {
        const mockDrafts = [
          { id: 'draft_1', content: 'Draft 1', mood_level: 5, energy_level: 5, stress_level: 5, created_at: '2025-01-01T00:00:00.000Z', is_draft: true },
          { id: 'draft_2', content: 'Draft 2', mood_level: 6, energy_level: 6, stress_level: 6, created_at: '2025-01-01T00:00:00.000Z', is_draft: true },
        ];

        (AsyncStorage.getItem as jest.Mock).mockResolvedValue(JSON.stringify(mockDrafts));

        await mobileStorageService.deleteDraftEntry('draft_1');

        expect(AsyncStorage.setItem).toHaveBeenCalledWith(
          'pulsecheck_draft_entries',
          JSON.stringify([mockDrafts[1]])
        );
      });

      it('should handle empty draft entries gracefully', async () => {
        (AsyncStorage.getItem as jest.Mock).mockResolvedValue(null);

        const drafts = await mobileStorageService.getDraftEntries();

        expect(drafts).toEqual([]);
      });
    });

    describe('Cache Management', () => {
      it('should cache journal entries', async () => {
        const mockEntries = [
          {
            id: '1',
            content: 'Test entry',
            mood_level: 7,
            energy_level: 6,
            stress_level: 4,
            created_at: '2025-01-01T00:00:00.000Z',
            user_id: 'user123',
          },
        ];

        await mobileStorageService.cacheEntries(mockEntries);

        expect(AsyncStorage.setItem).toHaveBeenCalledWith(
          'pulsecheck_cached_entries',
          JSON.stringify(mockEntries)
        );
        expect(AsyncStorage.setItem).toHaveBeenCalledWith(
          'pulsecheck_last_sync',
          expect.any(String)
        );
      });

      it('should retrieve cached entries', async () => {
        const mockEntries = [
          {
            id: '1',
            content: 'Cached entry',
            mood_level: 8,
            energy_level: 7,
            stress_level: 3,
            created_at: '2025-01-01T00:00:00.000Z',
            user_id: 'user123',
          },
        ];

        (AsyncStorage.getItem as jest.Mock).mockResolvedValue(JSON.stringify(mockEntries));

        const cachedEntries = await mobileStorageService.getCachedEntries();

        expect(cachedEntries).toEqual(mockEntries);
      });

      it('should get last sync time', async () => {
        const mockDate = '2025-01-01T12:00:00.000Z';
        (AsyncStorage.getItem as jest.Mock).mockResolvedValue(mockDate);

        const lastSync = await mobileStorageService.getLastSyncTime();

        expect(lastSync).toEqual(new Date(mockDate));
      });
    });

    describe('User Preferences', () => {
      it('should save user preferences', async () => {
        const preferences: UserPreferences = {
          notifications_enabled: true,
          reminder_time: '20:00',
          preferred_persona: 'pulse',
          theme: 'auto',
        };

        await mobileStorageService.saveUserPreferences(preferences);

        expect(AsyncStorage.setItem).toHaveBeenCalledWith(
          'pulsecheck_user_preferences',
          JSON.stringify(preferences)
        );
      });

      it('should get user preferences with defaults', async () => {
        (AsyncStorage.getItem as jest.Mock).mockResolvedValue(null);

        const preferences = await mobileStorageService.getUserPreferences();

        expect(preferences).toEqual({
          notifications_enabled: true,
          reminder_time: '20:00',
          preferred_persona: 'auto',
          theme: 'auto',
        });
      });

      it('should get saved user preferences', async () => {
        const savedPreferences: UserPreferences = {
          notifications_enabled: false,
          reminder_time: '09:00',
          preferred_persona: 'sage',
          theme: 'dark',
        };

        (AsyncStorage.getItem as jest.Mock).mockResolvedValue(JSON.stringify(savedPreferences));

        const preferences = await mobileStorageService.getUserPreferences();

        expect(preferences).toEqual(savedPreferences);
      });
    });

    describe('Storage Info and Utilities', () => {
      it('should get storage info', async () => {
        const mockDrafts = [{ id: 'draft_1', content: 'Test', mood_level: 5, energy_level: 5, stress_level: 5, created_at: '2025-01-01T00:00:00.000Z', is_draft: true }];
        const mockCached = [{ id: '1', content: 'Cached', mood_level: 5, energy_level: 5, stress_level: 5, created_at: '2025-01-01T00:00:00.000Z', user_id: 'user123' }];
        const mockLastSync = '2025-01-01T12:00:00.000Z';

        (AsyncStorage.getItem as jest.Mock)
          .mockResolvedValueOnce(JSON.stringify(mockDrafts))
          .mockResolvedValueOnce(JSON.stringify(mockCached))
          .mockResolvedValueOnce(mockLastSync);

        const storageInfo = await mobileStorageService.getStorageInfo();

        expect(storageInfo.draftCount).toBe(1);
        expect(storageInfo.cachedCount).toBe(1);
        expect(storageInfo.lastSync).toEqual(new Date(mockLastSync));
        expect(storageInfo.totalSize).toMatch(/\d+(\.\d+)? (bytes|KB)/);
      });

      it('should clear all data', async () => {
        await mobileStorageService.clearAllData();

        expect(AsyncStorage.removeItem).toHaveBeenCalledTimes(4);
        expect(AsyncStorage.removeItem).toHaveBeenCalledWith('pulsecheck_draft_entries');
        expect(AsyncStorage.removeItem).toHaveBeenCalledWith('pulsecheck_cached_entries');
        expect(AsyncStorage.removeItem).toHaveBeenCalledWith('pulsecheck_user_preferences');
        expect(AsyncStorage.removeItem).toHaveBeenCalledWith('pulsecheck_last_sync');
      });
    });

    describe('Network Connectivity', () => {
      it('should detect online status', async () => {
        (global.fetch as jest.Mock).mockResolvedValue({ ok: true });

        const isOnline = await mobileStorageService.isOnline();

        expect(isOnline).toBe(true);
        expect(global.fetch).toHaveBeenCalledWith(
          'https://pulsecheck-mobile-app-production.up.railway.app/health',
          { method: 'HEAD', cache: 'no-cache' }
        );
      });

      it('should detect offline status', async () => {
        (global.fetch as jest.Mock).mockRejectedValue(new Error('Network error'));

        const isOnline = await mobileStorageService.isOnline();

        expect(isOnline).toBe(false);
      });
    });
  });

  describe('Mobile Sync Service', () => {
    describe('Create Journal Entry', () => {
      it('should create entry online when connected', async () => {
        const mockEntry: JournalEntryCreate = {
          content: 'Online test entry',
          mood_level: 8,
          energy_level: 7,
          stress_level: 3,
        };

        const mockCreatedEntry = {
          id: '123',
          ...mockEntry,
          created_at: '2025-01-01T00:00:00.000Z',
          user_id: 'user123',
        };

        // Mock online status and API call
        (global.fetch as jest.Mock)
          .mockResolvedValueOnce({ ok: true }) // isOnline check
          .mockResolvedValueOnce({ 
            ok: true, 
            json: () => Promise.resolve(mockCreatedEntry) 
          }); // API call

        const result = await mobileSyncService.createJournalEntry(mockEntry);

        expect(result.success).toBe(true);
        expect(result.entry).toEqual(mockCreatedEntry);
        expect(result.isOffline).toBe(false);
      });

      it('should save as draft when offline', async () => {
        const mockEntry: JournalEntryCreate = {
          content: 'Offline test entry',
          mood_level: 6,
          energy_level: 5,
          stress_level: 6,
        };

        // Mock offline status
        (global.fetch as jest.Mock).mockRejectedValue(new Error('Network error'));

        const result = await mobileSyncService.createJournalEntry(mockEntry);

        expect(result.success).toBe(true);
        expect(result.draftId).toMatch(/^draft_\d+_[a-z0-9]+$/);
        expect(result.isOffline).toBe(true);
      });

      it('should fallback to offline when API fails', async () => {
        const mockEntry: JournalEntryCreate = {
          content: 'Fallback test entry',
          mood_level: 5,
          energy_level: 5,
          stress_level: 5,
        };

        // Mock online but API failure
        (global.fetch as jest.Mock)
          .mockResolvedValueOnce({ ok: true }) // isOnline check
          .mockRejectedValueOnce(new Error('API error')); // API call fails

        const result = await mobileSyncService.createJournalEntry(mockEntry);

        expect(result.success).toBe(true);
        expect(result.draftId).toBeDefined();
        expect(result.isOffline).toBe(true);
      });
    });

    describe('Get Journal Entries', () => {
      it('should fetch fresh entries when online and refresh needed', async () => {
        const mockEntries = [
          {
            id: '1',
            content: 'Fresh entry',
            mood_level: 7,
            energy_level: 6,
            stress_level: 4,
            created_at: '2025-01-01T00:00:00.000Z',
            user_id: 'user123',
          },
        ];

        // Mock online status and API call
        (global.fetch as jest.Mock)
          .mockResolvedValueOnce({ ok: true }) // isOnline check
          .mockResolvedValueOnce({ 
            ok: true, 
            json: () => Promise.resolve(mockEntries) 
          }); // API call

        // Mock no last sync (needs refresh)
        (AsyncStorage.getItem as jest.Mock).mockResolvedValue(null);

        const result = await mobileSyncService.getJournalEntries();

        expect(result.entries).toEqual(mockEntries);
        expect(result.isFromCache).toBe(false);
      });

      it('should return cached entries when offline', async () => {
        const mockCachedEntries = [
          {
            id: '1',
            content: 'Cached entry',
            mood_level: 6,
            energy_level: 5,
            stress_level: 5,
            created_at: '2025-01-01T00:00:00.000Z',
            user_id: 'user123',
          },
        ];

        // Mock offline status
        (global.fetch as jest.Mock).mockRejectedValue(new Error('Network error'));

        // Mock cached entries
        (AsyncStorage.getItem as jest.Mock)
          .mockResolvedValueOnce(JSON.stringify(mockCachedEntries)) // cached entries
          .mockResolvedValueOnce('2025-01-01T12:00:00.000Z'); // last sync

        const result = await mobileSyncService.getJournalEntries();

        expect(result.entries).toEqual(mockCachedEntries);
        expect(result.isFromCache).toBe(true);
      });
    });

    describe('Sync Draft Entries', () => {
      it('should sync all draft entries successfully', async () => {
        const mockDrafts = [
          {
            id: 'draft_1',
            content: 'Draft 1',
            mood_level: 7,
            energy_level: 6,
            stress_level: 4,
            created_at: '2025-01-01T00:00:00.000Z',
            is_draft: true,
          },
          {
            id: 'draft_2',
            content: 'Draft 2',
            mood_level: 8,
            energy_level: 7,
            stress_level: 3,
            created_at: '2025-01-01T01:00:00.000Z',
            is_draft: true,
          },
        ];

        // Mock online status and draft entries
        (global.fetch as jest.Mock)
          .mockResolvedValueOnce({ ok: true }) // isOnline check
          .mockResolvedValue({ 
            ok: true, 
            json: () => Promise.resolve({ id: 'synced_entry' }) 
          }); // API calls

        (AsyncStorage.getItem as jest.Mock).mockResolvedValue(JSON.stringify(mockDrafts));

        const result = await mobileSyncService.syncDraftEntries();

        expect(result.success).toBe(true);
        expect(result.syncedEntries).toBe(2);
        expect(result.failedEntries).toBe(0);
        expect(result.errors).toEqual([]);
      });

      it('should handle partial sync failures', async () => {
        const mockDrafts = [
          {
            id: 'draft_1',
            content: 'Draft 1',
            mood_level: 7,
            energy_level: 6,
            stress_level: 4,
            created_at: '2025-01-01T00:00:00.000Z',
            is_draft: true,
          },
          {
            id: 'draft_2',
            content: 'Draft 2',
            mood_level: 8,
            energy_level: 7,
            stress_level: 3,
            created_at: '2025-01-01T01:00:00.000Z',
            is_draft: true,
          },
        ];

        // Mock online status, first sync succeeds, second fails
        (global.fetch as jest.Mock)
          .mockResolvedValueOnce({ ok: true }) // isOnline check
          .mockResolvedValueOnce({ 
            ok: true, 
            json: () => Promise.resolve({ id: 'synced_entry' }) 
          }) // First API call succeeds
          .mockRejectedValueOnce(new Error('API error')); // Second API call fails

        (AsyncStorage.getItem as jest.Mock).mockResolvedValue(JSON.stringify(mockDrafts));

        const result = await mobileSyncService.syncDraftEntries();

        expect(result.success).toBe(false);
        expect(result.syncedEntries).toBe(1);
        expect(result.failedEntries).toBe(1);
        expect(result.errors).toHaveLength(1);
      });

      it('should return early when offline', async () => {
        // Mock offline status
        (global.fetch as jest.Mock).mockRejectedValue(new Error('Network error'));

        const result = await mobileSyncService.syncDraftEntries();

        expect(result.success).toBe(false);
        expect(result.syncedEntries).toBe(0);
        expect(result.failedEntries).toBe(0);
        expect(result.errors).toEqual(['Device is offline']);
      });

      it('should handle no drafts to sync', async () => {
        // Mock online status and no drafts
        (global.fetch as jest.Mock).mockResolvedValue({ ok: true });
        (AsyncStorage.getItem as jest.Mock).mockResolvedValue('[]');

        const result = await mobileSyncService.syncDraftEntries();

        expect(result.success).toBe(true);
        expect(result.syncedEntries).toBe(0);
        expect(result.failedEntries).toBe(0);
        expect(result.errors).toEqual([]);
      });
    });

    describe('Sync Status', () => {
      it('should get comprehensive sync status', async () => {
        const mockDrafts = [{ id: 'draft_1', content: 'Test', mood_level: 5, energy_level: 5, stress_level: 5, created_at: '2025-01-01T00:00:00.000Z', is_draft: true }];
        const mockLastSync = '2025-01-01T12:00:00.000Z';

        // Mock online status
        (global.fetch as jest.Mock).mockResolvedValue({ ok: true });

        (AsyncStorage.getItem as jest.Mock)
          .mockResolvedValueOnce(JSON.stringify(mockDrafts))
          .mockResolvedValueOnce(mockLastSync);

        const status = await mobileSyncService.getSyncStatus();

        expect(status.isOnline).toBe(true);
        expect(status.draftCount).toBe(1);
        expect(status.lastSync).toEqual(new Date(mockLastSync));
        expect(status.needsSync).toBe(true);
        expect(status.isCurrentlySyncing).toBe(false);
      });
    });

    describe('Auto Sync', () => {
      it('should auto-sync when conditions are met', async () => {
        const mockDrafts = [{ id: 'draft_1', content: 'Test', mood_level: 5, energy_level: 5, stress_level: 5, created_at: '2025-01-01T00:00:00.000Z', is_draft: true }];

        // Mock online status and successful sync
        (global.fetch as jest.Mock)
          .mockResolvedValueOnce({ ok: true }) // isOnline check for status
          .mockResolvedValueOnce({ ok: true }) // isOnline check for sync
          .mockResolvedValue({ 
            ok: true, 
            json: () => Promise.resolve({ id: 'synced_entry' }) 
          }); // API calls

        (AsyncStorage.getItem as jest.Mock)
          .mockResolvedValueOnce(JSON.stringify(mockDrafts)) // getDraftEntries for status
          .mockResolvedValueOnce('2025-01-01T12:00:00.000Z') // getLastSyncTime for status
          .mockResolvedValueOnce(JSON.stringify(mockDrafts)); // getDraftEntries for sync

        await mobileSyncService.autoSync();

        // Should have attempted sync
        expect(global.fetch).toHaveBeenCalledTimes(3); // status check + sync check + API call
      });

      it('should not auto-sync when no drafts exist', async () => {
        // Mock online status and no drafts
        (global.fetch as jest.Mock).mockResolvedValue({ ok: true });
        (AsyncStorage.getItem as jest.Mock)
          .mockResolvedValueOnce('[]') // no drafts
          .mockResolvedValueOnce('2025-01-01T12:00:00.000Z'); // last sync

        await mobileSyncService.autoSync();

        // Should only check status, not attempt sync
        expect(global.fetch).toHaveBeenCalledTimes(1);
      });
    });

    describe('Force Refresh', () => {
      it('should force refresh successfully', async () => {
        const mockEntries = [
          {
            id: '1',
            content: 'Refreshed entry',
            mood_level: 9,
            energy_level: 8,
            stress_level: 2,
            created_at: '2025-01-01T00:00:00.000Z',
            user_id: 'user123',
          },
        ];

        // Mock online status and API call
        (global.fetch as jest.Mock)
          .mockResolvedValueOnce({ ok: true }) // isOnline check
          .mockResolvedValueOnce({ ok: true }) // isOnline check for getJournalEntries
          .mockResolvedValueOnce({ 
            ok: true, 
            json: () => Promise.resolve(mockEntries) 
          }); // API call

        const result = await mobileSyncService.forceRefresh();

        expect(result.success).toBe(true);
        expect(result.error).toBeUndefined();
      });

      it('should fail force refresh when offline', async () => {
        // Mock offline status
        (global.fetch as jest.Mock).mockRejectedValue(new Error('Network error'));

        const result = await mobileSyncService.forceRefresh();

        expect(result.success).toBe(false);
        expect(result.error).toBe('Device is offline');
      });
    });
  });

  describe('Error Handling and Edge Cases', () => {
    it('should handle AsyncStorage errors gracefully', async () => {
      (AsyncStorage.getItem as jest.Mock).mockRejectedValue(new Error('Storage error'));

      const drafts = await mobileStorageService.getDraftEntries();

      expect(drafts).toEqual([]);
    });

    it('should handle JSON parsing errors', async () => {
      (AsyncStorage.getItem as jest.Mock).mockResolvedValue('invalid json');

      const drafts = await mobileStorageService.getDraftEntries();

      expect(drafts).toEqual([]);
    });

    it('should handle network timeouts', async () => {
      (global.fetch as jest.Mock).mockImplementation(() => 
        new Promise((_, reject) => 
          setTimeout(() => reject(new Error('Timeout')), 100)
        )
      );

      const isOnline = await mobileStorageService.isOnline();

      expect(isOnline).toBe(false);
    });

    it('should prevent concurrent sync operations', async () => {
      // Mock online status and slow API calls
      (global.fetch as jest.Mock)
        .mockResolvedValue({ ok: true })
        .mockImplementation(() => 
          new Promise(resolve => 
            setTimeout(() => resolve({ 
              ok: true, 
              json: () => Promise.resolve({ id: 'synced' }) 
            }), 200)
          )
        );

      (AsyncStorage.getItem as jest.Mock).mockResolvedValue(JSON.stringify([
        { id: 'draft_1', content: 'Test', mood_level: 5, energy_level: 5, stress_level: 5, created_at: '2025-01-01T00:00:00.000Z', is_draft: true }
      ]));

      // Start two sync operations
      const sync1Promise = mobileSyncService.syncDraftEntries();
      const sync2Promise = mobileSyncService.syncDraftEntries();

      const [result1, result2] = await Promise.all([sync1Promise, sync2Promise]);

      // One should succeed, one should be rejected due to concurrent sync
      const successCount = [result1, result2].filter(r => r.success).length;
      const errorCount = [result1, result2].filter(r => !r.success && r.errors.includes('Sync already in progress')).length;

      expect(successCount).toBe(1);
      expect(errorCount).toBe(1);
    });
  });
});

// Integration test helper
export const runOfflineFeatureTests = async () => {
  console.log('🧪 Running comprehensive offline feature tests...');
  
  try {
    // Test storage service
    const testEntry: JournalEntryCreate = {
      content: 'Integration test entry',
      mood_level: 7,
      energy_level: 6,
      stress_level: 4,
    };

    // Save draft
    const draftId = await mobileStorageService.saveDraftEntry(testEntry);
    console.log('✅ Draft saved:', draftId);

    // Get drafts
    const drafts = await mobileStorageService.getDraftEntries();
    console.log('✅ Drafts retrieved:', drafts.length);

    // Test preferences
    const preferences: UserPreferences = {
      notifications_enabled: true,
      reminder_time: '20:00',
      preferred_persona: 'pulse',
      theme: 'auto',
    };
    await mobileStorageService.saveUserPreferences(preferences);
    const savedPrefs = await mobileStorageService.getUserPreferences();
    console.log('✅ Preferences saved and retrieved');

    // Test network detection
    const isOnline = await mobileStorageService.isOnline();
    console.log('✅ Network status:', isOnline ? 'Online' : 'Offline');

    // Test sync status
    const syncStatus = await mobileSyncService.getSyncStatus();
    console.log('✅ Sync status:', syncStatus);

    // Get storage info
    const storageInfo = await mobileStorageService.getStorageInfo();
    console.log('✅ Storage info:', storageInfo);

    console.log('🎉 All offline feature tests passed!');
    return true;
  } catch (error) {
    console.error('❌ Offline feature test failed:', error);
    return false;
  }
}; 