# 🔒 الأمان — SECURITY.md

## الإبلاغ عن ثغرة أمنية

لو لقيت ثغرة أمنية في Disor (مشكلة صلاحيات، تسريب مفاتيح، حقن برومبت، أي حاجة):

- **متنشرش الثغرة علنًا** في Issues أو Discord قبل ما تتبصلح.
- ابعت رسالة **خاصة** لصاحب الريبو (من GitHub → Profile → Follow/Message) أو افتح **Security Advisory** من:
  `Repository → Security → Report a vulnerability`.

## الالتزامات الأمنية للمشروع

- **مفيش أسرار في الكود**: `TOKEN` و `KEY` دايمًا في `data.json` (معزول في `.gitignore`) أو متغيرات البيئة.
- **المشرفين بس**: وضع `ADMIN_ONLY` مفعل افتراضيًا — العضو العادي ممنوع.
- **صلاحيات لكل أمر**: كل مهارة ليها صلاحية مطلوبة من الطالب.
- **`administrator` مقموع**: `sanitize_perms` بتمسحها من أي صلاحيات تطلع من الموديل.
- **حماية ترتيب الرتب**: `guard()` بتمنع أي عملية على عضو/رتبة فوق رتبة البوت، أو على المالك والبوت نفسه.

## تشغيل آمن

```bash
cp data.example.json data.json   # ومتنساش تملاه
chmod 600 data.json              # Linux: قراءة ليك بس
```

وتأكد إن `data.json` و `warnings.json` و `guild_settings.json` مش متسجلين في git:

```bash
git status --short data.json     # لازم ميفضلش ظاهر
```
