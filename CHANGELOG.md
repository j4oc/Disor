# 📝 سجل التغييرات — CHANGELOG

كل التغييرات المهمة في Disor — نسخة **NX Edition**.

---

## 🔥 V3.5 — "القوة القصوى" (126 مهارة)

### مهارات جديدة (24) — إجمالي 126
- 🎙️ **الصوتيات (3):** `VoiceChannelInfo` • `MoveAllToVoice` • `DisconnectAllVoice`
- 🟩 **رتب جماعية (4):** `GiveRoleToAll` • `TakeRoleFromAll` • `GiveRoleToBots` • `GiveRoleToHumans`
- 🖼️ **براند السيرفر (5):** `ServerIcon` • `ServerBanner` • `ServerSplash` • `CreateVanityURL` • `ServerAvatar`
- 🟦 **قنوات متقدمة (4):** `SetChannelBitrate` • `SetChannelUserLimit` • `ChannelPermissionRole` • `ChannelPermissionMember`
- 🟪 **رسائل (2):** `SendMessage` • `ReactLastMessage`
- 🟥 **أعضاء (1):** `BanByID`
- 🎲 **متعة (5):** `FlipCoin` • `RollDice` • `RandomNumber` • `ChooseRandom` • `BotInfo`

### التصميم
- بانر 3D احترافي بأفاتار المطوّر الحقيقي (بدل الستايل المستقبلي)
- لوجو بوت 3D جديد (أيقونة تطبيق)
- رابط التواصل على ديسكورد في الـ README

### ملاحظة تقنية
- إصلاح تداخل أسماء المهارات: `RemoveRoleFromAll` → `TakeRoleFromAll`

---

## 🔥 V3.0 — "الإنجاز الخرافي" (100+ مهارة)

### المهارات الجديدة (إجمالي 102)
- 🟩 **السيرفر (18 مهارة):**
  `ServerInfo` • `MemberCount` • `OnlineCount` • `ServerBoostCount` • `RenameServer`
  • `SetVerificationLevel` • `SetAfkChannel` • `SetSystemChannel` • `SetWelcome`
  • `WelcomeOff` • `SetAutoRole` • `AutoRoleOff` • `GreetTest` • `PermsForMember`
  • `PermsForRole` • `HighestRole` • `RandomMember` • `MemberAvatar`
- 🟦 **الويبهوكس (3):** `CreateWebhook` • `DeleteWebhook` • `ListWebhooks`
- 🟧 **الإيموجي (3):** `AddEmoji` • `RemoveEmoji` • `ListEmojis`
- 🟫 **الإنفيتات (3):** `CreateInvite` • `ListInvites` • `RevokeInvites`
- 🟪 **الرسائل (10):** `ClearMessages` • `ClearChannel` • `ClearUserMessages`
  • `ClearBotMessages` • `Announce` • `CreatePoll` • `SendEmbed` • `PinLastMessage`
  • `UnpinLastMessage` • `SendDM`
- 🟥 **الأعضاء (21):** كل مهارات الطرد/البان/الكتم + `SoftBanMember` • `RemoveTimeout`
  • `ResetNickname` • `VoiceUnmute` • `VoiceDeafen` • `VoiceUndeafen` • `DisconnectMember`
  • `ClearWarnings` • `MemberInfo` • `BannedList` • `BoostersList`
- 🟩 **الرتب (14):** `RenameRole` • `SetRoleColor` • `SetRolePosition` • `SetRolePermissions`
  • `CopyRole` • `ToggleRoleHoist` • `ToggleRoleMentionable` • `RoleInfo` • `ListRoles`...
- 🟨 **الكاتجوريز (6):** `RenameCategory` • `ReorderCategory` • `ListCategories` • `CategoryInfo`
- 🟦 **القنوات (24):** أنواع منفصلة للإنشاء (نصي/صوتي/فوروم/ستيج) + إدارة ثريدز كاملة + معلومات

### البنية التحتية
- نظام **Dispatch** جدولي — كل مهارة → دالة → صلاحية (أسرع وأسهل للتوسع)
- دالة `_to_thread` لتشغيل استدعاءات الـ LLM في فايبرات
- أمر `!skills` يعرض عداد المهارات الحقيقي

---

## 🚀 V2.5 — "التوسعة العملاقة"

### المهارات الجديدة (إجمالي 75)
- ويبهوكس: إنشاء/حذف/عرض
- إيموجي مخصص: إضافة من رابط/حذف/عرض
- إنفيتات: عرض/حذف جماعي
- رسائل: مسح رسائل عضو/بوتات، إيمبيد منسق، تثبيت/فك تثبيت، رسالة خاصة (DM)
- سيرفر: تغيير اسم السيرفر، مستوى التحقق، روم AFK، قناة النظام

### تحسينات
- أمر `!skills` الجديد
- تحديث الـ About و الـ Schema بشكل كامل

---

## ⚡ V2.4 — "السيطرة الكاملة على الأعضاء"

### المهارات الجديدة (إجمالي 57)
- سوفت بان + فك كتم (RemoveTimeout)
- تصفير اسم العضو + فك كتم صوتي + طرشان/فك طرشان + فصل من الروم الصوتي
- مسح كل تحذيرات عضو (ClearWarnings)
- معلومات العضو الكاملة + قائمة المتبندين + قائمة البوسترز
- فصل مهارات الرتب: لون/ترتيب/صلاحيات/نسخ/عرض منفصل/منشن

### تحسينات
- حماية أقوى في `guard()` لكل العمليات على الأعضاء

---

## 🛠️ V2.3 — "فصل وتنظيم"

### المهارات الجديدة (إجمالي 43)
- أنواع منفصلة لإنشاء الرومات: نصي/صوتي/فوروم/ستيج (بحد أقصى للأعضاء)
- إدارة ثريدز كاملة: فتح/حذف/أرشفة/فك أرشفة/قفل/فتح
- فصل السلو مود (تفعيل/إيقاف) والـ NSFW (تفعيل/إيقاف) والقفل (قفل/فتح)
- مزامنة صلاحيات الروم مع الكاتجوري + معلومات الروم + قائمة الرومات
- كاتجوريز: إعادة تسمية/ترتيب/معلومات/قائمة

### البنية التحتية
- إعادة هيكلة كاملة بنظام **Dispatch** — أساس الـ 100+ مهارة

---

## ✨ V2.2 — "الأساس القوي"

### المهارات الجديدة (إجمالي 35)
- فصل إنشاء الرومات لأنواع (نصي/صوتي)
- نسخ روم (CloneChannel) + ثريد (CreateThread) + عرض أعضاء رتبة (RoleMembers)
- أوامر سلايش: `/help` `/status` `/settings` `/warnings`

### تحسينات
- أوامر سلايش بتتزامن تلقائيًا لكل سيرفر
- تحديث الـ README لنسخة ملونة + بانر

---

## 📜 الإصدارات السابقة

### [v2.1]
- وضع `ADMIN_ONLY` (المشرفين بس) + حماية ترتيب الرتب
- فايبرات للـ LLM + كاش سيرفر + MODEL_FAST + Retry
- نظام تحذيرات + استطلاعات + ترحيب + رول تلقائي + 29 مهارة

### [v2.0]
- إعادة بناء كاملة من النسخة الأصلية: 16 مهارة + إصلاح كل الأمان

### [v1.0]
- Disor الأصلي من MotionIV (مرجع الفكرة)
