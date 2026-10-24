cat << 'EOF' > pub.py
import time, json, urllib.request, ssl, urllib.error

TOKEN = '8619621181:AAHBXbxDvHcIcCzobF8av2UUTdFspUCa9Lk'
KEY = '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'

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# تعليمات الذكاء الاصطناعي لتقديم الخدمات العامة
SYSTEM_PROMPT = (
    "أنت مساعد ذكي احترافي مخصص لتقديم 'الخدمات الرقمية العامة والذكية'. "
    "تتضمن مهامك الرئيسية: "
    "1. صياغة الخطابات والرسائل والترجمة الدقيقة بين اللغات. "
    "2. حل المشكلات البرمجية (مثل بايثون، لينكس، وغيرها) وكتابة وتصحيح الأكواد. "
    "3. تلخيص النصوص والكتب والمقالات وتنسيق النقاط. "
    "4. تقديم أفكار تسويقية ومحتوى إبداعي وتنسيق الجداول. "
    "اجعل ردودك دائماً مرتبة، دقيقة، ومباشرة مع استخدام التنسيق الجيد والرموز التعبيرية المناسبة."
)

try:
    urllib.request.urlopen(f'https://api.telegram.org/bot{TOKEN}/deleteWebhook?drop_pending_updates=true', context=ctx)
except:
    pass

def get_free_model():
    try:
        req = urllib.request.Request('https://openrouter.ai/api/v1/models', headers={'Authorization': f'Bearer {KEY}'})
        with urllib.request.urlopen(req, context=ctx, timeout=10) as r:
            data = json.loads(r.read().decode())
            for m in data.get('data', []):
                mid = m.get('id', '')
                if ':free' in mid:
                    print(f'✨ تم اختيار نموذج مجاني تلقائياً: {mid}')
                    return mid
    except Exception as e:
        print(f'⚠️ تعذر جلب القائمة تلقائياً: {e}')
    return 'google/gemini-flash-1.5-8b:free'

MODEL = get_free_model()
print(f'🚀 بوت الخدمات العامة يعمل الآن بنجاح بالنموذج: {MODEL}')

offset = 0
while True:
    try:
        url = f'https://api.telegram.org/bot{TOKEN}/getUpdates?offset={offset}&timeout=30'
        with urllib.request.urlopen(url, context=ctx, timeout=35) as r:
            res = json.loads(r.read().decode())
            for u in res.get('result', []):
                offset = u['update_id'] + 1
                msg = u.get('message')
                if msg and 'text' in msg:
                    chat_id = msg['chat']['id']
                    text = msg['text'].strip()
                    print(f'📩 طلب من مستخدم: {text}')

                    # أمر البداية والتريحب
                    if text.startswith('/start'):
                        reply = (
                            "👋 أهلاً بك في بوت الخدمات الرقمية الذكية!\n\n"
                            "أنا مساعدك الذكي لتنفيذ جميع طلباتك وخدماتك الرقمية 🚀\n\n"
                            "💡 **أمثلة لما يمكنني مساعدتك به:**\n"
                            "▫️ صياغة الخطابات والترجمة وتعديل النصوص.\n"
                            "▫️ كتابة وفحص الأكواد البرمجية (Python, Shell, C++...).\n"
                            "▫️ تلخيص المقالات والتحليل وتنسيق البيانات.\n"
                            "▫️ التخطيط، كتابة المحتوى والأفكار التسويقية.\n\n"
                            "اكتب طلبك مباشرة في الشات وسأقوم بتنفيذه فوراً، أو أرسل /services لراية قائمة الخدمات!"
                        )
                    # قائمة الخدمات
                    elif text.startswith('/services') or text.startswith('/help'):
                        reply = (
                            "🛠️ **قائمة الخدمات المتاحة:**\n\n"
                            "1️⃣ **الخدمات الكتابية:** (ترجمة، إعادة صياغة، كتابة خطابات رسمية، تلخيص).\n"
                            "2️⃣ **الخدمات البرمجية:** (حل أخطاء الأكواد، كتابة سكربتات، شرح مفاهيم).\n"
                            "3️⃣ **إدارة المحتوى:** (أفكار بوستات، إعلانات، خطط عمل).\n"
                            "4️⃣ **الاستشارات العامة:** الإجابة على أي سؤال تقني أو عام.\n\n"
                            "👉 فقط اكتب ما تحتاجه بالتفصيل وسيتم الرد عليك فورا!"
                        )
                    else:
                        print('🧠 جاري معالجة الطلب عبر الذكاء الاصطناعي...')
                        try:
                            payload = {
                                'model': MODEL,
                                'messages': [
                                    {'role': 'system', 'content': SYSTEM_PROMPT},
                                    {'role': 'user', 'content': text}
                                ]
                            }
                            req_ai = urllib.request.Request(
                                'https://openrouter.ai/api/v1/chat/completions',
                                data=json.dumps(payload).encode(),
                                headers={'Authorization': f'Bearer {KEY}', 'Content-Type': 'application/json'},
                                method='POST'
                            )
                            with urllib.request.urlopen(req_ai, context=ctx) as ra:
                                reply = json.loads(ra.read().decode())['choices'][0]['message']['content']
                        except urllib.error.HTTPError as he:
                            err_detail = he.read().decode()
                            print(f'❌ تفاصيل خطأ OpenRouter: {err_detail}')
                            reply = f'عذراً، حدث خطأ أثناء تنفيذ الطلب. يرجى المحاولة لاحقاً.'
                        except Exception as ai_err:
                            print(f'❌ خطأ عام: {ai_err}')
                            reply = f'عذراً، حدث خطأ غير متوقع: {ai_err}'

                    # إرسال الرد إلى تيليجرام
                    try:
                        urllib.request.urlopen(
                            urllib.request.Request(
                                f'https://api.telegram.org/bot{TOKEN}/sendMessage',
                                data=json.dumps({'chat_id': chat_id, 'text': reply, 'parse_mode': 'Markdown'}).encode(),
                                headers={'Content-Type': 'application/json'},
                                method='POST'
                            ),
                            context=ctx
                        )
                        print('✅ تم تنفيذ الخدمة وإرسال الرد بنجاح!')
                    except Exception as tg_err:
                        # في حال وجود خطأ في تنسيق الماركداون يتم الإرسال كنص عادي
                        urllib.request.urlopen(
                            urllib.request.Request(
                                f'https://api.telegram.org/bot{TOKEN}/sendMessage',
                                data=json.dumps({'chat_id': chat_id, 'text': reply}).encode(),
                                headers={'Content-Type': 'application/json'},
                                method='POST'
                            ),
                            context=ctx
                        )
                        print(f'✅ تم الإرسال (كنص عادي): {tg_err}')

    except Exception as e:
        print(f'❌ خطأ رئيسي: {e}')
        time.sleep(2)
EOF
