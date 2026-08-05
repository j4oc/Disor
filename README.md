<div align="center">

<img src="assets/bot-logo.png" width="110" style="border-radius:24px;box-shadow:0 8px 30px rgba(168,85,247,.4);"/>

# <span style="background:linear-gradient(90deg,#a855f7,#22d3ee,#4ade80);-webkit-background-clip:text;background-clip:text;color:transparent;font-size:52px;font-weight:900;">DISOR</span>

### <span style="color:#22d3ee;">NX Edition</span> — بوت إدارة سيرفرات Discord بالذكاء الاصطناعي

<img src="assets/banner.jpg" alt="Disor NX Edition Banner" width="100%" style="border-radius:16px;box-shadow:0 8px 40px rgba(168,85,247,.35);"/>

<br/>

**اكتب طلبك بالعامية… والبوت ينفذه!** 🚀
مش أوامر ثابتة، مش Prefix معقد — مجرد كلام عادي بيتحول لأوامر حقيقية بتنفذ على سيرفرك.

<br/>

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white&style=for-the-badge)](https://www.python.org/)
[![discord.py](https://img.shields.io/badge/discord.py-2.3%2B-5865F2?logo=discord&logoColor=white&style=for-the-badge)](https://github.com/Rapptz/discord.py)
[![Groq](https://img.shields.io/badge/Powered_by-Groq_LLM-F55036?style=for-the-badge)](https://console.groq.com)
[![Skills](https://img.shields.io/badge/126-مهارة%20كاملة-8A2BE2?style=for-the-badge)](#-المهارات-126)
[![Tests](https://img.shields.io/badge/tests-20%20passed-brightgreen?style=for-the-badge)](tests/)
[![CI](https://img.shields.io/badge/CI-GitHub_Actions-blue?style=for-the-badge)](.github/workflows/ci.yml)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

<br/>

<table>
<tr>
<td align="center">
<img src="assets/developer-avatar.png" width="90" style="border-radius:50%;border:3px solid #a855f7;"/>
</td>
<td align="center" style="padding:10px 24px;">
<b style="font-size:20px;color:#a855f7;">مطوَّر بالكامل بواسطة:</b><br/>
<span style="font-size:26px;font-weight:900;background:linear-gradient(90deg,#a855f7,#22d3ee);-webkit-background-clip:text;background-clip:text;color:transparent;">NX</span>
<span style="color:#8b93a7;">(يوزر ديسكورد: <code>e4_1</code>)</span><br/>
<a href="https://discord.com/users/1254573563160039495" style="color:#22d3ee;text-decoration:none;">
💬 تواصل معي على ديسكورد — Discord ID: <code>1254573563160039495</code>
</a>
<br/><br/>
<a href="https://discord.com/users/1254573563160039495">
<img src="https://img.shields.io/badge/📨_تواصل_معي_على_ديسكورد-5865F2?style=for-the-badge&logo=discord&logoColor=white"/>
</a>
</td>
</tr>
</table>

</div>

---

## 📑 فهرس المحتويات

<details open>
<summary>اضغط للتنقل</summary>

- [🏆 الإنجازات](#-الإنجازات)
- [🕰️ رحلة التحديثات — 6 إصدارات](#️-رحلة-التحديثات--6-إصدارات)
- [🛠️ المهارات (126 مهارة)](#️-المهارات-126-مهارة)
- [⚡ أوامر سلايش وأوامر نصية](#-أوامر-سلايش-وأوامر-نصية)
- [🚀 التشغيل السريع](#-التشغيل-السريع)
- [⚙️ الإعدادات](#️-الإعدادات)
- [📂 هيكل المشروع](#-هيكل-المشروع)
- [🛡️ الأمان](#️-الأمان)
- [⚡ الأداء](#-الأداء)
- [🧪 الاختبارات و CI](#-الاختبارات-و-ci)
- [📦 النشر على GitHub](#-النشر-على-github)
- [❓ أسئلة شائعة](#-أسئلة-شائعة)
- [🤝 المساهمة](#-المساهمة)
- [📜 الرخصة](#-الرخصة)

</details>

---

## 🏆 الإنجازات

<div align="center">

| <span style="color:#a855f7;">🔐 أمان صارم</span> | <span style="color:#22d3ee;">⚡ رد أسرع</span> | <span style="color:#4ade80;">🧠 فهم أعمق</span> |
|---|---|---|
| المشرفين بس + صلاحية لكل أمر + administrator مقموع + حماية ترتيب الرتب | فايبرات LLM + كاش سيرفر + موديل سريع + Retry تلقائي | سياق محادثة + أمثلة few-shot (36 مثال) + محلل كيانات 3 مراحل |

| <span style="color:#f59e0b;">🛠️ 126 مهارة</span> | <span style="color:#ef4444;">📊 جاهز للنشر</span> | <span style="color:#38bdf8;">💬 بالعامية المصرية</span> |
|---|---|---|
| 9 مجموعات كاملة من إدارة السيرفر | CI + اختبارات + متغيرات بيئة + keep-alive | بيتكلم معاك زي صاحبك — مش روبوت جاف |

</div>

---

## 🕰️ رحلة التحديثات — 5 إصدارات

<div align="center">

| الإصدار | العنوان | الإضافة |
|---|---|---|
| <span style="color:#38bdf8;">**V2.2**</span> | ✨ الأساس القوي | فصل الرومات + نسخ + ثريد + سلايش |
| <span style="color:#22d3ee;">**V2.3**</span> | 🛠️ فصل وتنظيم | نظام Dispatch + إدارة ثريدز كاملة + 43 مهارة |
| <span style="color:#a855f7;">**V2.4**</span> | ⚡ السيطرة على الأعضاء | سوفت بان + صوتي كامل + 57 مهارة |
| <span style="color:#f59e0b;">**V2.5**</span> | 🚀 التوسعة العملاقة | ويبهوكس + إيموجي + إنفيتات + 75 مهارة |
| <span style="color:#4ade80;">**V3.0**</span> | 🔥 الإنجاز الخرافي | **102 مهارة** + إعدادات سيرفر كاملة |
| <span style="color:#e879f9;">**V3.5**</span> | 👑 القوة القصوى | **126 مهارة** + صوتيات + رتب جماعية + براند سيرفر + متعة |

</div>

<details>
<summary><b>📖 تفاصيل كل تحديث (اضغط للعرض)</b></summary>

### ✨ V2.2 — الأساس القوي
- فصل إنشاء الرومات لأنواع (نصي/صوتي) + نسخ روم + ثريد + عرض أعضاء رتبة
- أوامر سلايش بتتزامن تلقائيًا

### 🛠️ V2.3 — فصل وتنظيم
- إعادة هيكلة بنظام **Dispatch** جدولي (أساس الـ 100+)
- إدارة ثريدز كاملة: فتح/حذف/أرشفة/قفل/فتح
- فصل السلو مود والـ NSFW والقفل لمهارات مستقلة

### ⚡ V2.4 — السيطرة على الأعضاء
- سوفت بان + فك كتم + تصفير اسم + فك كتم صوتي + طرشان + فصل من الفويس
- مسح تحذيرات + معلومات عضو + قائمة المتبندين + البوسترز
- فصل مهارات الرتب (لون/ترتيب/صلاحيات/نسخ)

### 🚀 V2.5 — التوسعة العملاقة
- ويبهوكس (إنشاء/حذف/عرض) + إيموجي مخصص + إدارة إنفيتات
- رسائل متقدمة: إيمبيد منسق + تثبيت + رسالة خاصة + مسح رسائل عضو/بوتات

### 🔥 V3.0 — الإنجاز الخرافي
- إعدادات سيرفر كاملة: اسم السيرفر + مستوى التحقق + AFK + قناة النظام
- ترحيب + رول تلقائي + معاينة ترحيب + معلومات سيرفر شاملة
- الوصول لـ **102 مهارة**

### 👑 V3.5 — القوة القصوى
- 🎙️ صوتيات: معلومات روم صوتي + نقل الجميع + فصل الجميع
- 🟩 رتب جماعية: إعطاء/سحب رتبة لكل الأعضاء أو البوتات أو البشر
- 🖼️ براند السيرفر: أيقونة + بانر + سبلاش + Vanity URL
- 🟦 قنوات متقدمة: بيتريت + حد أقصى + صلاحيات رتبة/عضو على روم
- 🟪 رسائل: إرسال رسالة + ريأكشن على آخر رسالة
- 🎲 متعة: عملة + نرد + رقم عشوائي + اختيار عشوائي + معلومات البوت
- 🟥 بان بالـ ID + 🎨 تصميم 3D احترافي جديد بأفاتار حقيقي
- الوصول لـ **126 مهارة** — أقوى بوت إدارة عربي على جروك 👑

</details>

---

## 🛠️ المهارات (126 مهارة)

<div align="center">
<img src="https://img.shields.io/badge/11-مجموعات-brightgreen?style=for-the-badge"/>
<img src="https://img.shields.io/badge/126-مهارة%20كاملة-8A2BE2?style=for-the-badge"/>
</div>

### 🟦 القنوات (28)
| المهارة | الوصف |
|---|---|
| `CreateTextChannel` `CreateVoiceChannel` `CreateForumChannel` `CreateStageChannel` | إنشاء روم بأي نوع (مع حد أقصى للأعضاء) |
| `DeleteChannel` `RenameChannel` `SetChannelTopic` | حذف / إعادة تسمية / وصف |
| `MoveChannel` `SyncChannelPermissions` | نقل لكاتجوري / مزامنة الصلاحيات |
| `LockChannel` `UnlockChannel` | قفل / فتح الكتابة أو الكلام |
| `EnableSlowmode` `DisableSlowmode` | سلو مود تفعيل / إيقاف |
| `EnableNsfw` `DisableNsfw` | روم 18+ تفعيل / إيقاف |
| `CloneChannel` | نسخ الروم بنفس النوع |
| `SetChannelBitrate` | ضبط جودة الصوت (kbps) |
| `SetChannelUserLimit` | الحد الأقصى للأعضاء في الروم |
| `ChannelPermissionRole` `ChannelPermissionMember` | صلاحيات رتبة/عضو على روم معين |
| `CreateThread` `DeleteThread` | فتح / حذف ثريد |
| `ArchiveThread` `UnarchiveThread` | أرشفة / فك أرشفة |
| `LockThread` `UnlockThread` | قفل / فتح ثريد |
| `ChannelInfo` `ListChannels` | معلومات / قائمة الرومات |

### 🟨 الكاتجوريز (6)
`CreateCategory` `DeleteCategory` `RenameCategory` `ReorderCategory` `ListCategories` `CategoryInfo`

### 🟩 الرتب (18)
`CreateRole` `DeleteRole` `RenameRole` `SetRoleColor` `SetRolePosition` `SetRolePermissions` `GrantRole` `RemoveRole` `RoleMembers` `CopyRole` `ToggleRoleHoist` `ToggleRoleMentionable` `RoleInfo` `ListRoles` `GiveRoleToAll` `TakeRoleFromAll` `GiveRoleToBots` `GiveRoleToHumans`

### 🟥 الأعضاء (22)
`KickMember` `BanMember` `SoftBanMember` `UnbanMember` `BanByID` `TimeoutMember` `RemoveTimeout` `RenameMember` `ResetNickname` `VoiceMute` `VoiceUnmute` `VoiceDeafen` `VoiceUndeafen` `DisconnectMember` `MoveMember` `WarnMember` `UnwarnMember` `ShowWarnings` `ClearWarnings` `MemberInfo` `BannedList` `BoostersList`

### 🟪 الرسائل (12)
`ClearMessages` `ClearChannel` `ClearUserMessages` `ClearBotMessages` `Announce` `CreatePoll` `SendEmbed` `PinLastMessage` `UnpinLastMessage` `SendDM` `SendMessage` `ReactLastMessage`

### 🟫 الإنفيتات (3)
`CreateInvite` `ListInvites` `RevokeInvites`

### 🟧 الإيموجي (3)
`AddEmoji` `RemoveEmoji` `ListEmojis`

### 🟦 الويبهوكس (3)
`CreateWebhook` `DeleteWebhook` `ListWebhooks`

### 🎙️ الصوتيات (3)
`VoiceChannelInfo` `MoveAllToVoice` `DisconnectAllVoice`

### 🎲 المتعة (5)
`FlipCoin` `RollDice` `RandomNumber` `ChooseRandom` `BotInfo`

### 🟩 السيرفر (23)
`ServerInfo` `MemberCount` `OnlineCount` `ServerBoostCount` `RenameServer` `SetVerificationLevel` `SetAfkChannel` `SetSystemChannel` `SetWelcome` `WelcomeOff` `SetAutoRole` `AutoRoleOff` `GreetTest` `PermsForMember` `PermsForRole` `HighestRole` `RandomMember` `MemberAvatar` `ServerIcon` `ServerBanner` `ServerSplash` `CreateVanityURL` `ServerAvatar`

---

### 💬 أمثلة بالعامية

```text
@Disor اعمل روم اسمه chat وحطه في كاتجوري Generals
@Disor ادي محمد رتبة VIP وشيل من أحمد رتبة member
@Disor انقل محمد لروم الفويس واكتمه
@Disor حذر محمد عشان السبام
@Disor اعمل استطلاع في العام: احسن لعبة؟ فورتنايت ولا فري فاير
@Disor عمل ويبهوك في announcements اسمه تنبيهات
@Disor ضيف ايموجي اسمه cool من رابط
@Disor عرفني عن السيرفر
@Disor امسح اخر 20 رسالة وقفل روم chat
```

---

## ⚡ أوامر سلايش وأوامر نصية

### 🎛️ أوامر سلايش (بتظهر تلقائيًا)

| الأمر | الوظيفة |
|---|---|
| `/help` | كل مهارات البوت |
| `/status` | حالة البوت + البنق + الموديل |
| `/settings` | إعدادات السيرفر |
| `/warnings [@عضو]` | تحذيرات عضو |

### ⌨️ أوامر نصية

| الأمر | الوظيفة |
|---|---|
| `!help` / `!skills` | كل المهارات + عداد المهارات |
| `!ping` / `!status` | البنق + حالة مفصلة |
| `!welcome #قناة <نص>` / `!welcomeoff` | ترحيب الأعضاء الجدد |
| `!autorole @رتبة` / `!autoroleoff` | رول تلقائي للأعضاء الجدد |
| `!warnings @عضو` / `!settings` | تحذيرات + إعدادات |

---

## 🚀 التشغيل السريع

### المتطلبات
- ✅ Python **3.10+** • ✅ توكن بوت من [Discord Developer Portal](https://discord.com/developers/applications) • ✅ مفتاح Groq مجاني من [console.groq.com](https://console.groq.com)

### 1) الإعداد

```bash
git clone https://github.com/your-username/Disor.git
cd Disor

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp data.example.json data.json  # ثم عدّل data.json
```

### 2) ضبط الـ Intents (مهم جدًا)
من [Discord Developer Portal](https://discord.com/developers/applications) → Bot → فعّل:
- ✅ **Message Content Intent**
- ✅ **Server Members Intent**

### 3) التشغيل

```bash
python main.py
```

> **بديل أفضل**: متغيرات البيئة `DISCORD_TOKEN` و `GROQ_API_KEY` — مهم للاستضافة.

---

## ⚙️ الإعدادات

| المفتاح | الوصف | الافتراضي |
|---|---|---|
| `MODEL` | موديل Groq الرئيسي | `meta-llama/llama-4-scout-17b-16e-instruct` |
| `MODEL_FAST` | موديل سريع للراوتر ⚡ | `""` (نفس الرئيسي) |
| `ALLOWED_CHANNELS` | قنوات يشتغل فيها بس (`[]` = الكل) | `[]` |
| `REQUIRE_MENTION` | يرد بس لما يتعمل له mention | `true` |
| `ADMIN_ONLY` | **المشرفين بس — العضو العادي ممنوع** | `true` |
| `ALLOWED_ROLE` | رول إضافي يعامل كـ مشرف | `""` |
| `AUDIT_CHANNEL` | قناة سجل العمليات (id) | `""` |
| `MAX_HISTORY` | عدد رسائل الذاكرة لكل مستخدم | `12` |
| `JSON_MODE` | JSON mode للـ Parser (أدق) | `true` |
| `ACTION_COOLDOWN` | ثواني بين كل أمر | `3` |
| `RATE_LIMIT_PER_MIN` | أقصى رسائل/دقيقة لكل مستخدم | `8` |
| `PREFIX` | بريفكس الأوامر النصية | `!` |
| `WEB_PORT` | بورت سيرفر الويب keep-alive | `8080` |

---

## 📂 هيكل المشروع

```
Disor/
├── .github/workflows/ci.yml   # GitHub Actions — اختبارات تلقائية
├── tests/                     # 18 اختبار pytest (مفيش إنترنت)
├── assets/                    # بانر + صورة المطوّر
├── main.py                    # نقطة الدخول: الأحداث، الأمان، السلايش، الترحيب
├── ai.py                      # Groq: راوتر/شات/parser/محللو كيانات + retry
├── skills.py                  # 126 مهارة + Dispatch + صلاحيات + تحذيرات
├── memory.py                  # ذاكرة محادثة + سجل طلبات
├── guilddata.py               # إعدادات السيرفرات
├── settings.py                # إعدادات من data.json + متغيرات بيئة
├── web.py                     # سيرفر ويب keep-alive
├── requirements.txt           # المكتبات
├── data.example.json          # نموذج الإعدادات
├── SECURITY.md                # سياسة الثغرات
├── CODE_OF_CONDUCT.md         # قواعد السلوك
├── CONTRIBUTING.md            # دليل المساهمة
├── CHANGELOG.md               # سجل 5 تحديثات
└── LICENSE                    # MIT
```

---

## 🛡️ الأمان

| الحماية | الوصف |
|---|---|
| ⛔ **المشرفين بس** | `ADMIN_ONLY` مفعل — العضو العادي ممنوع نهائيًا |
| 🔑 **صلاحية لكل أمر** | كل مهارة من الـ 126 ليها صلاحية مطلوبة |
| 🚫 **administrator مقموع** | بيتشال من أي صلاحيات تطلع من الموديل |
| 🛡️ **حماية ترتيب الرتب** | ممنوع لمس اللي فوق رتبة البوت أو المالك أو البوت |
| 📋 **سجل عمليات** | Audit log اختياري |
| 🚦 **Rate limit** | حماية من السبام |
| 🔒 **مفاتيحك معزولة** | `data.json` في `.gitignore` |

---

## ⚡ الأداء

- **فايبرات**: استدعاءات LLM في `asyncio.to_thread` — مفيش تجميد
- **كاش ذكي**: بيانات السيرفر بتتحسب مرة وبتتجدد تلقائيًا
- **MODEL_FAST**: موديل سريع للقرارات اللحظية
- **Dispatch جدولي**: بحث فوري عن المهارة + دالة مباشرة
- **Retry تلقائي**: مع backoff عند مشاكل الشبكة

---

## 🧪 الاختبارات و CI

```bash
pip install -r requirements-dev.txt
python -m pytest tests/ -v
```

- 18 اختبار بتشتغل بدون توكن أو إنترنت
- CI على Python 3.10 → 3.13 في كل Push/PR

---

## 📦 النشر على GitHub

```bash
cd Disor
rm -rf __pycache__

git init
git add .
git commit -m "🚀 Disor NX Edition — Discord AI Bot: 126 skills, admin-only, fast & secure"

git branch -M main
git remote add origin https://github.com/username/Disor.git
git push -u origin main
```

> ⚠️ **الأهم**: `data.json` (فيه التوكن) في `.gitignore` — تأكد: `git status --short` ميفضلش فيه.

---

## ❓ أسئلة شائعة

**ليه العضو العادي مش بيرد عليه البوت؟**
ده المطلوب — `ADMIN_ONLY` مفعل افتراضيًا. غيّره لـ `false` لو عايز الكل.

**إزاي أعطي رول معين صلاحية استخدام البوت؟**
حط id/اسم الرول في `ALLOWED_ROLE`.

**البوت بيقول "رتبة البوت لازم تكون فوق"؟**
من Server Settings → Roles سحب رتبة البوت فوق كل الرتب اللي هيديرها.

**ممكن يدي `administrator` لحد؟**
مستحيل — الكود بيمسحها من أي صلاحيات تطلع من الموديل.

**أوامر السلايش مش ظاهرة؟**
بتتزامن تلقائيًا عند أول تشغيل — لو مش ظاهرة أعد تشغيل البوت.

**عايز تستضيفه 24/7؟**
البوت بيشغّل سيرفر ويب keep-alive على `WEB_PORT` — اربطه بـ UptimeRobot:
```
https://your-host:8080/health
```

---

## 🤝 المساهمة

أي مساهمة مرحّب بها! شوف [CONTRIBUTING.md](CONTRIBUTING.md) و [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

```bash
git checkout -b feature/اسم-الميزة
# عدّل + اختبر
python -m pytest tests/ -v
# اعمل Pull Request
```

---

## 📜 الرخصة

مشروع **MIT** — استخدمه وعدّله ووزّعه بحرية. [شوف LICENSE](LICENSE)

---

<div align="center">

### ⭐ لو عجبك المشروع، سيب ستار — ده بيساعدنا جدًا!

<br/>

<table>
<tr>
<td align="center">
<img src="assets/developer-avatar.png" width="70" style="border-radius:50%;border:2px solid #22d3ee;"/>
</td>
<td align="center" style="padding:8px 20px;">
<span style="font-size:18px;font-weight:bold;">تم تطويره بالكامل بواسطة</span><br/>
<span style="font-size:24px;font-weight:900;background:linear-gradient(90deg,#a855f7,#22d3ee);-webkit-background-clip:text;background-clip:text;color:transparent;">NX</span>
<span style="color:#8b93a7;">(e4_1)</span> —
<a href="https://discord.com/users/1254573563160039495" style="color:#22d3ee;text-decoration:none;">Discord ID: 1254573563160039495</a>
</td>
</tr>
</table>

<sub style="color:#8b93a7;">الفكرة مستوحاة من مشروع Disor الأصلي — أعيد بناؤه بالكامل من الصفر بواسطة NX</sub>

<br/>
<br/>

**Disor NX Edition** — مصنوع بـ ❤️ و Python + Groq LLM

</div>
