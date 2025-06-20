import { apiService } from '../services/api';

describe('AI Integration Tests', () => {
  // Test scenarios based on real tech worker experiences
  const testScenarios = [
    {
      name: 'High Stress Sprint Week',
      journalEntry: {
        content: "Sprint review is tomorrow and I'm still debugging this critical production issue. Been working 12+ hour days this week and barely sleeping. Team is stressed, product manager keeps asking for updates every hour. Feel like I'm drowning and can't catch up.",
        mood_level: 3,
        energy_level: 2,
        stress_level: 9,
        sleep_hours: 4,
        work_hours: 12,
        tags: ["burnout", "deadlines", "production-issues", "overworked"],
        work_challenges: ["debugging", "tight-deadlines", "team-pressure"]
      },
      expectedThemes: ['burnout', 'overwork', 'sleep-deprivation'],
      expectedTone: 'supportive and understanding'
    },
    {
      name: 'Imposter Syndrome After Promotion',
      journalEntry: {
        content: "Got promoted to senior developer last month but feeling completely out of my depth. Everyone expects me to know everything but I feel like I'm just pretending. Code reviews are terrifying - what if they realize I don't belong here? Started avoiding speaking up in architecture discussions.",
        mood_level: 4,
        energy_level: 6,
        stress_level: 7,
        sleep_hours: 6,
        work_hours: 8,
        tags: ["imposter-syndrome", "anxiety", "new-role", "self-doubt"],
        work_challenges: ["imposter-syndrome", "increased-responsibility"]
      },
      expectedThemes: ['imposter-syndrome', 'confidence', 'growth'],
      expectedTone: 'encouraging and validating'
    },
    {
      name: 'Good Day with Balance',
      journalEntry: {
        content: "Had a really productive day! Fixed that tricky bug that's been bothering me for days, got positive feedback on my code review, and even left work at 5:30 to have dinner with family. Feeling good about the project timeline and my contributions to the team.",
        mood_level: 8,
        energy_level: 7,
        stress_level: 3,
        sleep_hours: 7,
        work_hours: 8,
        tags: ["productive", "success", "work-life-balance", "team-collaboration"],
        work_challenges: []
      },
      expectedThemes: ['success', 'balance', 'achievement'],
      expectedTone: 'celebratory and encouraging'
    },
    {
      name: 'Remote Work Isolation',
      journalEntry: {
        content: "Working from home for 2 years now and starting to feel really isolated. Miss the casual conversations with teammates. Zoom fatigue is real - back-to-back meetings all day. Hard to separate work and personal life when everything happens in the same room.",
        mood_level: 5,
        energy_level: 4,
        stress_level: 6,
        sleep_hours: 7,
        work_hours: 9,
        tags: ["remote-work", "isolation", "zoom-fatigue", "work-life-balance"],
        work_challenges: ["remote-work-isolation", "meeting-fatigue"]
      },
      expectedThemes: ['isolation', 'remote-work', 'connection'],
      expectedTone: 'understanding and practical'
    }
  ];

  describe('Journal Entry Creation and AI Analysis', () => {
    testScenarios.forEach((scenario) => {
      it(`should handle "${scenario.name}" scenario with appropriate AI response`, async () => {
        console.log(`\n🧪 Testing Scenario: ${scenario.name}`);
        
        try {
          // Step 1: Create journal entry
          console.log('📝 Creating journal entry...');
          const journalEntry = await apiService.createJournalEntry(scenario.journalEntry);
          
          expect(journalEntry).toBeDefined();
          expect(journalEntry.id).toBeDefined();
          expect(journalEntry.content).toBe(scenario.journalEntry.content);
          expect(journalEntry.mood_level).toBe(scenario.journalEntry.mood_level);
          
          console.log(`✅ Journal entry created with ID: ${journalEntry.id}`);
          
          // Step 2: Get AI analysis
          console.log('🤖 Requesting AI analysis...');
          const aiAnalysis = await apiService.getAIAnalysis(journalEntry.id, false);
          
          expect(aiAnalysis).toBeDefined();
          expect(aiAnalysis.pulse_message).toBeDefined();
          expect(aiAnalysis.pulse_message.length).toBeGreaterThan(50); // Meaningful response
          
          console.log('📊 AI Analysis Response:');
          console.log(`   Message: ${aiAnalysis.pulse_message}`);
          console.log(`   Wellness Score: ${aiAnalysis.overall_wellness_score}`);
          console.log(`   Burnout Risk: ${aiAnalysis.burnout_risk_level}`);
          
          // Step 3: Get Pulse response
          console.log('💬 Getting Pulse response...');
          const pulseResponse = await apiService.getPulseResponse(journalEntry.id);
          
          expect(pulseResponse).toBeDefined();
          expect(pulseResponse.message).toBeDefined();
          expect(pulseResponse.message.length).toBeGreaterThan(50);
          expect(pulseResponse.response_time_ms).toBeLessThan(5000); // <5 second response
          
          console.log('🎯 Pulse Response:');
          console.log(`   Message: ${pulseResponse.message}`);
          console.log(`   Follow-up: ${pulseResponse.follow_up_question || 'None'}`);
          console.log(`   Response Time: ${pulseResponse.response_time_ms}ms`);
          console.log(`   Confidence: ${pulseResponse.confidence_score}`);
          
          // Quality checks
          expect(pulseResponse.confidence_score).toBeGreaterThan(0.7);
          expect(pulseResponse.response_time_ms).toBeLessThan(5000);
          
          // Content quality checks
          const message = pulseResponse.message.toLowerCase();
          
          // Should not contain clinical language
          expect(message).not.toMatch(/\b(diagnos|disorder|symptom|patholog|therapeutic)\b/);
          
          // Should be personalized (mention tech work context)
          const techTerms = ['work', 'code', 'debug', 'team', 'project', 'develop', 'tech', 'sprint', 'meeting'];
          const containsTechContext = techTerms.some(term => message.includes(term));
          expect(containsTechContext).toBe(true);
          
          console.log(`✅ Scenario "${scenario.name}" completed successfully\n`);
          
        } catch (error) {
          console.error(`❌ Error in scenario "${scenario.name}":`, error);
          throw error;
        }
      }, 15000); // 15 second timeout for AI processing
    });
  });

  describe('AI Response Quality Standards', () => {
    it('should maintain consistent Pulse personality across different scenarios', async () => {
      console.log('\n🎭 Testing personality consistency...');
      
      const responses = [];
      
      // Test with subset of scenarios
      for (const scenario of testScenarios.slice(0, 2)) {
        const journalEntry = await apiService.createJournalEntry(scenario.journalEntry);
        const pulseResponse = await apiService.getPulseResponse(journalEntry.id);
        responses.push({
          scenario: scenario.name,
          message: pulseResponse.message,
          confidence: pulseResponse.confidence_score
        });
      }
      
      // Analyze consistency
      responses.forEach((response, index) => {
        console.log(`Response ${index + 1} (${response.scenario}):`);
        console.log(`   Confidence: ${response.confidence}`);
        console.log(`   Tone: ${response.message.substring(0, 100)}...`);
        
        // All responses should have good confidence
        expect(response.confidence).toBeGreaterThan(0.7);
        
        // Should maintain supportive tone
        const supportiveWords = ['understand', 'notice', 'support', 'help', 'care', 'here for'];
        const isSupportive = supportiveWords.some(word => 
          response.message.toLowerCase().includes(word)
        );
        expect(isSupportive).toBe(true);
      });
      
      console.log('✅ Personality consistency verified');
    }, 20000);

    it('should handle edge cases gracefully', async () => {
      console.log('\n🔬 Testing edge cases...');
      
      const edgeCases = [
        {
          name: 'Very short entry',
          content: "Bad day.",
          mood_level: 2,
          energy_level: 3,
          stress_level: 8
        },
        {
          name: 'Very positive entry',
          content: "Everything is amazing! Best day ever! Love my job and team!",
          mood_level: 10,
          energy_level: 10,
          stress_level: 1
        },
        {
          name: 'Technical jargon heavy',
          content: "Spent all day debugging a race condition in our microservices architecture. The Kubernetes deployment is failing due to memory leaks in the Redis cache invalidation logic.",
          mood_level: 4,
          energy_level: 5,
          stress_level: 7
        }
      ];
      
      for (const edgeCase of edgeCases) {
        console.log(`Testing: ${edgeCase.name}`);
        
        const journalEntry = await apiService.createJournalEntry({
          content: edgeCase.content,
          mood_level: edgeCase.mood_level,
          energy_level: edgeCase.energy_level,
          stress_level: edgeCase.stress_level,
          tags: [],
          work_challenges: []
        });
        
        const pulseResponse = await apiService.getPulseResponse(journalEntry.id);
        
        // Should still provide meaningful response
        expect(pulseResponse.message.length).toBeGreaterThan(30);
        expect(pulseResponse.confidence_score).toBeGreaterThan(0.5);
        
        console.log(`   ✅ Handled "${edgeCase.name}" appropriately`);
      }
      
      console.log('✅ Edge cases handled gracefully');
    }, 30000);
  });

  describe('Performance and Error Handling', () => {
    it('should respond within acceptable time limits', async () => {
      console.log('\n⏱️ Testing response performance...');
      
      const journalEntry = await apiService.createJournalEntry({
        content: "Quick performance test entry to check response times.",
        mood_level: 5,
        energy_level: 5,
        stress_level: 5,
        tags: ["test"],
        work_challenges: []
      });
      
      const startTime = Date.now();
      const pulseResponse = await apiService.getPulseResponse(journalEntry.id);
      const totalTime = Date.now() - startTime;
      
      console.log(`Total API Response Time: ${totalTime}ms`);
      console.log(`AI Processing Time: ${pulseResponse.response_time_ms}ms`);
      
      // Performance expectations
      expect(totalTime).toBeLessThan(10000); // Total < 10 seconds
      expect(pulseResponse.response_time_ms).toBeLessThan(5000); // AI < 5 seconds
      
      console.log('✅ Performance meets expectations');
    }, 15000);

    it('should handle API errors gracefully', async () => {
      console.log('\n🛡️ Testing error handling...');
      
      try {
        // Test with invalid ID
        await apiService.getPulseResponse('invalid-uuid');
        fail('Should have thrown an error');
      } catch (error) {
        const errorMessage = apiService.handleError(error);
        expect(typeof errorMessage).toBe('string');
        expect(errorMessage.length).toBeGreaterThan(0);
        console.log(`✅ Error handled gracefully: ${errorMessage}`);
      }
    }, 10000);
  });
}); 