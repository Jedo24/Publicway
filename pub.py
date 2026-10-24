import time, json, urllib.request, ssl, urllib.error
TOKEN = '8619621181:AAHBXbxDvHcIcCzobF8av2UUTdFspUCa9Lk'
KEY = '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'
ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
try: urllib.request.urlopen(f'https://api.telegram.org/bot{TOKEN}/deleteWebhook?drop_pending_updates=true', context=ctx)
except: pass
def get_free_model():
    try:
        req = urllib.request.Request('https://openrouter.ai/api/v1/models', headers={'Authorization': f'Bearer {KEY}'})
        with urllib.request.urlopen(req, context=ctx, timeout=10) as r:
            data = json.loads(r.read().decode())
            for m in data.get('data', []):
                mid = m.get('id', '')
                if ':free' in mid:
                    print(f'✨ تم اختيار نموذج مجاني تلقائياً: {mid}')
                    return mid
    except Exception as e:
        print(f'⚠️ تعذر جلب القائمة تلقائياً: {e}')
    return 'google/gemini-flash-1.5-8b:free'
MODEL = get_free_model()
print(f'🚀 البوت يعمل الآن باستخدام النموذج: {MODEL}')
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
                    chat_id = msg['chat']['id']; text = msg['text']
                    print(f'📩 رسالة: {text}')
                    if text.startswith('/start'):
                        reply = 'أهلاً بك في بوت الخدمات الرقمية الذكية! أرسل لي أي استفسار وسأرد عليك فوراً.'
                    else:
                        print('🧠 جاري إرسال الطلب لـ OpenRouter...')
                        try:
                            req_ai = urllib.request.Request('https://openrouter.ai/api/v1/chat/completions', data=json.dumps({'model':MODEL,'messages':[{'role':'user','content':text}]}).encode(), headers={'Authorization': f'Bearer {KEY}', 'Content-Type': 'application/json'}, method='POST')
                            with urllib.request.urlopen(req_ai, context=ctx) as ra:
                                reply = json.loads(ra.read().decode())['choices'][0]['message']['content']
                        except urllib.error.HTTPError as he:
                            err_detail = he.read().decode()
                            print(f'❌ تفاصيل خطأ OpenRouter: {err_detail}')
                            reply = f'خطأ من OpenRouter: {err_detail}'
                        except Exception as ai_err:
                            print(f'❌ خطأ عام: {ai_err}')
                            reply = f'عذراً، حدث خطأ: {ai_err}'
                    try:
                        urllib.request.urlopen(urllib.request.Request(f'https://api.telegram.org/bot{TOKEN}/sendMessage', data=json.dumps({'chat_id': chat_id, 'text': reply}).encode(), headers={'Content-Type': 'application/json'}, method='POST'), context=ctx)
                        print('✅ تم الرد بنجاح!')
                    except Exception as tg_err:
                        print(f'❌ خطأ تيليجرام: {tg_err}')
    except Exception as e:
        print(f'❌ خطأ رئيسي: {e}')
        time.sleep(2)
