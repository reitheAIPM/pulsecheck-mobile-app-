import os
import tiktoken
from pathlib import Path

# Get the current working directory (where the script is run from)
REPO_PATH = os.getcwd()

# File extensions to include
INCLUDE_EXTENSIONS = {'.js', '.ts', '.tsx', '.py', '.json', '.md', '.txt', '.html', '.css', '.yaml', '.yml'}

# Directories to exclude (common directories that shouldn't be counted)
EXCLUDE_DIRS = {
    'node_modules', '.git', '__pycache__', '.venv', 'venv',
    'build', 'dist', '.next', '.nuxt', 'coverage', '.pytest_cache',
    'platform-docs', 'archive', 'personal', 'tests', 'scripts'
}

print(f"🔍 Scanning repository at: {REPO_PATH}")
print(f"📁 Including extensions: {', '.join(INCLUDE_EXTENSIONS)}")
print(f"🚫 Excluding directories: {', '.join(EXCLUDE_DIRS)}")

# Token encoder (using OpenAI's cl100k_base for GPT-4/Claude estimation)
try:
    encoding = tiktoken.get_encoding("cl100k_base")
    print("✅ Token encoder initialized successfully")
except Exception as e:
    print(f"❌ Error initializing token encoder: {e}")
    print("💡 Make sure you have tiktoken installed: pip install tiktoken")
    exit(1)

def estimate_tokens(text):
    return len(encoding.encode(text))

def should_skip_directory(dir_path):
    """Check if directory should be skipped"""
    dir_name = os.path.basename(dir_path)
    return dir_name in EXCLUDE_DIRS

total_tokens = 0
file_token_counts = []
files_processed = 0
files_skipped = 0

print("\n📊 Starting file scan...")

for root, dirs, files in os.walk(REPO_PATH):
    # Remove excluded directories from dirs list to prevent walking into them
    dirs[:] = [d for d in dirs if not should_skip_directory(os.path.join(root, d))]
    
    for file in files:
        ext = os.path.splitext(file)[1]
        if ext.lower() in INCLUDE_EXTENSIONS:
            try:
                file_path = os.path.join(root, file)
                # Get relative path for cleaner output
                rel_path = os.path.relpath(file_path, REPO_PATH)
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    contents = f.read()
                    tokens = estimate_tokens(contents)
                    total_tokens += tokens
                    file_token_counts.append((rel_path, tokens))
                    files_processed += 1
                    
                    # Print progress for large files
                    if tokens > 1000:
                        print(f"📄 {rel_path}: {tokens:,} tokens")
                        
            except Exception as e:
                print(f"⚠️  Skipped {file_path}: {e}")
                files_skipped += 1

# Output results
print(f"\n{'='*60}")
print(f"📊 SCAN COMPLETE")
print(f"{'='*60}")
print(f"🔢 Total Token Count: {total_tokens:,} tokens")
print(f"📄 Files Processed: {files_processed}")
print(f"⚠️  Files Skipped: {files_skipped}")

print(f"\n📄 Top 10 Largest Files:")
print("-" * 80)
for file_path, tokens in sorted(file_token_counts, key=lambda x: x[1], reverse=True)[:10]:
    print(f"{file_path:<60} {tokens:>8,} tokens")

# Cost estimation (Claude Sonnet)
token_input_cost = 0.000003  # $3.00 / 1M input tokens
token_output_cost = 0.000015  # $15.00 / 1M output tokens
estimated_cost = total_tokens * (token_input_cost + token_output_cost)

print(f"\n💰 Estimated Cost to Process with Claude 3 Sonnet: ${estimated_cost:.2f}")

# Additional context size estimates
print(f"\n📏 Context Size Estimates:")
print(f"GPT-4 (8K context): {'✅' if total_tokens <= 8000 else '❌'} ({total_tokens:,} / 8,000 tokens)")
print(f"GPT-4 (32K context): {'✅' if total_tokens <= 32000 else '❌'} ({total_tokens:,} / 32,000 tokens)")
print(f"Claude 3 (100K context): {'✅' if total_tokens <= 100000 else '❌'} ({total_tokens:,} / 100,000 tokens)")
print(f"Claude 3 (200K context): {'✅' if total_tokens <= 200000 else '❌'} ({total_tokens:,} / 200,000 tokens)") 