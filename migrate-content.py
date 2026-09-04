#!/usr/bin/env python3
"""
Content migration script for zeroasterisk.com unified site
Migrates content from the old split repositories into the new organized structure
"""

import os
import re
import yaml
from datetime import datetime
from pathlib import Path

def parse_frontmatter(content):
    """Parse YAML frontmatter from markdown content"""
    if not content.startswith('---'):
        return {}, content
    
    try:
        _, frontmatter_str, body = content.split('---', 2)
        frontmatter = yaml.safe_load(frontmatter_str.strip())
        return frontmatter, body.strip()
    except:
        return {}, content

def categorize_content(frontmatter, title, tags, categories):
    """Determine if content should go to work, posts, or personal"""
    
    # Work-related keywords
    work_keywords = ['ai', 'ml', 'agent', 'memory', 'llm', 'google', 'production', 
                     'engineering', 'system', 'architecture', 'scale', 'devops',
                     'programming', 'code', 'technical', 'development', 'algorithm']
    
    # Personal keywords  
    personal_keywords = ['family', 'personal', 'kids', 'anita', 'penelope', 
                        'parenting', 'life', 'home', 'vacation', 'holiday']
    
    text_to_check = f"{title.lower()} {' '.join(tags).lower()} {' '.join(categories).lower()}"
    
    # Check for personal content first (more specific)
    for keyword in personal_keywords:
        if keyword in text_to_check:
            return 'personal'
    
    # Check for work content
    for keyword in work_keywords:
        if keyword in text_to_check:
            return 'work' if any(k in text_to_check for k in ['ai', 'ml', 'system', 'production', 'scale']) else 'posts'
    
    # Default to posts for technical content
    return 'posts'

def migrate_post(source_path, target_dir):
    """Migrate a single post to the new structure"""
    
    with open(source_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    frontmatter, body = parse_frontmatter(content)
    
    title = frontmatter.get('title', 'Untitled')
    date = frontmatter.get('date', datetime.now().isoformat())
    tags = frontmatter.get('tags', [])
    categories = frontmatter.get('categories', [])
    
    # Categorize content
    content_type = categorize_content(frontmatter, title, tags, categories)
    
    # Create slug from title
    slug = re.sub(r'[^a-zA-Z0-9\s-]', '', title.lower())
    slug = re.sub(r'\s+', '-', slug).strip('-')
    
    # Update frontmatter for new structure
    new_frontmatter = {
        'title': title,
        'date': date,
        'description': frontmatter.get('description', frontmatter.get('summary', '')),
        'tags': tags,
        'type': content_type
    }
    
    if categories:
        new_frontmatter['topics'] = categories
    
    if content_type == 'work':
        new_frontmatter['featured'] = True
    
    # Create new content
    new_content = "---\n"
    for key, value in new_frontmatter.items():
        if isinstance(value, list):
            new_content += f"{key}: {yaml.dump(value).strip()}\n"
        else:
            new_content += f"{key}: {yaml.dump(value).strip()}\n"
    new_content += "---\n\n"
    new_content += body
    
    # Write to new location
    target_path = target_dir / content_type / f"{slug}.md"
    target_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(target_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Migrated: {source_path.name} -> {content_type}/{slug}.md")
    return content_type

def main():
    """Main migration function"""
    script_dir = Path(__file__).parent
    unified_dir = script_dir
    content_dir = unified_dir / 'content'
    
    # Create directories
    for section in ['work', 'posts', 'personal']:
        (content_dir / section).mkdir(parents=True, exist_ok=True)
    
    # Migration would happen here if source repos were available
    # For now, we'll just report the structure
    
    print("Content migration structure ready!")
    print(f"Target directory: {content_dir}")
    print(f"Sections: work/, posts/, personal/")
    print("\nTo migrate existing content:")
    print("1. Clone your existing Hugo repositories")
    print("2. Run this script with source paths")
    print("3. Review categorization results")
    print("4. Commit and deploy")

if __name__ == '__main__':
    main()