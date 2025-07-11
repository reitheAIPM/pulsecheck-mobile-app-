# PulseCheck Repository Reorganization Plan
*For Continue.dev Cost Optimization*

## 📊 Current Analysis

**Total Tokens:** 791,850 tokens  
**Files Processed:** 236  
**Estimated Claude 3 Sonnet Cost:** $14.25  

### 🚨 Large Files Requiring Attention (>50K tokens)
- `PulseCheckMobile\package-lock.json` (135,594 tokens) → **EXCLUDE**
- `spark-realm\package-lock.json` (124,199 tokens) → **EXCLUDE**
- `ai\CONTRIBUTING.md` (26,885 tokens) → **CHUNK**
- `backend\app\routers\debug.py` (22,867 tokens) → **CHUNK**

---

## 🏗️ Proposed New Structure

```
pulsecheck-optimized/
├── core_ai/                    # ~150K tokens
│   ├── services/              # AI service files
│   ├── routers/               # AI-related endpoints
│   └── models/                # AI data models
├── ui/                        # ~200K tokens
│   ├── spark-realm/           # React frontend
│   └── mobile/                # React Native app
├── backend_core/              # ~100K tokens
│   ├── core/                  # Backend core utilities
│   ├── middleware/            # Backend middleware
│   └── main.py               # Main FastAPI app
├── docs/                      # ~50K tokens
│   ├── ai/                   # AI documentation
│   ├── api/                  # API documentation
│   └── guides/               # Project guides
├── configs/                   # ~10K tokens
│   ├── package.json files
│   ├── tsconfig files
│   └── deployment configs
└── excluded/                  # Large files to exclude
    ├── package-lock.json files
    ├── node_modules/
    └── build artifacts
```

---

## 📋 Detailed Reorganization

### 1. **core_ai/** (~150K tokens)
**Purpose:** All AI-related functionality
**Files:**
- `backend/app/services/adaptive_ai_service.py` (13,217 tokens)
- `backend/app/services/comprehensive_proactive_ai_service.py` (14,752 tokens)
- `backend/app/services/ai_debugging_service.py` (7,785 tokens)
- `backend/app/services/pulse_ai.py` (8,977 tokens)
- `backend/app/services/persona_service.py` (4,933 tokens)
- `backend/app/services/user_pattern_analyzer.py` (5,791 tokens)
- `backend/app/services/weekly_summary_service.py` (6,898 tokens)
- `backend/app/routers/adaptive_ai.py` (5,213 tokens)
- `backend/app/routers/ai_debug.py` (4,695 tokens)
- `backend/app/routers/ai_monitoring.py` (7,182 tokens)
- `backend/app/routers/proactive_ai.py` (2,827 tokens)
- `backend/app/models/ai_insights.py` (3,519 tokens)

### 2. **ui/** (~200K tokens)
**Purpose:** All user interface code
**Files:**
- `spark-realm/src/` (all React components and pages)
- `PulseCheckMobile/src/` (all React Native components)
- `spark-realm/src/components/` (~50K tokens)
- `spark-realm/src/pages/` (~40K tokens)
- `PulseCheckMobile/src/screens/` (~10K tokens)
- `PulseCheckMobile/src/services/` (~5K tokens)

### 3. **backend_core/** (~100K tokens)
**Purpose:** Core backend functionality (non-AI)
**Files:**
- `backend/main.py` (14,437 tokens)
- `backend/app/core/` (all core files)
- `backend/app/middleware/` (all middleware)
- `backend/app/routers/journal.py` (18,323 tokens)
- `backend/app/routers/auth.py` (3,392 tokens)
- `backend/app/services/journal_service.py` (1,540 tokens)
- `backend/app/models/journal.py` (1,192 tokens)
- `backend/app/models/user.py` (1,347 tokens)

### 4. **docs/** (~50K tokens)
**Purpose:** All documentation
**Files:**
- `ai/CONTRIBUTING.md` (26,885 tokens) → **NEEDS CHUNKING**
- `ai/AI-DEBUGGING-SYSTEM.md` (9,290 tokens)
- `ai/DEVELOPER-GUIDE.md` (3,408 tokens)
- `ai/PROJECT-GUIDE.md` (2,450 tokens)
- `backend/API_DOCUMENTATION.md` (2,095 tokens)
- `README.md` (2,829 tokens)

### 5. **configs/** (~10K tokens)
**Purpose:** Configuration files
**Files:**
- `package.json` files
- `tsconfig.json` files
- `tailwind.config.ts`
- `vite.config.ts`
- `railway.toml`
- `vercel.json`
- `requirements.txt`

### 6. **excluded/** (Large files to exclude)
**Purpose:** Files too large or low-value for AI processing
**Files:**
- `PulseCheckMobile/package-lock.json` (135,594 tokens)
- `spark-realm/package-lock.json` (124,199 tokens)
- `backend/app/routers/debug.py` (22,867 tokens) → **MOVE TO ARCHIVE**
- All `node_modules/` directories
- All build artifacts

---

## 🔧 Implementation Steps

1. **Create new directory structure**
2. **Move files to appropriate directories**
3. **Chunk large files** (especially `ai/CONTRIBUTING.md`)
4. **Create README files** for each directory
5. **Update .gitignore** to exclude large files
6. **Test token counts** for each new directory

---

## 📈 Expected Results

**Before:** 791,850 tokens (single chunk)  
**After:** ~6 manageable chunks of 50-150K tokens each

**Cost Savings:** Ability to send focused chunks to Claude instead of entire codebase 