# LostDock

**LostDock** एक उद्योग-स्तरीय, क्रॉस-प्लेटफ़ॉर्म Google डॉर्किंग डेस्कटॉप टूल है, जो Python में लिखा गया है।
यह सभी सर्च इंजन ऑपरेटरों के साथ एक विज़ुअल क्वेरी बिल्डर, रेट-लिमिटिंग और प्रॉक्सी रोटेशन के साथ
मल्टी-इंजन निष्पादन, परिणामों का स्थायी भंडारण, URL री-चेकिंग, शेड्यूल किए गए डॉर्क, regex हाइलाइटिंग
और एक प्लगइन सिस्टम प्रदान करता है — सब कुछ एक नेटिव PySide6 (Qt) UI में जो **Windows, macOS और Linux**
पर चलता है।

> पूर्ण दस्तावेज़: [README.md](README.md)

---

## विशेषताएँ

- **विज़ुअल डॉर्क बिल्डर** — कीवर्ड, सटीक वाक्यांश, बूलियन लॉजिक (`AND`/`OR`/`NOT`), बहिष्करण,
  आवश्यक शब्द, साइटें, फ़ाइल प्रकार और सभी Google ऑपरेटरों को लाइव प्रीव्यू के साथ जोड़ें।
- **मल्टी-इंजन** — Google, DuckDuckGo और Bing एडेप्टर एक ही इंटरफ़ेस के पीछे।
- **रेट लिमिटिंग और एंटी-ब्लॉक** — टोकन-बकेट लिमिटर जिटर के साथ, रोटेटिंग User-Agents,
  बैकऑफ़ के साथ रीट्राई, और CAPTCHA/bot डिटेक्शन।
- **प्रॉक्सी रोटेशन** — राउंड-रॉबिन रोटेशन, फेल-कूलडाउन और वैलिडेशन के साथ प्रॉक्सी पूल।
- **स्थायी भंडारण** — हर जॉब और रिज़ल्ट SQLite में, इंजनों के बीच डीडुप्लीकेटेड।
- **URL री-चेकिंग** — संग्रहीत URL को दोबारा फेच करें और स्टेटस कोड / कंटेंट टाइप / टाइटल नोट करें।
- **शेड्यूल किए गए डॉर्क** — सेव किए गए डॉर्क को बैकग्राउंड में नियत अंतराल पर चलाएँ।
- **regex हाइलाइटिंग** — पैटर्न से मेल खाती पंक्तियों को तुरंत हाइलाइट करें।
- **फ़िल्टर** — डोमेन व्हाइटलिस्ट/ब्लैकलिस्ट और URL-regex फ़िल्टर (एक्सपोर्ट पर लागू)।
- **एक्सपोर्ट** — JSON, CSV, Markdown, और एक स्टाइलिश HTML रिपोर्ट।
- **सेव डॉर्क लाइब्रेरी** — डॉर्क को नाम दें, सेव करें, लोड करें, हटाएँ।
- **प्लगइन सिस्टम** — `~/.lostdock/plugins/` में Python मॉड्यूल, हुक: `setup`, `on_result`, `on_export`।
- **क्रॉस-प्लेटफ़ॉर्म** — Windows (`.exe`), macOS (`.app`), Linux के लिए एक ही कोड पैकेज।

## त्वरित उपयोग

1. क्वेरी बनाएँ: कीवर्ड, सटीक वाक्यांश, बहिष्करण, `AND`/`OR` शब्द, साइटें (`site:`), फ़ाइल प्रकार
   और इनलाइन ऑपरेटर।
2. इंजन और पेज चुनें।
3. **Run Search** दबाएँ — परिणाम टेबल में आते हैं और SQLite में सेव होते हैं।
4. **Re-check URLs** से हर रिज़ल्ट का लाइव स्टेटस जाँचें।
5. दिलचस्प पंक्तियों को उजागर करने के लिए **Highlight** regex सेट करें।
6. **Export...** से JSON, CSV, Markdown या HTML में सेव करें।

## समर्थित ऑपरेटर

`site:` · `inurl:` · `allinurl:` · `intitle:` · `allintitle:` · `intext:` · `allintext:` · `inanchor:` ·
`filetype:` · `ext:` · `cache:` · `link:` · `related:` · `info:` · `define:` · `author:` · `daterange:` ·
`numrange:` · `loc:` · `after:` · `before:` · `lang:` · सटीक वाक्यांश `"..."` · बहिष्करण `-term` ·
पर्यायवाची `~term` · वाइल्डकार्ड `*` · `term1 OR term2`।

## प्रॉक्सी

**Tools → Settings** में सेट करें, एक लाइन पर एक:

```
http://127.0.0.1:8080
socks5://127.0.0.1:1080
```

## शेड्यूल किए गए डॉर्क

1. एक डॉर्क सेव करें ("Dork name" फ़ील्ड में नाम दें)।
2. **Tools → Settings** में उसे चुनें और अंतराल मिनटों में सेट करें।
3. स्केड्यूलर उसे बैकग्राउंड में चलाता है और परिणाम नई जॉब के रूप में सेव करता है।

## प्लगइन

`~/.lostdock/plugins/` में `*.py` फ़ाइलें रखें। मॉड्यूल कोई भी उपसमुच्चय एक्सपोर्ट कर सकता है:

```python
NAME = "my_plugin"
def setup(app): ...
def on_result(result): return result   # छोड़ने के लिए None लौटाएँ
def on_export(results, fmt, path): ...
```

## डेटा भंडारण

- **डेटाबेस:** `~/.lostdock/lostdock.db` (SQLite)
- **प्लगइन:** `~/.lostdock/plugins/`

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

## Disclaimer

LostDock एक **सुरक्षा अनुसंधान और OSINT टूल** है। इसका उपयोग केवल उन्हीं सिस्टम पर करें जिनके आप
मालिक हैं या जिनका परीक्षण करने का आपको स्पष्ट अधिकार है। सर्च इंजन की सेवा शर्तों का सम्मान करें,
रेट सीमा कम रखें, प्रॉक्सी का ज़िम्मेदारी से उपयोग करें, और अनधिकृत पहुँच, व्यक्तिगत डेटा स्क्रैपिंग
या किसी अवैध गतिविधि के लिए इसका उपयोग कभी न करें।

## License

MIT — [LICENSE](LICENSE) देखें।
