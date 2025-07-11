#!/usr/bin/env python3
"""
Check token count for archive folder
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
            if file.endswith(('.py', '.ts', '.tsx', '.js', '.json', '.md', '.txt', '.html', '.css', '.yaml', '.yml', '.sql', '.ps1')):
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
    """Check token counts for archive folder"""
    archive_dir = Path("archive")
    
    if not archive_dir.exists():
        print("❌ Archive directory not found.")
        return
    
    print("🔍 Checking token counts for archive folder...")
    print("=" * 60)
    
    # Check main archive directory
    tokens, file_count, files_info = count_tokens_in_directory(archive_dir)
    
    print(f"\n📁 ARCHIVE FOLDER")
    print(f"   Files: {file_count}")
    print(f"   Tokens: {tokens:,}")
    print(f"   Estimated Cost: ${tokens * 0.000018:.2f}")
    
    # Show largest files
    if files_info:
        largest_files = sorted(files_info, key=lambda x: x[1], reverse=True)[:10]
        print("   Largest files:")
        for file_path, file_tokens in largest_files:
            rel_path = os.path.relpath(file_path, archive_dir)
            print(f"     {rel_path}: {file_tokens:,} tokens")
    
    # Check subdirectories
    subdirs = ['ai-research', 'chatgpt_talk', 'legacy', 'test-scripts', 'sql-fixes']
    
    print(f"\n📋 SUBDIRECTORY BREAKDOWN:")
    for subdir in subdirs:
        subdir_path = archive_dir / subdir
        if subdir_path.exists():
            sub_tokens, sub_file_count, _ = count_tokens_in_directory(subdir_path)
            percentage = (sub_tokens / tokens * 100) if tokens > 0 else 0
            print(f"   {subdir}: {sub_tokens:,} tokens ({percentage:.1f}%)")

if __name__ == "__main__":
    main() 