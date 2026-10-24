cat << 'EOF' > pub.py
import time, json, urllib.request, ssl, urllib.error, os

TOKEN = '8619621181:AAHBXbxDvHcIcCzobF8av2UUTdFspUCa9Lk'
KEY = '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'

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# تعليمات الذكاء الاصطناعي لتحليل النصوص وتغيير الصيغ والخدمات العامة
SYSTEM_PROMPT = (
    "أنت مساعد ذكي واحترافي لتقديم الخدمات الرقمية المتقدمة. "
    "مهمتك تشمل: "
    "1. تحليل النصوص، استخراج الأفكار الرئيسية، والتلخيص الدقيق. "
    "2. تغيير صيغة النصوص (إعادة صياغة احترافية، تحويل الأسلوب إلى رسمي، أكاديمي، أو إبداعي). "
    "3. الترجمة الفورية وتصحيح الأخطاء اللغوية والنحوية. "
    "4. المساعدة في الأكواد البرمجية والتخطيط التقني. "
    "اجعل ردودك دائماً مرتبة وواضحة ومنسقة."
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
print(f'🚀 بوت الخدمات العامة وتحميل الملفات يعمل الآن بالنموذج: {MODEL}')

# دالة إرسال الملفات عبر تيليجرام
def send_telegram_document(chat_id, file_path, caption=""):
    try:
        boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
        data = []
        data.append(f'--{boundary}\r\n'.encode())
        data.append(f'Content-Disposition: form-data; name="chat_id"\r\n\r\n{chat_id}\r\n'.encode())
        if caption:
            data.append(f'--{boundary}\r\n'.encode())
            data.append(f'Content-Disposition: form-data; name="caption"\r\n\r\n{caption}\r\n'.encode())
        
        filename = os.path.basename(file_path)
        with open(file_path, 'rb') as f:
            file_content = f.read()
        
        data.append(f'--{boundary}\r\n'.encode())
        data.append(f'Content-Disposition: form-data; name="document"; filename="{filename}"\r\n'.encode())
        data.append(b'Content-Type: application/octet-stream\r\n\r\n')
        data.append(file_content)
        data.append(f'\r\n--{boundary}--\r\n'.encode())
        
        body = b''.join(data)
        headers = {'Content-Type': f'multipart/form-data; boundary={boundary}'}
        req = urllib.request.Request(f'https://api.telegram.org/bot{TOKEN}/sendDocument', data=body, headers=headers, method='POST')
        with urllib.request.urlopen(req, context=ctx) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        print(f'❌ خطأ في إرسال الملف: {e}')
        return None

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
                    print(f'📩 طلب وارد: {text}')

                    # أمر البداية
                    if text.startswith('/start'):
                        reply = (
                            "👋 أهلاً بك في بوت الخدمات الذكية الشامل!\n\n"
                            "🛠️ **ما يمكنني فعله لأجلك:**\n"
                            "▫️ **تحليل وتغيير الصيغة:** تحليل النصوص، إعادة صياغتها، والتلخيص.\n"
                            "▫️ **تحميل الملفات:** أرسل الأمر `/download <الرابط>` لتحميل أي ملف من الإنترنت وإرساله لك فوراً.\n"
                            "▫️ **الخدمات العامة والبرمجية:** الإجابة على الاستفسارات وحل الأكواد.\n\n"
                            "فقط أرسل طلبك أو رابط التحميل لنبدأ العمل!"
                        )
                        urllib.request.urlopen(
                            urllib.request.Request(
                                f'https://api.telegram.org/bot{TOKEN}/sendMessage',
                                data=json.dumps({'chat_id': chat_id, 'text': reply}).encode(),
                                headers={'Content-Type': 'application/json'},
                                method='POST'
                            ),
                            context=ctx
                        )

                    # خدمة تحميل الملفات من الإنترنت
                    elif text.startswith('/download '):
                        file_url = text.replace('/download', '').strip()
                        print(f'📥 جاري تحميل الملف من الرابط: {file_url}')
                        
                        # إرسال رسالة انتظار للمستخدم
                        urllib.request.urlopen(
                            urllib.request.Request(
                                f'https://api.telegram.org/bot{TOKEN}/sendMessage',
                                data=json.dumps({'chat_id': chat_id, 'text': '⏳ جاري تحميل الملف من الإنترنت، ثوانٍ معدودة...'}).encode(),
                                headers={'Content-Type': 'application/json'},
                                method='POST'
                            ),
                            context=ctx
                        )
                        
                        try:
                            # تحميل الملف محلياً
                            local_filename = file_url.split('/')[-1].split('?')[0]
                            if not local_filename:
                                local_filename = "downloaded_file.bin"
                            
                            req_file = urllib.request.Request(file_url, headers={'User-Agent': 'Mozilla/5.0'})
                            with urllib.request.urlopen(req_file, context=ctx, timeout=30) as response, open(local_filename, 'wb') as out_file:
                                out_file.write(response.read())
                            
                            print(f'✅ تم تحميل الملف محلياً باسم: {local_filename}')
                            
                            # إرسال الملف إلى المستخدم عبر تيليجرام
                            send_telegram_document(chat_id, local_filename, caption=f"📁 تم التحميل بنجاح من:\n{file_url}")
                            
                            # حذف الملف من السيرفر بعد الإرسال لتوفير المساحة
                            if os.path.exists(local_filename):
                                os.remove(local_filename)
                                
                        except Exception as dl_err:
                            print(f'❌ خطأ في التحميل: {dl_err}')
                            err_msg = f'⚠️ عذراً، تعذر تحميل الملف من الرابط المحدد. الخطأ: {dl_err}'
                            urllib.request.urlopen(
                                urllib.request.Request(
                                    f'https://api.telegram.org/bot{TOKEN}/sendMessage',
                                    data=json.dumps({'chat_id': chat_id, 'text': err_msg}).encode(),
                                    headers={'Content-Type': 'application/json'},
                                    method='POST'
                                ),
                                context=ctx
                            )

                    # الخدمات النصية والتحليل وتغيير الصيغة عبر الذكاء الاصطناعي
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
                        except Exception as ai_err:
                            print(f'❌ خطأ الذكاء الاصطناعي: {ai_err}')
                            reply = f'عذراً، حدث خطأ أثناء معالجة طلبك: {ai_err}'

                        # إرسال الرد النصي
                        try:
                            urllib.request.urlopen(
                                urllib.request.Request(
                                    f'https://api.telegram.org/bot{TOKEN}/sendMessage',
                                    data=json.dumps({'chat_id': chat_id, 'text': reply}).encode(),
                                    headers={'Content-Type': 'application/json'},
                                    method='POST'
                                ),
                                context=ctx
                            )
                            print('✅ تم الرد على النص بنجاح!')
                        except Exception as tg_err:
                            print(f'❌ خطأ إرسال الرد: {tg_err}')

    except Exception as e:
        print(f'❌ خطأ رئيسي: {e}')
        time.sleep(2)
EOF
