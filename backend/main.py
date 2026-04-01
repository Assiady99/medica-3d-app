from fastapi import FastAPI, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn, os, json, re, httpx, asyncio
from dotenv import load_dotenv

load_dotenv()

# ─── Configuration ─────────────────────────────────────────────────────────────
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
TRIPO_API_KEY = "tsk_6ODdwjkfn7d5_8xTVsFhNiaYOr3eQ-CoLUPW0ptYwL0"
SKETCHFAB_API_TOKEN = "e2612b2d45d44426b56ea86c2c75586d"
GROQ_ENABLED = bool(GROQ_API_KEY)

if GROQ_ENABLED:
    try:
        from groq import AsyncGroq
        groq_client = AsyncGroq(api_key=GROQ_API_KEY)
        print("✅ Groq AI enabled (llama-3.3-70b-versatile).")
    except ImportError:
        print("⚠️  groq not installed. Run: pip install groq")

app = FastAPI(title="Medica 3D — AI Education API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])

class ModelRequest(BaseModel):
    prompt: str
    category: str = "medical_anatomy"

class ModelResponse(BaseModel):
    model_url: str
    name: str
    description: str
    parts: list[dict]
    quick_facts: list[str] = []
    suggestions: list[dict] = [] # List of related models/topics
    sketchfab_id: str = ""
    candidates: list[dict] = [] # List of {uid, name, thumbnail}
    status: str = "success"

# ─── Hardcoded Topics DB removed to prioritize Sketchfab ──────────────

# ─── Global Hub (Professional Institutional Models) ───────────────────────
# Mapping terms to verified high-quality external assets. 
GLOBAL_HUB = {
    # Space & Universe (Keeping only stable raw GLB sources)
    "earth": "https://raw.githubusercontent.com/nasa/NASA-3D-Resources/master/3D%20Models/Earth/Earth.glb",
    "أرض": "https://raw.githubusercontent.com/nasa/NASA-3D-Resources/master/3D%20Models/Earth/Earth.glb",
    "moon": "https://raw.githubusercontent.com/nasa/NASA-3D-Resources/master/3D%20Models/Moon/Moon.glb",
    "قمر": "https://raw.githubusercontent.com/nasa/NASA-3D-Resources/master/3D%20Models/Moon/Moon.glb",
    
    # Anatomy & Biology (High-Fidelity Local Assets are now absolute fallbacks)
    "liver": "https://code4fukui.github.io/human_organs/liver.glb",
    "كبد": "https://code4fukui.github.io/human_organs/liver.glb",
    "stomach": "https://code4fukui.github.io/human_organs/stomach.glb",
    "معدة": "https://code4fukui.github.io/human_organs/stomach.glb",
    "intestine": "https://code4fukui.github.io/human_organs/large_intestine.glb",
    "أمعاء": "https://code4fukui.github.io/human_organs/large_intestine.glb",
    "pancreas": "https://code4fukui.github.io/human_organs/pancreas.glb",
    "بنكرياس": "https://code4fukui.github.io/human_organs/pancreas.glb",
    "bee": "https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Assets/main/Models/Bee/glTF-Binary/Bee.glb",
    "نحلة": "https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Assets/main/Models/Bee/glTF-Binary/Bee.glb",
    "astronaut": "https://modelviewer.dev/shared-assets/models/Astronaut.glb",
    "رائد فضاء": "https://modelviewer.dev/shared-assets/models/Astronaut.glb",
    "robot": "https://modelviewer.dev/shared-assets/models/RobotExpressive.glb",
    "روبوت": "https://modelviewer.dev/shared-assets/models/RobotExpressive.glb",
}

# ─── Verified Professional Assets (Removed to prioritize Live Sketchfab Search) ──────

# ─── Fallback Translation (If Groq is offline) ────────────────────────────────
BASIC_TRANS = {
    "قلب انسان": "human heart anatomy", "دماغ بشري": "human brain anatomy",
    "قلب البشري": "human heart anatomy", "دماغ البشري": "human brain anatomy",
    "قلب": "human heart anatomy", "دماغ": "human brain anatomy", "مخ": "human brain anatomy", 
    "عين": "human eye anatomy", "أذن": "human ear anatomy", "اذن": "human ear anatomy",
    "رئة": "human lungs anatomy", "رئتين": "human lungs anatomy", "كلية": "human kidney anatomy", 
    "كبد": "human liver anatomy", "معدة": "human stomach anatomy", "أمعاء": "human intestines anatomy", 
    "بنكرياس": "human pancreas anatomy", "جمجمة": "human skull anatomy", "نحلة": "bee",
    "خلية": "biological cell model", "ذرة": "atom model", "قمر": "moon", "أرض": "earth", "صاروخ": "rocket"
}

# ─── Rich Fallback Content (If Groq is offline) ────────────────────────────────
FALLBACK_CONTENT = {
    "قلب": {
        "name": "القلب البشري",
        "description": "عضو عضلي يضخ الدم في جميع أنحاء الجسم عبر شبكة معقدة من الأوعية الدموية.",
        "parts": [
            {"name": "الأذين الأيمن", "info": "يستقبل الدم غير المؤكسج من الجسم."},
            {"name": "البطين الأيمن", "info": "يضخ الدم إلى الرئتين لاكتساب الأكسجين."},
            {"name": "الأذين الأيسر", "info": "يستقبل الدم المؤكسج نقيًا من الرئتين."},
            {"name": "البطين الأيسر", "info": "الغرفة الأقوى، تضخ الدم النقي لجميع أجزاء الجسم."},
            {"name": "الصمامات", "info": "تضمن تدفق الدم في اتجاه واحد دون ارتداد."}
        ]
    },
    "دماغ": {
        "name": "الدماغ البشري",
        "description": "مركز التحكم الرئيسي في الجهاز العصبي، مسؤول عن التفكير، الذاكرة، والحركة.",
        "parts": [
            {"name": "المخ", "info": "الجزء الأكبر، يتحكم في التفكير العقلاني والإرادي."},
            {"name": "قشرة الدماغ", "info": "الطبقة الخارجية المسؤولة عن معالجة المعلومات المعقدة."},
            {"name": "المخيخ", "info": "يتحكم في التوازن وتنسيق الحركات العضلية."},
            {"name": "جذع الدماغ", "info": "يربط الدماغ بالحبل الشوكي ويتحكم بالوظائف الحيوية كالتنفس."}
        ]
    },
    "أذن": {
        "name": "الأذن البشرية",
        "description": "عضو السمع والتوازن، يتكون من ثلاثة أجزاء رئيسية تعمل معاً لالتقاط الأصوات ونقلها للدماغ.",
        "parts": [
            {"name": "الأذن الخارجية", "info": "تشمل الصيوان والقناة السمعية، دورها تجميع الموجات الصوتية."},
            {"name": "طبلة الأذن", "info": "غشاء رقيق يهتز عند اصطدام الموجات الصوتية به."},
            {"name": "العظيمات الثلاث", "info": "المطرقة، السندان والركاب؛ تضخم الاهتزازات وتنقلها للأذن الداخلية."},
            {"name": "القوقعة", "info": "عضو حلزوني يحول الاهتزازات الميكانيكية إلى إشارات عصبية كهربائية."},
            {"name": "القنوات الهلالية", "info": "أنابيب مليئة بالسائل تساعد في الحفاظ على توازن الجسم."}
        ]
    },
    "عين": {
        "name": "العين البشرية",
        "description": "عضو الإبصار، يلتقط الضوء ويحوله لصور يفسرها الدماغ، قادرة على تمييز ملايين الألوان.",
        "parts": [
            {"name": "القرنية", "info": "الغطاء الشفاف الأمامي، تركز الضوء الساقط على العين."},
            {"name": "القزحية", "info": "الجزء الملون، ينظم كمية الضوء عبر التحكم بحجم الحدقة."},
            {"name": "العدسة", "info": "تغير شكلها لتركيز الصور على الشبكية بدقة."},
            {"name": "الشبكية", "info": "طبقة حساسة للضوء في الخلف، تحتوي على المستقبلات الضوئية."},
            {"name": "العصب البصري", "info": "ينقل الإشارات الكهربائية من الشبكية إلى الدماغ لمعالجتها."}
        ]
    },
    "رئة": {
        "name": "الرئتان البشريتان",
        "description": "عضوا التنفس الرئيسيان، يقومان بتبادل الأكسجين وثاني أكسيد الكربون مع الدم.",
        "parts": [
            {"name": "القصبة الهوائية", "info": "الأنبوب الرئيسي الذي ينقل الهواء إلى الرئتين."},
            {"name": "الشعب الهوائية", "info": "تتفرع داخل الرئة لتوزيع الهواء."},
            {"name": "الحويصلات الهوائية", "info": "أكياس دقيقة جداً حيث يتم تبادل الغازات مع الدم."},
            {"name": "غشاء الجنب", "info": "غشاء يحيط بالرئتين ويحميهما ويسهل حركتهما."}
        ]
    },
    "كلية": {
        "name": "الكلية البشرية",
        "description": "جهاز الترشيح الرئيسي في الجسم، تصفي الدم من السموم والفضلات وتنتج البول.",
        "parts": [
            {"name": "القشرة الكلوية", "info": "الطبقة الخارجية التي تحتوي على وحدات الفلترة (النيفرونات)."},
            {"name": "النخاع الكلوي", "info": "الطبقة الداخلية التي تجمع البول المتكون."},
            {"name": "الحوض الكلوي", "info": "قمع يجمع البول ويوجهه نحو الحالب."},
            {"name": "النيفرون", "info": "الوحدة الأساسية الوظيفية التي تصفي الدم المار عبرها."}
        ]
    },
    "خلية": {
        "name": "الخلية (Cell)",
        "description": "الوحدة الأساسية لكل الكائنات الحية، تحتوي على عضيات معقدة لأداء الوظائف الحيوية.",
        "parts": [
            {"name": "الغشاء الخلوي", "info": "يحيط بالخلية ويتحكم في مرور المواد منها وإليها."},
            {"name": "النواة", "info": "مركز التحكم، تحتوي على المادة الوراثية (DNA)."},
            {"name": "الميتوكوندريا", "info": "مصنع الطاقة الخلوي حيث يتم إنتاج الـ ATP."},
            {"name": "السيتوبلازم", "info": "سائل هلامي تسبح فيه العضيات الخلوية المختلفة."}
        ]
    }
}

@app.get("/proxy-model")
async def proxy_model(url: str):
    """Proxies external GLB files to bypass network/CORS restrictions."""
    print(f"🛰️ Proxying professional model: {url}")
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(url, follow_redirects=True, timeout=30)
            resp.raise_for_status()
            return Response(content=resp.content, media_type="model/gltf-binary")
        except Exception as e:
            print(f"❌ Proxy Failed for {url}: {e}")
            raise HTTPException(status_code=502, detail="Failed to fetch external model.")

def find_in_hub(prompt: str):
    """Searches the Global Hub using whole-word matching to prevent false positives (like 'ear' matching 'heart')."""
    p = prompt.lower()
    for kw, url in GLOBAL_HUB.items():
        # Match only whole words
        pattern = rf"\b{re.escape(kw)}\b"
        if re.search(pattern, p):
            print(f"🎯 Hub Match: Found whole word '{kw}' in prompt.")
            return url
    return None

async def generate_with_groq(prompt: str) -> dict:
    user_msg = f"""أنت مساعد تعليمي خبير. أجب بالعربية الفصحى.
الموضوع: "{prompt}"
أجب بـ JSON فقط—لا نص خارجه إطلاقاً:
{{
  "name": "اسم الموضوع العلمي",
  "description": "وصف تعليمي دقيق ومبسط من جملتين",
  "parts": [
    {{"name": "جزء أو مفهوم 1", "info": "شرح علمي مختصر"}},
    {{"name": "جزء أو مفهوم 2", "info": "شرح علمي مختصر"}},
    {{"name": "جزء أو مفهوم 3", "info": "شرح علمي مختصر"}},
    {{"name": "جزء أو مفهوم 4", "info": "شرح علمي مختصر"}},
    {{"name": "جزء أو مفهوم 5", "info": "شرح علمي مختصر"}}
  ],
  "quick_facts": [
    "حقيقة علمية مذهلة وقصيرة جداً متعلقة بالموضوع 1",
    "حقيقة علمية مذهلة وقصيرة جداً متعلقة بالموضوع 2",
    "حقيقة علمية مذهلة وقصيرة جداً متعلقة بالموضوع 3"
  ],
  "related_topics": [
    {{"name": "موضوع ذي صلة 1", "query": "بحث 1 بالإنجليزية"}},
    {{"name": "موضوع ذي صلة 2", "query": "بحث 2 بالإنجليزية"}},
    {{"name": "موضوع ذي صلة 3", "query": "بحث 3 بالإنجليزية"}}
  ]
}}"""
    completion = await groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": user_msg}],
        temperature=0.7,
        max_tokens=800,
        response_format={"type": "json_object"}
    )
    return json.loads(completion.choices[0].message.content.strip())

