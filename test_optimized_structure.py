#!/usr/bin/env python3
"""
Test Token Counts for Optimized PulseCheck Structure
"""

import os
import tiktoken
from pathlib import Path

# Token encoder
encoding = tiktoken.get_encoding("cl100k_base")

def estimate_tokens(text):
    return len(encoding.encode(text))

def count_tokens_in_directory(directory_path):
    """Count tokens in a specific directory"""
    total_tokens = 0
    file_count = 0
    files_info = []
    
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.endswith(('.py', '.ts', '.tsx', '.js', '.json', '.md', '.txt', '.html', '.css', '.yaml', '.yml')):
                try:
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        contents = f.read()
                        tokens = estimate_tokens(contents)
                        total_tokens += tokens
                        file_count += 1
                        files_info.append((file_path, tokens))
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
    
    return total_tokens, file_count, files_info

def main():
    """Test token counts for each directory in the optimized structure"""
    base_dir = Path("pulsecheck-optimized")
    
    if not base_dir.exists():
        print("❌ Optimized directory not found. Run reorganize_project.py first.")
        return
    
    print("🔍 Testing token counts for optimized structure...")
    print("=" * 60)
    
    directories = {
        "core_ai": "AI-related functionality",
        "backend_core": "Core backend functionality",
        "ui": "User interface code",
        "docs": "Documentation",
        "configs": "Configuration files"
    }
    
    total_project_tokens = 0
    
    for dir_name, description in directories.items():
        dir_path = base_dir / dir_name
        if dir_path.exists():
            tokens, file_count, files_info = count_tokens_in_directory(dir_path)
            total_project_tokens += tokens
            
            print(f"\n📁 {dir_name.upper()} ({description})")
            print(f"   Files: {file_count}")
            print(f"   Tokens: {tokens:,}")
            print(f"   Estimated Cost: ${tokens * 0.000018:.2f}")
            
            # Show largest files
            if files_info:
                largest_files = sorted(files_info, key=lambda x: x[1], reverse=True)[:3]
                print("   Largest files:")
                for file_path, file_tokens in largest_files:
                    rel_path = os.path.relpath(file_path, base_dir)
                    print(f"     {rel_path}: {file_tokens:,} tokens")
    
    print("\n" + "=" * 60)
    print(f"📊 TOTAL PROJECT TOKENS: {total_project_tokens:,}")
    print(f"💰 TOTAL ESTIMATED COST: ${total_project_tokens * 0.000018:.2f}")
    
    # Context size analysis
    print(f"\n📏 CONTEXT SIZE ANALYSIS:")
    print(f"GPT-4 (8K): {'✅' if total_project_tokens <= 8000 else '❌'} ({total_project_tokens:,} / 8,000)")
    print(f"GPT-4 (32K): {'✅' if total_project_tokens <= 32000 else '❌'} ({total_project_tokens:,} / 32,000)")
    print(f"Claude 3 (100K): {'✅' if total_project_tokens <= 100000 else '❌'} ({total_project_tokens:,} / 100,000)")
    print(f"Claude 3 (200K): {'✅' if total_project_tokens <= 200000 else '❌'} ({total_project_tokens:,} / 200,000)")
    
    # Individual directory analysis
    print(f"\n📋 DIRECTORY BREAKDOWN:")
    for dir_name in directories:
        dir_path = base_dir / dir_name
        if dir_path.exists():
            tokens, file_count, _ = count_tokens_in_directory(dir_path)
            percentage = (tokens / total_project_tokens * 100) if total_project_tokens > 0 else 0
            print(f"   {dir_name}: {tokens:,} tokens ({percentage:.1f}%)")

if __name__ == "__main__":
    main() 