# LostDock

**LostDock** هي أداة سطح مكتب متعددة المنصات بمستوى صناعي للبحث في جوجل (Google dorking)، مكتوبة بلغة Python.
توفر أداة بناء مرئية للاستعلامات مع جميع عوامل تشغيل محركات البحث، وتنفيذًا متعدد المحركات مع تحديد
السرعة وتدوير الوكلاء (proxies)، وتخزينًا دائمًا للنتائج، وإعادة فحص الروابط، وجداول زمنية للبحث،
وتمييزًا بالتعبيرات النمطية (regex)، ونظام إضافات (plugins) — كل ذلك في واجهة PySide6 (Qt) أصلية
تعمل على **Windows وmacOS وLinux**.

> الوثائق الكاملة: [README.md](README.md)

---

## المميزات

- **منشئ استعلامات مرئي** — ادمج الكلمات المفتاحية والعبارات الدقيقة والمنطق البولياني (`AND`/`OR`/`NOT`)
  والاستثناءات والكلمات المطلوبة والمواقع وأنواع الملفات وجميع عوامل جوجل، مع معاينة مباشرة.
- **محركات متعددة** — محولات لـ Google وDuckDuckGo وBing خلف واجهة واحدة.
- **تحديد السرعة ومكافحة الحظر** — محدد token-bucket مع تشويش (jitter)، وتدوير User-Agent،
  وإعادة محاولة مع backoff، وكشف CAPTCHA/البوت.
- **تدوير الوكلاء** — تجمع وكلاء مع تدوير دائري وتهدئة عند الفشل وتحقق.
- **تخزين دائم** — كل مهمة ونتيجة في SQLite، مع إزالة التكرار بين المحركات.
- **إعادة فحص الروابط** — يعيد تحميل الروابط المخزنة ويسجل رمز الحالة / نوع المحتوى / العنوان.
- **جداول زمنية** — تنفيذ عمليات البحث المحفوظة على فترات متكررة في الخلفية.
- **تمييز regex** — تمييز فوري للصفوف المطابقة للنمط.
- **فلاتر** — قائمة بيضاء/سوداء للنطاقات وفلاتر إبقاء بتعبيرات URL النمطية (عند التصدير).
- **تصدير** — JSON وCSV وMarkdown وتقرير HTML منسق ومستقل.
- **مكتبة العمليات** — تسمية العمليات وحفظها وتحميلها وحذفها.
- **نظام الإضافات** — وحدات Python في `~/.lostdock/plugins/` مع خطافات `setup` و`on_result` و`on_export`.
- **متعدد المنصات** — كود واحد يُعبّأ لـ Windows (`.exe`) وmacOS (`.app`) وLinux.

## الاستخدام السريع

1. أنشئ الاستعلام: كلمات مفتاحية، عبارة دقيقة، استثناءات، مصطلحات `AND`/`OR`، مواقع (`site:`)،
   أنواع ملفات وعوامل داخلية.
2. اختر المحرك وعدد الصفحات.
3. اضغط **Run Search** — تتدفق النتائج إلى الجدول وتُحفظ في SQLite.
4. استخدم **Re-check URLs** للتحقق من حالة كل نتيجة مباشرة.
5. عيّن **Highlight** بتعبير نمطي لإبراز الصفوف المهمة.
6. اضغط **Export...** للحفظ بصيغة JSON أو CSV أو Markdown أو HTML.

## العوامل المدعومة

`site:` · `inurl:` · `allinurl:` · `intitle:` · `allintitle:` · `intext:` · `allintext:` · `inanchor:` ·
`filetype:` · `ext:` · `cache:` · `link:` · `related:` · `info:` · `define:` · `author:` · `daterange:` ·
`numrange:` · `loc:` · `after:` · `before:` · `lang:` · عبارة دقيقة `"..."` · استثناء `-term` ·
مرادف `~term` · بدل `*` · `term1 OR term2`.

## الوكلاء (Proxies)

عيّنها في **Tools → Settings**، واحد لكل سطر:

```
http://127.0.0.1:8080
socks5://127.0.0.1:1080
```

## الجدولة الزمنية

1. احفظ عملية بحث (سمِّها في حقل "Dork name").
2. في **Tools → Settings**، اخترها وحدد الفاصل الزمني بالدقائق.
3. يقوم المجدول بتنفيذها في الخلفية ويحفظ النتائج كمهام جديدة.

## الإضافات

ضع ملفات `*.py` في `~/.lostdock/plugins/`. يمكن للوحدة تصدير أي مجموعة فرعية:

```python
NAME = "my_plugin"
def setup(app): ...
def on_result(result): return result   # أعد None لإسقاط النتيجة
def on_export(results, fmt, path): ...
```

## تخزين البيانات

- **قاعدة البيانات:** `~/.lostdock/lostdock.db` (SQLite)
- **الإضافات:** `~/.lostdock/plugins/`

## Installation

> Installation instructions are intentionally provided in English only.

### Prerequisites

- **Python 3.10+** — [python.org](https://www.python.org/downloads/)
- **uv** (fast package manager) — [docs.astral.sh/uv](https://docs.astral.sh/uv/getting-started/installation/)

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/your-user/lostdock.git
cd lostdock

# 2. Create a virtual environment and install
uv venv
uv pip install -e ".[dev]"

# 3. Run
uv run lostdock
```

If you do not have `uv`, you can use plain `pip`:

```bash
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
lostdock
```

## إخلاء مسؤولية

LostDock أداة **للبحث الأمني وOSINT**. استخدمها فقط ضد الأنظمة التي تملكها أو التي لديك إذن صريح
لاختبارها. احترم شروط استخدام محركات البحث، وحافظ على سرعات منخفضة، واستخدم الوكلاء بمسؤولية،
ولا تستخدمها أبدًا للوصول غير المصرح به أو جمع البيانات الشخصية أو أي نشاط غير قانوني.

## License

MIT — انظر [LICENSE](LICENSE).
