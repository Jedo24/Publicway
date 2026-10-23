import os
import logging
import json
import urllib.request
import ssl
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)
from pypdf import PdfReader

# --- الإعدادات الأساسية ---
TELEGRAM_BOT_TOKEN = "8619621181:AAHBXbxDvHcIcCzobF8av2UUTdFspUCa9Lk"
import os

# اجعل الكود يسحب المفتاح من بيئة السيرفر بأمان
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")


# إعداد السجلات
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

user_states = {}

# --- دالة الاتصال المباشر بـ Groq AI ---
def call_groq_ai(prompt_text: str) -> str:
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY.strip()}",
        "Content-Type": "application/json"
    }
    payload = {
model="llama-3.1-8b-instant"

        "messages": [{"role": "user", "content": prompt_text}],
        "temperature": 0.7
    }
    
    # تجاوز فحص الشهادات لتجنب مشاكل SSL على بيئة a-Shell
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    try:
        req = urllib.request.Request(
            url, 
            data=json.dumps(payload).encode('utf-8'), 
            headers=headers, 
            method='POST'
        )
        with urllib.request.urlopen(req, context=ctx) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            return res_data['choices'][0]['message']['content']
    except Exception as e:
        logger.error(f"Groq API Error: {e}")
        return f"عذراً، حدث خطأ في الذكاء الاصطناعي:\n`{e}`"

def analyze_cv_ai(cv_text: str) -> str:
    prompt = (
        "أنت مستشار توظيف خبير. قم بتحليل السيرة الذاتية التالية بعناية، ثم اعرض:\n"
        "1. تقييم عام ونقاط القوة والضعف.\n"
        "2. أبرز المهارات المستخرجة.\n"
        "3. اقتراح 3 مسميات وظيفية تناسب هذه الخبرة.\n"
        "4. صياغة موجزة لرسالة تقديم (Cover Letter) احترافية.\n\n"
        f"السيرة الذاتية:\n{cv_text}"
    )
    return call_groq_ai(prompt)

def summarize_text_ai(text: str) -> str:
    prompt = (
        "قم بتلخيص النص التالي بأسلوب احترافي، منظم في نقاط رئيسية، "
        "مع إبراز أهم الأفكار والدروس المستفادة:\n\n"
        f"{text}"
    )
    return call_groq_ai(prompt)

def explain_concept_ai(concept: str) -> str:
    prompt = (
        "اشرح المفهوم أو السؤال التالي بطريقة مبسطة، واضحة، مدعومة بأمثلة عملية:\n\n"
        f"{concept}"
    )
    return call_groq_ai(prompt)


# --- معالجات تيليجرام ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💼 تحليل السيرة الذاتية واقتراح الوظائف", callback_data="mode_cv")],
        [InlineKeyboardButton("📚 تلخيص كتاب أو كتيب", callback_data="mode_summarize")],
        [InlineKeyboardButton("🔍 شرح مفهوم أو سؤال علمي/تقني", callback_data="mode_explain")],
        [InlineKeyboardButton("📄 استخراج نص من PDF", callback_data="mode_extract")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_message = (
        "أهلاً بك في بوت الخدمات الرقمية الذكية! 🤖✨\n\n"
        "اختر الخدمة التي ترغب بها من القائمة أدناه:"
    )
    
    if update.message:
        await update.message.reply_text(welcome_message, reply_markup=reply_markup)
    else:
        await update.callback_query.message.reply_text(welcome_message, reply_markup=reply_markup)


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    if query.data == "mode_cv":
        user_states[user_id] = "cv"
        await query.edit_message_text(
            "ممتاز! 💼\nالرجاء إرسال سيرتك الذاتية (ملف PDF) وسأقوم بتحليلها واقتراح الوظائف المناسبة لك."
        )
    elif query.data == "mode_summarize":
        user_states[user_id] = "summarize"
        await query.edit_message_text(
            "رائع! 📚\nأرسل لي نص الكتيب أو المقال، أو ارفع ملف الـ PDF المراد تلخيصه."
        )
    elif query.data == "mode_explain":
        user_states[user_id] = "explain"
        await query.edit_message_text(
            "أهلاً بك! 🔍\nاكتب المفهوم أو السؤال الذي تريدني أن أشرحه لك بشكل مبسط."
        )
    elif query.data == "mode_extract":
        user_states[user_id] = "extract"
        await query.edit_message_text(
            "أرسل ملف الـ PDF وسأستخرج لك كل النصوص الموجودة فيه."
        )


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    current_mode = user_states.get(user_id, "extract")
    document = update.message.document
    
    if not document.file_name.lower().endswith('.pdf'):
        await update.message.reply_text("عذراً، يرجى إرسال ملف بصيغة PDF فقط.")
        return
        
    status_msg = await update.message.reply_text("⏳ جاري تنزيل الملف وقراءته...")
    
    file = await context.bot.get_file(document.file_id)
    file_path = f"temp_{user_id}_{document.file_name}"
    await file.download_to_drive(file_path)
    
    extracted_text = ""
    try:
        reader = PdfReader(file_path)
        for page in reader.pages:
            text = page.extract_text()
            if text:
                extracted_text += text + "\n"
    except Exception as e:
        logger.error(f"Error reading PDF: {e}")
        await status_msg.edit_text("حدث خطأ أثناء قراءة الملف. تأكد أنه صالح وليس تالفاً.")
        if os.path.exists(file_path):
            os.remove(file_path)
        return
        
    if os.path.exists(file_path):
        os.remove(file_path)
        
    if not extracted_text.strip():
        await status_msg.edit_text("لم يتم العثور على نص واضح داخل هذا الـ PDF.")
        return

    await status_msg.edit_text("🧠 جاري معالجة البيانات بالذكاء الاصطناعي...")

    if current_mode == "cv":
        result = analyze_cv_ai(extracted_text)
    elif current_mode == "summarize":
        result = summarize_text_ai(extracted_text)
    else:
        result = f"📄 **النص المستخرج من الملف:**\n\n{extracted_text[:3500]}"

    if len(result) > 4000:
        for i in range(0, len(result), 4000):
            await update.message.reply_text(result[i:i+4000])
    else:
        await update.message.reply_text(result)
        
    await start(update, context)


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    current_mode = user_states.get(user_id, "explain")
    text_input = update.message.text
    
    if current_mode == "explain":
        status_msg = await update.message.reply_text("🔍 جاري إعداد الشرح المبسط...")
        result = explain_concept_ai(text_input)
    elif current_mode == "summarize":
        status_msg = await update.message.reply_text("📚 جاري تلخيص النص...")
        result = summarize_text_ai(text_input)
    else:
        status_msg = await update.message.reply_text("🤖 جاري المعالجة...")
        result = explain_concept_ai(text_input)
        
    await status_msg.edit_text(result)
    await start(update, context)


if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    print("🚀 البوت يعمل الآن بكامل الطاقة!")
    app.run_polling()
