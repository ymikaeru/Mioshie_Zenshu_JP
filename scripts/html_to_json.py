
import json
from bs4 import BeautifulSoup
import os
import re

def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip()

def parse_html_to_json(html_path, json_path):
    print(f"Reading {html_path}...")
    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    content = []
    current_section = None

    # Find the body
    body = soup.find('body')
    if not body:
        print("No body tag found!")
        return

    # Iterate through all direct children of body or the specific content wrapper
    # In Google Docs export, usually everything is flat under body
    elements = body.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol'])
    
    # Initial root section
    root_section = {
        "title": "Introduction",
        "level": 0,
        "content": []
    }
    content.append(root_section)
    current_section = root_section

    for elem in elements:
        text = clean_text(elem.get_text())
        if not text and elem.name not in ['ul', 'ol']:
            continue

        if elem.name.startswith('h'):
            level = int(elem.name[1])
            new_section = {
                "title": text,
                "level": level,
                "content": []
            }
            content.append(new_section)
            current_section = new_section
        
        elif elem.name == 'p':
            if current_section:
                current_section['content'].append({
                    "type": "paragraph",
                    "text": text
                })
        
        elif elem.name in ['ul', 'ol']:
            items = [clean_text(li.get_text()) for li in elem.find_all('li')]
            if current_section and items:
                current_section['content'].append({
                    "type": "list",
                    "style": elem.name,
                    "items": items
                })

    # Post-processing to nest sections if needed (optional, keeping it flat for now is safer)
    # We remove empty sections
    content = [s for s in content if s['content'] or s['title']]

    print(f"Parsed {len(content)} sections.")
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({"title": "Yama to Mizu", "data": content}, f, ensure_ascii=False, indent=2)
    print(f"Saved to {json_path}")

if __name__ == "__main__":
    base_dir = "/Users/michael/Documents/Ensinamentos/Mioshie_Zenshu_JP"
    html_file = os.path.join(base_dir, "YamaToMizu_data.html")
    json_file = os.path.join(base_dir, "yamatomizu.json")
    parse_html_to_json(html_file, json_file)
