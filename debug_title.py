
import re
import os
from bs4 import BeautifulSoup

def extract_data(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    soup = BeautifulSoup(content, 'html.parser')
    
    # Simulate current extraction logic
    title = ""
    # Try to extract title from font size 5 or 4 strong tags (as per original logic roughly)
    # The original script does:
    # title_tag = soup.find('font', size=re.compile(r'[567]')) ...
    
    # Let's just assume we extracted "御光話（S24年8月）" or "S24年8月"
    # To be precise let's look at what the original script does for title extraction
    # It seems it searches for specific tags.
    # checking M240899.html: <font size="4"><strong>御光話</strong></font><font ...><strong>（S24年8月）</strong></font>
    
    # Let's try to mimic the "generic title" detection logic
    title = "御光話（S24年8月）" # Simplified assumption of what's extracted
    
    body_text = soup.body.get_text(separator="\n", strip=True) if soup.body else ""
    
    GENERIC_TERMS = ["御光話", "御垂示", "巻頭言", "御教え", "講話", "栄光", "地上天国", "救世", "信仰", "天国", "論文集", "随筆"]
    
    is_generic = False
    
    # Logic 1: Contains generic term
    for term in GENERIC_TERMS:
        if term in title and len(title) < 15:
             is_generic = True
             break
    
    # Logic 2: Date like
    if re.match(r'^[SsＳｓ]\d+', title) or re.match(r'^昭和\d+', title):
         is_generic = True
         
    print(f"Title: {title}")
    print(f"Is Generic: {is_generic}")
    
    if is_generic or title.endswith('.html'):
        lines = body_text.split('\n')
        candidate_title = ""
        
        for line in lines:
            line = line.strip()
            if not line: continue
            
            if '『' in line and '』' in line: continue 
            if '昭和' in line and ('発行' in line or '年' in line): continue 
            if '岡田自観師' in line: continue 
            if line.startswith('――'): 
                # !!! Notes: M240899 has line starting with ―― but it ALSO contains the question content
                # "――「大本教の..."
                # My logic says: if line.startswith('――'): continue
                # THIS IS THE BUG. It skips the question because it starts with dash.
                pass
            
            print(f"Checking line: {line[:50]}...")
            if line.startswith('――'): 
                print("SKIPPED due to starting with ――")
                continue

            if any(term in line for term in GENERIC_TERMS) and len(line) < 20: continue 
            if re.match(r'^\[.*\]$', line): continue
            
            paren_match = re.match(r'^[（\(]([^）\)]+)[）\)].*', line)
            if paren_match:
                candidate_title = paren_match.group(1)
                break
            
            quote_match = re.search(r'「([^」]+)」', line)
            if quote_match:
                quote_text = quote_match.group(1)
                if len(quote_text) > 5: 
                    candidate_title = quote_text
                    break
            
            if len(line) > 5 and len(line) < 50:
                candidate_title = line
                break
            elif len(line) >= 50:
                candidate_title = line[:50] + "..."
                break
        
        print(f"Candidate Title: {candidate_title}")

extract_data('/Users/michael/Documents/Ensinamentos/Mioshie_Zenshu_JP/search1/situmon/m240899.html')
