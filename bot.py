import asyncio
import os
import requests
import json
import logging
import threading
from datetime import datetime
from quart import Quart, render_template_string, jsonify, request
from quart_cors import cors
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
from motor.motor_asyncio import AsyncIOMotorClient

# ================== কনফিগারেশন (আপনার ডেটা) ==================
API_TOKEN = '8162462190:AAFqdr69Et6tQ4_CvW3OjNjniu8yz056TCM'
MONGO_URL = 'mongodb+srv://roxiw19528:roxiw19528@cluster0.vl508y4.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'
ADMIN_ID = 7120801813
APP_URL = "https://bongobdbot.onrender.com"

# ================== ডাটাবেস এবং বট লজিক ==================
client = AsyncIOMotorClient(MONGO_URL)
db = client['bongobd_ultra_mega_v1']
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

class PostState(StatesGroup):
    title = State()
    photo = State()
    content = State()

class BroadcastState(StatesGroup):
    message = State()

# ================== মিনি অ্যাপের বিশাল ডিজাইন (HTML/CSS/JS) ==================
# এখানে প্রতিটি লাইন বিস্তারিত ভাবে ডিজাইন করা হয়েছে
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title id="web-title">BongoBD Master App</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        :root { --pink: #ff006e; --bg: #000; --card: #121212; --text: #fff; --gray: #888; }
        * { box-sizing: border-box; -webkit-tap-highlight-color: transparent; outline: none; }
        body { background: var(--bg); color: var(--text); font-family: 'Segoe UI', Tahoma, sans-serif; margin: 0; padding: 0; overflow-x: hidden; }
        
        /* নোটিশ বার */
        #notice-bar { background: var(--pink); color: #fff; padding: 12px; text-align: center; font-size: 14px; font-weight: bold; display: none; position: sticky; top: 0; z-index: 2000; box-shadow: 0 4px 15px rgba(255, 0, 110, 0.4); }

        /* হেডার */
        header { padding: 20px; text-align: center; border-bottom: 1px solid #222; background: rgba(0,0,0,0.9); backdrop-filter: blur(15px); }
        .logo { color: var(--pink); font-size: 28px; font-weight: 900; text-transform: uppercase; letter-spacing: 3px; text-shadow: 0 0 10px var(--pink); }

        .container { padding: 15px; max-width: 1400px; margin: 0 auto; min-height: 100vh; }

        /* সার্চ বক্স */
        .search-area { padding: 10px 15px; }
        .search-input { width: 100%; padding: 14px; border-radius: 12px; border: 1px solid #333; background: #111; color: #fff; font-size: 15px; }

        /* স্লাইডার সেকশন */
        .section-header { font-size: 18px; margin: 25px 0 15px; display: flex; align-items: center; gap: 10px; font-weight: bold; }
        .section-header::before { content: ''; width: 4px; height: 22px; background: var(--pink); border-radius: 2px; }
        
        .slider-wrapper { display: flex; overflow-x: auto; gap: 15px; padding-bottom: 15px; scrollbar-width: none; }
        .slider-wrapper::-webkit-scrollbar { display: none; }
        .slide-card { min-width: 280px; height: 160px; background: var(--card); border-radius: 15px; overflow: hidden; position: relative; border: 1px solid #333; flex-shrink: 0; }
        .slide-card img { width: 100%; height: 100%; object-fit: cover; opacity: 0.5; }
        .slide-label { position: absolute; bottom: 15px; left: 15px; font-size: 15px; font-weight: bold; }

        /* ভিডিও গ্রিড (রেসপন্সিভ) */
        .video-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; }
        @media (min-width: 768px) { .video-grid { grid-template-columns: repeat(3, 1fr); } }
        @media (min-width: 1024px) { .video-grid { grid-template-columns: repeat(5, 1fr); } }

        .video-card { background: var(--card); border-radius: 15px; overflow: hidden; border: 1px solid #222; transition: 0.4s; position: relative; }
        .video-card:hover { border-color: var(--pink); transform: translateY(-5px); }
        .thumb-img { width: 100%; height: 160px; object-fit: cover; }
        .video-info { padding: 12px; }
        .video-title { font-size: 14px; font-weight: bold; height: 38px; overflow: hidden; margin-bottom: 12px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }
        .unlock-btn { background: var(--pink); color: #fff; border: none; width: 100%; padding: 12px; border-radius: 8px; font-weight: bold; cursor: pointer; transition: 0.3s; }
        .unlock-btn:active { transform: scale(0.95); opacity: 0.8; }

        /* পেজিনেশন (১, ২, ৩...) */
        .pagination-container { display: flex; justify-content: center; align-items: center; gap: 8px; padding: 40px 0 120px; }
        .pg-link { background: #1a1a1a; border: 1px solid #333; color: #fff; padding: 10px 16px; border-radius: 8px; cursor: pointer; font-weight: bold; text-decoration: none; }
        .pg-link.active { background: var(--pink); border-color: var(--pink); }
        .pg-link:disabled { opacity: 0.3; cursor: not-allowed; }

        /* প্রোফাইল পেজ */
        .profile-section { background: linear-gradient(180deg, var(--pink) 0%, #000 100%); padding: 60px 20px; text-align: center; }
        .u-avatar { width: 100px; height: 100px; background: #fff; border-radius: 50%; margin: 0 auto 15px; display: flex; align-items: center; justify-content: center; font-size: 40px; color: #000; font-weight: bold; border: 5px solid rgba(255,255,255,0.2); }
        .u-stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-top: 35px; }
        .stat-card { background: rgba(255,255,255,0.06); padding: 20px 10px; border-radius: 15px; border: 1px solid #222; }
        .stat-val { font-size: 22px; font-weight: bold; color: var(--pink); }
        .stat-lab { font-size: 11px; color: #aaa; text-transform: uppercase; margin-top: 5px; }

        /* নেভিগেশন (৫টি বাটন) */
        .bottom-nav { position: fixed; bottom: 0; width: 100%; background: rgba(10,10,10,0.95); backdrop-filter: blur(20px); display: flex; justify-content: space-around; padding: 15px 0; border-top: 1px solid #222; z-index: 1000; }
        .nav-tab { color: #777; text-decoration: none; font-size: 11px; text-align: center; flex: 1; transition: 0.3s; cursor: pointer; }
        .nav-tab.active { color: var(--pink); font-weight: bold; }
        .nav-icon { font-size: 22px; margin-bottom: 5px; display: block; }

        .page { display: none; }
        .page.active { display: block; }
        #loader { position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); color: var(--pink); font-size: 20px; font-weight: bold; }
    </style>
</head>
<body>
    <div id="notice-bar"></div>
    <header><div class="logo" id="app-header-name">BongoBD</div></header>

    <div id="loader">লোড হচ্ছে...</div>

    <!-- হোম পেজ -->
    <div id="page-home" class="page container">
        <div class="search-area"><input type="text" class="search-input" placeholder="মুভি বা ভিডিও সার্চ করুন..." id="search-box" oninput="doSearch()"></div>
        
        <div class="section-header">পপুলার স্লাইডার 🔥</div>
        <div class="slider-wrapper" id="slider-list"></div>

        <div class="section-header">লেটেস্ট ভিডিও 🎬</div>
        <div class="video-grid" id="video-list"></div>

        <div class="pagination-container" id="pagination-ui"></div>
    </div>

    <!-- প্রোফাইল পেজ -->
    <div id="page-profile" class="page">
        <div class="profile-section">
            <div class="u-avatar" id="u-initial">?</div>
            <h2 id="u-fullname">Guest</h2>
            <div id="u-username" style="color:rgba(255,255,255,0.6); font-size:13px;">@username</div>
            <div class="u-stats">
                <div class="stat-card"><div class="stat-val" id="s-liked">0</div><div class="stat-lab">Liked</div></div>
                <div class="stat-card"><div class="stat-val" id="s-today">0</div><div class="stat-lab">Today Ads</div></div>
                <div class="stat-card"><div class="stat-val">30</div><div class="stat-lab">Daily Limit</div></div>
            </div>
        </div>
    </div>

    <!-- টিউটোরিয়াল ও লিংক পেজ -->
    <div id="page-links" class="page container" style="text-align:center; padding-top:100px;">
        <h3 class="pink">তথ্য ও সাহায্য</h3>
        <div id="links-content" style="color:#888;">লোড হচ্ছে...</div>
    </div>

    <!-- ফুটার নেভিগেশন (৫টি বাটন) -->
    <div class="bottom-nav">
        <div class="nav-tab active" onclick="switchTab('home', this)"><span class="nav-icon">🏠</span>হোম</div>
        <div class="nav-tab" onclick="switchTab('home', this)"><span class="nav-icon">❤️</span>পছন্দ</div>
        <div class="nav-tab" onclick="switchTab('links', this)"><span class="nav-icon">ℹ️</span>টিউটোরিয়াল</div>
        <div class="nav-tab" onclick="switchTab('links', this)"><span class="nav-icon">🔗</span>লিংক</div>
        <div class="nav-tab" onclick="switchTab('profile', this)"><span class="nav-icon">👤</span>প্রোফাইল</div>
    </div>

    <script>
        let tg = window.Telegram.WebApp;
        tg.expand();
        let user = tg.initDataUnsafe.user || {id: 0, first_name: 'Guest', username: 'user'};
        let currentPage = 1;
        let adStepCount = 0;

        async function startApp() {
            try {
                const sReq = await fetch('/api/settings');
                const set = await sReq.json();
                document.getElementById('web-title').innerText = set.name;
                document.getElementById('app-header-name').innerText = set.name;
                if(set.notice) {
                    const nb = document.getElementById('notice-bar');
                    nb.innerText = set.notice; nb.style.display = 'block';
                }
                loadSlider(set.slider_count || 6);
                loadVideos(1);
                document.getElementById('loader').style.display = 'none';
                document.getElementById('page-home').classList.add('active');
            } catch(e) { document.getElementById('loader').innerText = "সার্ভার এরর!"; }
        }

        async function loadSlider(count) {
            const res = await fetch(`/api/slider?count=${count}`);
            const data = await res.json();
            const slider = document.getElementById('slider-list');
            slider.innerHTML = '';
            data.forEach(p => {
                slider.innerHTML += `<div class="slide-card"><img src="${p.photo_url}"><div class="slide-text">${p.title}</div></div>`;
            });
        }

        async function loadVideos(page, query = '') {
            currentPage = page;
            const res = await fetch(`/api/posts?page=${page}&q=${query}`);
            const data = await res.json();
            const grid = document.getElementById('video-list');
            grid.innerHTML = '';
            data.posts.forEach(p => {
                grid.innerHTML += `
                    <div class="video-card">
                        <img src="${p.photo_url}" class="thumb-img">
                        <div class="video-info">
                            <div class="video-title">${p.title}</div>
                            <div id="step-txt-${p._id}" style="font-size:11px; color:var(--pink); margin-bottom:8px;">ADS: 0/${data.target_steps}</div>
                            <button class="unlock-btn" onclick="handleAds('${p._id}', ${data.target_steps})">🎬 UNLOCK</button>
                        </div>
                    </div>`;
            });
            renderPaginationUI(data.total_pages, page);
        }

        function renderPaginationUI(total, current) {
            const ui = document.getElementById('pagination-ui');
            ui.innerHTML = '';
            // Prev
            ui.innerHTML += `<button class="pg-link" ${current==1?'disabled':''} onclick="loadVideos(${current-1})">Prev</button>`;
            // Pages
            for(let i=1; i<=total; i++) {
                if(i == 1 || i == total || (i >= current-1 && i <= current+1)) {
                    ui.innerHTML += `<button class="pg-link ${i==current?'active':''}" onclick="loadVideos(${i})">${i}</button>`;
                } else if (i == current-2 || i == current+2) {
                    ui.innerHTML += `<span style="color:#333;">...</span>`;
                }
            }
            // Next
            ui.innerHTML += `<button class="pg-link" ${current==total?'disabled':''} onclick="loadVideos(${current+1})">Next</button>`;
        }

        async function handleAds(id, target) {
            const sdkRes = await fetch('/api/sdks');
            const sdks = await sdkRes.json();
            if(adStepCount < target) {
                if(sdks.length > 0) window.open(sdks[0].link, '_blank');
                adStepCount++;
                document.getElementById('step-txt-'+id).innerText = `ADS: ${adStepCount}/${target}`;
                fetch('/api/ad-click', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({user_id:user.id})});
            } else {
                alert("আনলক হয়েছে! মুভি লোড হচ্ছে...");
                adStepCount = 0;
            }
        }

        function doSearch() {
            const q = document.getElementById('search-box').value;
            loadVideos(1, q);
        }

        function switchTab(pageId, el) {
            document.querySelectorAll('.nav-tab').forEach(b => b.classList.remove('active'));
            el.classList.add('active');
            document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
            document.getElementById('page-' + pageId).classList.add('active');
            if(pageId === 'profile') loadProfileData();
            window.scrollTo(0,0);
        }

        async function loadProfileData() {
            const res = await fetch(`/api/user/${user.id}`);
            const data = await res.json();
            document.getElementById('u-fullname').innerText = user.first_name;
            document.getElementById('u-username').innerText = '@' + (user.username || 'user');
            document.getElementById('u-initial').innerText = user.first_name[0].toUpperCase();
            document.getElementById('s-liked').innerText = data.liked || 0;
            document.getElementById('s-today').innerText = data.ads_today || 0;
        }

        startApp();
    </script>
</body>
</html>
"""

# ================== এপিআই লজিক (QUART - ASYNC) ==================
app = Quart(__name__)
app = cors(app)

@app.route('/')
async def index(): return render_template_string(HTML_TEMPLATE)

@app.route('/api/settings')
async def get_settings():
    s = await db.settings.find_one({"id": "config"}) or {"name": "BongoBD", "notice": "", "steps": 3, "slider_count": 6}
    return jsonify(s)

@app.route('/api/posts')
async def get_posts():
    page = int(request.args.get('page', 1))
    query = request.args.get('q', '')
    limit = 20
    filter_db = {"title": {"$regex": query, "$options": "i"}} if query else {}
    total = await db.posts.count_documents(filter_db)
    posts = await db.posts.find(filter_db).sort('_id', -1).skip((page-1)*limit).limit(limit).to_list(limit)
    for p in posts: p['_id'] = str(p['_id'])
    set_db = await db.settings.find_one({"id": "config"}) or {"steps": 3}
    return jsonify({"posts": posts, "total_pages": (total // limit) + (1 if total % limit > 0 else 0), "target_steps": set_db.get("steps", 3)})

@app.route('/api/slider')
async def get_slider():
    count = int(request.args.get('count', 6))
    posts = await db.posts.find().sort('_id', -1).limit(count).to_list(count)
    for p in posts: p['_id'] = str(p['_id'])
    return jsonify(posts)

@app.route('/api/user/<int:uid>')
async def get_user_info(uid):
    u = await db.users.find_one({"user_id": uid}) or {"ads_today": 0, "liked": 0}
    return jsonify(u)

@app.route('/api/ad-click', methods=['POST'])
async def ad_count_update():
    data = await request.json
    await db.users.update_one({"user_id": data['user_id']}, {"$inc": {"ads_today": 1}}, upsert=True)
    return jsonify({"status": "ok"})

@app.route('/api/sdks')
async def get_sdks_list():
    return jsonify(await db.sdks.find().to_list(20))

# ================== বটের বিশাল কমান্ড ম্যানেজমেন্ট ==================

@dp.message_handler(commands=['start'])
async def start_handler(m: types.Message):
    # ইউজার রেজিস্ট্রেশন
    await db.users.update_one({"user_id": m.from_user.id}, {"$set": {"name": m.from_user.full_name}}, upsert=True)
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    # মেইন বাটন
    markup.row(types.InlineKeyboardButton("🎬 ভিডিও দেখুন (Mini App)", web_app=types.WebAppInfo(url=APP_URL)))
    
    # ডাইনামিক চ্যানেল বাটন
    channels = await db.channels.find().to_list(10)
    for c in channels: markup.add(types.InlineKeyboardButton(c['name'], url=c['link']))
    
    # ডাইনামিক টিউটোরিয়াল বাটন
    tuts = await db.tutorials.find().to_list(10)
    for t in tuts: markup.add(types.InlineKeyboardButton(f"ℹ️ {t['name']}", url=t['link']))

    # হুবহু আপনার স্ক্রিনশটের মতো ওয়েলকাম ডিজাইন
    welcome_msg = (
        "✨ **WELCOME TO VIRAL VIDEO BOT** ✨\n\n"
        "🔍 **আপনাকে অবশ্যই আমাদের সকল চ্যানেলে জয়েন করতে হবে ✅**\n\n"
        "আমাদের নিচের Channel গুলোতে ও ভিডিও দেওয়া হয়\n\n"
        "🎬 **ভিডিও দেখতে হলে অবশ্যই আপনাকে নিচের চ্যানেল গুলোতে Join করার পর [🎬 ভিডিও দেখুন] এ ক্লিক করে ভিডিও দেখতে পারবেন 👇**"
    )
    
    # ফটো যদি Telegra.ph এরর দেয় তবে সাধারণ মেসেজ
    banner = "https://telegra.ph/file/a8677c3e1c66288828b80.jpg"
    try:
        await m.answer_photo(photo=banner, caption=welcome_msg, reply_markup=markup, parse_mode="Markdown")
    except:
        await m.answer(welcome_msg, reply_markup=markup, parse_mode="Markdown")

# --- এডমিন প্যানেল কমান্ড ---

@dp.message_handler(commands=['post'], user_id=ADMIN_ID)
async def post_init(m: types.Message):
    await m.answer("📝 ভিডিও টাইটেল দিন:"); await PostState.title.set()

@dp.message_handler(state=PostState.title)
async def post_title(m: types.Message, state: FSMContext):
    await state.update_data(title=m.text); await m.answer("📸 ভিডিও ফটো পাঠান:"); await PostState.photo.set()

@dp.message_handler(content_types=['photo'], state=PostState.photo)
async def post_photo(m: types.Message, state: FSMContext):
    file = await bot.get_file(m.photo[-1].file_id)
    url = f"https://api.telegram.org/file/bot{API_TOKEN}/{file.file_path}"
    await state.update_data(photo=url); await m.answer("🔗 ভিডিও লিংক বা ফাইল পাঠান:"); await PostState.content.set()

@dp.message_handler(state=PostState.content, content_types=['any'])
async def post_final(m: types.Message, state: FSMContext):
    data = await state.get_data()
    val = m.text or m.video.file_id or m.document.file_id
    await db.posts.insert_one({"title": data['title'], "photo_url": data['photo'], "content": val})
    await m.answer("✅ ভিডিও সফলভাবে পোস্ট করা হয়েছে!"); await state.finish()

@dp.message_handler(commands=['broadcast'], user_id=ADMIN_ID)
async def broadcast_start(m: types.Message):
    await m.answer("📢 ব্রডকাস্ট মেসেজটি লিখুন:"); await BroadcastState.message.set()

@dp.message_handler(state=BroadcastState.message)
async def broadcast_send(m: types.Message, state: FSMContext):
    users = await db.users.find().to_list(None)
    for u in users:
        try: await bot.send_message(u['user_id'], m.text)
        except: pass
    await m.answer("✅ সবার কাছে পাঠানো হয়েছে।"); await state.finish()

@dp.message_handler(commands=['name'], user_id=ADMIN_ID)
async def set_app_name(m: types.Message):
    await db.settings.update_one({"id": "config"}, {"$set": {"name": m.get_args()}}, upsert=True)
    await m.answer("✅ অ্যাপ নাম সেভ হয়েছে।")

@dp.message_handler(commands=['notice'], user_id=ADMIN_ID)
async def set_app_notice(m: types.Message):
    await db.settings.update_one({"id": "config"}, {"$set": {"notice": m.get_args()}}, upsert=True)
    await m.answer("✅ নোটিশ সেভ হয়েছে।")

@dp.message_handler(commands=['step'], user_id=ADMIN_ID)
async def set_app_step(m: types.Message):
    await db.settings.update_one({"id": "config"}, {"$set": {"steps": int(m.get_args())}}, upsert=True)
    await m.answer("✅ অ্যাড স্টেপ সেট হয়েছে।")

@dp.message_handler(commands=['addchannel'], user_id=ADMIN_ID)
async def add_ch(m: types.Message):
    args = m.get_args().split(maxsplit=1)
    await db.channels.update_one({"name": args[0]}, {"$set": {"link": args[1]}}, upsert=True)
    await m.answer("✅ বাটন এড হয়েছে।")

@dp.message_handler(commands=['delchannel'], user_id=ADMIN_ID)
async def del_ch(m: types.Message):
    await db.channels.delete_one({"name": m.get_args()})
    await m.answer("🗑 ডিলেট হয়েছে।")

@dp.message_handler(commands=['sdk'], user_id=ADMIN_ID)
async def add_sdk(m: types.Message):
    args = m.get_args().split()
    await db.sdks.update_one({"id": args[0]}, {"$set": {"link": args[1]}}, upsert=True)
    await m.answer("✅ SDK সেভ হয়েছে।")

@dp.message_handler(commands=['deleteall'], user_id=ADMIN_ID)
async def clear_all(m: types.Message):
    await db.posts.delete_many({}); await db.users.delete_many({}); await m.answer("💥 ক্লিনড!")

# ================== অটো-সেটআপ ও রানার লজিক ==================

async def bot_auto_config():
    # ১. অটো ওয়েবহুক
    await bot.delete_webhook()
    await asyncio.sleep(1)
    await bot.set_webhook(f"{APP_URL}/tg-webhook")
    
    # ২. মেনু বাটন অটো ফিক্স (নিচের বাম দিকের বাটন)
    menu_data = {
        "type": "web_app",
        "text": "🎬 ভিডিও দেখুন",
        "web_app": {"url": APP_URL}
    }
    requests.post(f"https://api.telegram.org/bot{API_TOKEN}/setChatMenuButton", json={"menu_button": menu_data})

@app.before_serving
async def on_startup():
    asyncio.create_task(bot_auto_config())

@app.route('/tg-webhook', methods=['POST'])
async def handle_webhook():
    update_data = await request.json
    update = types.Update.to_object(update_data)
    Dispatcher.set_current(dp)
    Bot.set_current(bot)
    await dp.process_update(update)
    return "ok", 200

if __name__ == '__main__':
    # রান কমান্ড: python bot.py
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
