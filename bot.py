import asyncio
import os
import requests
import json
import logging
from datetime import datetime
from quart import Quart, render_template_string, jsonify, request
from quart_cors import cors
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from motor.motor_asyncio import AsyncIOMotorClient

# ================= কনফিগারেশন =================
API_TOKEN = '8162462190:AAFqdr69Et6tQ4_CvW3OjNjniu8yz056TCM'
MONGO_URL = 'mongodb+srv://roxiw19528:roxiw19528@cluster0.vl508y4.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'
ADMIN_ID = 7120801813
APP_URL = "https://bongobdbot.onrender.com"

# ================= ডাটাবেস ও বট সেটআপ =================
client = AsyncIOMotorClient(MONGO_URL)
db = client['bongobd_master_final_v1']
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

class PostState(StatesGroup):
    title = State()
    photo = State()
    content = State()

# ================= মিনি অ্যাপ আল্ট্রা ডিজাইন (HTML/CSS/JS) =================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title id="web-title">BongoBD Master</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        :root { --pink: #ff006e; --bg: #000; --card: #121212; --text: #fff; }
        * { box-sizing: border-box; -webkit-tap-highlight-color: transparent; outline: none; }
        body { background: var(--bg); color: var(--text); font-family: 'Segoe UI', sans-serif; margin: 0; padding: 0; overflow-x: hidden; }
        
        /* নোটিশ বার */
        #notice-bar { background: var(--pink); color: #fff; padding: 12px; text-align: center; font-size: 14px; font-weight: bold; display: none; position: sticky; top: 0; z-index: 2000; box-shadow: 0 2px 10px rgba(255,0,110,0.5); }
        
        /* হেডার */
        header { padding: 20px; text-align: center; border-bottom: 1px solid #222; background: rgba(0,0,0,0.9); backdrop-filter: blur(10px); }
        .logo { color: var(--pink); font-size: 26px; font-weight: 900; text-transform: uppercase; letter-spacing: 2px; }

        .container { padding: 15px; max-width: 1200px; margin: 0 auto; min-height: 100vh; }
        .section-title { font-size: 18px; margin: 25px 0 15px; display: flex; align-items: center; gap: 10px; font-weight: bold; border-left: 4px solid var(--pink); padding-left: 10px; }

        /* স্লাইডার */
        .slider { display: flex; overflow-x: auto; gap: 15px; padding-bottom: 15px; scrollbar-width: none; }
        .slider::-webkit-scrollbar { display: none; }
        .slide-item { min-width: 280px; height: 160px; background: var(--card); border-radius: 15px; overflow: hidden; position: relative; border: 1px solid #333; flex-shrink: 0; }
        .slide-item img { width: 100%; height: 100%; object-fit: cover; opacity: 0.5; }
        .slide-label { position: absolute; bottom: 12px; left: 12px; font-size: 14px; font-weight: bold; text-shadow: 0 2px 4px #000; }

        /* রেসপন্সিভ গ্রিড */
        .grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; }
        @media (min-width: 768px) { .grid { grid-template-columns: repeat(5, 1fr); } }

        .card { background: var(--card); border-radius: 12px; overflow: hidden; border: 1px solid #222; transition: 0.3s; }
        .card:hover { border-color: var(--pink); transform: translateY(-5px); }
        .card-img { width: 100%; height: 150px; object-fit: cover; }
        .card-body { padding: 12px; }
        .card-title { font-size: 13px; font-weight: bold; height: 35px; overflow: hidden; margin-bottom: 12px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }
        .unlock-btn { background: var(--pink); color: #fff; border: none; width: 100%; padding: 12px; border-radius: 8px; font-weight: bold; cursor: pointer; transition: 0.2s; }
        .unlock-btn:active { transform: scale(0.95); opacity: 0.8; }

        /* পেজিনেশন */
        .pagination { display: flex; justify-content: center; align-items: center; gap: 10px; padding: 40px 0 120px; }
        .pg-btn { background: #1a1a1a; border: 1px solid var(--pink); color: #fff; padding: 10px 20px; border-radius: 8px; cursor: pointer; font-weight: bold; }
        .pg-btn:disabled { border-color: #333; color: #555; cursor: not-allowed; }

        /* প্রোফাইল পেজ */
        .profile-hero { background: linear-gradient(180deg, var(--pink) 0%, #000 100%); padding: 60px 20px; text-align: center; }
        .avatar { width: 90px; height: 90px; background: #fff; border-radius: 50%; margin: 0 auto 15px; display: flex; align-items: center; justify-content: center; font-size: 35px; color: #000; font-weight: 900; border: 4px solid rgba(255,255,255,0.2); }
        .stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-top: 30px; }
        .stat-item { background: rgba(255,255,255,0.05); padding: 20px 10px; border-radius: 15px; border: 1px solid #222; }
        .stat-val { font-size: 20px; font-weight: bold; color: var(--pink); }
        .stat-lab { font-size: 10px; color: #aaa; text-transform: uppercase; margin-top: 5px; }

        /* ফুটার মেনু */
        .navbar { position: fixed; bottom: 0; width: 100%; background: rgba(10,10,10,0.95); backdrop-filter: blur(15px); display: flex; justify-content: space-around; padding: 15px 0; border-top: 1px solid #222; z-index: 1000; }
        .nav-link { color: #666; text-decoration: none; font-size: 11px; text-align: center; flex: 1; transition: 0.3s; cursor: pointer; }
        .nav-link.active { color: var(--pink); font-weight: bold; }
        .nav-icon { font-size: 22px; margin-bottom: 4px; display: block; }

        .hidden { display: none; }
        #loader { position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); color: var(--pink); font-weight: bold; }
    </style>
</head>
<body>
    <div id="notice-bar"></div>
    <header><div class="logo" id="app-name">BongoBD</div></header>

    <div id="loader">লোড হচ্ছে...</div>

    <!-- হোম পেজ -->
    <div id="page-home" class="container hidden">
        <div class="section-title">পপুলার ভিডিও স্লাইডার</div>
        <div class="slider" id="slider-content"></div>
        <div class="section-title">সব ভিডিও</div>
        <div class="grid" id="main-grid"></div>
        <div class="pagination">
            <button class="pg-btn" id="prev-btn" onclick="changePage(-1)">← Prev</button>
            <span id="page-info" style="font-weight:bold; color:var(--pink);">Page 1 of 1</span>
            <button class="pg-btn" id="next-btn" onclick="changePage(1)">Next →</button>
        </div>
    </div>

    <!-- প্রোফাইল পেজ -->
    <div id="page-profile" class="hidden">
        <div class="profile-hero">
            <div class="avatar" id="u-avatar">?</div>
            <h2 id="u-name">Guest User</h2>
            <div id="u-tag" style="color:#ccc; font-size:13px;">@username</div>
            <div class="stats">
                <div class="stat-item"><div class="stat-val" id="s-liked">0</div><div class="stat-lab">Liked</div></div>
                <div class="stat-item"><div class="stat-val" id="s-today">0</div><div class="stat-lab">Today Ads</div></div>
                <div class="stat-item"><div class="stat-val">30</div><div class="stat-lab">Limit</div></div>
            </div>
        </div>
    </div>

    <!-- নেভিগেশন -->
    <div class="navbar">
        <div class="nav-link active" onclick="nav('home', this)"><span class="nav-icon">🏠</span>হোম</div>
        <div class="nav-link" onclick="nav('home', this)"><span class="nav-icon">❤️</span>পছন্দ</div>
        <div class="nav-link" onclick="nav('home', this)"><span class="nav-icon">ℹ️</span>টিউটোরিয়াল</div>
        <div class="nav-link" onclick="nav('home', this)"><span class="nav-icon">🔗</span>লিংক</div>
        <div class="nav-link" onclick="nav('profile', this)"><span class="nav-icon">👤</span>প্রোফাইল</div>
    </div>

    <script>
        let tg = window.Telegram.WebApp;
        tg.expand();
        let user = tg.initDataUnsafe.user || {id: 0, first_name: 'Guest', username: 'user'};
        let currentPage = 1;
        let adStep = 0;

        async function init() {
            const set = await (await fetch('/api/settings')).json();
            document.getElementById('app-name').innerText = set.name;
            if(set.notice) {
                const nb = document.getElementById('notice-bar');
                nb.innerText = set.notice; nb.style.display = 'block';
            }
            await loadSlider(set.slider_count || 5);
            await loadPosts(1);
            document.getElementById('loader').style.display = 'none';
            document.getElementById('page-home').classList.remove('hidden');
        }

        async function loadSlider(count) {
            const res = await fetch(`/api/slider?count=${count}`);
            const data = await res.json();
            const slider = document.getElementById('slider-content');
            data.forEach(p => {
                slider.innerHTML += `<div class="slide-item"><img src="${p.photo_url}"><div class="slide-label">${p.title}</div></div>`;
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
                    <div class="card">
                        <img src="${p.photo_url}" class="card-img">
                        <div class="card-body">
                            <div class="card-title">${p.title}</div>
                            <div id="st-${p._id}" style="font-size:10px;color:var(--pink);margin-bottom:8px;">ADS STEP: 0/${data.steps}</div>
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
                document.getElementById('st-'+id).innerText = `ADS STEP: ${adStep}/${target}`;
                fetch('/api/ad-click', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({user_id:user.id})});
            } else { alert("ভিডিও আনলক হয়েছে!"); adStep = 0; }
        }

        function nav(p, el) {
            document.querySelectorAll('.nav-link').forEach(i => i.classList.remove('active'));
            el.classList.add('active');
            document.getElementById('page-home').classList.add('hidden');
            document.getElementById('page-profile').classList.add('hidden');
            if(p === 'home') document.getElementById('page-home').classList.remove('hidden');
            if(p === 'profile') {
                document.getElementById('page-profile').classList.remove('hidden');
                loadProfile();
            }
            window.scrollTo(0,0);
        }

        async function loadProfile() {
            const res = await fetch(`/api/user/${user.id}`);
            const data = await res.json();
            document.getElementById('u-name').innerText = user.first_name;
            document.getElementById('u-tag').innerText = '@' + (user.username || 'user');
            document.getElementById('u-avatar').innerText = user.first_name[0].toUpperCase();
            document.getElementById('s-today').innerText = data.ads_today || 0;
        }

        function changePage(d) { loadPosts(currentPage + d); window.scrollTo(0,0); }
        init();
    </script>
</body>
</html>
"""

# ================= API ENDPOINTS (Quart Async) =================
app = Quart(__name__)
app = cors(app)

@app.route('/')
async def index():
    return render_template_string(HTML_TEMPLATE)

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
    return jsonify({"posts": posts, "total_pages": (total // limit) + (1 if total % limit > 0 else 0), "steps": s.get("steps", 3)})

@app.route('/api/slider')
async def get_slider():
    count = int(request.args.get('count', 5))
    posts = await db.posts.find().sort('_id', -1).limit(count).to_list(count)
    for p in posts: p['_id'] = str(p['_id'])
    return jsonify(posts)

@app.route('/api/user/<int:uid>')
async def get_user(uid):
    u = await db.users.find_one({"user_id": uid}) or {"ads_today": 0}
    return jsonify(u)

@app.route('/api/ad-click', methods=['POST'])
async def ad_click():
    data = await request.json
    await db.users.update_one({"user_id": data['user_id']}, {"$inc": {"ads_today": 1}}, upsert=True)
    return jsonify({"ok": True})

@app.route('/api/sdks')
async def get_sdks():
    return jsonify(await db.sdks.find().to_list(10))

# ================= বটের লজিক ও প্রফেশনাল ডিজাইন =================

@dp.message_handler(commands=['start'])
async def start(m: types.Message):
    # ইউজার রেজিস্ট্রেশন
    await db.users.update_one({"user_id": m.from_user.id}, {"$set": {"name": m.from_user.full_name}}, upsert=True)
    
    # আপনার স্ক্রিনশটের মতো হুবহু ডিজাইন
    welcome_text = (
        "✨ **WELCOME TO VIRAL VIDEO BOT** ✨\n\n"
        "🔍 **আপনাকে অবশ্যই আমাদের সকল চ্যানেলে জয়েন করতে হবে ✅**\n\n"
        "আমাদের নিচের Channel গুলোতে ও ভিডিও দেওয়া হয়\n\n"
        "🎬 **ভিডিও দেখতে হলে অবশ্যই আপনাকে নিচের চ্যানেল গুলোতে Join করার পর [🎬 ভিডিও দেখুন] এ ক্লিক করে ভিডিও দেখতে পারবেন 👇**"
    )
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.row(types.InlineKeyboardButton("🎬 ভিডিও দেখুন", web_app=types.WebAppInfo(url=APP_URL)))
    markup.add(
        types.InlineKeyboardButton("বাচ্চাদের ভিডিও ↗️", url="https://t.me/your_channel"),
        types.InlineKeyboardButton("ভিডিও গ্রুপ ↗️", url="https://t.me/your_group")
    )
    markup.row(types.InlineKeyboardButton("টিউটোরিয়াল ভিডিও ↗️", url="https://t.me/tutorial"))

    # ব্যানার ইমেজ সহ স্টার্ট মেসেজ
    try:
        await m.answer_photo(photo="https://telegra.ph/file/a8677c3e1c66288828b80.jpg", caption=welcome_text, reply_markup=markup, parse_mode="Markdown")
    except:
        await m.answer(welcome_text, reply_markup=markup, parse_mode="Markdown")

# এডমিন কমান্ডসমূহ
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
    await state.update_data(photo=url); await m.answer("🔗 ভিডিও লিংক দিন:"); await PostState.content.set()

@dp.message_handler(state=PostState.content)
async def post_f(m: types.Message, state: FSMContext):
    data = await state.get_data()
    await db.posts.insert_one({"title": data['title'], "photo_url": data['photo'], "content": m.text})
    await m.answer("✅ ভিডিও পোস্ট সফল হয়েছে।"); await state.finish()

@dp.message_handler(commands=['name'], user_id=ADMIN_ID)
async def admin_name(m: types.Message):
    await db.settings.update_one({"id": "config"}, {"$set": {"name": m.get_args()}}, upsert=True)
    await m.answer("✅ অ্যাপের নাম পরিবর্তন হয়েছে।")

@dp.message_handler(commands=['notice'], user_id=ADMIN_ID)
async def admin_notice(m: types.Message):
    await db.settings.update_one({"id": "config"}, {"$set": {"notice": m.get_args()}}, upsert=True)
    await m.answer("✅ নোটিশ আপডেট হয়েছে।")

@dp.message_handler(commands=['step'], user_id=ADMIN_ID)
async def admin_step(m: types.Message):
    await db.settings.update_one({"id": "config"}, {"$set": {"steps": int(m.get_args())}}, upsert=True)
    await m.answer("✅ অ্যাড স্টেপ সেট হয়েছে।")

@dp.message_handler(commands=['sdk'], user_id=ADMIN_ID)
async def admin_sdk(m: types.Message):
    args = m.get_args().split()
    await db.sdks.update_one({"id": args[0]}, {"$set": {"link": args[1]}}, upsert=True)
    await m.answer("✅ SDK সেভ হয়েছে।")

@dp.message_handler(commands=['deleteall'], user_id=ADMIN_ID)
async def admin_clear(m: types.Message):
    await db.posts.delete_many({}); await m.answer("💥 সব ডিলিট হয়েছে!")

# ================= অটো-সেটআপ ও রানার লজিক =================

async def setup_systems():
    # ১. আগের সব ওয়েবহুক মুছে ফেলে নতুন ওয়েবহুক সেট করা
    await bot.delete_webhook()
    await asyncio.sleep(1)
    await bot.set_webhook(f"{APP_URL}/tg-webhook")
    
    # ২. মেনু বাটন (নীচের বাম দিকের বাটন) অটো সেট করা
    menu_button = {
        "type": "web_app",
        "text": "🎬 ভিডিও দেখুন",
        "web_app": {"url": APP_URL}
    }
    requests.post(f"https://api.telegram.org/bot{API_TOKEN}/setChatMenuButton", json={"menu_button": menu_button})

@app.before_serving
async def startup_task():
    asyncio.create_task(setup_systems())

@app.route('/tg-webhook', methods=['POST'])
async def telegram_webhook():
    update_data = await request.json
    update = types.Update.to_object(update_data)
    Dispatcher.set_current(dp)
    Bot.set_current(bot)
    await dp.process_update(update)
    return "ok", 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
