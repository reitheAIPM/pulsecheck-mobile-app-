// Sync Service for PulseCheck React Native App
// Handles online/offline synchronization and data management

import { mobileApiService, JournalEntry, JournalEntryCreate } from './api';
import { mobileStorageService, DraftEntry } from './storage';

export interface SyncResult {
  success: boolean;
  syncedEntries: number;
  failedEntries: number;
  errors: string[];
}

class MobileSyncService {
  private isCurrentlySyncing = false;

  // Create journal entry with offline support
  async createJournalEntry(entry: JournalEntryCreate): Promise<{ 
    success: boolean; 
    entry?: JournalEntry; 
    draftId?: string; 
    isOffline: boolean;
  }> {
    const isOnline = await mobileStorageService.isOnline();
    
    if (isOnline) {
      try {
        // Try to create online first
        const createdEntry = await mobileApiService.createJournalEntry(entry);
        
        // Cache the successful entry
        const cachedEntries = await mobileStorageService.getCachedEntries();
        await mobileStorageService.cacheEntries([createdEntry, ...cachedEntries]);
        
        console.log('✅ Entry created online and cached');
        return { success: true, entry: createdEntry, isOffline: false };
      } catch (error) {
        console.warn('⚠️ Online creation failed, saving as draft:', error);
        // Fall back to offline mode
      }
    }
    
    // Save as draft for offline mode
    try {
      const draftId = await mobileStorageService.saveDraftEntry(entry);
      console.log('📝 Entry saved as draft for offline sync');
      return { success: true, draftId, isOffline: true };
    } catch (error) {
      console.error('❌ Failed to save draft entry:', error);
      return { success: false, isOffline: true };
    }
  }

  // Get journal entries with offline support
  async getJournalEntries(forceRefresh = false): Promise<{
    entries: JournalEntry[];
    isFromCache: boolean;
    lastSync: Date | null;
  }> {
    const isOnline = await mobileStorageService.isOnline();
    
    if (isOnline && (forceRefresh || await this.shouldRefreshCache())) {
      try {
        // Fetch fresh data from API
        const freshEntries = await mobileApiService.getJournalEntries(1, 50);
        
        // Cache the fresh data
        await mobileStorageService.cacheEntries(freshEntries);
        
        const lastSync = await mobileStorageService.getLastSyncTime();
        console.log('🔄 Fresh entries loaded and cached');
        return { entries: freshEntries, isFromCache: false, lastSync };
      } catch (error) {
        console.warn('⚠️ Failed to fetch fresh entries, using cache:', error);
      }
    }
    
    // Return cached entries
    const cachedEntries = await mobileStorageService.getCachedEntries();
    const lastSync = await mobileStorageService.getLastSyncTime();
    
    console.log('💾 Returning cached entries:', cachedEntries.length);
    return { entries: cachedEntries, isFromCache: true, lastSync };
  }

  // Sync draft entries when online
  async syncDraftEntries(): Promise<SyncResult> {
    if (this.isCurrentlySyncing) {
      console.log('🔄 Sync already in progress');
      return { success: false, syncedEntries: 0, failedEntries: 0, errors: ['Sync already in progress'] };
    }

    const isOnline = await mobileStorageService.isOnline();
    if (!isOnline) {
      return { success: false, syncedEntries: 0, failedEntries: 0, errors: ['Device is offline'] };
    }

    this.isCurrentlySyncing = true;
    console.log('🔄 Starting draft sync...');

    try {
      const draftEntries = await mobileStorageService.getDraftEntries();
      
      if (draftEntries.length === 0) {
        console.log('✅ No drafts to sync');
        return { success: true, syncedEntries: 0, failedEntries: 0, errors: [] };
      }

      let syncedEntries = 0;
      let failedEntries = 0;
      const errors: string[] = [];
      const syncedDraftIds: string[] = [];

      // Sync each draft entry
      for (const draft of draftEntries) {
        try {
          const entryToCreate: JournalEntryCreate = {
            content: draft.content,
            mood_level: draft.mood_level,
            energy_level: draft.energy_level,
            stress_level: draft.stress_level,
            sleep_hours: draft.sleep_hours,
            work_hours: draft.work_hours,
            tags: draft.tags,
            work_challenges: draft.work_challenges,
            gratitude_items: draft.gratitude_items,
          };

          const createdEntry = await mobileApiService.createJournalEntry(entryToCreate);
          
          // Add to cache
          const cachedEntries = await mobileStorageService.getCachedEntries();
          await mobileStorageService.cacheEntries([createdEntry, ...cachedEntries]);
          
          syncedDraftIds.push(draft.id);
          syncedEntries++;
          
          console.log(`✅ Synced draft: ${draft.id}`);
        } catch (error) {
          failedEntries++;
          errors.push(`Failed to sync draft ${draft.id}: ${error}`);
          console.error(`❌ Failed to sync draft ${draft.id}:`, error);
        }
      }

      // Remove successfully synced drafts
      for (const draftId of syncedDraftIds) {
        await mobileStorageService.deleteDraftEntry(draftId);
      }

      console.log(`🔄 Sync complete: ${syncedEntries} synced, ${failedEntries} failed`);
      
      return {
        success: failedEntries === 0,
        syncedEntries,
        failedEntries,
        errors,
      };

    } catch (error) {
      console.error('❌ Sync process failed:', error);
      return {
        success: false,
        syncedEntries: 0,
        failedEntries: 0,
        errors: [`Sync process failed: ${error}`],
      };
    } finally {
      this.isCurrentlySyncing = false;
    }
  }

  // Check if cache should be refreshed
  private async shouldRefreshCache(): Promise<boolean> {
    const lastSync = await mobileStorageService.getLastSyncTime();
    
    if (!lastSync) {
      return true; // No previous sync
    }
    
    const now = new Date();
    const timeSinceSync = now.getTime() - lastSync.getTime();
    const fiveMinutes = 5 * 60 * 1000;
    
    return timeSinceSync > fiveMinutes;
  }

  // Get sync status
  async getSyncStatus(): Promise<{
    isOnline: boolean;
    draftCount: number;
    lastSync: Date | null;
    needsSync: boolean;
    isCurrentlySyncing: boolean;
  }> {
    const [isOnline, drafts, lastSync] = await Promise.all([
      mobileStorageService.isOnline(),
      mobileStorageService.getDraftEntries(),
      mobileStorageService.getLastSyncTime(),
    ]);

    return {
      isOnline,
      draftCount: drafts.length,
      lastSync,
      needsSync: drafts.length > 0 && isOnline,
      isCurrentlySyncing: this.isCurrentlySyncing,
    };
  }

  // Auto-sync when app becomes active
  async autoSync(): Promise<void> {
    try {
      const status = await this.getSyncStatus();
      
      if (status.needsSync && !status.isCurrentlySyncing) {
        console.log('🔄 Auto-syncing draft entries...');
        await this.syncDraftEntries();
      }
    } catch (error) {
      console.error('❌ Auto-sync failed:', error);
    }
  }

  // Force refresh from server
  async forceRefresh(): Promise<{ success: boolean; error?: string }> {
    try {
      const isOnline = await mobileStorageService.isOnline();
      
      if (!isOnline) {
        return { success: false, error: 'Device is offline' };
      }

      // Clear cache and fetch fresh data
      await mobileStorageService.cacheEntries([]);
      const result = await this.getJournalEntries(true);
      
      console.log('🔄 Force refresh completed');
      return { success: true };
    } catch (error) {
      console.error('❌ Force refresh failed:', error);
      return { success: false, error: String(error) };
    }
  }
}

// Export singleton instance
export const mobileSyncService = new MobileSyncService(); 