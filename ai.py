"""
Disor v2 — طبقة الذكاء الاصطناعي
كل استدعاءات Groq LLM: الراوتر، الشات، مؤكد التنفيذ، الـ Parser (JSON)، ومحللو الكيانات
- retry تلقائي عند مشاكل الشبكة/الحد
- موديل سريع اختياري للراوتر (رد أسرع)
- سياق محادثة للـ Parser (فهم أعمق للإشارات)
"""
import asyncio
import json
import logging
import re
import time

from groq import Groq

log = logging.getLogger("disor.ai")

MAX_INPUT = 1500


# --------------------------------------------------------------------------
# أدوات مساعدة
# --------------------------------------------------------------------------
def extract_json(text: str) -> dict:
    """يستخرج كائن JSON من نص الموديل (حتى لو حط code fences أو كلام حوالينه)."""
    if not text:
        raise ValueError("الموديل رجّع نص فاضي")
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("مفيش JSON object في الرد")
    obj = json.loads(text[start:end + 1])
    if not isinstance(obj, dict):
        raise ValueError("الرد مش object")
    return obj


def _digits_only(text: str) -> str:
    return re.sub(r"\D", "", text or "")


# --------------------------------------------------------------------------
# شارت المهارات اللي الـ Parser بيشتغل بيه
# --------------------------------------------------------------------------
SKILL_SCHEMA = """Available skills (100+) — reply with JSON ONLY, numbered keys for multiple actions (CreateTextChannel0, CreateTextChannel1...).

🟦 CHANNELS:
- CreateTextChannel {"Name","Category":null}
- CreateVoiceChannel {"Name","Category":null,"UserLimit":0}
- CreateForumChannel {"Name","Category":null}
- CreateStageChannel {"Name","Category":null}
- DeleteChannel {"Channel"}
- RenameChannel {"Channel","Name"}
- SetChannelTopic {"Channel","Topic"}
- MoveChannel {"Channel","Category"}
- LockChannel {"Channel"}
- UnlockChannel {"Channel"}
- EnableSlowmode {"Channel","Seconds":5}
- DisableSlowmode {"Channel"}
- EnableNsfw {"Channel"}
- DisableNsfw {"Channel"}
- CloneChannel {"Channel","Name":null}
- SyncChannelPermissions {"Channel"}
- CreateThread {"Channel","Name"}
- DeleteThread {"Channel","Name"}
- ArchiveThread {"Channel","Name"}
- UnarchiveThread {"Channel","Name"}
- LockThread {"Channel","Name"}
- UnlockThread {"Channel","Name"}
- ChannelInfo {"Channel"}
- ListChannels {}
- SetChannelBitrate {"Channel","Kbps":64}
- SetChannelUserLimit {"Channel","Limit":0}
- ChannelPermissionRole {"Channel","Role","Perms":{}}
- ChannelPermissionMember {"Channel","Member","Perms":{}}

🟨 CATEGORIES:
- CreateCategory {"Name"}
- DeleteCategory {"Name"}
- RenameCategory {"Name","NewName"}
- ReorderCategory {"Name","Position"}
- ListCategories {}
- CategoryInfo {"Name"}

🟩 ROLES:
- CreateRole {"Name","Color":"#99AAB5","Position":0,"Perms":{},"Hoist":false,"Mentionable":false}
- DeleteRole {"Name"}
- RenameRole {"Role","Name"}
- SetRoleColor {"Role","Color"}
- SetRolePosition {"Role","Position"}
- SetRolePermissions {"Role","Perms"}
- GrantRole {"Member","Role"}
- RemoveRole {"Member","Role"}
- RoleMembers {"Role"}
- CopyRole {"Role","Name":null}
- ToggleRoleHoist {"Role","Hoist":true}
- ToggleRoleMentionable {"Role","Mentionable":true}
- RoleInfo {"Role"}
- ListRoles {}
- GiveRoleToAll {"Role"}
- TakeRoleFromAll {"Role"}
- GiveRoleToBots {"Role"}
- GiveRoleToHumans {"Role"}

🟥 MEMBERS:
- KickMember {"Member","Reason":""}
- BanMember {"Member","Reason":"","DeleteMessages":false}
- SoftBanMember {"Member","Reason":""}
- UnbanMember {"Member"}
- TimeoutMember {"Member","Minutes":30}
- RemoveTimeout {"Member"}
- RenameMember {"Member","Nickname":""}
- ResetNickname {"Member"}
- VoiceMute {"Member"}
- VoiceUnmute {"Member"}
- VoiceDeafen {"Member"}
- VoiceUndeafen {"Member"}
- DisconnectMember {"Member"}
- MoveMember {"Member","Channel"}
- WarnMember {"Member","Reason":""}
- UnwarnMember {"Member"}
- ShowWarnings {"Member"}
- ClearWarnings {"Member"}
- MemberInfo {"Member"}
- BannedList {}
- BoostersList {}
- BanByID {"UserID","Reason":""}

🟪 MESSAGES:
- ClearMessages {"Count":10}
- ClearChannel {}
- ClearUserMessages {"Member","Count":20}
- ClearBotMessages {"Count":20}
- Announce {"Message","Channel":null}
- CreatePoll {"Question","Options":["a","b"],"Channel":null}
- SendEmbed {"Title","Description","Color":"#5865F2","Channel":null}
- PinLastMessage {"Channel":null}
- UnpinLastMessage {"Channel":null}
- SendDM {"Member","Message"}
- SendMessage {"Message","Channel":null}
- ReactLastMessage {"Emoji","Channel":null}

🟫 INVITES:
- CreateInvite {"Channel","Uses":0,"MaxAge":0}
- ListInvites {}
- RevokeInvites {"Channel":null}

🟧 EMOJIS:
- AddEmoji {"Name","URL"}
- RemoveEmoji {"Name"}
- ListEmojis {}

🟦 WEBHOOKS:
- CreateWebhook {"Channel","Name"}
- DeleteWebhook {"Channel","Name"}
- ListWebhooks {}

🎙️ VOICE:
- VoiceChannelInfo {"Channel"}
- MoveAllToVoice {"Channel"}
- DisconnectAllVoice {}

🎲 FUN:
- FlipCoin {}
- RollDice {"Sides":6}
- RandomNumber {"Min":1,"Max":100}
- ChooseRandom {"Choices":["أ","ب"]}
- BotInfo {}

🟩 SERVER:
- ServerInfo {}
- MemberCount {}
- OnlineCount {}
- ServerBoostCount {}
- RenameServer {"Name"}
- SetVerificationLevel {"Level":"low|medium|high|highest"}
- SetAfkChannel {"Channel"}
- SetSystemChannel {"Channel"}
- SetWelcome {"Channel","Text"}
- WelcomeOff {}
- SetAutoRole {"Role"}
- AutoRoleOff {}
- GreetTest {}
- PermsForMember {"Member"}
- PermsForRole {"Role"}
- HighestRole {"Member"}
- RandomMember {}
- MemberAvatar {"Member"}
- ServerIcon {"URL"}
- ServerBanner {"URL"}
- ServerSplash {"URL"}
- CreateVanityURL {"Code"}
- ServerAvatar {}

RULES (very important):
- Reply with the JSON object ONLY, NEVER add anything else around it.
- For multiple actions use numbered keys: CreateTextChannel0, CreateTextChannel1, ...
- If the request is NOT covered by any skill, reply exactly: {"NoSkill0": {"Reply": "natural Arabic reply saying you can't do it"}}
- NEVER leave a field empty and NEVER invent names. "Channel", "Role", "Category", "Member" must be exact names from Server Information, from the user's message, or from the conversation context.
- Defaults when missing: Color "#99AAB5", Position 0, Perms {}, Reason "", Minutes 30, DeleteMessages false, Count 10, Options ["نعم","لا"], Type "text".
- "Perms" may ONLY contain Discord permission keys listed in "About you" with true/false values.
- NEVER include "administrator" in Perms unless the user EXPLICITLY asks for full admin — and even then the system may refuse.
- "Position" (role): if the user wants a role above another role, use that role's Pos; below it, use Pos - 1 (from Server Information).
- Arabic meanings: Warn=حذر, Poll=استطلاع/تصويت, Thread=ثريد, Webhook=ويبهوك, Hoist=عرض منفصل, Slowmode=سلو مود, NSFW=18+, Embed=رسالة منسقة, SoftBan=سوفت بان, Timeout=كتم."""