async def search_sketchfab(queries: list[str], count: int = 1, category: str = "") -> list[str]:
    """Searches Sketchfab with strict filtering. Returns a list of UIDs."""
    url = "https://api.sketchfab.com/v3/search"
    headers = {"Authorization": f"Token {SKETCHFAB_API_TOKEN}"}
    
    FORBIDDEN_TERMS = ["camera", "lens", "mask", "خوذة", "قناع", "كاميرا", "نظارة"]
    found_results = [] # List of {uid, name, thumbnail}
    found_uids = set()

    async with httpx.AsyncClient() as client:
        for q in queries:
            if not q: continue
            
            # --- Attempt 1: Strict & Educational ---
            safe_query = f"{q} -camera -lens -mask -helmet"
            params = {
                "q": safe_query, 
                "type": "models", 
                "count": 10,
                "license": "by",
                "sort_by": "-likeCount",
                "downloadable": True
            }
            
            # Map our categories to Sketchfab categories
            if category == "medical_anatomy":
                params["categories"] = "science-technology"
            elif category == "animals_nature":
                params["categories"] = "animals-pets"
            elif category == "vehicles":
                params["categories"] = "cars-vehicles"
            elif category == "architecture":
                params["categories"] = "architecture"
            
            try:
                resp = await client.get(url, params=params, headers=headers, timeout=10)
                results = []
                if resp.status_code == 200:
                    results = resp.json().get("results", [])
                
                # --- Attempt 2: Broader (If no educational models found) ---
                if not results:
                    params.pop("categories", None)
                    params["q"] = q # Original query without filters
                    resp = await client.get(url, params=params, headers=headers, timeout=10)
                    if resp.status_code == 200:
                        results = resp.json().get("results", [])

                for res in results:
                    name = res["name"]
                    name_lower = name.lower()
                    uid = res["uid"]
                    if uid in found_uids: continue
                    
                    has_forbidden = any(term in name_lower for term in FORBIDDEN_TERMS)
                    query_words = q.lower().split()
                    matches_query = any(word in name_lower for word in query_words if len(word) > 2)

                    if not has_forbidden and (matches_query or len(results) < 3):
                        thumb = ""
                        try:
                            # Safely extract thumbnail
                            images = res.get("thumbnails", {}).get("images", [])
                            if images:
                                # Use a medium sized image if available, else first
                                thumb = images[min(2, len(images)-1)].get("url", "")
                        except: pass
                        
                        found_results.append({"uid": uid, "name": name, "thumbnail": thumb})
                        found_uids.add(uid)
                        if len(found_results) >= count:
                            return found_results
                            
            except Exception as e:
                print(f"⚠️ Sketchfab search failed for '{q}': {e}")
        return found_results
    return found_uids

