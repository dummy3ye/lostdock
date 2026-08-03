# LostDock

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB.svg)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](../LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](#التثبيت)

**LostDock** هي أداة سطح مكتب لـ Google dorking وبحوث OSINT. تجمع بين منشئ استعلامات مرئي
وبحث متعدد المحركات وتحديد سرعة وتدوير وكلاء وتخزين دائم للنتائج — كل ذلك في واجهة PySide6
(Qt) أصلية تعمل على **Windows وmacOS وLinux**.

> **اقرأ هذا README بـ:** [English](../README.md) · [中文](../README.zh-CN.md) · [Español](../i18n/README.es.md) · [Français](../i18n/README.fr.md) · [Deutsch](../i18n/README.de.md) · [हिन्दी](../i18n/README.hi.md) · [Português](../i18n/README.pt-BR.md) · [Русский](../i18n/README.ru.md) · [日本語](../README.ja.md) · [한국어](../i18n/README.ko.md) · [Italiano](../i18n/README.it.md)

---

## جدول المحتويات

- [المميزات](#المميزات)
- [البنية](#البنية)
- [التثبيت](#التثبيت)
- [الاستخدام](#الاستخدام)
- [العوامل المدعومة](#العوامل-المدعومة)
- [محركات البحث](#محركات-البحث)
- [الوكلاء](#الوكلاء)
- [الجداول الزمنية](#الجداول-الزمنية)
- [إعادة فحص الروابط](#إعادة-فحص-الروابط)
- [الإضافات](#الإضافات)
- [التصدير](#التصدير)
- [تخزين البيانات](#تخزين-البيانات)
- [التغليف](#التغليف)
- [الإصدارات](#الإصدارات)
- [التطوير](#التطوير)
- [إخلاء المسؤولية](#إخلاء-المسؤولية)
- [الترخيص](#الترخيص)

---

## المميزات

- **منشئ استعلامات مرئي** — ادمج الكلمات المفتاحية والعبارات الدقيقة والمنطق البولياني
  (`AND`/`OR`/`NOT`) والاستثناءات والكلمات المطلوبة والمواقع وأنواع الملفات وجميع عوامل
  Google، مع معاينة مباشرة للاستعلام.
- **بحث متعدد المحركات** — Google وDuckDuckGo وBing خلف واجهة واحدة، إضافة إلى وضع Chrome
  "pipe" الذي ينفذ البحث في متصفحك الخاص. أو شغّل الثلاثة معًا وادمج النتائج.
- **تحديد السرعة ومكافحة الحظر** — محدد token-bucket مع تشويش (jitter)، وتدوير User-Agent،
  وإعادة محاولة مع backoff، وكشف CAPTCHA/البوت. يلجأ Google إلى عرض Chromium headless عندما
  يُحظر HTTP البسيط.
- **تدوير الوكلاء** — تجمع وكلاء مع تدوير دائري وتهدئة عند الفشل وتحقق.
- **تخزين دائم** — كل مهمة ونتيجة في SQLite، مع إزالة التكرار بين المحركات.
- **إعادة فحص الروابط مباشرة** — يعيد تحميل الروابط المخزنة ويسجل رمز الحالة ونوع المحتوى
  والعنوان.
- **جداول زمنية** — تنفيذ العمليات المحفوظة على فترات متكررة في الخلفية.
- **تمييز regex** — تمييز فوري للصفوف المطابقة لنمط.
- **فلاتر** — قائمة بيضاء/سوداء للنطاقات وفلاتر إبقاء بتعبيرات URL النمطية عند التصدير.
- **تصدير** — JSON وCSV وMarkdown وتقرير HTML منسق ومستقل.
- **مكتبة العمليات** — حفظ العمليات وتحميلها وإدارتها بالاسم.
- **نظام الإضافات** — إضافة وحدات Python بخطافات `setup` و`on_result` و`on_export`.
- **السمات** — أنماط داكنة وفاتحة وWin98 GDI الكلاسيكية.
- **متعدد المنصات** — قاعدة كود واحدة لـ Windows وmacOS وLinux، مع مثبّت/محدّث لـ Windows.

## البنية

```
┌─ طبقة الواجهة (PySide6/Qt) ────────────────────────────┐
│  Dork Builder │ Results Grid │ Scheduler │ Settings      │
│  السمات (dark / light / win98)                           │
└───────────────┬──────────────────────────────────────────┘
┌───────────────▼──────────────────────────────────────────┐
│  طبقة الخدمات                                             │
│  Repository │ Query │ Filter │ Crawler │ Scheduler │      │
│  Exporter │ Plugins                                       │
└───────────────┬──────────────────────────────────────────┘
┌───────────────▼──────────────────────────────────────────┐
│  المحرك الأساسي                                           │
│  Adapters (Google / DuckDuckGo / Bing / Chrome)           │
│  Multi-Engine (all) │ Rate Limiter │ Proxy Pool           │
│  Compiler │ Operators                                     │
└───────────────┬──────────────────────────────────────────┘
┌───────────────▼──────────────────────────────────────────┐
│  SQLite (jobs, results, dorks, schedules, config)         │
└───────────────────────────────────────────────────────────┘
```

## التثبيت

> تعليمات التثبيت مقدمة بالإنجليزية فقط عمدًا.

### المتطلبات

- **Python 3.10+** — [python.org](https://www.python.org/downloads/)
- **uv** (مدير حزم سريع) — [docs.astral.sh/uv](https://docs.astral.sh/uv/getting-started/installation/)

### الخطوات

```bash
# 1. استنساخ المستودع
git clone https://github.com/dummy3ye/lostdock.git
cd lostdock

# 2. إنشاء بيئة افتراضية وتثبيت
uv venv
uv pip install -e ".[dev]"

# 3. تثبيت Chromium headless المستخدم في احتياطي مكافحة الحظر لدى Google
uv run python -m playwright install chromium

# 4. التشغيل
uv run lostdock
```

إذا لم يكن لديك `uv`، يمكنك استخدام `pip` مباشرة:

```bash
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
python -m playwright install chromium
lostdock
```

### بديل: التشغيل من جذر المستودع دون تثبيت

```bash
cd src
QT_QPA_PLATFORM=offscreen python -m lostdock.main   # offscreen للاختبارات دون واجهة
```

## الاستخدام

1. **أنشئ استعلامًا** — اكتب كلمات مفتاحية وأضف عبارة دقيقة واستثناءات وشروط `AND`/`OR`
   ومواقع (`site:`) وأنواع ملفات وعوامل داخلية. يُحدَّث الاستعلام المترجم مباشرة.
2. **اختر محركًا** — Google أو DuckDuckGo أو Bing أو Chrome أو "all" — وعدد الصفحات.
3. انقر **Run Search**. تتدفق النتائج إلى الجدول؛ يُحفظ كل نتيجة في SQLite.
4. استخدم **Re-check URLs** لتحميل كل نتيجة وتسجيل حالتها مباشرة.
5. عيّن **Highlight** بتعبير نمطي لإبراز الصفوف المهمة.
6. انقر **Export...** للحفظ بصيغة JSON أو CSV أو Markdown أو تقرير HTML.

## العوامل المدعومة

يدعم المنشئ مجموعة عوامل Google الكاملة:

| العامل | المعنى |
|--------|--------|
| `site:` | تقييد النتائج بنطاق |
| `inurl:` / `allinurl:` | كلمات في الرابط |
| `intitle:` / `allintitle:` | كلمات في العنوان |
| `intext:` / `allintext:` | كلمات في نص الصفحة |
| `inanchor:` | كلمات في نص رابط المرساة |
| `filetype:` / `ext:` | تقييد بنوع ملف |
| `cache:` | النسخة المخزنة لدى Google |
| `link:` | صفحات ترتبط برابط |
| `related:` | صفحات مشابهة |
| `info:` | نظرة عامة على الصفحة |
| `define:` | تعريف مصطلح |
| `author:` | مؤلف النتيجة |
| `daterange:` / `numrange:` | نطاقات رقمية |
| `loc:` | الموقع |
| `after:` / `before:` | فلاتر التاريخ (`YYYY-MM-DD`) |
| `lang:` | تقييد اللغة |
| `"phrase"` | عبارة دقيقة |
| `-term` | استبعاد مصطلح |
| `~term` | تضمين مرادفات |
| `*` | بدل |
| `term1 OR term2` | أي من المصطلحين |

## محركات البحث

تتقاسم جميع المحركات الواجهة نفسها (`SearchEngine` في `adapters/base.py`) وهي محدودة السرعة
افتراضيًا. أضف محركًا جديدًا بوراثة `SearchEngine` وتسجيله في `adapters/__init__.py`.

- **Google** — يستخلص SERP عبر HTTP أولًا. إذا استجاب Google بـ CAPTCHA أو حظر بحد السرعة،
  يعيد عرض الصفحة في Chromium headless حقيقي (عبر Playwright)، مما يتجاوز كشف البوت السلوكي
  في معظم الشبكات السكنية. على عناوين IP الخاصة بمراكز البيانات قد يحظر Google على مستوى IP
  على أي حال — أضف وكلاء في Tools → Settings أو استخدم محركًا آخر. يتطلب ثنائي Chromium
  مرة واحدة (`python -m playwright install chromium`). لاستخدام إنتاجي متوافق تمامًا، ادمج
  واجهة Google Custom Search JSON (100 استعلام مجاني يوميًا).
- **DuckDuckGo** — نقطة HTML خفيفة، تتسامح عمومًا مع الوصول الآلي بمعدلات معتدلة.
- **Bing** — استخلاص SERP؛ محدود السرعة وقد يتعرض لفحوصات البوت على نطاق واسع.
- **Chrome (pipe)** — يفتح البحث مباشرة في متصفح Chrome/Chromium الخاص بك لمراجعته هناك. لا
  تُلتقط أي نتائج إلى LostDock؛ وهي أبسط طريقة للبحث عندما يحظر Google كل ما عداه. عيّن
  `LOSTDOCK_CHROME` للإشارة إلى ثنائي محدد عند الحاجة.
- **All** — يشغل Google وDuckDuckGo وBing لنفس الاستعلام ويدمج النتائج. لا يوقف المحرك
  المحظور البحث أبدًا؛ تُزال النتائج المكررة حسب الرابط.

## الوكلاء

عيّن الوكلاء في **Tools → Settings**. واحد لكل سطر:

```
http://127.0.0.1:8080
socks5://127.0.0.1:1080
```

تُدور الوكلاء لكل طلب؛ الوكلاء الفاشلون يدخلون فترة تهدئة. استخدم مسار "validate" (في الكود
`ProxyPool.validate()`) للتخلص من الوكلاء الميتة.

## الجداول الزمنية

1. احفظ عملية (سمِّها في حقل "Dork name").
2. في **Tools → Settings**، اختر العملية وحدد فاصلًا بالدقائق واحفظ.
3. ينفذ المجدول في الخلفية العمليات المستحقة ويخزن النتائج كمهام جديدة ويرحّل التشغيل التالي.

## إعادة فحص الروابط

يجلب زر **Re-check URLs** كل رابط من النتائج الحالية خارج خيط الواجهة، مع تأخيرات مهذبة،
ويسجل على كل صف `رمز الحالة` و`نوع المحتوى` و`<title>` مباشر، ويحفظ النتائج في قاعدة
البيانات. تُسجل الإخفاقات في موضعها ولا تعطّل الواجهة أبدًا.

## الإضافات

ضع ملفات `*.py` في `~/.lostdock/plugins/` (أو في دليل `plugins/` المرفق). يمكن لوحدة إضافة
تصدير أي مجموعة فرعية:

```python
NAME = "my_plugin"

def setup(app): ...                    # مرة واحدة عند الإقلاع
def on_result(result): return result   # أعد None لإسقاط النتيجة
def on_export(results, fmt, path): ... # قبل التصدير
```

انظر `plugins/example_skip_tracking.py` لمثال عملي.

## التصدير

| الصيغة | الامتداد | ملاحظات |
|--------|----------|---------|
| JSON | `.json` | نتائج منظمة كاملة |
| CSV | `.csv` | جاهز للجداول (UTF-8 BOM) |
| Markdown | `.md` | قابل للقراءة |
| HTML | `.html` | تقرير مستقل بروابط قابلة للنقر |

## تخزين البيانات

- **قاعدة البيانات:** `~/.lostdock/lostdock.db` (SQLite)
- **الإضافات:** `~/.lostdock/plugins/`
- الجداول: `jobs` و`results` و`saved_dorks` و`schedules` و`settings`. تُرحَّل قواعد
  البيانات القديمة تلقائيًا.

## التغليف

يتضمن المشروع ملف `lostdock.spec` لـ PyInstaller. أنشئ حسب المنصة:

```bash
uv pip install pyinstaller
pyinstaller lostdock.spec          # ينشئ dist/lostdock
```

- **Windows:** `dist/lostdock.exe`، إضافة إلى `lostdock-installer.exe` أحادي الملف الذي
  يعمل كمثبّت ومحدّث ومزيل دون صلاحيات مسؤول (`src/installer/windows/main.py`).
- **macOS:** اجمع في `dist/lostdock.app` (وقّع بـ `codesign` للتوزيع).
- **Linux:** ثنائي `dist/lostdock`، أو لفه في AppImage/Flatpak. يوجد `PKGBUILD` لـ Arch
  Linux في `packaging/aur/`.

## الإصدارات

الإصدارات مدفوعة بالوسوم (tags) ومؤتمتة. لإصدار نسخة جديدة تحتاج `git-cliff`
(`cargo install git-cliff`):

```bash
make release                # يرفع الإصدار، يعيد إنشاء CHANGELOG.md، يلتزم ويسم
```

يقرأ `make release` الالتزامات التقليدية منذ آخر وسم لاختيار إصدار semver التالي (أو مرره
صراحة: `./scripts/release.sh 0.2.0`). ثم يرفع الإصدار في `pyproject.toml` و
`src/lostdock/__init__.py`، ويشغل مجموعة الاختبارات، ويعيد إنشاء `CHANGELOG.md`، وينشئ وسمًا
معلقًا `vX.Y.Z`.

يؤدي دفع الوسم إلى تشغيل CI، الذي يبني ثنائيات Windows وLinux ومثبّت Windows الموقّع ذاتيًا،
ثم ينشر GitHub Release بملاحظات مولدة تلقائيًا (ميزات/إصلاحات مجمعة ومراجع قضايا ومساهمون)
عبر [git-cliff](https://git-cliff.org).

## التطوير

```bash
uv run pytest                     # تشغيل مجموعة الاختبارات
uv run python -m compileall -q src  # فحص سليم للاستيرادات
uv run ruff check src tests       # التحقق من الأسلوب
```

هيكل المشروع:

```
src/lostdock/
├── core/         نموذج Dork والعوامل ومترجم الاستعلامات ومحدد السرعة وتجمع الوكلاء
├── adapters/     محولات Google / DuckDuckGo / Bing / Chrome وعارض المتصفح
├── services/     repository, query, filter, crawler, scheduler, exporter, plugins
├── ui/           عناصر PySide6: dork builder, results grid, worker, settings, theme, main window
└── main.py       نقطة الدخول
src/installer/    مثبّت/محدّث/مزيل Windows
tests/            مجموعة pytest (compiler, engines, services, proxy, scheduler, plugins)
```

## إخلاء المسؤولية

LostDock أداة **للبحث الأمني وOSINT**. استخدمها فقط ضد أنظمة تملكها أو لديك إذن صريح
لاختبارها. احترم شروط استخدام محركات البحث: حافظ على معدلات منخفضة، واستخدم الوكلاء
بمسؤولية، ولا تستخدم هذه الأداة أبدًا للوصول غير المصرح به أو جمع البيانات الشخصية أو أي
نشاط غير قانوني. المؤلفون غير مسؤولين عن سوء الاستخدام.

## الترخيص

MIT — انظر [LICENSE](../LICENSE).
