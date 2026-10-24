cat << 'EOF' > pub.py
import time, json, urllib.request, ssl, urllib.error, os

TOKEN = '8619621181:AAHBXbxDvHcIcCzobF8av2UUTdFspUCa9Lk'
KEY = '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'

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# تخزين حالات المستخدمين (أي خدمة مفعلة حالياً لكل مستخدم)
user_states = {}

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
                    return mid
    except:
        pass
    return 'google/gemini-flash-1.5-8b:free'

MODEL = get_free_model()
print(f'🚀 بوت القوائم التفاعلية يعمل بالنموذج: {MODEL}')

# دالة إرسال الرسائل مع الأزرار التفاعلية
def send_menu(chat_id):
    keyboard = {
        "inline_keyboard": [
            [{"text": "💬 شات ذكاء اصطناعي", "callback_data": "chat_ai"}],
            [{"text": "📝 تلخيص مقال", "callback_data": "summarize"}, {"text": "✍️ تغيير الصياغة", "callback_data": "rephrase"}],
            [{"text": "📥 تحميل ملف من رابط", "callback_data": "download"}]
        ]
    }
    text = (
        "👋 **أهلاً بك في منصة الخدمات الرقمية الذكية!**\n\n"
        "الرجاء اختيار الخدمة المطلوبة من القائمة أدناه لتفعيلها:"
    )
    payload = {
        "chat_id": chat_id,
        "text": text,
        "reply_markup": keyboard,
        "parse_mode": "Markdown"
    }
    req = urllib.request.Request(
        f'https://api.telegram.org/bot{TOKEN}/sendMessage',
        data=json.dumps(payload).encode(),
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    urllib.request.urlopen(req, context=ctx)

def send_message(chat_id, text):
    payload = {"chat_id": chat_id, "text": text}
    req = urllib.request.Request(
        f'https://api.telegram.org/bot{TOKEN}/sendMessage',
        data=json.dumps(payload).encode(),
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    urllib.request.urlopen(req, context=ctx)

def send_document(chat_id, file_path, caption):
    try:
        boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
        body_data = []
        body_data.append(f'--{boundary}\r\n'.encode())
        body_data.append(f'Content-Disposition: form-data; name="chat_id"\r\n\r\n{chat_id}\r\n'.encode())
        body_data.append(f'--{boundary}\r\n'.encode())
        body_data.append(f'Content-Disposition: form-data; name="caption"\r\n\r\n{caption}\r\n'.encode())
        body_data.append(f'--{boundary}\r\n'.encode())
        body_data.append(f'Content-Disposition: form-data; name="document"; filename="{os.path.basename(file_path)}"\r\n'.encode())
        body_data.append(b'Content-Type: application/octet-stream\r\n\r\n')
        with open(file_path, 'rb') as f:
            body_data.append(f.read())
        body_data.append(f'\r\n--{boundary}--\r\n'.encode())
        
        doc_req = urllib.request.Request(
            f'https://api.telegram.org/bot{TOKEN}/sendDocument',
            data=b''.join(body_data),
            headers={'Content-Type': f'multipart/form-data; boundary={boundary}'},
            method='POST'
        )
        urllib.request.urlopen(doc_req, context=ctx)
    except Exception as e:
        send_message(chat_id, f'❌ خطأ في إرسال الملف: {e}')

offset = 0
while True:
    try:
        url = f'https://api.telegram.org/bot{TOKEN}/getUpdates?offset={offset}&timeout=30'
        with urllib.request.urlopen(url, context=ctx, timeout=35) as r:
            res = json.loads(r.read().decode())
            for u in res.get('result', []):
                offset = u['update_id'] + 1
                
                # 1. معالجة نقرات الأزرار التفاعلية (Callback Query)
                if 'callback_query' in u:
                    cq = u['callback_query']
                    chat_id = cq['message']['chat']['id']
                    data = cq['data']
                    query_id = cq['id']
                    
                    # الرد على النكرة لتفريغ التحميل من الزر
                    try:
                        ans_payload = {"callback_query_id": query_id, "text": "تم تفعيل الخدمة ✅"}
                        urllib.request.urlopen(urllib.request.Request(f'https://api.telegram.org/bot{TOKEN}/answerCallbackQuery', data=json.dumps(ans_payload).encode(), headers={'Content-Type': 'application/json'}, method='POST'), context=ctx)
                    except:
                        pass
                    
                    user_states[chat_id] = data
                    
                    if data == 'chat_ai':
                        send_message(chat_id, "💬 **تم تفعيل وضع شات الذكاء الاصطناعي.**\nأرسل أي استفسار أو سؤال وسأجيبك فوراً!\n\n(للعودة للقائمة الرئيسية في أي وقت، أكتب /menu)")
                    elif data == 'summarize':
                        send_message(chat_id, "📝 **تم تفعيل وضع تلخيص المقالات.**\nأرسل النص أو المقال الذي تريد تلخيصه وسأقوم بترتيبه في نقاط واضحة.")
                    elif data == 'rephrase':
                        send_message(chat_id, "✍️ **تم تفعيل وضع تغيير وتحسين الصياغة.**\nأرسل النص الذي ترغب بإعادة صياغته أو تصحيحه.")
                    elif data == 'download':
                        send_message(chat_id, "📥 **تم تفعيل وضع تحميل الملفات.**\nأرسل رابط الملف المباشر (مثل PDF أو رابط صورة) وسأقوم بتحميله وإرساله لك حالاً.")
                    continue

                # 2. معالجة الرسائل النصية العادية بناءً على حالة المستخدم
                msg = u.get('message')
                if msg and 'text' in msg:
                    chat_id = msg['chat']['id']
                    text = msg['text'].strip()
                    
                    if text.startswith('/start') or text.startswith('/menu'):
                        user_states[chat_id] = 'chat_ai'
                        send_menu(chat_id)
                        continue
                    
                    current_state = user_states.get(chat_id, 'chat_ai')
                    
                    # إذا كان الوضع هو تحميل ملف
                    if current_state == 'download':
                        send_message(chat_id, "⏳ جاري تحميل الملف من الرابط، يرجى الانتظار...")
                        try:
                            headers = {'User-Agent': 'Mozilla/5.0'}
                            req_file = urllib.request.Request(text, headers=headers)
                            local_filename = text.split('/')[-1].split('?')[0]
                            if not local_filename or '.' not in local_filename:
                                local_filename = "downloaded_file.bin"
                            
                            with urllib.request.urlopen(req_file, context=ctx, timeout=30) as resp, open(local_filename, 'wb') as out:
                                out.write(resp.read())
                            
                            send_document(chat_id, local_filename, caption=f"📁 تم التحميل بنجاح من:\n{text}")
                            if os.path.exists(local_filename):
                                os.remove(local_filename)
                        except Exception as dl_err:
                            send_message(chat_id, f'⚠️ تعذر التحميل من هذا الرابط. الخطأ:\n{dl_err}')
                    
                    # إذا كان الوضع ذكاء اصطناعي أو تلخيص أو تغيير صيغة
                    else:
                        system_prompt = "أنت مساعد ذكي متعدد الخدمات."
                        if current_state == 'summarize':
                            system_prompt = "أنت خبير تلخيص. قم بتلخيص النص التالي بدقة واختصار في نقاط رئيسية مرتبة."
                        elif current_state == 'rephrase':
                            system_prompt = "أنت مدقق لغوي وكاتب محترف. قم بإعادة صياغة النص التالي وتحسين أسلوبه وجعله أكثر احترافية."
                        elif current_state == 'chat_ai':
                            system_prompt = "أنت مساعد ذكي عام ومحترف تقدم إجابات مباشرة ومفيدة."

                        try:
                            payload = {
                                'model': MODEL,
                                'messages': [
                                    {'role': 'system', 'content': system_prompt},
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
                            reply = f'عذراً، حدث خطأ في معالجة الطلب: {ai_err}'

                        send_message(chat_id, reply)

    except Exception as e:
        print(f'❌ خطأ رئيسي: {e}')
        time.sleep(2)
EOF