async def generate_3d_model(arabic_prompt: str, category: str) -> tuple[str, str, list[dict]]:
    """Finds professional models and returns (url, primary_uid, candidates)."""
    
    # 1. Translate Arabic to English keyword
    # Smart dictionary match for multi-word prompts
    arabic_lower = arabic_prompt.strip().lower()
    english_keyword = arabic_lower
    
    # Check for exact matches first
    if arabic_lower in BASIC_TRANS and category == "medical_anatomy":
        english_keyword = BASIC_TRANS[arabic_lower]
    else:
        # Fallback to substring matching
        if category == "medical_anatomy":
            for ar_word, en_word in BASIC_TRANS.items():
                if ar_word in arabic_lower:
                    english_keyword = en_word
                    break

    if GROQ_ENABLED:
        try:
            category_instructions = ""
            if category == "medical_anatomy":
                category_instructions = "Context: MEDICAL HUMAN ANATOMY. Example: 'كلية' -> 'kidney human anatomy', 'قلب' -> 'heart human anatomy'. MUST APPEND 'anatomy'."
            elif category == "animals_nature":
                category_instructions = "Context: ANIMALS AND NATURE. Example: 'كلب' -> 'dog', 'شجرة' -> 'tree'."
            elif category == "vehicles":
                category_instructions = "Context: VEHICLES AND CARS. Example: 'سيارة' -> 'car vehicle'."
            elif category == "architecture":
                category_instructions = "Context: ARCHITECTURE AND BUILDINGS. Example: 'منزل' -> 'house building'."
            else:
                category_instructions = "Context: GENERAL. Translate the word into precise, standalone English nouns. DO NOT truncate words. Example: 'قلب' -> 'heart', 'كتاب' -> 'book'."

            trans_msg = f"""Translate this Arabic word '{arabic_prompt}' to 2-3 specific English keywords for a 3D model search on Sketchfab.
            {category_instructions}
            - Return ONLY the English keywords separated by spaces.
            - Do not include any tags, numbers, or punctuation."""
            trans_resp = await groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": trans_msg}],
                temperature=0.0,
                max_tokens=100
            )
            english_keyword = trans_resp.choices[0].message.content.strip().strip('"').lower()
            english_keyword = english_keyword.replace('\r', '').replace('\n', '')
            print(f"🌍 AI Translated: '{arabic_prompt}' -> '{english_keyword}'")
        except Exception as e:
            print(f"⚠️ Translation error: {e}")
            pass

    # 💎 ONLY PRIORITY: Sketchfab Search (Professional Real Models)
    # Try the translated English keyword first
    candidates = await search_sketchfab([english_keyword], count=5, category=category)
    
    # If translation fails to find results, fallback to exactly what the user typed in Arabic
    if not candidates and english_keyword != arabic_prompt:
        print(f"🔄 English failed on Sketchfab. Falling back to Arabic query: '{arabic_prompt}'")
        candidates = await search_sketchfab([arabic_prompt], count=5, category=category)

    if candidates:
        return "", candidates[0]["uid"], candidates

    # Return empty if nothing found on Sketchfab
    return "", "", []

