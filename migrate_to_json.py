import os
import json
import re
from bs4 import BeautifulSoup

ROOT_DIR = "/Users/michael/Documents/Ensinamentos/Mioshie_Zenshu_JP"
SEARCH_DIRS = ["search1", "search2"]
OUTPUT_FILE = "data.js" # Outputting as a JS file for direct inclusion

# MASSIVELY EXPANDED TAGGING DICTIONARY
# Keys correspond to the 'value' attributes in the advanced_search.html dropdown
CATEGORY_TAGS = {
    # ============ 人物 (Figures) ============
    "figures": {
        "教祖": ["教祖", "明主", "岡田茂吉", "自観", "大先生", "明主様"],
        "宗教家": ["イエス", "キリスト", "釈迦", "仏陀", "日蓮", "親鸞", "弘法", "空海", "法然", "伝教", "聖徳太子", "出口", "王仁三郎", "天理", "中山みき", "金光", "黒住", "マホメット", "孔子", "老子", "孟子"],
        "歴史人物": ["秀吉", "家康", "信長", "頼朝", "義経", "楠木正成", "西郷隆盛", "乃木", "東郷", "日露", "ヒトラー", "ムッソリーニ", "スターリン", "レーニン", "マルクス", "ナポレオン", "リンカーン", "ワシントン", "ガンジー"],
        "芸術家": ["光琳", "乾山", "光悦", "応挙", "又兵衛", "歌麿", "北斎", "広重", "雪舟", "利休", "遠州"],
        "神仏": ["天照", "素戔嗚", "月読", "国常立", "盤古", "大自在天", "観音", "阿弥陀", "薬師", "地蔵", "不動", "弁天", "大黒", "恵比寿", "龍神", "稲荷", "天狗"]
    },

    # ============ 場所 (Locations) ============
    "locations": {
        "聖地": ["熱海", "箱根", "京都", "亀岡", "綾部", "奈良", "日光", "伊勢", "出雲", "高千穂", "富士"],
        "熱海": ["瑞雲", "水晶殿", "救世会館", "美術館", "梅園", "来宮"],
        "箱根": ["強羅", "神山", "早雲山", "芦ノ湖", "美術館", "神仙郷"],
        "国内": ["東京", "日比谷", "上野", "浅草", "銀座", "清水", "玉川", "名古屋", "大阪", "博多", "北海道", "沖縄"],
        "海外": ["アメリカ", "米国", "イギリス", "英国", "フランス", "仏国", "ドイツ", "独逸", "イタリア", "伊太利", "ロシア", "ソ連", "中国", "支那", "朝鮮", "韓国", "インド", "エジプト"]
    },

    # ============ 時代 (Eras) ============
    "eras": {
        "時代": ["明治", "大正", "昭和", "平成", "江戸", "徳川", "元禄", "平安", "奈良", "縄文", "神代"],
        "時期": ["戦前", "戦中", "戦後", "終戦", "21世紀", "二十一世紀", "昼の時代", "夜の時代", "転換期", "過渡期", "末法"]
    },

    # ============ 健康・医療 (Health/Medicine) ============
    "medicine_specific": {
        "薬剤": ["アスピリン", "ピラミドン", "カルモチ", "スルファ", "サルファ", "ペニシリン", "ストレプトマイシン", "マイシン", "インスリン", "ブドウ糖", "リンゲル", "ワクチン", "血清", "BCG", "種痘", "予防接種", "睡眠薬", "下剤", "浣腸", "解熱剤", "鎮痛剤", "麻酔", "モルヒネ"],
        "医療器具": ["レントゲン", "X光線", "ラジウム", "聴診器", "体温計", "顕微鏡", "メス", "ギプス", "義足", "義眼"],
        "処置": ["手術", "切開", "縫合", "輸血", "輸液", "湿布", "マッサージ", "指圧", "鍼", "灸", "温泉", "湯治", "サナトリウム"]
    },
    "disease_detail": {
        "癌": ["胃癌", "肺癌", "子宮癌", "乳癌", "喉頭癌", "舌癌", "皮膚癌", "直腸癌", "食道癌", "肉腫"],
        "結核": ["肺結核", "結核", "カリエス", "脊椎カリエス", "胸膜炎", "肋膜", "腹膜炎", "脳膜炎", "リンパ腺", "痔瘻"],
        "胃腸": ["胃潰瘍", "十二指腸潰瘍", "胃下垂", "胃酸過多", "胃痙攣", "胃カタル", "腸カタル", "盲腸", "虫垂炎", "脱腸", "痔"],
        "心臓・脳": ["弁膜症", "狭心症", "心筋梗塞", "脳溢血", "脳卒中", "脳貧血", "脳出血", "高血圧", "動脈硬化"],
        "婦人": ["子宮後屈", "子宮筋腫", "内膜炎", "卵巣嚢腫", "つわり", "難産", "流産", "不妊", "更年期", "ヒステリー", "冷え性"],
        "目": ["白内障", "緑内障", "そこひ", "トラコーマ", "結膜炎", "網膜剥離", "近視", "乱視", "盲目", "色盲", "ものもらい"],
        "他": ["糖尿病", "腎臓病", "肝臓病", "喘息", "リウマチ", "神経痛", "梅毒", "淋病", "中耳炎", "蓄膿症", "水虫", "あかぎれ"]
    },
    "body_parts": {
        "頭部": ["脳", "前頭葉", "後頭部", "延髄", "こめかみ", "目", "耳", "鼻", "口", "歯", "喉", "扁桃腺"],
        "胴体": ["首", "頸部", "肩", "鎖骨", "背中", "脊柱", "胸", "肋骨", "心臓", "肺", "胃", "肝臓", "腎臓", "膵臓", "脾臓", "胆嚢", "腸", "盲腸", "子宮", "卵巣"],
        "四肢": ["腕", "肘", "手", "指", "爪", "股関節", "足", "膝", "足首", "踵", "土踏まず", "鼠径部", "リンパ"]
    },

    # ============ 食 (Food) ============
    "food": {
        "主食": ["米", "白米", "玄米", "餅", "パン", "麦", "うどん", "蕎麦", "ラーメン"],
        "調味料": ["味噌", "醤油", "塩", "酢", "砂糖", "味の素", "山椒", "唐辛子", "わさび", "胡椒"],
        "飲み物": ["酒", "日本酒", "ビール", "洋酒", "ウイスキー", "茶", "緑茶", "抹茶", "珈琲", "コーヒー", "紅茶", "水", "牛乳"],
        "副食": ["肉", "牛肉", "豚肉", "鶏肉", "魚", "刺身", "鯛", "鮪", "鰹", "鰯", "鯖", "貝", "海老", "蟹", "卵", "豆腐", "納豆"],
        "野菜": ["野菜", "大根", "人参", "芋", "薩摩芋", "じゃがいも", "葱", "玉ねぎ", "白菜", "キャベツ", "トマト", "茄子", "胡瓜", "南瓜", "牛蒡", "蓮根"],
        "果物": ["果物", "梨", "柿", "蜜柑", "林檎", "葡萄", "桃", "西瓜", "メロン", "栗"],
        "嗜好品": ["菓子", "饅頭", "羊羹", "煎餅", "飴", "チョコレート", "煙草", "タバコ", "麻薬", "阿片"]
    },

    # ============ 芸術・文化 (Arts/Culture) ============
    "art_detail": {
        "美術": ["日本画", "洋画", "油絵", "水墨画", "浮世絵", "掛軸", "屏風", "額", "彫刻", "仏像", "建築", "庭園"],
        "工芸": ["陶器", "磁器", "茶碗", "花瓶", "皿", "壺", "漆器", "蒔絵", "刀剣", "刀"],
        "芸能": ["能", "狂言", "歌舞伎", "文楽", "浄瑠璃", "邦楽", "三味線", "琴", "尺八", "謡曲", "映画", "演劇", "オペラ", "音楽", "レコード"],
        "芸道": ["茶道", "茶の湯", "華道", "生け花", "書道", "香道"]
    },

    # ============ 社会・生活 (Society/Life) ============
    "society": {
        "政治": ["政治", "選挙", "国会", "憲法", "法律", "裁判", "警察", "検事", "弁護士", "刑務所"],
        "イズム": ["民主主義", "共産主義", "社会主義", "資本主義", "ファシズム", "ナチス", "軍国主義", "唯物論", "無神論"],
        "経済": ["経済", "景気", "インフレ", "デフレ", "恐慌", "金", "銀行", "株", "税金", "借金", "貧乏", "月給", "ボーナス"],
        "問題": ["犯罪", "殺人", "泥棒", "強盗", "詐欺", "横領", "賄賂", "汚職", "心中", "自殺", "ストライキ", "争議"],
        "メディア": ["新聞", "雑誌", "ラジオ", "放送", "ニュース", "広告", "宣伝"]
    },

    # ============ 自然 (Nature) ============
    "nature_detail": {
        "天体": ["太陽", "月", "星", "地球", "宇宙"],
        "気象": ["天気", "晴", "曇", "雨", "雪", "雷", "風", "嵐", "台風", "虹", "霧", "霜", "露"],
        "災害": ["地震", "津波", "洪水", "火事", "噴火", "干ばつ", "冷害", "凶作"],
        "植物": ["桜", "梅", "松", "竹", "柳", "紅葉", "菊", "牡丹", "芍薬", "蓮", "水仙"],
        "動物": ["犬", "猫", "馬", "牛", "鳥", "鶏", "虫", "蚊", "蝿", "蚤", "虱"]
    },

    # ============ 霊的 (Spiritual) ============
    "spiritual_detail": {
        "霊界": ["天国", "極楽", "地獄", "霊界", "現界", "幽界", "神界", "仏界", "龍神界", "天狗界"],
        "霊": ["霊", "霊魂", "主守護神", "守護霊", "指導霊", "支配霊", "副守護神", "正守護神", "祖霊", "浮遊霊", "地縛霊", "悪霊", "邪霊", "生霊", "死霊", "怨霊"],
        "憑依": ["狐", "稲荷", "天狗", "龍", "蛇", "狸", "犬神", "化猫", "七面鳥", "ムジナ"],
        "現象": ["霊視", "霊聴", "霊感", "夢", "正夢", "金縛り", "奇蹟", "奇跡", "御利益", "罰", "祟り", "浄化", "毒素"]
    },
    
    # ============ 治療 (Treatment) ============
    "treatment": { 
        "浄霊": ["浄霊", "御浄霊", "お光", "かざす", "手かざし", "霊気", "施術"],
        "浄霊法": ["急所", "ツボ", "患部", "遠隔", "写真", "指圧", "マッサージ"],
        "医療": ["医師", "医者", "病院", "診断", "誤診", "手遅れ", "医学"],
        "健康法": ["栄養","ビタミン", "カロリー", "断食", "温泉", "灸", "漢方", "民間療法"],
        "回復": ["全快", "完治", "奇蹟的", "好転", "緩解", "治癒"]
    },

    # ============ 霊的・神様 (Divine/Spiritual) ============
    "divine": { 
        "神名": ["主神", "天照", "観音", "メシヤ", "素戔嗚", "国常立", "龍神", "稲荷", "天狗", "救世主"],
        "仏": ["釈迦", "阿弥陀", "日蓮", "親鸞", "弘法", "法然", "如来", "菩薩", "明王", "大師"],
        "神道": ["祝詞", "神社", "参拝", "鳥居", "産土", "氏神"],
        "キリスト": ["キリスト", "イエス", "聖書", "十字架", "マリア"],
        "行事": ["大祭", "月次祭", "礼拝", "祭典", "儀式"]
    },
    "karma": { 
        "法則": ["真理", "順序", "法則", "霊主体従", "火水土", "五六七", "日月地", "経緯"],
        "因縁": ["因縁", "メグリ", "罪", "穢れ", "業", "カルマ", "曇り", "毒素", "浄化", "償い"],
        "運命": ["運", "運命", "宿命", "幸福", "不幸", "災難", "厄", "禍", "吉凶"]
    },

    # ============ 哲学・社会 (Philosophy/Society) ============
    "truth": { 
        "教え": ["教義", "御教え", "講話", "論文", "天国の福音", "善言讃詞", "天津祝詞"],
        "善悪": ["善", "悪", "正義", "邪", "嘘", "誠", "愛", "慈悲", "奉仕", "感謝", "謙虚"],
        "光": ["光", "太陽", "月", "火", "水", "土", "昼", "夜"]
    },
    "family": { 
        "家族": ["夫婦", "結婚", "離婚", "再婚", "親子", "兄弟", "嫁姑", "養子", "遺産"],
        "生活": ["衣食住", "食事", "酒", "煙草", "肉食", "菜食", "風呂", "睡眠"],
        "対人": ["信用", "評判", "友情", "交際", "恩", "義理"]
    }
}

