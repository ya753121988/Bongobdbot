import logging
import asyncio
import threading
import os
import requests
from flask import Flask, render_template_string, jsonify, request
from flask_cors import CORS
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

# ================= CONFIGURATION =================
API_TOKEN = '8162462190:AAFqdr69Et6tQ4_CvW3OjNjniu8yz056TCM'
MONGO_URL = 'mongodb+srv://roxiw19528:roxiw19528@cluster0.vl508y4.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'
ADMIN_ID = 7120801813
APP_URL = "https://bongobdbot.onrender.com"

# ================= DB & BOT SETUP =================
client = AsyncIOMotorClient(MONGO_URL)
db = client['bongobd_ultra_db']
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

class PostState(StatesGroup):
    title = State()
    photo = State()
    content = State()

# ================= MINI APP UI (ULTRA DESIGN) =================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title id="web-title">BongoBD</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        :root { --pink: #ff006e; --bg: #000; --card: #111; --text: #fff; }
        * { box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
        body { background: var(--bg); color: var(--text); font-family: 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; overflow-x: hidden; }
        
        /* Notice Bar */
        #notice { background: var(--pink); color: #fff; padding: 10px; text-align: center; font-size: 14px; font-weight: bold; display: none; position: sticky; top: 0; z-index: 2000; }
        
        /* Header */
        header { padding: 20px; text-align: center; border-bottom: 1px solid #222; background: rgba(0,0,0,0.8); backdrop-filter: blur(10px); }
        .logo { color: var(--pink); font-size: 24px; font-weight: 900; letter-spacing: 1px; }

        .container { padding: 15px; max-width: 1200px; margin: 0 auto; }
        .section-title { font-size: 18px; margin: 20px 0 10px; display: flex; align-items: center; gap: 8px; }
        .section-title::before { content: ''; width: 4px; height: 20px; background: var(--pink); border-radius: 2px; display: inline-block; }

        /* Horizontal Slider */
        .slider { display: flex; overflow-x: auto; gap: 15px; padding-bottom: 10px; scrollbar-width: none; }
        .slider::-webkit-scrollbar { display: none; }
        .slide-card { min-width: 280px; height: 160px; background: var(--card); border-radius: 15px; overflow: hidden; position: relative; border: 1px solid #333; }
        .slide-card img { width: 100%; height: 100%; object-fit: cover; opacity: 0.6; }
        .slide-info { position: absolute; bottom: 10px; left: 10px; right: 10px; }

        /* Responsive Grid */
        .grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; }
        @media (min-width: 768px) { .grid { grid-template-columns: repeat(4, 1fr); } }
        @media (min-width: 1024px) { .grid { grid-template-columns: repeat(5, 1fr); } }

        .post-card { background: var(--card); border-radius: 12px; overflow: hidden; border: 1px solid #222; transition: 0.3s; }
        .post-card:hover { border-color: var(--pink); transform: translateY(-5px); }
        .post-img { width: 100%; height: 150px; object-fit: cover; }
        .post-details { padding: 10px; }
        .post-title { font-size: 14px; font-weight: bold; height: 40px; overflow: hidden; margin-bottom: 10px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }
        .unlock-btn { background: var(--pink); color: #fff; border: none; width: 100%; padding: 10px; border-radius: 8px; font-weight: bold; cursor: pointer; transition: 0.2s; }
        .unlock-btn:active { opacity: 0.8; transform: scale(0.95); }

        /* Pagination */
        .pagination { display: flex; justify-content: center; align-items: center; gap: 15px; padding: 30px 0 100px; }
        .pg-btn { background: #222; border: 1px solid var(--pink); color: #fff; padding: 10px 20px; border-radius: 8px; cursor: pointer; font-weight: bold; }
        .pg-btn:disabled { border-color: #444; color: #444; cursor: not-allowed; }

        /* Profile Page */
        .profile-hero { background: linear-gradient(180deg, var(--pink) 0%, #000 100%); padding: 50px 20px; text-align: center; }
        .avatar { width: 90px; height: 90px; background: #fff; border-radius: 50%; margin: 0 auto 15px; display: flex; align-items: center; justify-content: center; font-size: 35px; color: #000; font-weight: 900; border: 4px solid rgba(255,255,255,0.2); }
        .stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-top: 30px; }
        .stat-item { background: rgba(255,255,255,0.05); padding: 15px; border-radius: 15px; border: 1px solid #222; }
        .stat-val { font-size: 20px; font-weight: bold; color: var(--pink); }
        .stat-lab { font-size: 11px; color: #aaa; text-transform: uppercase; margin-top: 5px; }

        /* Footer Nav */
        .footer { position: fixed; bottom: 0; width: 100%; background: rgba(10,10,10,0.95); backdrop-filter: blur(15px); display: flex; justify-content: space-around; padding: 15px 0; border-top: 1px solid #222; z-index: 1000; }
        .nav-item { color: #666; text-decoration: none; font-size: 11px; text-align: center; flex: 1; transition: 0.3s; cursor: pointer; }
        .nav-item.active { color: var(--pink); }
        .nav-icon { font-size: 22px; margin-bottom: 4px; display: block; }

        .hidden { display: none; }
    </style>
</head>
<body>
    <div id="notice"></div>
    <header><div class="logo" id="app-name">BongoBD</div></header>

    <!-- Home Page -->
    <div id="page-home" class="container">
        <div class="section-title">পপুলার স্লাইডার</div>
        <div class="slider" id="slider-content"></div>

        <div class="section-title">সব ভিডিও</div>
        <div class="grid" id="main-grid"></div>

        <div class="pagination">
            <button class="pg-btn" id="prev-btn" onclick="changePage(-1)">Previous</button>
            <span id="page-info">Page 1 of 1</span>
            <button class="pg-btn" id="next-btn" onclick="changePage(1)">Next</button>
        </div>
    </div>

    <!-- Profile Page -->
    <div id="page-profile" class="hidden">
        <div class="profile-hero">
            <div class="avatar" id="u-avatar">?</div>
            <h2 id="u-name">Guest User</h2>
            <div id="u-tag" style="color:#ccc;">@username</div>
            <div class="stats">
                <div class="stat-item"><div class="stat-val" id="s-liked">0</div><div class="stat-lab">Liked</div></div>
                <div class="stat-item"><div class="stat-val" id="s-today">0</div><div class="stat-lab">Today Ads</div></div>
                <div class="stat-item"><div class="stat-val" id="s-limit">30</div><div class="stat-lab">Daily Limit</div></div>
            </div>
        </div>
    </div>

    <!-- Footer Nav -->
    <div class="footer">
        <div class="nav-item active" onclick="nav('home', this)"><span class="nav-icon">🏠</span>হোম</div>
        <div class="nav-item" onclick="nav('liked', this)"><span class="nav-icon">❤️</span>পছন্দ</div>
        <div class="nav-item" onclick="nav('tut', this)"><span class="nav-icon">ℹ️</span>টিউটোরিয়াল</div>
        <div class="nav-item" onclick="nav('link', this)"><span class="nav-icon">🔗</span>লিংক</div>
        <div class="nav-item" onclick="nav('profile', this)"><span class="nav-icon">👤</span>প্রোফাইল</div>
    </div>

    <script>
        let tg = window.Telegram.WebApp;
        tg.expand();
        let user = tg.initDataUnsafe.user || {id: 0, first_name: 'Guest', username: 'user'};
        let currentPage = 1;
        let adStep = 0;

        async function init() {
            const set = await (await fetch('/api/settings')).json();
            document.getElementById('web-title').innerText = set.name;
            document.getElementById('app-name').innerText = set.name;
            if(set.notice) {
                const nb = document.getElementById('notice');
                nb.innerText = set.notice;
                nb.style.display = 'block';
            }
            loadSlider(set.slider_count);
            loadPosts(1);
        }

        async function loadSlider(count) {
            const res = await fetch(`/api/slider?count=${count}`);
            const data = await res.json();
            const container = document.getElementById('slider-content');
            data.forEach(p => {
                container.innerHTML += `
                    <div class="slide-card">
                        <img src="${p.photo_url}">
                        <div class="slide-info"><b>${p.title}</b></div>
                    </div>`;
            });
        }

        async function loadPosts(page) {
            currentPage = page;
            const res = await fetch(`/api/posts?page=${page}`);
            const data = await res.json();
            const grid = document.getElementById('main-grid');
            grid.innerHTML = '';
            data.posts.forEach(p => {
                grid.innerHTML += `
                    <div class="post-card">
                        <img src="${p.photo_url}" class="post-img">
                        <div class="post-details">
                            <div class="post-title">${p.title}</div>
                            <div id="unlock-st-${p._id}" style="font-size:10px;color:#ff006e;margin-bottom:5px;">ADS STEP: 0/${data.steps}</div>
                            <button class="unlock-btn" onclick="unlock('${p._id}', ${data.steps})">🎬 UNLOCK</button>
                        </div>
                    </div>`;
            });
            document.getElementById('page-info').innerText = `Page ${page} of ${data.total_pages}`;
            document.getElementById('prev-btn').disabled = page === 1;
            document.getElementById('next-btn').disabled = page >= data.total_pages;
        }

        async function unlock(id, target) {
            const sdks = await (await fetch('/api/sdks')).json();
            if(adStep < target) {
                if(sdks.length > 0) window.open(sdks[0].link, '_blank');
                adStep++;
                document.getElementById('unlock-st-'+id).innerText = `ADS STEP: ${adStep}/${target}`;
                fetch('/api/ad-click', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({user_id:user.id})});
            } else {
                alert("ভিডিও আনলক হয়েছে!");
                adStep = 0;
            }
        }

        function nav(page, el) {
            document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
            el.classList.add('active');
            document.getElementById('page-home').classList.add('hidden');
            document.getElementById('page-profile').classList.add('hidden');
            if(page === 'home') document.getElementById('page-home').classList.remove('hidden');
            if(page === 'profile') {
                document.getElementById('page-profile').classList.remove('hidden');
                loadProfile();
            }
        }

        async function loadProfile() {
            const res = await fetch(`/api/user/${user.id}`);
            const data = await res.json();
            document.getElementById('u-name').innerText = user.first_name;
            document.getElementById('u-tag').innerText = '@' + (user.username || 'user');
            document.getElementById('u-avatar').innerText = user.first_name[0].toUpperCase();
            document.getElementById('s-liked').innerText = data.liked || 0;
            document.getElementById('s-today').innerText = data.ads_today || 0;
        }

        function changePage(delta) {
            loadPosts(currentPage + delta);
            window.scrollTo(0,0);
        }

        init();
    </script>
</body>
</html>
"""

# ================= API ENDPOINTS =================
app = Flask(__name__)
CORS(app)

@app.route('/')
def index(): return render_template_string(HTML_TEMPLATE)

@app.route('/api/settings')
async def get_settings():
    s = await db.settings.find_one({"id": "config"}) or {"name": "BongoBD", "notice": "", "steps": 3, "slider_count": 5}
    return jsonify(s)

@app.route('/api/posts')
async def get_posts():
    page = int(request.args.get('page', 1))
    limit = 20
    total = await db.posts.count_documents({})
    posts = await db.posts.find().sort('_id', -1).skip((page-1)*limit).limit(limit).to_list(limit)
    for p in posts: p['_id'] = str(p['_id'])
    s = await db.settings.find_one({"id": "config"}) or {"steps": 3}
    return jsonify({"posts": posts, "total_pages": (total // limit) + (1 if total % limit > 0 else 0), "steps": s['steps']})

@app.route('/api/slider')
async def get_slider():
    count = int(request.args.get('count', 5))
    posts = await db.posts.find().sort('_id', -1).limit(count).to_list(count)
    for p in posts: p['_id'] = str(p['_id'])
    return jsonify(posts)

@app.route('/api/user/<int:uid>')
async def get_user(uid):
    u = await db.users.find_one({"user_id": uid}) or {"ads_today": 0, "liked": 0}
    return jsonify(u)

@app.route('/api/ad-click', methods=['POST'])
async def ad_click():
    uid = request.json['user_id']
    await db.users.update_one({"user_id": uid}, {"$inc": {"ads_today": 1}}, upsert=True)
    return jsonify({"ok": True})

@app.route('/api/sdks')
async def get_sdks():
    return jsonify(await db.sdks.find().to_list(10))

# ================= BOT COMMANDS =================

@dp.message_handler(commands=['start'])
async def start(m: types.Message):
    await db.users.update_one({"user_id": m.from_user.id}, {"$set": {"name": m.from_user.full_name}}, upsert=True)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🎬 ওপেন মিনি অ্যাপ", web_app=types.WebAppInfo(url=APP_URL)))
    await m.answer(f"✨ **স্বাগতম {m.from_user.first_name}**\n\nভিডিও দেখতে নিচের বাটনে ক্লিক করুন 👇", reply_markup=markup, parse_mode="Markdown")

@dp.message_handler(commands=['name'], user_id=ADMIN_ID)
async def set_name(m: types.Message):
    name = m.get_args()
    await db.settings.update_one({"id": "config"}, {"$set": {"name": name}}, upsert=True)
    await m.answer(f"✅ অ্যাপের নাম আপডেট হয়েছে: {name}")

@dp.message_handler(commands=['notice'], user_id=ADMIN_ID)
async def set_notice(m: types.Message):
    txt = m.get_args()
    await db.settings.update_one({"id": "config"}, {"$set": {"notice": txt}}, upsert=True)
    await m.answer("✅ নোটিশ আপডেট হয়েছে।")

@dp.message_handler(commands=['delnotice'], user_id=ADMIN_ID)
async def del_notice(m: types.Message):
    await db.settings.update_one({"id": "config"}, {"$set": {"notice": ""}}, upsert=True)
    await m.answer("🗑 নোটিশ ডিলেট হয়েছে।")

@dp.message_handler(commands=['step'], user_id=ADMIN_ID)
async def set_step(m: types.Message):
    await db.settings.update_one({"id": "config"}, {"$set": {"steps": int(m.get_args())}}, upsert=True)
    await m.answer(f"⚙️ অ্যাড স্টেপ {m.get_args()} সেট করা হয়েছে।")

@dp.message_handler(commands=['slidercount'], user_id=ADMIN_ID)
async def set_sl(m: types.Message):
    await db.settings.update_one({"id": "config"}, {"$set": {"slider_count": int(m.get_args())}}, upsert=True)
    await m.answer(f"✅ স্লাইডারে এখন {m.get_args()}টি পোস্ট থাকবে।")

@dp.message_handler(commands=['post'], user_id=ADMIN_ID)
async def post_s(m: types.Message):
    await m.answer("📝 টাইটেল দিন:"); await PostState.title.set()

@dp.message_handler(state=PostState.title)
async def post_t(m: types.Message, state: FSMContext):
    await state.update_data(title=m.text); await m.answer("📸 ফটো পাঠান:"); await PostState.photo.set()

@dp.message_handler(content_types=['photo'], state=PostState.photo)
async def post_p(m: types.Message, state: FSMContext):
    file = await bot.get_file(m.photo[-1].file_id)
    url = f"https://api.telegram.org/file/bot{API_TOKEN}/{file.file_path}"
    await state.update_data(photo=url); await m.answer("🔗 ভিডিও লিংক/ফাইল দিন:"); await PostState.content.set()

@dp.message_handler(state=PostState.content, content_types=['any'])
async def post_f(m: types.Message, state: FSMContext):
    data = await state.get_data()
    val = m.text or m.video.file_id or m.document.file_id
    await db.posts.insert_one({"title": data['title'], "photo_url": data['photo'], "content": val})
    await m.answer("✅ ভিডিও পোস্ট সফল হয়েছে।")
    await state.finish()

@dp.message_handler(commands=['sdk'], user_id=ADMIN_ID)
async def add_sdk(m: types.Message):
    args = m.get_args().split()
    await db.sdks.update_one({"id": args[0]}, {"$set": {"link": args[1]}}, upsert=True)
    await m.answer("✅ SDK আপডেট হয়েছে।")

@dp.message_handler(commands=['deleteall'], user_id=ADMIN_ID)
async def clr(m: types.Message):
    await db.posts.delete_many({}); await db.users.delete_many({}); await m.answer("💥 সব মুছে ফেলা হয়েছে!")

# ================= WEBHOOK & RUN =================
def setup_webhook():
    webhook_url = f"https://api.telegram.org/bot{API_TOKEN}/setWebhook?url={APP_URL}/webhook"
    requests.get(webhook_url)

@app.route('/webhook', methods=['POST'])
def telegram_webhook():
    update = types.Update.to_object(request.json)
    Dispatcher.set_current(dp)
    asyncio.run(dp.process_update(update))
    return "ok", 200

if __name__ == '__main__':
    setup_webhook()
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5000)).start()