@app.post("/generate", response_model=ModelResponse)
async def generate_model(request: ModelRequest):
    prompt = request.prompt.strip()
    
    # 1. Get high-quality Arabic content
    ai_content = None
    if GROQ_ENABLED:
        try:
            ai_content = await generate_with_groq(prompt)
            # Make parsing extremely robust. Check if it's a list. Look for the first dictionary.
            if isinstance(ai_content, list):
                valid_dict = next((item for item in ai_content if isinstance(item, dict) and "description" in item), None)
                ai_content = valid_dict # Will be None if not found, triggering fallback
            
            # If it's a dict but doesn't have a description, mark it as invalid
            if isinstance(ai_content, dict) and "description" not in ai_content:
                ai_content = None

        except Exception as e:
            print(f"⚠️ Groq AI generation failed: {e}")
        
    if not ai_content:
        # Check rich fallback
        found_fallback = False
        # Normalize prompt for better matching (e.g., كليه vs كلية)
        prompt_norm = prompt.replace("ة", "ه")
        
        for key, content in FALLBACK_CONTENT.items():
            key_norm = key.replace("ة", "ه")
            if key_norm in prompt_norm or key in prompt:
                ai_content = content
                found_fallback = True
                break
        
        if not found_fallback:
            ai_content = {
                "name": prompt, 
                "description": "استكشف تفاصيل هذا المجسم ثلاثي الأبعاد المذهل لتعزيز فهمك.", 
                "parts": [
                    {"name": "ملاحظة عامة", "info": "المعلومات التفصيلية الدقيقة تتطلب تغطية ذكاء اصطناعي فعالة (حاليا في وضع الاوفلاين)."}
                ],
                "quick_facts": ["هل تعلم أن الذكاء الاصطناعي يمكنه توليد حقائق مذهلة حول أي مجسم بمجرد تنشيطه؟", "هذا المجسم الاحترافي من Sketchfab مصمم لأغراض العرض التعليمي وتقريب الفكرة."]
            }

    # 2. Get 3D Model & Candidates
    model_url, sketchfab_id, candidates = await generate_3d_model(request.prompt, request.category)
    
    status = "success" if (model_url or sketchfab_id) else "fallback"
    desc = ai_content["description"]
    if status == "fallback":
        desc += " (ملاحظة: يتم عرض نموذج تقريبي نظراً لعدم توفر موديل احترافي حالياً)."

    return ModelResponse(
        model_url=model_url,
        sketchfab_id=sketchfab_id,
        name=ai_content["name"],
        description=desc,
        parts=ai_content.get("parts", []),
        quick_facts=ai_content.get("quick_facts", []),
        suggestions=ai_content.get("related_topics", []),
        candidates=candidates,
        status=status
    )

# Static files
script_dir = os.path.dirname(os.path.realpath(__file__))
root_dir = os.path.abspath(os.path.join(script_dir, ".."))
app.mount("/models", StaticFiles(directory=os.path.join(root_dir, "models")), name="models")
app.mount("/js", StaticFiles(directory=os.path.join(root_dir, "js")), name="js")
app.mount("/css", StaticFiles(directory=os.path.join(root_dir, "css")), name="css")
app.mount("/", StaticFiles(directory=root_dir, html=True), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