def extract_tags(text):
    found_tags = set()
    for cat_key, subcats in CATEGORY_TAGS.items():
        for tag_name, keywords in subcats.items():
            for keyword in keywords:
                if keyword in text:
                    found_tags.add(tag_name)
                    break # Found this tag, move to next tag
    return list(found_tags)

def extract_data_from_html(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Extract Title
        title = ""
        font_titles = soup.find_all('font', size=re.compile(r'[4-6]'))
        for ft in font_titles:
            text = ft.get_text(strip=True)
            if len(text) > 1:
                title = text
                break
        
        if not title:
             strongs = soup.find_all('strong')
             for s in strongs:
                 text = s.get_text(strip=True)
                 if len(text) > 2:
                     title = text
                     break

        # Extract Main Content
        blockquote = soup.find('blockquote')
        body_text = ""
        source_text = ""
        date_text = ""

        if blockquote:
            # Get text but also check first <p> tag separately
            body_text = blockquote.get_text(separator="\n", strip=True)
            
            # Try to find first paragraph which often contains source/date
            first_p = blockquote.find('p')
            if first_p:
                p_text = first_p.get_text(separator="\n", strip=True)
                lines = p_text.split('\n')
                
                # Look through first few lines for source/date pattern
                for line in lines[:5]:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Pattern: 『source』date
                    if '『' in line and '』' in line and '昭和' in line:
                        # Extract source
                        source_match = re.search(r'『([^』]+)』', line)
                        if source_match:
                            source_text = source_match.group(1)
                        
                        # Extract date  
                        date_match = re.search(r'昭和\d+\(\d+\)年\d+月\d+日発行', line)
                        if date_match:
                            date_text = date_match.group()
                        else:
                            # Try simpler pattern
                            date_match = re.search(r'昭和\d+.*?発行', line)
                            if date_match:
                                date_text = date_match.group()
                        break
                    # Just date without source
                    elif '昭和' in line and ('発行' in line or '年' in line):
                        date_match = re.search(r'昭和\d+\(\d+\)年\d+月\d+日発行', line)
                        if date_match:
                            date_text = date_match.group()
                        else:
                            date_match = re.search(r'昭和\d+.*?発行', line)
                            if date_match:
                                date_text = date_match.group()
                        break
            
        else:
            if soup.body:
                body_text = soup.body.get_text(separator="\n", strip=True)

        # Ignore generic titles and try to find better one from content
        GENERIC_TERMS = ["御光話", "御垂示", "巻頭言", "御教え", "講話", "栄光", "地上天国", "救世", "信仰", "天国", "論文集", "随筆"]
        
        is_generic = False
        if not title:
            is_generic = True
        else:
            # Check if title is generic (e.g. "御垂示録10号" contains "御垂示")
            for term in GENERIC_TERMS:
                if term in title and len(title) < 15:
                     is_generic = True
                     break
            
            # Check if title looks like a date (e.g. S26年5月1日 or 昭和26年 or （S24年...）)
            if re.match(r'^[\(（]?[SsＳｓ]\d+', title) or re.match(r'^[\(（]?昭和\d+', title):
                 is_generic = True
        
        if is_generic or title.endswith('.html'):
            # Try to extract first meaningful line from body
            lines = body_text.split('\n')
            candidate_title = ""
            
            for line in lines:
                line = line.strip()
                if not line: continue
                
                # Skip typical header/source lines
                if '『' in line and '』' in line: continue # Source ref
                if '昭和' in line and ('発行' in line or '年' in line) and len(line) < 40: continue # Date (but allow if line is long/content)
                if '岡田自観師' in line: continue # Header
                
                # Handle lines starting with ―― (often questions)
                if line.startswith('――'): 
                    line = line.replace('――', '').strip()
                    if not line: continue
                    # This is a question/content line, use it as title!
                    # Truncate if too long (e.g. > 60 chars)
                    if len(line) > 60:
                        candidate_title = line[:60] + "..."
                    else:
                        candidate_title = line
                    break
                
                if any(term in line for term in GENERIC_TERMS) and len(line) < 20: continue # Skip repeated generic headers in body
                if re.match(r'^\[.*\]$', line): continue # Skip dates like [六月一日]
                
                # Check for Parenthetical Summary (Highest Priority)
                # Matches （...） or (...) at start of line
                paren_match = re.match(r'^[（\(]([^）\)]+)[）\)].*', line)
                if paren_match:
                    pot_title = paren_match.group(1)
                    # Create title but reject if it looks like a date or is just generic
                    if not (re.match(r'^[\(（]?[SsＳｓ]\d+', pot_title) or re.match(r'^[\(（]?昭和\d+', pot_title) or pot_title in GENERIC_TERMS):
                        candidate_title = pot_title
                        break
                
                # Check for Quote/Question (Second Priority)
                # Matches 「...」
                quote_match = re.search(r'「([^」]+)」', line)
                if quote_match:
                    # Use the quote content, but limit length
                    quote_text = quote_match.group(1)
                    if len(quote_text) > 5 and len(quote_text) < 60: 
                        candidate_title = quote_text
                        break
                
                # Fallback: First meaningful sentence
                # Must ensure it's not just a date or simple string
                if len(line) > 5 and len(line) < 60:
                    if not (re.match(r'^[\(（]?[SsＳｓ]\d+', line) or re.match(r'^[\(（]?昭和\d+', line)):
                        candidate_title = line
                        break
                elif len(line) >= 60:
                    # If line is long, take first bit
                    candidate_title = line[:60] + "..."
                    break
            
            if candidate_title:
                title = candidate_title
        
        # Final fallback check: if title is still generic or date-like, try harder or use filename
        if re.match(r'^[\(（]?[SsＳｓ]\d+', title) or re.match(r'^[\(（]?昭和\d+', title) or title in GENERIC_TERMS:
             # Last resort: Scan lines again for ANY non-date text > 10 chars
             new_fallback = ""
             for line in lines:
                 sline = line.strip().replace('――', '')
                 if not sline: continue
                 if '『' in sline and '』' in sline: continue 
                 if len(sline) > 10 and not (re.match(r'^[\(（]?[SsＳｓ]\d+', sline) or re.match(r'^[\(（]?昭和\d+', sline)):
                     new_fallback = sline[:40] + "..."
                     break
             
             if new_fallback:
                 title = new_fallback
             else:
                 title = os.path.splitext(os.path.basename(filepath))[0]

        # Generate Tags based on title and content
        full_text = title + " " + body_text
        tags = extract_tags(full_text)
        
        return {
            "title": title,
            "content": body_text,
            "source": source_text,
            "date": date_text,
            "path": os.path.relpath(filepath, ROOT_DIR),
            "tags": sorted(list(set(tags))) # Deduplicate and sort
        }

    except Exception as e:
        # print(f"Error processing {filepath}: {e}")
        return None

def main():
    all_data = []
    
    for search_dir in SEARCH_DIRS:
        full_search_dir = os.path.join(ROOT_DIR, search_dir)
        if not os.path.exists(full_search_dir):
            print(f"Directory not found: {full_search_dir}")
            continue

        for root, dirs, files in os.walk(full_search_dir):
            for file in files:
                if file.lower().endswith('.html') or file.lower().endswith('.htm'):
                    filepath = os.path.join(root, file)
                    data = extract_data_from_html(filepath)
                    if data:
                        data['id'] = os.path.splitext(file)[0]
                        all_data.append(data)
    
    output_path = os.path.join(ROOT_DIR, OUTPUT_FILE)
    
    # Prepare the category map for frontend
    # Flatten the CATEGORY_TAGS to category -> list of tags
    # Frontend expects: category (e.g. 'disease') -> ['結核', '癌', ...]
    category_map_for_frontend = {}
    for cat_key, subcats in CATEGORY_TAGS.items():
        category_map_for_frontend[cat_key] = list(subcats.keys())

    # Write as specific JS variable assignment
    json_str = json.dumps(all_data, ensure_ascii=False, indent=2)
    cat_map_str = json.dumps(category_map_for_frontend, ensure_ascii=False, indent=2)
    
    js_content = f"const allData = {json_str};\n\nconst categoryTagMap = {cat_map_str};\n"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(js_content)
    
    print(f"Extracted {len(all_data)} items to {output_path}")

if __name__ == "__main__":
    main()
