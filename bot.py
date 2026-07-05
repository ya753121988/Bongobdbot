import logging
import asyncio
import threading
import json
import os
from flask import Flask, render_template_string, jsonify, request
from flask_cors import CORS
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

# --- CONFIGURATION ---
API_TOKEN = 'আপনার_বট_টোকেন'
MONGO_URL = 'আপনার_মংগোডিবি_ইউআরএল'
ADMIN_ID = 12345678 # আপনার টেলিগ্রাম আইডি
APP_URL = "https://your-app-link.vercel.app" # আপনার ডিপ্লয় করা লিংক

# --- DATABASE SETUP ---
client = AsyncIOMotorClient(MONGO_URL)
db = client['viral_video_complete_db']

# --- BOT SETUP ---
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

class PostState(StatesGroup):
    title = State()
    photo = State()
    content = State()

# --- MINI APP UI (HTML/CSS/JS) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>বাংলা ভাইরাল ভিডিও</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        body { background: #000; color: #fff; font-family: sans-serif; margin: 0; padding: 0; overflow-x: hidden; }
        .pink { color: #ff006e; }
        .page { display: none; padding: 15px; padding-bottom: 90px; }
        .active { display: block; }
        
        /* Profile Header Style */
        .profile-card { background: linear-gradient(180deg, #ff006e 0%, #000 100%); padding: 40px 20px; text-align: center; border-radius: 0 0 30px 30px; }
        .avatar { width: 75px; height: 75px; background: #fff; border-radius: 50%; margin: 0 auto 10px; display: flex; align-items: center; justify-content: center; color: #000; font-size: 28px; font-weight: bold; }
        .stats-row { display: flex; justify-content: space-around; background: #111; padding: 15px; border-radius: 15px; margin-top: 25px; border: 1px solid #222; }
        .stat-item { text-align: center; }
        .stat-num { color: #ff006e; font-size: 18px; font-weight: bold; }
        .stat-label { font-size: 10px; color: #777; text-transform: uppercase; margin-top: 3px; }

        /* Post Card Style */
        .post-card { background: #111; border-radius: 15px; margin-bottom: 20px; overflow: hidden; border: 1px solid #222; }
        .post-img { width: 100%; height: 210px; object-fit: cover; }
        .post-info { padding: 15px; }
        .post-title { font-size: 15px; font-weight: bold; margin-bottom: 12px; display: block; }
        .unlock-btn { background: #ff006e; color: #fff; border: none; width: 100%; padding: 13px; border-radius: 8px; font-weight: bold; cursor: pointer; text-transform: uppercase; }

        /* Bottom Nav Bar */
        .nav-bar { position: fixed; bottom: 0; width: 100%; background: #0a0a0a; display: flex; justify-content: space-around; padding: 12px 0; border-top: 1px solid #222; z-index: 1000; }
        .nav-item { color: #666; text-decoration: none; font-size: 10px; text-align: center; flex: 1; cursor: pointer; }
        .nav-item.active { color: #ff006e; }
        .nav-item i { font-size: 18px; display: block; margin-bottom: 4px; }
    </style>
</head>
<body>
    <!-- Home Page -->
    <div id="home" class="page active">
        <h3 class="pink" style="text-align:center;">বাংলা ভাইরাল ভিডিও</h3>
        <div id="posts-container"></div>
    </div>

    <!-- Profile Page -->
    <div id="profile" class="page">
        <div class="profile-card">
            <div class="avatar" id="avatar-init">TE</div>
            <h3 id="profile-name">USER</h3>
            <div id="profile-tag" style="color:#bbb; font-size:12px;">@username</div>
            
            <div class="stats-row">
                <div class="stat-item"><div class="stat-num" id="s-liked">0</div><div class="stat-label">Liked</div></div>
                <div class="stat-item"><div class="stat-num" id="s-today">0</div><div class="stat-label">Today Ads</div></div>
                <div class="stat-item"><div class="stat-num">30</div><div class="stat-label">Daily Limit</div></div>
            </div>
        </div>
    </div>

    <!-- Nav Bar -->
    <div class="nav-bar">
        <div class="nav-item active" onclick="switchPage('home', this)">🏠<br>হোম</div>
        <div class="nav-item" onclick="switchPage('home', this)">❤️<br>পছন্দের</div>
        <div class="nav-item" onclick="switchPage('home', this)">ℹ️<br>টিউটোরিয়াল</div>
        <div class="nav-item" onclick="switchPage('home', this)">🔗<br>লিংক</div>
        <div class="nav-item" onclick="switchPage('profile', this)">👤<br>প্রোফাইল</div>
    </div>

    <script>
        let tg = window.Telegram.WebApp;
        tg.expand();
        let user = tg.initDataUnsafe.user || {id: 0, first_name: 'Guest', username: 'guest'};
        let currentAds = 0;

        function switchPage(pageId, el) {
            document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
            document.getElementById(pageId).classList.add('active');
            document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
            el.classList.add('active');
            if(pageId === 'profile') loadProfile();
        }

        async function loadPosts() {
            const res = await fetch('/api/posts');
            const posts = await res.json();
            const set = await (await fetch('/api/settings')).json();
            const container = document.getElementById('posts-container');
            container.innerHTML = '';
            posts.forEach(p => {
                container.innerHTML += `
                    <div class="post-card">
                        <img src="${p.photo_url}" class="post-img">
                        <div class="post-info">
                            <span class="post-title">${p.title}</span>
                            <div style="color:#ff006e; font-size:12px; margin-bottom:6px;" id="stat-${p._id}">UNLOCK — 0/${set.steps} ADS</div>
                            <button class="unlock-btn" onclick="handleUnlock('${p._id}', ${set.steps})">UNLOCK — ভিডিও দেখুন</button>
                        </div>
                    </div>`;
            });
        }

        async function loadProfile() {
            const res = await fetch(`/api/user/${user.id}`);
            const data = await res.json();
            document.getElementById('profile-name').innerText = user.first_name;
            document.getElementById('profile-tag').innerText = '@' + (user.username || 'user');
            document.getElementById('avatar-init').innerText = user.first_name[0].toUpperCase();
            document.getElementById('s-today').innerText = data.ads_today || 0;
            document.getElementById('s-liked').innerText = data.liked || 0;
        }

        async function handleUnlock(pid, target) {
            const sdks = await (await fetch('/api/sdks')).json();
            if(currentAds < target) {
                if(sdks.length > 0) window.open(sdks[0].link, '_blank');
                currentAds++;
                document.getElementById('stat-'+pid).innerText = `UNLOCK — ${currentAds}/${target} ADS`;
                // Update DB
                fetch('/api/ad-click', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({user_id: user.id}) });
            } else {
                alert("ভিডিও আনলক হয়েছে!");
                currentAds = 0;
            }
        }
        loadPosts();
    </script>
</body>
</html>
"""

# --- FLASK API ---
app = Flask(__name__)
CORS(app)

@app.route('/')
def index(): return render_template_string(HTML_TEMPLATE)

@app.route('/api/posts')
async def get_posts():
    posts = await db.posts.find().to_list(100)
    for p in posts: p['_id'] = str(p['_id'])
    return jsonify(posts)

@app.route('/api/user/<int:uid>')
async def get_u(uid):
    u = await db.users.find_one({"user_id": uid}) or {"ads_today": 0, "liked": 0}
    return jsonify(u)

@app.route('/api/ad-click', methods=['POST'])
async def ad_c():
    uid = request.json['user_id']
    await db.users.update_one({"user_id": uid}, {"$inc": {"ads_today": 1}}, upsert=True)
    return jsonify({"ok": True})

@app.route('/api/sdks')
async def get_s(): return jsonify(await db.sdks.find().to_list(20))

@app.route('/api/settings')
async def get_st(): return jsonify(await db.settings.find_one({"id": "config"}) or {"steps": 3})

# --- BOT COMMANDS ---

@dp.message_handler(commands=['start'])
async def start(m: types.Message):
    # Register user in DB
    await db.users.update_one({"user_id": m.from_user.id}, {"$set": {"name": m.from_user.full_name}}, upsert=True)
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton("🎬 ভিডিও দেখুন (Mini App)", web_app=types.WebAppInfo(url=APP_URL)))
    
    # Dynamic Channels
    chs = await db.channels.find().to_list(50)
    for c in chs: markup.add(types.InlineKeyboardButton(c['name'], url=c['link']))
    
    # Dynamic Tutorials
    tuts = await db.tutorials.find().to_list(50)
    for t in tuts: markup.add(types.InlineKeyboardButton(f"ℹ️ {t['name']}", url=t['link']))

    welcome = "✨ **WELCOME TO VIRAL VIDEO BOT** ✨\n\nআপনাকে অবশ্যই আমাদের সকল চ্যানেলে জয়েন করতে হবে ✅"
    await m.answer_photo("https://telegra.ph/file/a8677c3e1c66288828b80.jpg", caption=welcome, reply_markup=markup, parse_mode="Markdown")

# Admin Management Commands
@dp.message_handler(commands=['addchannel'], user_id=ADMIN_ID)
async def add_ch(m: types.Message):
    args = m.get_args().split(maxsplit=1)
    await db.channels.update_one({"name": args[0]}, {"$set": {"link": args[1]}}, upsert=True)
    await m.answer("✅ চ্যানেল এড হয়েছে।")

@dp.message_handler(commands=['delchannel'], user_id=ADMIN_ID)
async def del_ch(m: types.Message):
    await db.channels.delete_one({"name": m.get_args()})
    await m.answer("🗑 ডিলেট হয়েছে।")

@dp.message_handler(commands=['addtutorial'], user_id=ADMIN_ID)
async def add_tut(m: types.Message):
    args = m.get_args().split(maxsplit=1)
    await db.tutorials.update_one({"name": args[0]}, {"$set": {"link": args[1]}}, upsert=True)
    await m.answer("✅ টিউটোরিয়াল এড হয়েছে।")

@dp.message_handler(commands=['deltutorial'], user_id=ADMIN_ID)
async def del_tut(m: types.Message):
    await db.tutorials.delete_one({"name": m.get_args()})
    await m.answer("🗑 টিউটোরিয়াল ডিলেট হয়েছে।")

@dp.message_handler(commands=['step'], user_id=ADMIN_ID)
async def set_step(m: types.Message):
    await db.settings.update_one({"id": "config"}, {"$set": {"steps": int(m.get_args())}}, upsert=True)
    await m.answer(f"⚙️ অ্যাড স্টেপ {m.get_args()} সেট হয়েছে।")

@dp.message_handler(commands=['sdk'], user_id=ADMIN_ID)
async def add_sdk(m: types.Message):
    args = m.get_args().split()
    await db.sdks.update_one({"id": args[0]}, {"$set": {"link": args[1]}}, upsert=True)
    await m.answer(f"✅ SDK {args[0]} আপডেট হয়েছে।")

@dp.message_handler(regexp=r'^/sdkd\d+', user_id=ADMIN_ID)
async def del_sdk(m: types.Message):
    await db.sdks.delete_one({"id": m.text[5:]})
    await m.answer("🗑 SDK ডিলেট হয়েছে।")

@dp.message_handler(commands=['post'], user_id=ADMIN_ID)
async def post_s(m: types.Message):
    await m.answer("📝 টাইটেল দিন:")
    await PostState.title.set()

@dp.message_handler(state=PostState.title)
async def post_t(m: types.Message, state: FSMContext):
    await state.update_data(title=m.text)
    await m.answer("📸 ফটো পাঠান:")
    await PostState.photo.set()

@dp.message_handler(content_types=['photo'], state=PostState.photo)
async def post_p(m: types.Message, state: FSMContext):
    file = await bot.get_file(m.photo[-1].file_id)
    url = f"https://api.telegram.org/file/bot{API_TOKEN}/{file.file_path}"
    await state.update_data(photo=url)
    await m.answer("🔗 ফাইল/লিংক দিন:")
    await PostState.content.set()

@dp.message_handler(state=PostState.content, content_types=['any'])
async def post_f(m: types.Message, state: FSMContext):
    data = await state.get_data()
    val = m.text or m.video.file_id or m.document.file_id
    await db.posts.insert_one({"title": data['title'], "photo_url": data['photo'], "content": val})
    await m.answer("✅ পোস্ট সফল!")
    await state.finish()

@dp.message_handler(commands=['deleteall'], user_id=ADMIN_ID)
async def clr(m: types.Message):
    await db.posts.delete_many({}); await db.channels.delete_many({}); await db.tutorials.delete_many({}); await db.sdks.delete_many({})
    await m.answer("💥 সব মুছে ফেলা হয়েছে।")

@dp.message_handler(commands=['deletep'], user_id=ADMIN_ID)
async def delp(m: types.Message):
    await db.posts.delete_one({"title": m.get_args()})
    await m.answer("🗑 পোস্ট ডিলেট হয়েছে।")

# --- RUNNER ---
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))).start()
    executor.start_polling(dp, skip_updates=True)
