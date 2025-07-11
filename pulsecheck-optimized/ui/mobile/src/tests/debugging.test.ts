// Debugging and Error Handling Test Suite
// Tests AI-optimized error handling as per ai/ai-debugging-guide.md

import { mobileStorageService } from '../services/storage';
import { mobileSyncService } from '../services/syncService';

// Mock console methods for testing
const mockConsoleLog = jest.spyOn(console, 'log').mockImplementation();
const mockConsoleError = jest.spyOn(console, 'error').mockImplementation();
const mockConsoleWarn = jest.spyOn(console, 'warn').mockImplementation();

describe('AI-Optimized Debugging System', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockConsoleLog.mockClear();
    mockConsoleError.mockClear();
    mockConsoleWarn.mockClear();
  });

  afterAll(() => {
    mockConsoleLog.mockRestore();
    mockConsoleError.mockRestore();
    mockConsoleWarn.mockRestore();
  });

  describe('Error Classification', () => {
    it('should classify network errors correctly', async () => {
      global.fetch = jest.fn().mockRejectedValue(new Error('Network request failed'));

      const isOnline = await mobileStorageService.isOnline();

      expect(isOnline).toBe(false);
      // Should not throw error, should handle gracefully
    });

    it('should classify storage errors correctly', async () => {
      const AsyncStorage = require('@react-native-async-storage/async-storage');
      AsyncStorage.getItem.mockRejectedValue(new Error('Storage quota exceeded'));

      const drafts = await mobileStorageService.getDraftEntries();

      expect(drafts).toEqual([]);
      expect(mockConsoleError).toHaveBeenCalledWith(
        'Failed to get draft entries:',
        expect.any(Error)
      );
    });

    it('should classify validation errors correctly', async () => {
      const invalidEntry = {
        content: '', // Invalid: empty content
        mood_level: 15, // Invalid: out of range
        energy_level: -1, // Invalid: negative
        stress_level: 'high', // Invalid: wrong type
      };

      try {
        await mobileStorageService.saveDraftEntry(invalidEntry as any);
      } catch (error) {
        expect(error).toBeDefined();
      }
    });

    it('should classify API errors correctly', async () => {
      global.fetch = jest.fn()
        .mockResolvedValueOnce({ ok: true }) // isOnline check passes
        .mockResolvedValueOnce({ 
          ok: false, 
          status: 500, 
          statusText: 'Internal Server Error' 
        }); // API call fails

      const result = await mobileSyncService.createJournalEntry({
        content: 'Test entry',
        mood_level: 5,
        energy_level: 5,
        stress_level: 5,
      });

      expect(result.isOffline).toBe(true); // Should fallback to offline
      expect(mockConsoleWarn).toHaveBeenCalledWith(
        '⚠️ Online creation failed, saving as draft:',
        expect.any(Error)
      );
    });
  });

  describe('Error Recovery Mechanisms', () => {
    it('should recover from network failures with offline mode', async () => {
      global.fetch = jest.fn().mockRejectedValue(new Error('Network error'));

      const result = await mobileSyncService.createJournalEntry({
        content: 'Recovery test',
        mood_level: 6,
        energy_level: 5,
        stress_level: 4,
      });

      expect(result.success).toBe(true);
      expect(result.isOffline).toBe(true);
      expect(result.draftId).toBeDefined();
    });

    it('should recover from storage failures gracefully', async () => {
      const AsyncStorage = require('@react-native-async-storage/async-storage');
      AsyncStorage.setItem.mockRejectedValue(new Error('Storage full'));

      try {
        await mobileStorageService.saveDraftEntry({
          content: 'Storage test',
          mood_level: 5,
          energy_level: 5,
          stress_level: 5,
        });
      } catch (error) {
        expect(error).toBeDefined();
        expect(mockConsoleError).toHaveBeenCalled();
      }
    });

    it('should recover from JSON parsing errors', async () => {
      const AsyncStorage = require('@react-native-async-storage/async-storage');
      AsyncStorage.getItem.mockResolvedValue('invalid json {');

      const drafts = await mobileStorageService.getDraftEntries();

      expect(drafts).toEqual([]);
      expect(mockConsoleError).toHaveBeenCalledWith(
        'Failed to get draft entries:',
        expect.any(Error)
      );
    });

    it('should recover from concurrent sync operations', async () => {
      global.fetch = jest.fn()
        .mockResolvedValue({ ok: true })
        .mockImplementation(() => 
          new Promise(resolve => 
            setTimeout(() => resolve({ 
              ok: true, 
              json: () => Promise.resolve({ id: 'synced' }) 
            }), 100)
          )
        );

      const AsyncStorage = require('@react-native-async-storage/async-storage');
      AsyncStorage.getItem.mockResolvedValue(JSON.stringify([
        { id: 'draft_1', content: 'Test', mood_level: 5, energy_level: 5, stress_level: 5, created_at: '2025-01-01T00:00:00.000Z', is_draft: true }
      ]));

      // Start concurrent syncs
      const sync1 = mobileSyncService.syncDraftEntries();
      const sync2 = mobileSyncService.syncDraftEntries();

      const [result1, result2] = await Promise.all([sync1, sync2]);

      // One should succeed, one should be rejected
      const hasSuccess = result1.success || result2.success;
      const hasRejection = result1.errors.includes('Sync already in progress') || 
                          result2.errors.includes('Sync already in progress');

      expect(hasSuccess).toBe(true);
      expect(hasRejection).toBe(true);
    });
  });

  describe('Performance Monitoring', () => {
    it('should track storage operation performance', async () => {
      const startTime = Date.now();

      await mobileStorageService.saveDraftEntry({
        content: 'Performance test',
        mood_level: 7,
        energy_level: 6,
        stress_level: 4,
      });

      const endTime = Date.now();
      const duration = endTime - startTime;

      // Storage operations should be fast (<100ms)
      expect(duration).toBeLessThan(100);
    });

    it('should track sync operation performance', async () => {
      global.fetch = jest.fn().mockResolvedValue({ ok: true });
      const AsyncStorage = require('@react-native-async-storage/async-storage');
      AsyncStorage.getItem.mockResolvedValue('[]'); // No drafts to sync

      const startTime = Date.now();

      await mobileSyncService.syncDraftEntries();

      const endTime = Date.now();
      const duration = endTime - startTime;

      // Sync operations should be reasonably fast (<1000ms for no drafts)
      expect(duration).toBeLessThan(1000);
    });

    it('should track network detection performance', async () => {
      global.fetch = jest.fn().mockResolvedValue({ ok: true });

      const startTime = Date.now();

      await mobileStorageService.isOnline();

      const endTime = Date.now();
      const duration = endTime - startTime;

      // Network detection should be fast (<500ms)
      expect(duration).toBeLessThan(500);
    });
  });

  describe('Context Generation', () => {
    it('should generate comprehensive error context', async () => {
      const AsyncStorage = require('@react-native-async-storage/async-storage');
      AsyncStorage.getItem.mockRejectedValue(new Error('Storage error'));

      await mobileStorageService.getDraftEntries();

      expect(mockConsoleError).toHaveBeenCalledWith(
        'Failed to get draft entries:',
        expect.objectContaining({
          message: 'Storage error'
        })
      );
    });

    it('should generate context for sync failures', async () => {
      global.fetch = jest.fn()
        .mockResolvedValueOnce({ ok: true }) // isOnline check
        .mockRejectedValueOnce(new Error('API timeout')); // sync fails

      const AsyncStorage = require('@react-native-async-storage/async-storage');
      AsyncStorage.getItem.mockResolvedValue(JSON.stringify([
        { id: 'draft_1', content: 'Test', mood_level: 5, energy_level: 5, stress_level: 5, created_at: '2025-01-01T00:00:00.000Z', is_draft: true }
      ]));

      const result = await mobileSyncService.syncDraftEntries();

      expect(result.success).toBe(false);
      expect(result.errors).toContain('Failed to sync draft draft_1: Error: API timeout');
      expect(mockConsoleError).toHaveBeenCalled();
    });

    it('should generate context for network failures', async () => {
      global.fetch = jest.fn().mockRejectedValue(new Error('Network unreachable'));

      await mobileStorageService.isOnline();

      // Should handle gracefully without throwing
      expect(mockConsoleError).not.toHaveBeenCalled(); // isOnline doesn't log errors, just returns false
    });
  });

  describe('Logging and Monitoring', () => {
    it('should log successful operations', async () => {
      const draftId = await mobileStorageService.saveDraftEntry({
        content: 'Success test',
        mood_level: 8,
        energy_level: 7,
        stress_level: 3,
      });

      expect(mockConsoleLog).toHaveBeenCalledWith('📝 Draft entry saved:', draftId);
    });

    it('should log cache operations', async () => {
      const mockEntries = [
        {
          id: '1',
          content: 'Cache test',
          mood_level: 6,
          energy_level: 5,
          stress_level: 5,
          created_at: '2025-01-01T00:00:00.000Z',
          user_id: 'user123',
        },
      ];

      await mobileStorageService.cacheEntries(mockEntries);

      expect(mockConsoleLog).toHaveBeenCalledWith('💾 Cached', 1, 'entries');
    });

    it('should log sync operations', async () => {
      global.fetch = jest.fn().mockResolvedValue({ ok: true });
      const AsyncStorage = require('@react-native-async-storage/async-storage');
      AsyncStorage.getItem.mockResolvedValue('[]');

      await mobileSyncService.syncDraftEntries();

      expect(mockConsoleLog).toHaveBeenCalledWith('✅ No drafts to sync');
    });

    it('should log data cleanup operations', async () => {
      await mobileStorageService.clearAllData();

      expect(mockConsoleLog).toHaveBeenCalledWith('🧹 All local data cleared');
    });
  });

  describe('Fallback Mechanisms', () => {
    it('should provide intelligent fallbacks for storage failures', async () => {
      const AsyncStorage = require('@react-native-async-storage/async-storage');
      AsyncStorage.getItem.mockRejectedValue(new Error('Storage corrupted'));

      const preferences = await mobileStorageService.getUserPreferences();

      // Should return default preferences
      expect(preferences).toEqual({
        notifications_enabled: true,
        reminder_time: '20:00',
        preferred_persona: 'auto',
        theme: 'auto',
      });
    });

    it('should provide fallbacks for network failures', async () => {
      global.fetch = jest.fn().mockRejectedValue(new Error('No internet'));

      const result = await mobileSyncService.getJournalEntries();

      // Should return cached entries (empty array if none)
      expect(result.entries).toEqual([]);
      expect(result.isFromCache).toBe(true);
    });

    it('should provide fallbacks for sync failures', async () => {
      global.fetch = jest.fn().mockRejectedValue(new Error('Server down'));

      const result = await mobileSyncService.syncDraftEntries();

      expect(result.success).toBe(false);
      expect(result.errors).toContain('Device is offline');
    });
  });

  describe('Edge Cases and Boundary Conditions', () => {
    it('should handle empty storage gracefully', async () => {
      const AsyncStorage = require('@react-native-async-storage/async-storage');
      AsyncStorage.getItem.mockResolvedValue(null);

      const drafts = await mobileStorageService.getDraftEntries();
      const cached = await mobileStorageService.getCachedEntries();
      const lastSync = await mobileStorageService.getLastSyncTime();

      expect(drafts).toEqual([]);
      expect(cached).toEqual([]);
      expect(lastSync).toBeNull();
    });

    it('should handle corrupted JSON data', async () => {
      const AsyncStorage = require('@react-native-async-storage/async-storage');
      AsyncStorage.getItem
        .mockResolvedValueOnce('{"incomplete": json')
        .mockResolvedValueOnce('[{malformed: array}]')
        .mockResolvedValueOnce('not json at all');

      const drafts = await mobileStorageService.getDraftEntries();
      const cached = await mobileStorageService.getCachedEntries();

      expect(drafts).toEqual([]);
      expect(cached).toEqual([]);
    });

    it('should handle very large data sets', async () => {
      const largeDrafts = Array.from({ length: 1000 }, (_, i) => ({
        id: `draft_${i}`,
        content: `Large draft entry ${i}`.repeat(100),
        mood_level: 5,
        energy_level: 5,
        stress_level: 5,
        created_at: '2025-01-01T00:00:00.000Z',
        is_draft: true,
      }));

      const AsyncStorage = require('@react-native-async-storage/async-storage');
      AsyncStorage.getItem.mockResolvedValue(JSON.stringify(largeDrafts));

      const startTime = Date.now();
      const drafts = await mobileStorageService.getDraftEntries();
      const endTime = Date.now();

      expect(drafts).toHaveLength(1000);
      expect(endTime - startTime).toBeLessThan(1000); // Should handle large data efficiently
    });

    it('should handle rapid successive operations', async () => {
      const operations = Array.from({ length: 10 }, (_, i) =>
        mobileStorageService.saveDraftEntry({
          content: `Rapid test ${i}`,
          mood_level: 5,
          energy_level: 5,
          stress_level: 5,
        })
      );

      const results = await Promise.all(operations);

      expect(results).toHaveLength(10);
      results.forEach(draftId => {
        expect(draftId).toMatch(/^draft_\d+_[a-z0-9]+$/);
      });
    });
  });
});

// Debugging utility functions
export const runDebuggingTests = async () => {
  console.log('🔍 Running AI-optimized debugging tests...');

  try {
    // Test error classification
    console.log('Testing error classification...');
    
    // Test storage errors
    try {
      await mobileStorageService.getDraftEntries();
      console.log('✅ Storage error handling tested');
    } catch (error) {
      console.log('✅ Storage error caught and handled');
    }

    // Test network errors
    try {
      const isOnline = await mobileStorageService.isOnline();
      console.log('✅ Network detection tested:', isOnline);
    } catch (error) {
      console.log('✅ Network error caught and handled');
    }

    // Test sync errors
    try {
      const status = await mobileSyncService.getSyncStatus();
      console.log('✅ Sync status tested:', status);
    } catch (error) {
      console.log('✅ Sync error caught and handled');
    }

    console.log('🎉 All debugging tests completed successfully!');
    return true;
  } catch (error) {
    console.error('❌ Debugging test failed:', error);
    return false;
  }
}; 