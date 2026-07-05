import asyncio
import os
import requests
import json
import logging
import sys
from datetime import datetime
from quart import Quart, render_template_string, jsonify, request
from quart_cors import cors
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

# ==================== আল্ট্রা কনফিগারেশন ====================
API_TOKEN = '8162462190:AAFqdr69Et6tQ4_CvW3OjNjniu8yz056TCM'
MONGO_URL = 'mongodb+srv://roxiw19528:roxiw19528@cluster0.vl508y4.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'
ADMIN_ID = 7120801813
APP_URL = "https://bongobdbot.onrender.com"

# ডাটাবেস এবং বট ইনিশিয়ালাইজেশন
client = AsyncIOMotorClient(MONGO_URL)
db = client['bongobd_ultra_final_v10']
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# লগিং সেটআপ
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# স্টেট ম্যানেজমেন্ট
class PostState(StatesGroup):
    title = State()
    photo = State()
    content = State()

# ==================== মিনি অ্যাপের বিশাল ডিজাইন (HTML/CSS/JS) ====================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title id="web-title">BongoBD Ultra</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        :root { --pink: #ff006e; --bg: #000; --card: #121212; --text: #fff; }
        * { box-sizing: border-box; -webkit-tap-highlight-color: transparent; outline: none; margin: 0; padding: 0; }
        body { background: var(--bg); color: var(--text); font-family: 'Segoe UI', Tahoma, sans-serif; overflow-x: hidden; }
        
        #notice-bar { background: var(--pink); color: #fff; padding: 14px; text-align: center; font-size: 14px; font-weight: bold; display: none; position: sticky; top: 0; z-index: 9999; box-shadow: 0 4px 10px rgba(255,0,110,0.4); }
        header { padding: 25px; text-align: center; border-bottom: 1px solid #222; background: rgba(0,0,0,0.9); backdrop-filter: blur(15px); }
        .logo { color: var(--pink); font-size: 28px; font-weight: 900; letter-spacing: 2px; text-transform: uppercase; text-shadow: 0 0 15px var(--pink); }

        .container { padding: 15px; max-width: 1400px; margin: 0 auto; min-height: 100vh; }
        .section-title { font-size: 18px; margin: 25px 0 15px; display: flex; align-items: center; gap: 10px; font-weight: bold; border-left: 5px solid var(--pink); padding-left: 12px; }

        /* স্লাইডার ডিজাইন */
        .slider-box { display: flex; overflow-x: auto; gap: 15px; padding-bottom: 20px; scrollbar-width: none; }
        .slider-box::-webkit-scrollbar { display: none; }
        .slide-item { min-width: 280px; height: 160px; background: var(--card); border-radius: 18px; overflow: hidden; position: relative; border: 1px solid #333; flex-shrink: 0; transition: 0.3s; }
        .slide-item img { width: 100%; height: 100%; object-fit: cover; opacity: 0.5; }
        .slide-cap { position: absolute; bottom: 15px; left: 15px; right: 15px; font-size: 14px; font-weight: bold; text-shadow: 0 2px 5px #000; }

        /* রেসপন্সিভ গ্রিড (মোবাইল: ২, পিসি: ৫) */
        .grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; }
        @media (min-width: 768px) { .grid { grid-template-columns: repeat(4, 1fr); } }
        @media (min-width: 1024px) { .grid { grid-template-columns: repeat(5, 1fr); } }

        .post-card { background: var(--card); border-radius: 15px; overflow: hidden; border: 1px solid #222; transition: 0.4s; position: relative; }
        .post-card:hover { border-color: var(--pink); transform: translateY(-5px); box-shadow: 0 5px 15px rgba(255,0,110,0.2); }
        .post-img { width: 100%; height: 160px; object-fit: cover; }
        .post-info { padding: 12px; }
        .post-title { font-size: 14px; font-weight: 600; height: 38px; overflow: hidden; margin-bottom: 12px; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }
        .unlock-btn { background: var(--pink); color: #fff; border: none; width: 100%; padding: 12px; border-radius: 8px; font-weight: bold; cursor: pointer; transition: 0.3s; font-size: 13px; }
        .unlock-btn:active { transform: scale(0.95); opacity: 0.8; }

        /* পেজিনেশন ডিজাইন (Next, Prev, 1, 2, 3) */
        .pagination-bar { display: flex; justify-content: center; align-items: center; gap: 8px; padding: 50px 0 120px; flex-wrap: wrap; }
        .pg-node { background: #1a1a1a; border: 1px solid #333; color: #fff; padding: 10px 18px; border-radius: 8px; cursor: pointer; font-weight: bold; transition: 0.3s; }
        .pg-node.active { background: var(--pink); border-color: var(--pink); }
        .pg-node:disabled { opacity: 0.3; cursor: not-allowed; }

        /* প্রোফাইল পেজ */
        .profile-page { background: linear-gradient(180deg, var(--pink) 0%, #000 100%); padding: 70px 20px; text-align: center; }
        .avatar { width: 100px; height: 100px; background: #fff; border-radius: 50%; margin: 0 auto 20px; display: flex; align-items: center; justify-content: center; font-size: 40px; color: #000; font-weight: 900; border: 5px solid rgba(255,255,255,0.3); box-shadow: 0 0 20px rgba(0,0,0,0.5); }
        .stats-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-top: 40px; padding: 0 10px; }
        .stat-card { background: rgba(255,255,255,0.08); padding: 25px 10px; border-radius: 20px; border: 1px solid #333; }
        .stat-val { font-size: 22px; font-weight: bold; color: var(--pink); }
        .stat-lab { font-size: 10px; color: #bbb; text-transform: uppercase; margin-top: 8px; letter-spacing: 1px; }

        /* ৫টি মেনু নেভিগেশন */
        .footer-nav { position: fixed; bottom: 0; width: 100%; background: rgba(10,10,10,0.98); backdrop-filter: blur(20px); display: flex; justify-content: space-around; padding: 15px 0; border-top: 1px solid #222; z-index: 1000; }
        .nav-link { color: #777; text-decoration: none; font-size: 11px; text-align: center; flex: 1; transition: 0.4s; cursor: pointer; }
        .nav-link.active { color: var(--pink); font-weight: bold; }
        .nav-icon { font-size: 24px; margin-bottom: 6px; display: block; }

        .hidden { display: none; }
        #app-loader { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: #000; color: var(--pink); display: flex; align-items: center; justify-content: center; font-size: 20px; font-weight: bold; z-index: 10000; }
    </style>
</head>
<body>
    <div id="app-loader">বংগোবিডি লোড হচ্ছে...</div>
    <div id="notice-bar"></div>
    <header><div class="logo" id="header-name">BONGOBD</div></header>

    <div id="home-page" class="container hidden">
        <div class="section-title">পপুলার ভিডিও স্লাইডার 🔥</div>
        <div class="slider-box" id="slider-data"></div>
        <div class="section-title">লেটেস্ট ভিডিও 🎬</div>
        <div class="grid" id="grid-data"></div>
        <div class="pagination-bar" id="pg-ui"></div>
    </div>

    <div id="profile-page" class="hidden">
        <div class="profile-page">
            <div class="avatar" id="av-init">?</div>
            <h2 id="u-full-name">User</h2>
            <div id="u-handle" style="color:rgba(255,255,255,0.7); font-size:13px;">@username</div>
            <div class="stats-row">
                <div class="stat-card"><div class="stat-val" id="st-liked">0</div><div class="stat-lab">Liked</div></div>
                <div class="stat-card"><div class="stat-val" id="st-today">0</div><div class="stat-lab">Today Ads</div></div>
                <div class="stat-card"><div class="stat-val">30</div><div class="stat-lab">Limit</div></div>
            </div>
        </div>
    </div>

    <div id="links-page" class="container hidden" style="text-align:center; padding-top:100px;">
        <h3 class="pink">তথ্য ও সাহায্য</h3>
        <p style="color:#666; margin-top:20px;">এখানে প্রয়োজনীয় টিউটোরিয়াল এবং লিঙ্ক পাওয়া যাবে।</p>
    </div>

    <div class="footer-nav">
        <div class="nav-link active" onclick="switchPage('home', this)"><span class="nav-icon">🏠</span>হোম</div>
        <div class="nav-link" onclick="switchPage('home', this)"><span class="nav-icon">❤️</span>পছন্দ</div>
        <div class="nav-link" onclick="switchPage('links', this)"><span class="nav-icon">ℹ️</span>টিউটোরিয়াল</div>
        <div class="nav-link" onclick="switchPage('links', this)"><span class="nav-icon">🔗</span>লিংক</div>
        <div class="nav-link" onclick="switchPage('profile', this)"><span class="nav-icon">👤</span>প্রোফাইল</div>
    </div>

    <script>
        let tg = window.Telegram.WebApp;
        tg.expand();
        let user = tg.initDataUnsafe.user || {id: 0, first_name: 'Guest', username: 'user'};
        let currentP = 1;
        let adStep = 0;

        async function initApp() {
            try {
                const s = await (await fetch('/api/settings')).json();
                document.getElementById('web-title').innerText = s.name;
                document.getElementById('header-name').innerText = s.name;
                if(s.notice) {
                    const nb = document.getElementById('notice-bar');
                    nb.innerText = s.notice; nb.style.display = 'block';
                }
                loadSlider(s.slider_count || 6);
                loadPosts(1);
                document.getElementById('app-loader').style.display = 'none';
                document.getElementById('home-page').classList.remove('hidden');
            } catch(e) { document.getElementById('app-loader').innerText = "সার্ভার এরর!"; }
        }

        async function loadSlider(count) {
            const res = await fetch(`/api/slider?count=${count}`);
            const data = await res.json();
            const box = document.getElementById('slider-data');
            box.innerHTML = '';
            data.forEach(p => {
                box.innerHTML += `<div class="slide-item"><img src="${p.photo_url}"><div class="slide-cap">${p.title}</div></div>`;
            });
        }

        async function loadPosts(page) {
            currentP = page;
            const res = await fetch(`/api/posts?page=${page}`);
            const data = await res.json();
            const grid = document.getElementById('grid-data');
            grid.innerHTML = '';
            data.posts.forEach(p => {
                grid.innerHTML += `
                    <div class="post-card">
                        <img src="${p.photo_url}" class="post-img">
                        <div class="post-info">
                            <div class="post-title">${p.title}</div>
                            <div id="ads-st-${p._id}" style="font-size:11px;color:var(--pink);margin-bottom:8px;">UNLOCKED: 0/${data.steps} ADS</div>
                            <button class="unlock-btn" onclick="handleUnlock('${p._id}', ${data.steps})">🎬 UNLOCK VIDEO</button>
                        </div>
                    </div>`;
            });
            renderPG(data.total_pages, page);
        }

        function renderPG(total, current) {
            const ui = document.getElementById('pg-ui');
            ui.innerHTML = '';
            ui.innerHTML += `<button class="pg-node" ${current==1?'disabled':''} onclick="loadPosts(${current-1})">Prev</button>`;
            for(let i=1; i<=total; i++) {
                if(i==1 || i==total || (i>=current-1 && i<=current+1)) {
                    ui.innerHTML += `<button class="pg-node ${i==current?'active':''}" onclick="loadPosts(${i})">${i}</button>`;
                } else if(i==current-2 || i==current+2) {
                    ui.innerHTML += `<span style="color:#444;">...</span>`;
                }
            }
            ui.innerHTML += `<button class="pg-node" ${current==total?'disabled':''} onclick="loadPosts(${current+1})">Next</button>`;
        }

        async function handleUnlock(pid, target) {
            const s = await (await fetch('/api/sdks')).json();
            if(adStep < target) {
                if(s.length > 0) window.open(s[0].link, '_blank');
                adStep++;
                document.getElementById('ads-st-'+pid).innerText = `UNLOCKED: ${adStep}/${target} ADS`;
                fetch('/api/ad-click', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({user_id:user.id})});
            } else { alert("ভিডিও আনলক হয়েছে!"); adStep = 0; }
        }

        function switchPage(pageId, el) {
            document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
            el.classList.add('active');
            document.querySelectorAll('.container, #profile-page, #links-page').forEach(p => p.classList.add('hidden'));
            document.getElementById(pageId + '-page').classList.remove('hidden');
            if(pageId === 'profile') loadUserProfile();
            window.scrollTo(0,0);
        }

        async function loadUserProfile() {
            const res = await fetch(`/api/user/${user.id}`);
            const data = await res.json();
            document.getElementById('u-full-name').innerText = user.first_name;
            document.getElementById('u-handle').innerText = '@' + (user.username || 'user');
            document.getElementById('av-init').innerText = user.first_name[0].toUpperCase();
            document.getElementById('st-liked').innerText = data.liked || 0;
            document.getElementById('st-today').innerText = data.ads_today || 0;
        }

        initApp();
    </script>
</body>
</html>
"""

# ==================== এপিআই লজিক (Quart Async) ====================
app = Quart(__name__)
app = cors(app)

@app.route('/')
async def index():
    return await render_template_string(HTML_TEMPLATE)

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
    s_db = await db.settings.find_one({"id": "config"}) or {"steps": 3}
    return jsonify({"posts": posts, "total_pages": (total // limit) + (1 if total % limit > 0 else 0), "steps": s_db.get("steps", 3)})

@app.route('/api/slider')
async def get_slider():
    count = int(request.args.get('count', 6))
    posts = await db.posts.find().sort('_id', -1).limit(count).to_list(count)
    for p in posts: p['_id'] = str(p['_id'])
    return jsonify(posts)

@app.route('/api/user/<int:uid>')
async def get_user_data(uid):
    u = await db.users.find_one({"user_id": uid}) or {"ads_today": 0, "liked": 0}
    return jsonify(u)

@app.route('/api/ad-click', methods=['POST'])
async def ad_click():
    data = await request.json
    await db.users.update_one({"user_id": data['user_id']}, {"$inc": {"ads_today": 1}}, upsert=True)
    return jsonify({"ok": True})

@app.route('/api/sdks')
async def get_sdks():
    return jsonify(await db.sdks.find().to_list(20))

# ==================== টেলিগ্রাম বটের বিশাল লজিক ====================

@dp.message_handler(commands=['start'])
async def start_cmd(m: types.Message):
    # ইউজার রেজিস্টার
    await db.users.update_one({"user_id": m.from_user.id}, {"$set": {"name": m.from_user.full_name}}, upsert=True)
    
    # আপনার স্ক্রিনশটের হুবহু ডিজাইন
    caption = (
        "✨ **WELCOME TO VIRAL VIDEO BOT** ✨\n\n"
        "🔍 **আপনাকে অবশ্যই আমাদের সকল চ্যানেলে জয়েন করতে হবে ✅**\n\n"
        "আমাদের নিচের Channel গুলোতে ও ভিডিও দেওয়া হয়\n\n"
        "🎬 **ভিডিও দেখতে হলে অবশ্যই আপনাকে নিচের চ্যানেল গুলোতে Join করার পর [🎬 ভিডিও দেখুন] এ ক্লিক করে ভিডিও দেখতে পারবেন 👇**"
    )
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.row(types.InlineKeyboardButton("🎬 ভিডিও দেখুন", web_app=types.WebAppInfo(url=APP_URL)))
    
    channels = await db.channels.find().to_list(10)
    for c in channels:
        markup.add(types.InlineKeyboardButton(c['name'], url=c['link']))
    
    tuts = await db.tutorials.find().to_list(10)
    for t in tuts:
        markup.add(types.InlineKeyboardButton(f"ℹ️ {t['name']}", url=t['link']))

    try:
        await m.answer_photo(photo="https://telegra.ph/file/a8677c3e1c66288828b80.jpg", caption=caption, reply_markup=markup, parse_mode="Markdown")
    except:
        await m.answer(caption, reply_markup=markup, parse_mode="Markdown")

# এডমিন কমান্ডসমূহ
@dp.message_handler(commands=['post'], user_id=ADMIN_ID)
async def admin_post(m: types.Message):
    await m.answer("📝 টাইটেল দিন:"); await PostState.title.set()

@dp.message_handler(state=PostState.title)
async def admin_title(m: types.Message, state: FSMContext):
    await state.update_data(title=m.text); await m.answer("📸 ফটো পাঠান:"); await PostState.photo.set()

@dp.message_handler(content_types=['photo'], state=PostState.photo)
async def admin_photo(m: types.Message, state: FSMContext):
    file = await bot.get_file(m.photo[-1].file_id)
    url = f"https://api.telegram.org/file/bot{API_TOKEN}/{file.file_path}"
    await state.update_data(photo=url); await m.answer("🔗 ভিডিও লিংক/ফাইল পাঠান:"); await PostState.content.set()

@dp.message_handler(state=PostState.content, content_types=['any'])
async def admin_done(m: types.Message, state: FSMContext):
    data = await state.get_data()
    val = m.text or m.video.file_id or m.document.file_id
    await db.posts.insert_one({"title": data['title'], "photo_url": data['photo'], "content": val})
    await m.answer("✅ ভিডিও পোস্ট সফল হয়েছে!"); await state.finish()

@dp.message_handler(commands=['name'], user_id=ADMIN_ID)
async def admin_name(m: types.Message):
    name = m.get_args()
    await db.settings.update_one({"id": "config"}, {"$set": {"name": name}}, upsert=True)
    await m.answer(f"✅ অ্যাপ নাম সেট হয়েছে: {name}")

@dp.message_handler(commands=['notice'], user_id=ADMIN_ID)
async def admin_notice(m: types.Message):
    txt = m.get_args()
    await db.settings.update_one({"id": "config"}, {"$set": {"notice": txt}}, upsert=True)
    await m.answer("✅ নোটিশ আপডেট হয়েছে।")

@dp.message_handler(commands=['delnotice'], user_id=ADMIN_ID)
async def admin_del_notice(m: types.Message):
    await db.settings.update_one({"id": "config"}, {"$set": {"notice": ""}}, upsert=True)
    await m.answer("🗑 নোটিশ ডিলিট হয়েছে।")

@dp.message_handler(commands=['step'], user_id=ADMIN_ID)
async def admin_step(m: types.Message):
    v = int(m.get_args())
    await db.settings.update_one({"id": "config"}, {"$set": {"steps": v}}, upsert=True)
    await m.answer(f"⚙️ অ্যাড আনলক স্টেপ {v} এ সেট হয়েছে।")

@dp.message_handler(commands=['slidercount'], user_id=ADMIN_ID)
async def admin_slider(m: types.Message):
    v = int(m.get_args())
    await db.settings.update_one({"id": "config"}, {"$set": {"slider_count": v}}, upsert=True)
    await m.answer(f"✅ স্লাইডার সংখ্যা আপডেট হয়েছে।")

@dp.message_handler(commands=['addchannel'], user_id=ADMIN_ID)
async def admin_add_ch(m: types.Message):
    a = m.get_args().split(maxsplit=1)
    await db.channels.update_one({"name": a[0]}, {"$set": {"link": a[1]}}, upsert=True)
    await m.answer(f"✅ বাটন '{a[0]}' এড হয়েছে।")

@dp.message_handler(commands=['delchannel'], user_id=ADMIN_ID)
async def admin_del_ch(m: types.Message):
    await db.channels.delete_one({"name": m.get_args()})
    await m.answer("🗑 বাটন ডিলেট হয়েছে।")

@dp.message_handler(commands=['addtutorial'], user_id=ADMIN_ID)
async def admin_add_tut(m: types.Message):
    a = m.get_args().split(maxsplit=1)
    await db.tutorials.update_one({"name": a[0]}, {"$set": {"link": a[1]}}, upsert=True)
    await m.answer(f"✅ টিউটোরিয়াল '{a[0]}' এড হয়েছে।")

@dp.message_handler(commands=['deltutorial'], user_id=ADMIN_ID)
async def admin_del_tut(m: types.Message):
    await db.tutorials.delete_one({"name": m.get_args()})
    await m.answer("🗑 টিউটোরিয়াল ডিলেট হয়েছে।")

@dp.message_handler(commands=['sdk'], user_id=ADMIN_ID)
async def admin_sdk(m: types.Message):
    a = m.get_args().split()
    await db.sdks.update_one({"id": a[0]}, {"$set": {"link": a[1]}}, upsert=True)
    await m.answer(f"✅ SDK {a[0]} আপডেট হয়েছে।")

@dp.message_handler(commands=['deletep'], user_id=ADMIN_ID)
async def admin_delp(m: types.Message):
    await db.posts.delete_one({"title": m.get_args()})
    await m.answer("🗑 পোস্ট ডিলেট হয়েছে।")

@dp.message_handler(commands=['deleteall'], user_id=ADMIN_ID)
async def admin_clear(m: types.Message):
    await db.posts.delete_many({}); await db.users.delete_many({}); await m.answer("💥 সব মুছে ফেলা হয়েছে!")

# ==================== অটো-সেটআপ ও রানার ====================

async def setup_systems():
    # ১. ওয়েবহুক রিসেট
    await bot.delete_webhook()
    await asyncio.sleep(1)
    await bot.set_webhook(f"{APP_URL}/tg-webhook")
    # ২. মেনু বাটন সেট (আপনার লাল গোল চিহ্নিত বাটন)
    menu_btn = {"type": "web_app", "text": "🎬 ভিডিও দেখুন", "web_app": {"url": APP_URL}}
    requests.post(f"https://api.telegram.org/bot{API_TOKEN}/setChatMenuButton", json={"menu_button": menu_btn})

@app.before_serving
async def on_startup():
    asyncio.create_task(setup_systems())

@app.route('/tg-webhook', methods=['POST'])
async def tg_webhook_receiver():
    update_data = await request.json
    update = types.Update.to_object(update_data)
    Dispatcher.set_current(dp)
    Bot.set_current(bot)
    await dp.process_update(update)
    return "ok", 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
