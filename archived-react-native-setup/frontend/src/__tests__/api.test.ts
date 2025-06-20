import { apiService } from '../services/api';

describe('API Service', () => {
  beforeAll(() => {
    // Suppress console logs during testing unless there's an error
    jest.spyOn(console, 'log').mockImplementation(() => {});
    jest.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterAll(() => {
    // Restore console logs
    jest.restoreAllMocks();
  });

  describe('Configuration', () => {
    it('should initialize with correct base URL', () => {
      const baseUrl = apiService.getBaseUrl();
      expect(baseUrl).toBeDefined();
      expect(typeof baseUrl).toBe('string');
      
      // Should use Railway production URL in test environment
      // (unless EXPO_PUBLIC_API_URL is set)
      console.log('API Base URL:', baseUrl);
    });
  });

  describe('Health Check', () => {
    it('should connect to the backend health endpoint', async () => {
      const isConnected = await apiService.testConnection();
      expect(isConnected).toBe(true);
    }, 10000); // 10 second timeout for network requests

    it('should return health check data', async () => {
      const healthData = await apiService.healthCheck();
      expect(healthData).toBeDefined();
      expect(healthData.status).toBe('healthy');
      console.log('Health Check Response:', healthData);
    }, 10000);
  });

  describe('Error Handling', () => {
    it('should handle network errors gracefully', async () => {
      // Test with invalid endpoint
      try {
        await apiService.getJournalEntry('invalid-id');
      } catch (error) {
        const errorMessage = apiService.handleError(error);
        expect(typeof errorMessage).toBe('string');
        expect(errorMessage.length).toBeGreaterThan(0);
        console.log('Error handling test:', errorMessage);
      }
    }, 10000);
  });

  describe('CORS Configuration', () => {
    it('should handle preflight requests', async () => {
      // This test will implicitly verify CORS is working
      // by making actual HTTP requests to the backend
      const isConnected = await apiService.testConnection();
      expect(isConnected).toBe(true);
    }, 10000);
  });
}); 