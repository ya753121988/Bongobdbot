import asyncio
import os
import requests
import json
import logging
import threading
from quart import Quart, render_template_string, jsonify, request
from quart_cors import cors
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

# ================== কনফিগারেশন (আপনার ডেটা) ==================
API_TOKEN = '8162462190:AAFqdr69Et6tQ4_CvW3OjNjniu8yz056TCM'
MONGO_URL = 'mongodb+srv://roxiw19528:roxiw19528@cluster0.vl508y4.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'
ADMIN_ID = 7120801813
APP_URL = "https://bongobdbot.onrender.com"

# ================== ডাটাবেস এবং বট লজিক ==================
client = AsyncIOMotorClient(MONGO_URL)
db = client['bongobd_mega_system']
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

class PostState(StatesGroup):
    title = State()
    photo = State()
    content = State()

# ================== মিনি অ্যাপের বিশাল ডিজাইন (HTML/CSS/JS) ==================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title id="web-title">Loading...</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        :root { --pink: #ff006e; --bg: #000; --card: #121212; --text: #fff; --gray: #888; }
        * { box-sizing: border-box; -webkit-tap-highlight-color: transparent; outline: none; }
        body { background: var(--bg); color: var(--text); font-family: 'Segoe UI', sans-serif; margin: 0; padding: 0; overflow-x: hidden; }
        
        /* নোটিশ বার ডিজাইন */
        #notice-bar { background: var(--pink); color: #fff; padding: 12px; text-align: center; font-size: 14px; font-weight: bold; display: none; position: sticky; top: 0; z-index: 2000; animation: slideDown 0.5s ease; }
        @keyframes slideDown { from { transform: translateY(-100%); } to { transform: translateY(0); } }

        /* হেডার */
        header { padding: 20px; text-align: center; border-bottom: 1px solid #222; background: rgba(0,0,0,0.9); backdrop-filter: blur(10px); }
        .logo { color: var(--pink); font-size: 26px; font-weight: 900; text-transform: uppercase; letter-spacing: 2px; }

        .container { padding: 15px; max-width: 1400px; margin: 0 auto; min-height: 100vh; }
        
        /* স্লাইডার সেকশন */
        .section-header { font-size: 18px; margin: 25px 0 15px; display: flex; align-items: center; gap: 10px; font-weight: bold; border-left: 4px solid var(--pink); padding-left: 10px; }
        .slider-wrapper { display: flex; overflow-x: auto; gap: 15px; padding-bottom: 15px; scrollbar-width: none; -ms-overflow-style: none; }
        .slider-wrapper::-webkit-scrollbar { display: none; }
        .slide-card { min-width: 260px; height: 150px; background: var(--card); border-radius: 12px; overflow: hidden; position: relative; border: 1px solid #333; flex-shrink: 0; transition: 0.3s; }
        .slide-card img { width: 100%; height: 100%; object-fit: cover; opacity: 0.5; }
        .slide-text { position: absolute; bottom: 10px; left: 10px; font-size: 14px; font-weight: bold; text-shadow: 0 2px 4px #000; }

        /* রেসপন্সিভ গ্রিড (PC: 5, Tablet: 3, Mobile: 2) */
        .video-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }
        @media (min-width: 768px) { .video-grid { grid-template-columns: repeat(3, 1fr); } }
        @media (min-width: 1024px) { .video-grid { grid-template-columns: repeat(5, 1fr); } }

        .video-card { background: var(--card); border-radius: 12px; overflow: hidden; border: 1px solid #222; transition: 0.3s; position: relative; }
        .video-card:hover { border-color: var(--pink); transform: scale(1.02); }
        .thumb-img { width: 100%; height: 130px; object-fit: cover; }
        .video-info { padding: 10px; }
        .video-title { font-size: 13px; font-weight: 600; height: 35px; overflow: hidden; margin-bottom: 10px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }
        .unlock-btn { background: var(--pink); color: #fff; border: none; width: 100%; padding: 10px; border-radius: 6px; font-weight: bold; cursor: pointer; font-size: 12px; }

        /* অ্যাডভান্স পেজিনেশন (Next, Prev, 1, 2, 3...) */
        .pagination-area { display: flex; justify-content: center; align-items: center; gap: 8px; padding: 40px 0 120px; flex-wrap: wrap; }
        .pg-node { background: #1a1a1a; border: 1px solid #333; color: #fff; padding: 8px 14px; border-radius: 5px; cursor: pointer; font-weight: bold; transition: 0.3s; }
        .pg-node.active { background: var(--pink); border-color: var(--pink); }
        .pg-node:hover:not(.active) { border-color: var(--pink); }
        .pg-node:disabled { opacity: 0.3; cursor: not-allowed; }

        /* প্রোফাইল পেজ ডিজাইন */
        .profile-container { background: linear-gradient(180deg, var(--pink) 0%, #000 100%); padding: 60px 20px; text-align: center; }
        .user-avatar { width: 90px; height: 90px; background: #fff; border-radius: 50%; margin: 0 auto 15px; display: flex; align-items: center; justify-content: center; font-size: 35px; color: #000; font-weight: bold; border: 4px solid rgba(255,255,255,0.2); }
        .user-stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-top: 30px; padding: 0 15px; }
        .stat-box { background: rgba(255,255,255,0.05); padding: 15px 5px; border-radius: 12px; border: 1px solid #222; }
        .stat-num { font-size: 18px; font-weight: bold; color: var(--pink); }
        .stat-txt { font-size: 10px; color: #aaa; text-transform: uppercase; margin-top: 5px; }

        /* নেভিগেশন মেনু (৫টি বাটন) */
        .nav-footer { position: fixed; bottom: 0; width: 100%; background: rgba(10,10,10,0.98); backdrop-filter: blur(15px); display: flex; justify-content: space-around; padding: 12px 0; border-top: 1px solid #222; z-index: 1000; }
        .nav-btn { color: #666; text-decoration: none; font-size: 11px; text-align: center; flex: 1; transition: 0.3s; cursor: pointer; }
        .nav-btn.active { color: var(--pink); }
        .nav-icon { font-size: 22px; margin-bottom: 4px; display: block; }

        .page-content { display: none; }
        .page-content.active { display: block; }
        #loader { position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); color: var(--pink); font-weight: bold; }
    </style>
</head>
<body>
    <div id="notice-bar"></div>
    <header><div class="logo" id="app-display-name">BONGOBD</div></header>

    <div id="loader">অ্যাপ লোড হচ্ছে...</div>

    <!-- হোম পেজ -->
    <div id="page-home" class="page-content container">
        <div class="section-header">পপুলার স্লাইডার 🔥</div>
        <div class="slider-wrapper" id="slider-content"></div>

        <div class="section-header">সব ভিডিও ভিডিও 🎬</div>
        <div class="video-grid" id="main-grid"></div>

        <div class="pagination-area" id="pagination-ui"></div>
    </div>

    <!-- প্রোফাইল পেজ -->
    <div id="page-profile" class="page-content">
        <div class="profile-container">
            <div class="user-avatar" id="avatar-text">?</div>
            <h2 id="full-name">User Name</h2>
            <div id="username-tag" style="color:#ccc; font-size:13px;">@username</div>
            <div class="user-stats">
                <div class="stat-box"><div class="stat-num" id="stat-liked">0</div><div class="stat-txt">Liked</div></div>
                <div class="stat-box"><div class="stat-num" id="stat-today">0</div><div class="stat-txt">Today Ads</div></div>
                <div class="stat-box"><div class="stat-num">30</div><div class="stat-txt">Limit</div></div>
            </div>
        </div>
    </div>

    <!-- টিউটোরিয়াল পেজ -->
    <div id="page-tut" class="page-content container" style="text-align:center; padding-top:50px;">
        <h3 class="pink">টিউটোরিয়াল ও সাহায্য</h3>
        <div id="tut-list" style="color:#888;">লোড হচ্ছে...</div>
    </div>

    <!-- ফুটার নেভিগেশন -->
    <div class="nav-footer">
        <div class="nav-btn active" onclick="changeTab('home', this)"><span class="nav-icon">🏠</span>হোম</div>
        <div class="nav-btn" onclick="changeTab('home', this)"><span class="nav-icon">❤️</span>পছন্দ</div>
        <div class="nav-btn" onclick="changeTab('tut', this)"><span class="nav-icon">ℹ️</span>টিউটোরিয়াল</div>
        <div class="nav-btn" onclick="changeTab('tut', this)"><span class="nav-icon">🔗</span>লিংক</div>
        <div class="nav-btn" onclick="changeTab('profile', this)"><span class="nav-icon">👤</span>প্রোফাইল</div>
    </div>

    <script>
        let tg = window.Telegram.WebApp;
        tg.expand();
        let user = tg.initDataUnsafe.user || {id: 0, first_name: 'Guest', username: 'user'};
        let currentPage = 1;
        let globalAdStep = 0;

        async function initApp() {
            try {
                const setRes = await fetch('/api/settings');
                const set = await setRes.json();
                document.getElementById('web-title').innerText = set.name;
                document.getElementById('app-display-name').innerText = set.name;
                if(set.notice) {
                    const nb = document.getElementById('notice-bar');
                    nb.innerText = set.notice; nb.style.display = 'block';
                }
                loadSlider(set.slider_count || 5);
                loadVideos(1);
                document.getElementById('loader').style.display = 'none';
                document.getElementById('page-home').classList.add('active');
            } catch(e) { document.getElementById('loader').innerText = "সার্ভার এরর!"; }
        }

        async function loadSlider(count) {
            const res = await fetch(`/api/slider?count=${count}`);
            const data = await res.json();
            const slider = document.getElementById('slider-content');
            slider.innerHTML = '';
            data.forEach(p => {
                slider.innerHTML += `<div class="slide-card"><img src="${p.photo_url}"><div class="slide-text">${p.title}</div></div>`;
            });
        }

        async function loadVideos(page) {
            currentPage = page;
            const res = await fetch(`/api/posts?page=${page}`);
            const data = await res.json();
            const grid = document.getElementById('main-grid');
            grid.innerHTML = '';
            data.posts.forEach(p => {
                grid.innerHTML += `
                    <div class="video-card">
                        <img src="${p.photo_url}" class="thumb-img">
                        <div class="video-info">
                            <div class="video-title">${p.title}</div>
                            <div id="step-info-${p._id}" style="font-size:10px; color:var(--pink); margin-bottom:5px;">ADS: 0/${data.target_steps}</div>
                            <button class="unlock-btn" onclick="handleUnlock('${p._id}', ${data.target_steps})">UNLOCK VIDEO</button>
                        </div>
                    </div>`;
            });
            renderPagination(data.total_pages, page);
        }

        function renderPagination(total, current) {
            const ui = document.getElementById('pagination-ui');
            ui.innerHTML = '';
            // Prev Button
            ui.innerHTML += `<button class="pg-node" ${current==1?'disabled':''} onclick="loadVideos(${current-1})">Prev</button>`;
            // Page Numbers (১, ২, ৩...)
            for(let i=1; i<=total; i++) {
                if(i == 1 || i == total || (i >= current-1 && i <= current+1)) {
                    ui.innerHTML += `<button class="pg-node ${i==current?'active':''}" onclick="loadVideos(${i})">${i}</button>`;
                } else if (i == current-2 || i == current+2) {
                    ui.innerHTML += `<span style="color:#444;">...</span>`;
                }
            }
            // Next Button
            ui.innerHTML += `<button class="pg-node" ${current==total?'disabled':''} onclick="loadVideos(${current+1})">Next</button>`;
        }

        async function handleUnlock(id, target) {
            const sdks = await (await fetch('/api/sdks')).json();
            if(globalAdStep < target) {
                if(sdks.length > 0) window.open(sdks[0].link, '_blank');
                globalAdStep++;
                document.getElementById('step-info-'+id).innerText = `ADS: ${globalAdStep}/${target}`;
                fetch('/api/ad-click', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({user_id:user.id})});
            } else {
                alert("ভিডিও আনলক হয়েছে!");
                globalAdStep = 0;
            }
        }

        function changeTab(pageId, el) {
            document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
            el.classList.add('active');
            document.querySelectorAll('.page-content').forEach(p => p.classList.remove('active'));
            document.getElementById('page-' + pageId).classList.add('active');
            if(pageId === 'profile') loadUserProfile();
            window.scrollTo(0,0);
        }

        async function loadUserProfile() {
            const res = await fetch(`/api/user/${user.id}`);
            const data = await res.json();
            document.getElementById('full-name').innerText = user.first_name;
            document.getElementById('username-tag').innerText = '@' + (user.username || 'user');
            document.getElementById('avatar-text').innerText = user.first_name[0].toUpperCase();
            document.getElementById('stat-liked').innerText = data.liked || 0;
            document.getElementById('stat-today').innerText = data.ads_today || 0;
        }

        initApp();
    </script>
</body>
</html>
"""

# ================== এপিআই লজিক (QUART) ==================
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
    limit = 20
    total = await db.posts.count_documents({})
    posts = await db.posts.find().sort('_id', -1).skip((page-1)*limit).limit(limit).to_list(limit)
    for p in posts: p['_id'] = str(p['_id'])
    conf = await db.settings.find_one({"id": "config"}) or {"steps": 3}
    return jsonify({"posts": posts, "total_pages": (total // limit) + (1 if total % limit > 0 else 0), "target_steps": conf.get("steps", 3)})

@app.route('/api/slider')
async def get_slider():
    count = int(request.args.get('count', 6))
    posts = await db.posts.find().sort('_id', -1).limit(count).to_list(count)
    for p in posts: p['_id'] = str(p['_id'])
    return jsonify(posts)

@app.route('/api/user/<int:uid>')
async def get_user_profile(uid):
    u = await db.users.find_one({"user_id": uid}) or {"ads_today": 0, "liked": 0}
    return jsonify(u)

@app.route('/api/ad-click', methods=['POST'])
async def ad_count_update():
    data = await request.json
    await db.users.update_one({"user_id": data['user_id']}, {"$inc": {"ads_today": 1}}, upsert=True)
    return jsonify({"ok": True})

@app.route('/api/sdks')
async def get_active_sdks():
    return jsonify(await db.sdks.find().to_list(20))

# ================== বটের কমান্ড ম্যানেজমেন্ট ==================

@dp.message_handler(commands=['start'])
async def start_handler(m: types.Message):
    # ইউজার রেজিস্ট্রেশন
    await db.users.update_one({"user_id": m.from_user.id}, {"$set": {"name": m.from_user.full_name}}, upsert=True)
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(types.InlineKeyboardButton("🎬 ওপেন মিনি অ্যাপ", web_app=types.WebAppInfo(url=APP_URL)))
    
    # ডাইনামিক চ্যানেল বাটন
    channels = await db.channels.find().to_list(10)
    for c in channels: markup.add(types.InlineKeyboardButton(c['name'], url=c['link']))
    
    # ডাইনামিক টিউটোরিয়াল বাটন
    tuts = await db.tutorials.find().to_list(10)
    for t in tuts: markup.add(types.InlineKeyboardButton(f"ℹ️ {t['name']}", url=t['link']))

    welcome_msg = f"✨ **স্বাগতম {m.from_user.first_name}**\n\nআমাদের ভিডিও সেবা পেতে নিচের বাটনে ক্লিক করে অ্যাপটি ওপেন করুন 👇"
    await m.answer_photo(photo="https://telegra.ph/file/a8677c3e1c66288828b80.jpg", caption=welcome_msg, reply_markup=markup, parse_mode="Markdown")

# এডমিন কমান্ডসমূহ
@dp.message_handler(commands=['post'], user_id=ADMIN_ID)
async def admin_post_start(m: types.Message):
    await m.answer("📝 ভিডিও টাইটেল দিন:"); await PostState.title.set()

@dp.message_handler(state=PostState.title)
async def admin_post_title(m: types.Message, state: FSMContext):
    await state.update_data(title=m.text); await m.answer("📸 ভিডিও ফটো পাঠান:"); await PostState.photo.set()

@dp.message_handler(content_types=['photo'], state=PostState.photo)
async def admin_post_photo(m: types.Message, state: FSMContext):
    file = await bot.get_file(m.photo[-1].file_id)
    url = f"https://api.telegram.org/file/bot{API_TOKEN}/{file.file_path}"
    await state.update_data(photo=url); await m.answer("🔗 ভিডিও লিংক বা ফাইল পাঠান:"); await PostState.content.set()

@dp.message_handler(state=PostState.content, content_types=['any'])
async def admin_post_final(m: types.Message, state: FSMContext):
    data = await state.get_data()
    val = m.text or m.video.file_id or m.document.file_id
    await db.posts.insert_one({"title": data['title'], "photo_url": data['photo'], "content": val})
    await m.answer("✅ ভিডিও সফলভাবে পোস্ট করা হয়েছে!"); await state.finish()

@dp.message_handler(commands=['name'], user_id=ADMIN_ID)
async def admin_change_name(m: types.Message):
    name = m.get_args()
    await db.settings.update_one({"id": "config"}, {"$set": {"name": name}}, upsert=True)
    await m.answer(f"✅ অ্যাপের নাম আপডেট হয়েছে: {name}")

@dp.message_handler(commands=['notice'], user_id=ADMIN_ID)
async def admin_add_notice(m: types.Message):
    txt = m.get_args()
    await db.settings.update_one({"id": "config"}, {"$set": {"notice": txt}}, upsert=True)
    await m.answer("✅ নোটিশ বার আপডেট হয়েছে।")

@dp.message_handler(commands=['delnotice'], user_id=ADMIN_ID)
async def admin_del_notice(m: types.Message):
    await db.settings.update_one({"id": "config"}, {"$set": {"notice": ""}}, upsert=True)
    await m.answer("🗑 নোটিশ ডিলিট করা হয়েছে।")

@dp.message_handler(commands=['step'], user_id=ADMIN_ID)
async def admin_set_step(m: types.Message):
    await db.settings.update_one({"id": "config"}, {"$set": {"steps": int(m.get_args())}}, upsert=True)
    await m.answer(f"⚙️ অ্যাড আনলক স্টেপ {m.get_args()} এ সেট হয়েছে।")

@dp.message_handler(commands=['slidercount'], user_id=ADMIN_ID)
async def admin_set_slider(m: types.Message):
    await db.settings.update_one({"id": "config"}, {"$set": {"slider_count": int(m.get_args())}}, upsert=True)
    await m.answer(f"✅ স্লাইডারে এখন {m.get_args()}টি পোস্ট থাকবে।")

@dp.message_handler(commands=['addchannel'], user_id=ADMIN_ID)
async def admin_add_ch(m: types.Message):
    args = m.get_args().split(maxsplit=1)
    await db.channels.update_one({"name": args[0]}, {"$set": {"link": args[1]}}, upsert=True)
    await m.answer(f"✅ বাটন '{args[0]}' এড হয়েছে।")

@dp.message_handler(commands=['delchannel'], user_id=ADMIN_ID)
async def admin_del_ch(m: types.Message):
    await db.channels.delete_one({"name": m.get_args()})
    await m.answer("🗑 চ্যানেল বাটন ডিলিট হয়েছে।")

@dp.message_handler(commands=['addtutorial'], user_id=ADMIN_ID)
async def admin_add_tut(m: types.Message):
    args = m.get_args().split(maxsplit=1)
    await db.tutorials.update_one({"name": args[0]}, {"$set": {"link": args[1]}}, upsert=True)
    await m.answer(f"✅ টিউটোরিয়াল বাটন '{args[0]}' এড হয়েছে।")

@dp.message_handler(commands=['deltutorial'], user_id=ADMIN_ID)
async def admin_del_tut(m: types.Message):
    await db.tutorials.delete_one({"name": m.get_args()})
    await m.answer("🗑 টিউটোরিয়াল বাটন ডিলিট হয়েছে।")

@dp.message_handler(commands=['sdk'], user_id=ADMIN_ID)
async def admin_add_sdk(m: types.Message):
    args = m.get_args().split()
    await db.sdks.update_one({"id": args[0]}, {"$set": {"link": args[1]}}, upsert=True)
    await m.answer(f"✅ SDK {args[0]} আপডেট হয়েছে।")

@dp.message_handler(regexp=r'^/sdkd\d+', user_id=ADMIN_ID)
async def admin_del_sdk(m: types.Message):
    sid = m.text.replace('/sdkd', '')
    await db.sdks.delete_one({"id": sid})
    await m.answer(f"🗑 SDK {sid} ডিলেট হয়েছে।")

@dp.message_handler(commands=['deleteall'], user_id=ADMIN_ID)
async def admin_clear_db(m: types.Message):
    await db.posts.delete_many({}); await db.users.delete_many({})
    await db.channels.delete_many({}); await db.tutorials.delete_many({}); await db.sdks.delete_many({})
    await m.answer("💥 বটের সকল ডাটা ক্লিন করা হয়েছে!")

# ================== ওয়েবহুক এবং রানার লজিক ==================

@app.before_serving
async def setup_systems():
    # অটো ওয়েবহুক কনফিগারেশন
    await bot.delete_webhook()
    await bot.set_webhook(f"{APP_URL}/tg-webhook")
    # ব্যাকগ্রাউন্ডে বট পোলিং (যদি প্রয়োজন হয়)
    asyncio.create_task(dp.start_polling())

@app.route('/tg-webhook', methods=['POST'])
async def handle_tg_webhook():
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