# --------------------------------------------------------------------------
# الفئة الرئيسية
# --------------------------------------------------------------------------
class AI:
    def __init__(self, api_key: str, model: str, about: str, json_mode: bool = True, model_fast: str | None = None):
        self.client = Groq(api_key=api_key)
        self.model = model
        self.model_fast = model_fast or model
        self.about = about
        self.json_mode = json_mode

    # ---------- استدعاء عام مع retry ----------
    def complete(self, messages, json_mode=False, temperature=0.3, model=None) -> str:
        last_err = None
        for attempt in range(3):
            kwargs = {
                "model": model or self.model,
                "messages": messages,
                "temperature": temperature,
            }
            if json_mode:
                kwargs["response_format"] = {"type": "json_object"}
            try:
                resp = self.client.chat.completions.create(**kwargs)
                return resp.choices[0].message.content
            except Exception as e:
                last_err = e
                if json_mode and attempt == 0:
                    log.warning("JSON mode فشل (%s) — بنحاول من غيره", e)
                    json_mode = False
                    continue
                log.warning("استدعاء Groq فشل (%s) — محاولة %d", e, attempt + 1)
                time.sleep(1.0 + attempt)  # backoff بسيط
        raise last_err or RuntimeError("استدعاء فشل")

    def _chat(self, system: str, few: list, user: str, temperature=0.0, json_mode=False, model=None) -> str:
        messages = [{"role": "system", "content": system}]
        for u, a in few:
            messages.append({"role": "user", "content": u})
            messages.append({"role": "assistant", "content": a})
        messages.append({"role": "user", "content": user})
        return self.complete(messages, json_mode=json_mode, temperature=temperature, model=model)

    # ---------- 1) الراوتر: يتكلم ولا ينفذ؟ (موديل سريع = رد أسرع) ----------
    def router(self, user_text: str) -> str:
        system = (
            "You decide if the user wants to TALK (chat/ask/info) or wants an ACTION "
            "(something done on the Discord server: create/delete/edit channels, categories, roles, "
            "give/remove roles, kick/ban/unban/timeout/move/warn members, mute, clear messages, "
            "move channels, polls, announcements, invites...).\n"
            "Return ONLY 'USER_IS_MESSAGING' or 'USER_WANTS_ACTION'.\n"
            f"About you:\n{self.about}"
        )
        few = [
            ("عامل اي يسطا", "USER_IS_MESSAGING"),
            ("ممكن تطرد الشخص ده من السيرفر", "USER_WANTS_ACTION"),
            ("الو", "USER_IS_MESSAGING"),
            ("اعملي روم سميه chat", "USER_WANTS_ACTION"),
            ("اهلا", "USER_IS_MESSAGING"),
            ("ممكن تشرحلي يعني ايه اذونات", "USER_IS_MESSAGING"),
            ("اعمل استطلاع في روم العام عن افضل لعبة", "USER_WANTS_ACTION"),
            ("انقل محمد لروم الفويس", "USER_WANTS_ACTION"),
            ("حذر محمد عشان السبام", "USER_WANTS_ACTION"),
            ("شو رايك في فكرة النشر؟", "USER_IS_MESSAGING"),
            ("كم عضو عندنا في السيرفر؟", "USER_IS_MESSAGING"),
        ]
        ans = self._chat(system, few, user_text[:MAX_INPUT], model=self.model_fast).strip().upper()
        return "USER_WANTS_ACTION" if "ACTION" in ans else "USER_IS_MESSAGING"

    # ---------- 2) الشات العادي ----------
    def chat(self, user_text: str, history: list, server_info: str) -> str:
        system = (
            f"{self.about}\n\n"
            "You are chatting with the user now. Help them, answer their questions.\n"
            "Use the Server Information to answer questions about the server (channels, roles, members, counts).\n"
            f"Server Information:\n{server_info}"
        )
        messages = [{"role": "system", "content": system}]
        messages += history[-20:]
        messages.append({"role": "user", "content": user_text[:MAX_INPUT]})
        reply = self.complete(messages, temperature=0.7)
        return (reply or "").strip()[:1990]

    # ---------- 3) مؤكد التنفيذ (رسالة "لحظات") ----------
    def actioner(self, user_text: str) -> str:
        system = (
            "You tell the user you will TRY to do the action, but you're not sure it will succeed.\n"
            "- Say things like 'let me try' or 'give me a sec' or 'on it' — in Egyptian Arabic\n"
            "- NEVER say 'done' or 'completed' because you don't know yet\n"
            "- Keep it short, ONE sentence only"
        )
        few = [
            ("اعملي روم اسمه chat", "لحظات هعمله"),
            ("اطرد هذا الشخص", "دعني اقوم بذلك"),
            ("احذف هذا الروم", "حسنا ثواني..."),
        ]
        return self._chat(system, few, user_text[:MAX_INPUT], model=self.model_fast).strip()[:500]

    # ---------- 4) الـ Parser: الكلام → JSON (مع سياق المحادثة) ----------
    def parse(self, user_text: str, server_info: str, context: list = None) -> dict:
        system = (
            f"About you:\n{self.about}\n\n"
            f"{SKILL_SCHEMA}\n\n"
            f"Server Information:\n{server_info}\n"
            "Reply with the JSON object ONLY."
        )
        few = [
            ("اعملي روم سميه chat",
             '{"CreateTextChannel0": {"Name": "chat", "Category": null}}'),
            ("اعملي روم صوتي اسمه voice 1 وحطه في كاتجوري Generals",
             '{"CreateVoiceChannel0": {"Name": "voice 1", "Category": "Generals"}}'),
            ("اعملي روم اسمه chat وروم تاني اسمه welcome",
             '{"CreateTextChannel0": {"Name": "chat", "Category": null}, "CreateTextChannel1": {"Name": "welcome", "Category": null}}'),
            ("احذف الروم اللي اسمه chat",
             '{"DeleteChannel0": {"Channel": "chat"}}'),
            ("غير اسم الروم chat لـ welcome",
             '{"RenameChannel0": {"Channel": "chat", "Name": "welcome"}}'),
            ("قفل روم chat",
             '{"LockChannel0": {"Channel": "chat"}}'),
            ("افتح روم chat",
             '{"UnlockChannel0": {"Channel": "chat"}}'),
            ("حط سلو مود على روم chat 5 ثواني",
             '{"EnableSlowmode0": {"Channel": "chat", "Seconds": 5}}'),
            ("شيل السلو مود من chat",
             '{"DisableSlowmode0": {"Channel": "chat"}}'),
            ("حط وصف على روم welcome مكتوب فيه الترحيب",
             '{"SetChannelTopic0": {"Channel": "welcome", "Topic": "الترحيب"}}'),
            ("اعملي رتبة اسمها VIP لونها اخضر وصلاحية add_reactions",
             '{"CreateRole0": {"Name": "VIP", "Color": "#00FF00", "Position": 0, "Perms": {"add_reactions": true}}}'),
            ("ادي محمد رتبة VIP",
             '{"GrantRole0": {"Member": "محمد", "Role": "VIP"}}'),
            ("شيل رتبة VIP من محمد",
             '{"RemoveRole0": {"Member": "محمد", "Role": "VIP"}}'),
            ("غير لون رتبة VIP لاحمر",
             '{"SetRoleColor0": {"Role": "VIP", "Color": "#FF0000"}}'),
            ("اطرد محمد من السيرفر",
             '{"KickMember0": {"Member": "محمد", "Reason": ""}}'),
            ("اعمل بان لـ محمد",
             '{"BanMember0": {"Member": "محمد", "Reason": "", "DeleteMessages": false}}'),
            ("اكتم محمد نص ساعة",
             '{"TimeoutMember0": {"Member": "محمد", "Minutes": 30}}'),
            ("غير اسم محمد لـ أبو حميد",
             '{"RenameMember0": {"Member": "محمد", "Nickname": "أبو حميد"}}'),
            ("انقل محمد لروم الفويس",
             '{"MoveMember0": {"Member": "محمد", "Channel": "الفويس"}}'),
            ("اكتم محمد في الفويس",
             '{"VoiceMute0": {"Member": "محمد"}}'),
            ("حذر محمد عشان السبام",
             '{"WarnMember0": {"Member": "محمد", "Reason": "السبام"}}'),
            ("مين لابس رتبة VIP",
             '{"RoleMembers0": {"Role": "VIP"}}'),
            ("اعمل ثريد اسمه أخبار في روم announcements",
             '{"CreateThread0": {"Channel": "announcements", "Name": "أخبار"}}'),
            ("انسخ روم chat وسميه chat2",
             '{"CloneChannel0": {"Channel": "chat", "Name": "chat2"}}'),
            ("اعملي كاتجوري اسمه Generals",
             '{"CreateCategory0": {"Name": "Generals"}}'),
            ("اعمل لينك انفيت لروم chat",
             '{"CreateInvite0": {"Channel": "chat", "Uses": 0, "MaxAge": 0}}'),
            ("اعلن في روم announcements ان السيرفر اتفتح",
             '{"Announce0": {"Message": "ان السيرفر اتفتح", "Channel": "announcements"}}'),
            ("اعمل استطلاع في روم العام: احسن لعبة؟ فورتنايت ولا فري فاير",
             '{"CreatePoll0": {"Question": "احسن لعبة؟", "Options": ["فورتنايت", "فري فاير"], "Channel": "العام"}}'),
            ("ابعت ايمبيد في العام بعنوان ترحيب ووصف اهلا بيكم",
             '{"SendEmbed0": {"Title": "ترحيب", "Description": "اهلا بيكم", "Color": "#5865F2", "Channel": "العام"}}'),
            ("امسح اخر 20 رسالة",
             '{"ClearMessages0": {"Count": 20}}'),
            ("امسح رسائل محمد في الروم ده",
             '{"ClearUserMessages0": {"Member": "محمد", "Count": 20}}'),
            ("عمل ويبهوك في روم announcements اسمه تنبيهات",
             '{"CreateWebhook0": {"Channel": "announcements", "Name": "تنبيهات"}}'),
            ("ضيف ايموجي اسمه cool من رابط https://example.com/cool.png",
             '{"AddEmoji0": {"Name": "cool", "URL": "https://example.com/cool.png"}}'),
            ("عرفني عن السيرفر",
             '{"ServerInfo0": {}}'),
            ("اعطي رتبة member لكل الأعضاء",
             '{"GiveRoleToAll0": {"Role": "member"}}'),
            ("شيل رتبة VIP من كل الأعضاء",
             '{"TakeRoleFromAll0": {"Role": "VIP"}}'),
            ("انقل كل اللي في الفويسات لروم الفويس الرئيسي",
             '{"MoveAllToVoice0": {"Channel": "الفويس الرئيسي"}}'),
            ("اطرد كل اللي في الفويس",
             '{"DisconnectAllVoice0": {}}'),
            ("اعمل بان لليوزر 123456789 عشان سبام",
             '{"BanByID0": {"UserID": "123456789", "Reason": "سبام"}}'),
            ("ارمي نرد",
             '{"RollDice0": {"Sides": 6}}'),
            ("اعمل بانر للسيرفر من رابط https://example.com/banner.png",
             '{"ServerBanner0": {"URL": "https://example.com/banner.png"}}'),
            ("زود صلاحية send_messages لرتبة VIP على روم chat",
             '{"ChannelPermissionRole0": {"Channel": "chat", "Role": "VIP", "Perms": {"send_messages": true}}}'),
            ("ابعت رسالة في العام مكتوب فيها اهلا",
             '{"SendMessage0": {"Channel": "العام", "Message": "اهلا"}}'),
            ("ممكن تعمل حاجة؟",  # مثال NoSkill
             '{"NoSkill0": {"Reply": "مش عندي مهارة لده يا صاحبي 😅"}}'),
        ]

        user = user_text[:MAX_INPUT]
        if context:
            ctx_lines = "\n".join(f"- {c}" for c in context[-3:])
            user = f"Conversation context (recent requests from the same user):\n{ctx_lines}\n\nNow the current request:\n{user}"

        raw = self._chat(system, few, user, temperature=0.2, json_mode=self.json_mode)
        log.info("Parser raw output: %s", raw)
        return extract_json(raw)

    # ---------- 5) محللو الكيانات (اسم → ID) ----------
    def resolve_channel(self, guild, target: str):
        """يرجع كائن القناة أو None — يدعم mention وID واسم مضبوط وLLM fuzzy."""
        target = (target or "").strip()
        m = re.search(r"<#(\d+)>", target)
        if m:
            return guild.get_channel(int(m.group(1)))
        if target.isdigit():
            return guild.get_channel(int(target))
        for ch in guild.channels:
            if ch.name.lower() == target.lower():
                return ch
        names = {c.name: str(c.id) for c in guild.channels}
        if not names:
            return None
        ex = {"شات العام": "111", "voice 1": "222", "welcomes": "333"}
        few = [
            ("شات العام\nchannels: " + str(ex), "111"),
            ("الروم الصوتي رقم 1 ده\nchannels: " + str(ex), "222"),
            ("welcomes | ترحيب\nchannels: " + str(ex), "333"),
        ]
        ans = self._chat(
            "You are given a description of a Discord channel and a list of channels with IDs. "
            "Find the BEST matching channel and return ONLY its id as digits, or NOT_FOUND if none matches. Don't chat.",
            few,
            f"{target}\nchannels: {names}",
        )
        if "NOT_FOUND" in ans.upper():
            return None
        try:
            return guild.get_channel(int(_digits_only(ans)))
        except (ValueError, TypeError):
            return None

    def resolve_category(self, guild, target: str):
        target = (target or "").strip()
        for cat in guild.categories:
            if cat.name.lower() == target.lower():
                return cat
        names = {c.name: str(c.id) for c in guild.categories}
        if not names:
            return None
        ex = {"System": "111", "Generals": "222", "Moderators": "333"}
        few = [
            ("ديه الكاتجوري الرئيسية\ncategories: " + str(ex), "222"),
            ("في كاتجوري هنا الادمنز\ncategories: " + str(ex), "333"),
            ("System\ncategories: " + str(ex), "111"),
        ]
        ans = self._chat(
            "You are given a description of a Discord category and a list of categories with IDs. "
            "Find the BEST matching category and return ONLY its id as digits, or NOT_FOUND if none matches. Don't chat.",
            few,
            f"{target}\ncategories: {names}",
        )
        if "NOT_FOUND" in ans.upper():
            return None
        try:
            return guild.get_channel(int(_digits_only(ans)))
        except (ValueError, TypeError):
            return None

    def resolve_role(self, guild, target: str):
        target = (target or "").strip()
        m = re.search(r"<@&(\d+)>", target)
        if m:
            return guild.get_role(int(m.group(1)))
        if target.isdigit():
            return guild.get_role(int(target))
        for role in guild.roles:
            if role.name.lower() == target.lower():
                return role
        names = {r.name: str(r.id) for r in guild.roles if r.name != "@everyone"}
        if not names:
            return None
        ex = {"vip": "111", "admin": "222", "member": "333"}
        few = [
            ("اللي لونها احمر\nroles: " + str(ex), "111"),
            ("الادمن | admin\nroles: " + str(ex), "222"),
            ("العضو او ممبر\nroles: " + str(ex), "333"),
        ]
        ans = self._chat(
            "You are given a description of a Discord role and a list of roles with IDs. "
            "Find the BEST matching role and return ONLY its id as digits, or NOT_FOUND if none matches. Don't chat.",
            few,
            f"{target}\nroles: {names}",
        )
        if "NOT_FOUND" in ans.upper():
            return None
        try:
            return guild.get_role(int(_digits_only(ans)))
        except (ValueError, TypeError):
            return None

    async def resolve_member(self, guild, target: str):
        target = (target or "").strip()
        m = re.search(r"<@!?(\d+)>", target)
        if m:
            return await self._get_member(guild, int(m.group(1)))
        if target.isdigit():
            return await self._get_member(guild, int(target))
        low = target.lower()
        for mem in guild.members:
            if mem.name == target or (mem.global_name and mem.global_name == target) or (mem.nick and mem.nick == target):
                return mem
        for mem in guild.members:
            if (mem.global_name or "").lower() == low or mem.name.lower() == low:
                return mem
        for mem in guild.members:  # fuzzy
            if low in (mem.global_name or "").lower() or low in mem.name.lower():
                return mem
        if not guild.members:
            return None
        lst = "\n".join(f"{m.name} | {m.global_name or m.name} | {m.nick or ''} ({m.id})" for m in guild.members[:200])
        fake = "ahmed | Hamada |  (111)\nmostafa | MOSTAFA IZ |  (222)\nmohammed | Zigzag 0C |  (333)"
        few = [
            ("حماده\nMembers:\n" + fake, "111"),
            ("mostafa iz\nMembers:\n" + fake, "222"),
            ("Zigzag\nMembers:\n" + fake, "333"),
        ]
        ans = await asyncio.to_thread(
            self._chat,
            "You are given a description of a Discord member and a members list with IDs. "
            "Return ONLY the matching member's id as digits, or NOT_FOUND if none matches. Don't chat.",
            few,
            f"{target}\nMembers:\n{lst}",
        )
        if "NOT_FOUND" in ans.upper():
            return None
        try:
            return await self._get_member(guild, int(_digits_only(ans)))
        except (ValueError, TypeError):
            return None

    async def _get_member(self, guild, uid: int):
        mem = guild.get_member(uid)
        if mem is None:
            try:
                mem = await guild.fetch_member(uid)
            except Exception:
                return None
        return mem
