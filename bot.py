import logging
import asyncio
import threading
from flask import Flask, render_template_string, jsonify
from flask_cors import CORS
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
from motor.motor_asyncio import AsyncIOMotorClient
import os

# --- কনফিগারেশন (আপনার তথ্য দিয়ে পরিবর্তন করুন) ---
API_TOKEN = 'আপনার_বট_টোকেন'
MONGO_URL = 'আপনার_মংগোডিবি_ইউআরএল'
ADMIN_ID = 12345678  # আপনার টেলিগ্রাম আইডি
APP_URL = "https://your-app-name.onrender.com" # রেন্ডার বা কোয়েব এর হোস্ট লিংক

# --- ডাটাবেস কানেকশন ---
client = AsyncIOMotorClient(MONGO_URL)
db = client['viral_video_complete_db']

# --- বট সেটআপ ---
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

class PostState(StatesGroup):
    title = State()
    photo = State()
    content = State()

# --- মিনি অ্যাপ (ওয়েব) ডিজাইন ও লজিক ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>বাংলা ভাইরাল ভিডিও</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        body { background: #000; color: #fff; font-family: 'Segoe UI', sans-serif; margin: 0; padding: 10px; padding-bottom: 90px; }
        .header { text-align: center; padding: 15px; border-bottom: 1px solid #222; position: sticky; top: 0; background: #000; z-index: 100; }
        .header h3 { margin: 0; color: #ff006e; }
        
        .post-card { background: #121212; border-radius: 15px; margin-bottom: 20px; overflow: hidden; border: 1px solid #333; box-shadow: 0 4px 15px rgba(255,0,110,0.1); }
        .post-img { width: 100%; height: 230px; object-fit: cover; }
        .post-info { padding: 15px; }
        .post-title { font-size: 16px; font-weight: bold; line-height: 1.4; display: block; margin-bottom: 12px; }
        
        .status-box { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
        .status-text { color: #ff006e; font-size: 13px; font-weight: bold; }
        .unlock-btn { background: linear-gradient(45deg, #ff006e, #ff5c9d); color: #fff; border: none; width: 100%; padding: 14px; border-radius: 10px; font-weight: bold; cursor: pointer; font-size: 14px; transition: 0.3s; }
        .unlock-btn:active { transform: scale(0.95); }

        /* ফুটার মেনু ডিজাইন (আপনার স্ক্রিনশটের মতো) */
        .footer-menu { position: fixed; bottom: 0; left: 0; width: 100%; background: #0a0a0a; display: flex; justify-content: space-around; padding: 12px 0; border-top: 1px solid #222; }
        .menu-item { color: #888; text-decoration: none; font-size: 11px; text-align: center; flex: 1; }
        .menu-item i { font-size: 20px; margin-bottom: 4px; display: block; }
        .menu-item.active { color: #ff006e; }
        
        #loading { text-align: center; padding: 50px; color: #ff006e; }
    </style>
</head>
<body>
    <div class="header"><h3>বাংলা ভাইরাল ভিডিও</h3></div>
    
    <div id="loading">লোড হচ্ছে...</div>
    <div id="posts-container"></div>

    <!-- ফুটার মেনু -->
    <div class="footer-menu">
        <a href="#" class="menu-item active">🏠<br>হোম</a>
        <a href="#" class="menu-item">❤️<br>পছন্দের</a>
        <a href="#" class="menu-item">ℹ️<br>টিউটোরিয়াল</a>
        <a href="#" class="menu-item">🔗<br>লিংক</a>
        <a href="#" class="menu-item">👤<br>প্রোফাইল</a>
    </div>

    <script>
        let tg = window.Telegram.WebApp;
        tg.expand();
        let currentAds = 0;

        async function init() {
            try {
                const [postsReq, settingsReq, sdksReq] = await Promise.all([
                    fetch('/api/posts'), fetch('/api/settings'), fetch('/api/sdks')
                ]);
                
                const posts = await postsReq.json();
                const settings = await settingsReq.json();
                const sdks = await sdksReq.json();
                
                document.getElementById('loading').style.display = 'none';
                const container = document.getElementById('posts-container');

                if(posts.length === 0) {
                    container.innerHTML = '<p style="text-align:center; padding:20px;">কোন ভিডিও নেই!</p>';
                    return;
                }

                posts.forEach(post => {
                    const card = document.createElement('div');
                    card.className = 'post-card';
                    card.innerHTML = `
                        <img src="${post.photo_url}" class="post-img">
                        <div class="post-info">
                            <span class="post-title">${post.title}</span>
                            <div class="status-box">
                                <div class="status-text" id="status-${post._id}">UNLOCK — 0/${settings.steps} ADS</div>
                            </div>
                            <button class="unlock-btn" onclick="handleUnlock('${post._id}', ${settings.steps}, ${JSON.stringify(sdks).replace(/"/g, '&quot;')})">🎬 UNLOCK — ভিডিও দেখুন</button>
                        </div>
                    `;
                    container.appendChild(card);
                });
            } catch (err) {
                document.getElementById('loading').innerText = "সার্ভার এরর!";
            }
        }

        function handleUnlock(postId, target, sdks) {
            if (currentAds < target) {
                if (sdks.length === 0) { alert("অ্যাড লিংক নেই!"); return; }
                const randomAd = sdks[Math.floor(Math.random() * sdks.length)].link;
                window.open(randomAd, '_blank');
                currentAds++;
                document.getElementById('status-'+postId).innerText = `UNLOCK — ${currentAds}/${target} ADS`;
            } else {
                alert("ভিডিও আনলক হয়েছে! এখন আপনি দেখতে পারবেন।");
                // এখানে ভিডিও ফাইল আইডি বা ডিরেক্ট লিংক দিয়ে প্লে করার ফাংশন যোগ করতে পারেন
                currentAds = 0;
            }
        }
        init();
    </script>
</body>
</html>
"""

# --- ফ্লাস্ক এপিআই সার্ভার ---
app = Flask(__name__)
CORS(app)

@app.route('/')
def index(): return render_template_string(HTML_TEMPLATE)

@app.route('/api/posts')
async def get_posts():
    posts = await db.posts.find().to_list(length=100)
    for p in posts: p['_id'] = str(p['_id'])
    return jsonify(posts)

@app.route('/api/settings')
async def get_settings():
    s = await db.settings.find_one({"id": "config"}) or {"steps": 3}
    return jsonify({"steps": s.get("steps", 3)})

@app.route('/api/sdks')
async def get_sdks():
    return jsonify(await db.sdks.find().to_list(length=100))

# --- বটের কমান্ডসমূহ (সব আলাদা কমান্ড) ---

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    # মেইন মিনি অ্যাপ বাটন
    markup.add(types.InlineKeyboardButton("🎬 ভিডিও দেখুন (Mini App)", web_app=types.WebAppInfo(url=APP_URL)))
    
    # ডাইনামিক চ্যানেল বাটন
    channels = await db.channels.find().to_list(length=100)
    if channels:
        markup.add(*[types.InlineKeyboardButton(c['name'], url=c['link']) for c in channels])
    
    # ডাইনামিক টিউটোরিয়াল বাটন
    tutorials = await db.tutorials.find().to_list(length=100)
    if tutorials:
        markup.add(*[types.InlineKeyboardButton(f"ℹ️ {t['name']}", url=t['link']) for t in tutorials])
    
    welcome_text = "✨ **WELCOME TO VIRAL VIDEO BOT** ✨\n\nভিডিও দেখতে অবশ্যই আমাদের সকল চ্যানেলে জয়েন করুন।\n\nনিচের বাটন থেকে ভিডিও দেখুন 👇"
    await message.answer_photo(photo="https://telegra.ph/file/a8677c3e1c66288828b80.jpg", caption=welcome_text, reply_markup=markup, parse_mode="Markdown")

# --- কমান্ড লজিক (Add/Delete/Management) ---

@dp.message_handler(commands=['addchannel'], user_id=ADMIN_ID)
async def add_channel(message: types.Message):
    args = message.get_args().split(maxsplit=1)
    if len(args) < 2: return await message.answer("ব্যবহার: /addchannel নাম লিঙ্ক")
    await db.channels.update_one({"name": args[0]}, {"$set": {"link": args[1]}}, upsert=True)
    await message.answer(f"✅ চ্যানেল বাটন '{args[0]}' এড হয়েছে।")

@dp.message_handler(commands=['delchannel'], user_id=ADMIN_ID)
async def del_channel(message: types.Message):
    name = message.get_args()
    await db.channels.delete_one({"name": name})
    await message.answer(f"🗑 বাটন '{name}' ডিলেট হয়েছে।")

@dp.message_handler(commands=['addtutorial'], user_id=ADMIN_ID)
async def add_tutorial(message: types.Message):
    args = message.get_args().split(maxsplit=1)
    if len(args) < 2: return await message.answer("ব্যবহার: /addtutorial নাম লিঙ্ক")
    await db.tutorials.update_one({"name": args[0]}, {"$set": {"link": args[1]}}, upsert=True)
    await message.answer(f"✅ টিউটোরিয়াল '{args[0]}' এড হয়েছে।")

@dp.message_handler(commands=['deltutorial'], user_id=ADMIN_ID)
async def del_tutorial(message: types.Message):
    name = message.get_args()
    await db.tutorials.delete_one({"name": name})
    await message.answer(f"🗑 টিউটোরিয়াল '{name}' ডিলেট হয়েছে।")

@dp.message_handler(commands=['step'], user_id=ADMIN_ID)
async def set_step(message: types.Message):
    num = message.get_args()
    if not num: return await message.answer("ব্যবহার: /step 3")
    await db.settings.update_one({"id": "config"}, {"$set": {"steps": int(num)}}, upsert=True)
    await message.answer(f"⚙️ আনলক স্টেপ {num} এ সেট করা হয়েছে।")

@dp.message_handler(commands=['sdk'], user_id=ADMIN_ID)
async def add_sdk(message: types.Message):
    args = message.get_args().split(maxsplit=1)
    if len(args) < 2: return await message.answer("ব্যবহার: /sdk 1 লিঙ্ক")
    await db.sdks.update_one({"id": args[0]}, {"$set": {"link": args[1]}}, upsert=True)
    await message.answer(f"✅ SDK {args[0]} লিঙ্ক এড হয়েছে।")

@dp.message_handler(regexp=r'^/sdkd\d+', user_id=ADMIN_ID)
async def delete_sdk(message: types.Message):
    sdk_id = message.text.replace('/sdkd', '')
    await db.sdks.delete_one({"id": sdk_id})
    await message.answer(f"🗑 SDK {sdk_id} ডিলেট হয়েছে।")

@dp.message_handler(commands=['post'], user_id=ADMIN_ID)
async def post_start(message: types.Message):
    await message.answer("📝 পোস্টের নাম (Title) দিন:")
    await PostState.title.set()

@dp.message_handler(state=PostState.title)
async def post_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("📸 এখন সরাসরি একটি ফটো (Photo) পাঠান:")
    await PostState.photo.set()

@dp.message_handler(content_types=['photo'], state=PostState.photo)
async def post_photo(message: types.Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    file = await bot.get_file(photo_id)
    # টেলিগ্রাম ফাইল আইডি থেকে পাবলিক ইউআরএল জেনারেট
    photo_url = f"https://api.telegram.org/file/bot{API_TOKEN}/{file.file_path}"
    await state.update_data(photo_url=photo_url)
    await message.answer("🔗 এবার ভিডিও ফাইল অথবা স্ট্রিম লিংক দিন:")
    await PostState.content.set()

@dp.message_handler(content_types=['text', 'video', 'document'], state=PostState.content)
async def post_done(message: types.Message, state: FSMContext):
    data = await state.get_data()
    content = message.text if message.text else (message.video.file_id if message.video else message.document.file_id)
    await db.posts.insert_one({
        "title": data['title'],
        "photo_url": data['photo_url'],
        "content": content,
        "type": message.content_type
    })
    await message.answer("✅ সফলভাবে ভিডিও পোস্ট হয়েছে!")
    await state.finish()

@dp.message_handler(commands=['deleteall'], user_id=ADMIN_ID)
async def del_everything(message: types.Message):
    await db.posts.delete_many({})
    await db.channels.delete_many({})
    await db.tutorials.delete_many({})
    await db.sdks.delete_many({})
    await message.answer("💥 বটের সকল পোস্ট, বাটন ও ডাটা ক্লিন করা হয়েছে!")

@dp.message_handler(commands=['deletep'], user_id=ADMIN_ID)
async def del_one_post(message: types.Message):
    title = message.get_args()
    if not title: return await message.answer("ব্যবহার: /deletep টাইটেল_নাম")
    await db.posts.delete_one({"title": title})
    await message.answer(f"🗑 '{title}' পোস্টটি ডিলিট হয়েছে।")

# --- রানার ---
def start_web():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    threading.Thread(target=start_web).start()
    executor.start_polling(dp, skip_updates=True)
