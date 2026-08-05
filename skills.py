"""
Disor v2.3+ — طبقة تنفيذ الأوامر (المهارات)
- نظام Dispatch جدول: كل مهارة → دالة → صلاحية مطلوبة
- 100+ مهارة مقسمة على: قنوات، كاتجوريز، رتب، أعضاء، رسائل، إنفيتات، إيموجي، ويبهوكس، سيرفر
- تعقيم الصلاحيات: administrator ممنوع تلقائيًا
- حماية ترتيب الرتب: البوت ميقدرش يعدل على اللي فوقه
- نظام تحذيرات محلي (warnings.json)
"""
import asyncio
import json
import os
import random
import time
from datetime import timedelta

import aiohttp
import discord

# ==========================================================================
# خريطة الصلاحيات: كل مهارة → الصلاحية المطلوبة من الطالب
# ==========================================================================
SKILL_PERM_MAP = {
    # ---- A) القنوات (24) ----
    "CreateTextChannel": "manage_channels",
    "CreateVoiceChannel": "manage_channels",
    "CreateForumChannel": "manage_channels",
    "CreateStageChannel": "manage_channels",
    "DeleteChannel": "manage_channels",
    "RenameChannel": "manage_channels",
    "SetChannelTopic": "manage_channels",
    "MoveChannel": "manage_channels",
    "LockChannel": "manage_channels",
    "UnlockChannel": "manage_channels",
    "EnableSlowmode": "manage_channels",
    "DisableSlowmode": "manage_channels",
    "EnableNsfw": "manage_channels",
    "DisableNsfw": "manage_channels",
    "CloneChannel": "manage_channels",
    "SyncChannelPermissions": "manage_channels",
    "CreateThread": "create_public_threads",
    "DeleteThread": "manage_threads",
    "ArchiveThread": "manage_threads",
    "UnarchiveThread": "manage_threads",
    "LockThread": "manage_threads",
    "UnlockThread": "manage_threads",
    "ChannelInfo": "view_channel",
    "ListChannels": "view_channel",
    "SetChannelBitrate": "manage_channels",
    "SetChannelUserLimit": "manage_channels",
    "ChannelPermissionRole": "manage_channels",
    "ChannelPermissionMember": "manage_channels",

    # ---- B) الكاتجوريز (6) ----
    "CreateCategory": "manage_channels",
    "DeleteCategory": "manage_channels",
    "RenameCategory": "manage_channels",
    "ReorderCategory": "manage_channels",
    "ListCategories": "view_channel",
    "CategoryInfo": "view_channel",

    # ---- C) الرتب (14) ----
    "CreateRole": "manage_roles",
    "DeleteRole": "manage_roles",
    "RenameRole": "manage_roles",
    "SetRoleColor": "manage_roles",
    "SetRolePosition": "manage_roles",
    "SetRolePermissions": "manage_roles",
    "GrantRole": "manage_roles",
    "RemoveRole": "manage_roles",
    "RoleMembers": "manage_roles",
    "CopyRole": "manage_roles",
    "ToggleRoleHoist": "manage_roles",
    "ToggleRoleMentionable": "manage_roles",
    "RoleInfo": "manage_roles",
    "ListRoles": "manage_roles",
    "GiveRoleToAll": "manage_roles",
    "TakeRoleFromAll": "manage_roles",
    "GiveRoleToBots": "manage_roles",
    "GiveRoleToHumans": "manage_roles",

    # ---- D) الأعضاء (21) ----
    "KickMember": "kick_members",
    "BanMember": "ban_members",
    "SoftBanMember": "ban_members",
    "UnbanMember": "ban_members",
    "TimeoutMember": "moderate_members",
    "RemoveTimeout": "moderate_members",
    "RenameMember": "manage_nicknames",
    "ResetNickname": "manage_nicknames",
    "VoiceMute": "mute_members",
    "VoiceUnmute": "mute_members",
    "VoiceDeafen": "deafen_members",
    "VoiceUndeafen": "deafen_members",
    "DisconnectMember": "move_members",
    "MoveMember": "move_members",
    "WarnMember": "moderate_members",
    "UnwarnMember": "moderate_members",
    "ShowWarnings": "moderate_members",
    "ClearWarnings": "moderate_members",
    "MemberInfo": "view_channel",
    "BannedList": "ban_members",
    "BoostersList": "view_channel",
    "BanByID": "ban_members",

    # ---- E) الرسائل (10) ----
    "ClearMessages": "manage_messages",
    "ClearChannel": "manage_messages",
    "ClearUserMessages": "manage_messages",
    "ClearBotMessages": "manage_messages",
    "Announce": "manage_guild",
    "CreatePoll": "manage_messages",
    "SendEmbed": "manage_messages",
    "PinLastMessage": "manage_messages",
    "UnpinLastMessage": "manage_messages",
    "SendDM": "manage_guild",
    "SendMessage": "manage_messages",
    "ReactLastMessage": "manage_messages",

    # ---- F) الإنفيتات (3) ----
    "CreateInvite": "create_instant_invite",
    "ListInvites": "manage_guild",
    "RevokeInvites": "manage_guild",

    # ---- G) الإيموجي (3) ----
    "AddEmoji": "manage_expressions",
    "RemoveEmoji": "manage_expressions",
    "ListEmojis": "manage_expressions",

    # ---- H) الويبهوكس (3) ----
    "CreateWebhook": "manage_webhooks",
    "DeleteWebhook": "manage_webhooks",
    "ListWebhooks": "manage_webhooks",

    # ---- J) الصوتيات (3) ----
    "VoiceChannelInfo": "view_channel",
    "MoveAllToVoice": "move_members",
    "DisconnectAllVoice": "move_members",

    # ---- K) المتعة (5) ----
    "FlipCoin": "view_channel",
    "RollDice": "view_channel",
    "RandomNumber": "view_channel",
    "ChooseRandom": "view_channel",
    "BotInfo": "view_channel",

    # ---- I) السيرفر (18) ----
    "ServerInfo": "view_channel",
    "MemberCount": "view_channel",
    "OnlineCount": "view_channel",
    "ServerBoostCount": "view_channel",
    "RenameServer": "manage_guild",
    "SetVerificationLevel": "manage_guild",
    "SetAfkChannel": "manage_guild",
    "SetSystemChannel": "manage_guild",
    "SetWelcome": "manage_guild",
    "WelcomeOff": "manage_guild",
    "SetAutoRole": "manage_guild",
    "AutoRoleOff": "manage_guild",
    "GreetTest": "manage_guild",
    "PermsForMember": "view_channel",
    "PermsForRole": "view_channel",
    "HighestRole": "view_channel",
    "RandomMember": "view_channel",
    "MemberAvatar": "view_channel",
    "ServerIcon": "manage_guild",
    "ServerBanner": "manage_guild",
    "ServerSplash": "manage_guild",
    "CreateVanityURL": "manage_guild",
    "ServerAvatar": "view_channel",
}

MAX_TIMEOUT_MINUTES = 40320          # 28 يوم
POLL_EMOJIS = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
VERIF_LEVELS = {"none": 0, "low": 1, "medium": 2, "high": 3, "highest": 4,
                "0": 0, "1": 1, "2": 2, "3": 3, "4": 4}

# ==========================================================================
# نظام التحذيرات (ملف محلي)
# ==========================================================================
WARN_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "warnings.json")
_warn_data = None


def _load_warns() -> dict:
    global _warn_data
    if _warn_data is None:
        try:
            with open(WARN_FILE, "r", encoding="utf-8") as f:
                _warn_data = json.load(f)
        except Exception:
            _warn_data = {}
    return _warn_data


def _save_warns():
    with open(WARN_FILE, "w", encoding="utf-8") as f:
        json.dump(_load_warns(), f, ensure_ascii=False, indent=2)


def _guild_warns(guild_id: int) -> dict:
    return _load_warns().setdefault(str(guild_id), {})


def add_warning(guild_id: int, member_id: int, reason: str, by: str) -> list:
    gw = _guild_warns(guild_id)
    lst = gw.setdefault(str(member_id), [])
    lst.append({"reason": reason, "by": by, "ts": time.time()})
    _save_warns()
    return lst


def remove_last_warning(guild_id: int, member_id: int):
    gw = _guild_warns(guild_id)
    lst = gw.get(str(member_id))
    if lst:
        removed = lst.pop()
        if not lst:
            gw.pop(str(member_id), None)
        _save_warns()
        return removed
    return None


def list_warnings(guild_id: int, member_id: int) -> list:
    return _guild_warns(guild_id).get(str(member_id), [])


def clear_all_warnings(guild_id: int, member_id: int) -> int:
    gw = _guild_warns(guild_id)
    lst = gw.pop(str(member_id), [])
    if lst:
        _save_warns()
    return len(lst)


# ==========================================================================
# أدوات مساعدة
# ==========================================================================
def pget(payload, *keys, default=None):
    """قراءة آمنة من الـ payload مع دعم أسماء مفاتيح مختلفة."""
    if not isinstance(payload, dict):
        return default
    for k in keys:
        if k in payload:
            return payload[k]
    return default


def sanitize_perms(raw) -> dict:
    """تعقيم الصلاحيات: بس مفاتيح صالحة وboolean، والـ administrator بيتشال دائمًا."""
    if not isinstance(raw, dict):
        return {}
    clean = {}
    for k, v in raw.items():
        if k in discord.Permissions.VALID_FLAGS and isinstance(v, bool):
            clean[k] = v
    clean.pop("administrator", None)  # 🔒 خط الدفاع الأخير
    return clean


def has_permission(member: discord.Member, perm: str) -> bool:
    if member == member.guild.owner:
        return True
    if member.guild_permissions.administrator:
        return True
    return bool(getattr(member.guild_permissions, perm, False))


def guard(target: discord.Member, invoker: discord.Member, guild: discord.Guild, action_word: str) -> str | None:
    """فحوصات الحماية قبل أي عملية على عضو."""
    if target == invoker:
        return f"مش ممكن {action_word} نفسك 😅"
    if target == guild.owner:
        return f"مش ممكن {action_word} مالك السيرفر"
    if target == guild.me:
        return f"مش ممكن {action_word} البوت نفسه"
    if target.top_role >= guild.me.top_role:
        return f"رتبة البوت لازم تكون فوق رتبة {target.mention} عشان تقدر {action_word}و"
    return None


def _ok(text): return {"ok": True, "text": text}
def _fail(text): return {"ok": False, "text": text}


def _color(value, default="#99AAB5"):
    value = str(value or default).strip()
    if not value.startswith("#"):
        value = "#" + value
    try:
        return discord.Colour.from_str(value)
    except ValueError:
        return discord.Colour.from_str(default)


async def _to_thread(fn, *args):
    """تنفيذ استدعاء LLM في فايبر — مش بيبلوك الأحداث."""
    return await asyncio.to_thread(fn, *args)


def _resolve_target(guild, payload, *keys) -> str:
    return str(pget(payload, *keys, default="")).strip()


async def _fetch_image(url: str):
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(url) as r:
                if r.status == 200:
                    return await r.read()
    except Exception:
        return None
    return None


def _format_warns(lst: list, mention: str) -> str:
    lines = [f"⚠️ تحذيرات {mention} ({len(lst)}):"]
    for i, w in enumerate(lst, 1):
        ts = time.strftime("%Y-%m-%d %H:%M", time.localtime(w["ts"]))
        lines.append(f"{i}. {w['reason']} — بواسطة {w['by']} ({ts})")
    return "\n".join(lines)


# ==========================================================================
# A) القنوات — 24 مهارة
# ==========================================================================
async def _create_channel(guild, ai, payload, invoker, channel, ctype: str, label: str):
    name = _resolve_target(guild, payload, "Name", "name") or f"new-{ctype}"
    cat_name = pget(payload, "Category", "category")
    kwargs = {}
    if ctype == "voice" and pget(payload, "UserLimit", default=0):
        try:
            kwargs["user_limit"] = max(0, min(int(pget(payload, "UserLimit")), 99))
        except (TypeError, ValueError):
            pass
    create = {
        "text": guild.create_text_channel,
        "voice": guild.create_voice_channel,
        "forum": guild.create_forum_channel,
        "stage": guild.create_stage_channel,
    }[ctype]
    ch = await create(name=name, **kwargs)
    msg = f"تم إنشاء الروم `{name}` ({label})"
    if cat_name:
        cat = await _to_thread(ai.resolve_category, guild, str(cat_name))
        if cat:
            await ch.edit(category=cat)
            msg += f" في كاتجوري `{cat.name}`"
        else:
            msg += " ⚠️ ملقيتش الكاتجوري — اتضاف من غيرها"
    return _ok(msg)


async def h_create_text(guild, ai, payload, invoker, channel):
    return await _create_channel(guild, ai, payload, invoker, channel, "text", "نصي")


async def h_create_voice(guild, ai, payload, invoker, channel):
    return await _create_channel(guild, ai, payload, invoker, channel, "voice", "صوتي")


async def h_create_forum(guild, ai, payload, invoker, channel):
    return await _create_channel(guild, ai, payload, invoker, channel, "forum", "فوروم")


async def h_create_stage(guild, ai, payload, invoker, channel):
    return await _create_channel(guild, ai, payload, invoker, channel, "stage", "ستيج")


async def h_delete_channel(guild, ai, payload, invoker, channel):
    ch = await _to_thread(ai.resolve_channel, guild, _resolve_target(guild, payload, "Channel", "Name"))
    if ch is None:
        return _fail("مش لاقي الروم المطلوب")
    name = ch.name
    await ch.delete()
    return _ok(f"تم حذف الروم `{name}`")


async def h_rename_channel(guild, ai, payload, invoker, channel):
    ch = await _to_thread(ai.resolve_channel, guild, _resolve_target(guild, payload, "Channel"))
    new_name = _resolve_target(guild, payload, "Name", "NewName")
    if ch is None:
        return _fail("مش لاقي الروم المطلوب")
    if not new_name:
        return _fail("مفيش الاسم الجديد")
    await ch.edit(name=new_name)
    return _ok(f"اتغير اسم الروم من `{ch.name}` إلى `{new_name}`")


async def h_set_topic(guild, ai, payload, invoker, channel):
    ch = await _to_thread(ai.resolve_channel, guild, _resolve_target(guild, payload, "Channel"))
    if ch is None:
        return _fail("مش لاقي الروم المطلوب")
    topic = _resolve_target(guild, payload, "Topic", "topic")
    await ch.edit(topic=topic or None)
    return _ok(f"تم تحديث وصف الروم `{ch.name}`")


async def h_move_channel(guild, ai, payload, invoker, channel):
    ch = await _to_thread(ai.resolve_channel, guild, _resolve_target(guild, payload, "Channel"))
    cat = await _to_thread(ai.resolve_category, guild, _resolve_target(guild, payload, "Category"))
    if ch is None:
        return _fail("مش لاقي الروم المطلوب")
    if cat is None:
        return _fail("مش لاقي الكاتجوري المطلوبة")
    await ch.edit(category=cat)
    return _ok(f"اتنقل الروم `{ch.name}` لكاتجوري `{cat.name}`")


async def _lock(guild, ai, payload, invoker, channel, locked: bool):
    ch = await _to_thread(ai.resolve_channel, guild, _resolve_target(guild, payload, "Channel"))
    if ch is None:
        return _fail("مش لاقي الروم المطلوب")
    everyone = guild.default_role
    if isinstance(ch, (discord.VoiceChannel, discord.StageChannel)):
        ow = discord.PermissionOverwrite(connect=locked, speak=locked)
        what = "الكلام"
    else:
        ow = discord.PermissionOverwrite(send_messages=locked)
        what = "الكتابة"
    await ch.set_permissions(everyone, overwrite=ow)
    return _ok(f"تم {'قفل' if locked else 'فتح'} الروم `{ch.name}` ({what})")


async def h_lock(guild, ai, payload, invoker, channel):
    return await _lock(guild, ai, payload, invoker, channel, False)


async def h_unlock(guild, ai, payload, invoker, channel):
    return await _lock(guild, ai, payload, invoker, channel, True)


async def _slowmode(guild, ai, payload, invoker, channel, seconds):
    ch = await _to_thread(ai.resolve_channel, guild, _resolve_target(guild, payload, "Channel"))
    if ch is None:
        return _fail("مش لاقي الروم المطلوب")
    if not isinstance(ch, discord.TextChannel):
        return _fail("السلو مود بيشتغل بس على الرومات النصية")
    await ch.edit(slowmode_delay=seconds)
    return _ok(f"تم ضبط السلو مود على `{ch.name}` ({seconds}s)" if seconds else f"تم إيقاف السلو مود على `{ch.name}`")


async def h_slowmode_on(guild, ai, payload, invoker, channel):
    try:
        sec = max(0, min(int(pget(payload, "Seconds", "seconds", default=5)), 21600))
    except (TypeError, ValueError):
        sec = 5
    return await _slowmode(guild, ai, payload, invoker, channel, sec)


async def h_slowmode_off(guild, ai, payload, invoker, channel):
    return await _slowmode(guild, ai, payload, invoker, channel, 0)


async def _nsfw(guild, ai, payload, invoker, channel, value: bool):
    ch = await _to_thread(ai.resolve_channel, guild, _resolve_target(guild, payload, "Channel"))
    if ch is None:
        return _fail("مش لاقي الروم المطلوب")
    if not isinstance(ch, discord.TextChannel):
        return _fail("الـ NSFW بيشتغل بس على الرومات النصية")
    await ch.edit(nsfw=value)
    return _ok(f"تم تفعيل NSFW على `{ch.name}` 🔞" if value else f"تم إيقاف NSFW على `{ch.name}`")


async def h_nsfw_on(guild, ai, payload, invoker, channel):
    return await _nsfw(guild, ai, payload, invoker, channel, True)


async def h_nsfw_off(guild, ai, payload, invoker, channel):
    return await _nsfw(guild, ai, payload, invoker, channel, False)


async def h_clone_channel(guild, ai, payload, invoker, channel):
    ch = await _to_thread(ai.resolve_channel, guild, _resolve_target(guild, payload, "Channel"))
    if ch is None:
        return _fail("مش لاقي الروم المطلوب")
    new_name = _resolve_target(guild, payload, "Name", "name") or (ch.name + "-copy")
    new_ch = await ch.clone(name=new_name)
    return _ok(f"تم نسخ الروم `{ch.name}` → `{new_ch.name}`")


async def h_sync_channel(guild, ai, payload, invoker, channel):
    ch = await _to_thread(ai.resolve_channel, guild, _resolve_target(guild, payload, "Channel"))
    if ch is None:
        return _fail("مش لاقي الروم المطلوب")
    if ch.category is None:
        return _fail("الروم ده مش في كاتجوري عشان يتزامن معاها")
    await ch.edit(sync_permissions=True)
    return _ok(f"تمت مزامنة صلاحيات `{ch.name}` مع كاتجوري `{ch.category.name}`")


# ---- الثريدز ----
async def _find_thread(ch, name: str):
    for t in getattr(ch, "threads", []):
        if t.name.lower() == name.lower():
            return t
    return None


async def _thread_target(guild, ai, payload):
    ch = await _to_thread(ai.resolve_channel, guild, _resolve_target(guild, payload, "Channel"))
    if ch is None:
        return None, _fail("مش لاقي الروم المطلوب")
    tname = _resolve_target(guild, payload, "Name", "name")
    if not tname:
        return None, _fail("مفيش اسم الثريد")
    thread = await _find_thread(ch, tname)
    if thread is None:
        return None, _fail(f"مفيش ثريد باسم `{tname}` في `{ch.name}`")
    return thread, None


async def h_create_thread(guild, ai, payload, invoker, channel):
    ch = await _to_thread(ai.resolve_channel, guild, _resolve_target(guild, payload, "Channel"))
    if ch is None:
        return _fail("مش لاقي الروم المطلوب")
    if not isinstance(ch, discord.TextChannel):
        return _fail("الثريدز بتتفتح بس في الرومات النصية")
    name = _resolve_target(guild, payload, "Name", "name") or "thread"
    thread = await ch.create_thread(name=name, type=discord.ChannelType.public_thread)
    return _ok(f"تم فتح ثريد `{thread.name}` في `{ch.name}` 🧵")


async def h_delete_thread(guild, ai, payload, invoker, channel):
    thread, err = await _thread_target(guild, ai, payload)
    if err:
        return err
    name = thread.name
    await thread.delete()
    return _ok(f"تم حذف الثريد `{name}`")


async def h_archive_thread(guild, ai, payload, invoker, channel):
    thread, err = await _thread_target(guild, ai, payload)
    if err:
        return err
    await thread.edit(archived=True)
    return _ok(f"تم أرشفة الثريد `{thread.name}` 📦")


async def h_unarchive_thread(guild, ai, payload, invoker, channel):
    thread, err = await _thread_target(guild, ai, payload)
    if err:
        return err
    await thread.edit(archived=False)
    return _ok(f"تم فك أرشفة الثريد `{thread.name}`")


async def h_lock_thread(guild, ai, payload, invoker, channel):
    thread, err = await _thread_target(guild, ai, payload)
    if err:
        return err
    await thread.edit(locked=True)
    return _ok(f"تم قفل الثريد `{thread.name}` 🔒")


async def h_unlock_thread(guild, ai, payload, invoker, channel):
    thread, err = await _thread_target(guild, ai, payload)
    if err:
        return err
    await thread.edit(locked=False)
    return _ok(f"تم فتح الثريد `{thread.name}`")


async def h_channel_info(guild, ai, payload, invoker, channel):
    ch = await _to_thread(ai.resolve_channel, guild, _resolve_target(guild, payload, "Channel", "Name"))
    if ch is None:
        return _fail("مش لاقي الروم المطلوب")
    kind = type(ch).__name__.replace("Channel", "")
    lines = [
        f"📁 **{ch.name}** (`{ch.id}`)",
        f"النوع: {kind}",
        f"الكاتجوري: {ch.category.name if ch.category else '—'}",
    ]
    if isinstance(ch, discord.TextChannel):
        lines.append(f"الوصف: {ch.topic or '—'}")
        lines.append(f"سلو مود: {ch.slowmode_delay}s" if ch.slowmode_delay else "سلو مود: معطل")
        lines.append(f"NSFW: {'✅' if ch.nsfw else '❌'}")
        lines.append(f"ثريدز: {len(ch.threads)}")
    elif isinstance(ch, discord.VoiceChannel):
        lines.append(f"الحد الأقصى: {ch.user_limit or '∞'}")
    return _ok("\n".join(lines))


async def h_list_channels(guild, ai, payload, invoker, channel):
    lines = ["📁 **القنوات:**"]
    for cat in guild.categories:
        lines.append(f"📂 {cat.name}")
        for ch in cat.channels:
            lines.append(f"  - {ch.mention}")
    for ch in guild.channels:
        if ch.category is None:
            lines.append(f"- {ch.mention}")
    return _ok("\n".join(lines[:40]))


async def h_set_voice_bitrate(guild, ai, payload, invoker, channel):
    ch = await _to_thread(ai.resolve_channel, guild, _resolve_target(guild, payload, "Channel"))
    if ch is None:
        return _fail("مش لاقي الروم المطلوب")
    if not isinstance(ch, discord.VoiceChannel):
        return _fail("البيتريت بيشتغل على رومات صوتية بس")
    try:
        kbps = int(pget(payload, "Kbps", "kbps", "Bitrate", "bitrate", default=64))
    except (TypeError, ValueError):
        kbps = 64
    kbps = max(8, min(kbps, 384))
    await ch.edit(bitrate=kbps * 1000)
    return _ok(f"تم ضبط البيتريت على `{ch.name}`: {kbps} kbps")


async def h_set_voice_limit(guild, ai, payload, invoker, channel):
    ch = await _to_thread(ai.resolve_channel, guild, _resolve_target(guild, payload, "Channel"))
    if ch is None:
        return _fail("مش لاقي الروم المطلوب")
    if not isinstance(ch, discord.VoiceChannel):
        return _fail("الحد الأقصى بيشتغل على رومات صوتية بس")
    try:
        limit = int(pget(payload, "Limit", "limit", "UserLimit", "user_limit", default=0))
    except (TypeError, ValueError):
        limit = 0
    limit = max(0, min(limit, 99))
    await ch.edit(user_limit=limit or None)
    return _ok(f"تم ضبط الحد الأقصى على `{ch.name}`: {limit or '∞'}")


async def _channel_perm(guild, ai, payload, invoker, target):
    ch = await _to_thread(ai.resolve_channel, guild, _resolve_target(guild, payload, "Channel"))
    if ch is None:
        return _fail("مش لاقي الروم المطلوب")
    if target is None:
        return _fail("مش لاقي الرتبة/العضو المطلوب")
    perms = sanitize_perms(pget(payload, "Perms", "perms", default={}))
    if not perms:
        await ch.set_permissions(target, overwrite=None)
        return _ok(f"اتشالت كل صلاحيات {target.mention} الخاصة على `{ch.name}`")
    await ch.set_permissions(target, overwrite=discord.PermissionOverwrite(**perms))
    keys = ", ".join(perms.keys())
    return _ok(f"تم تعديل صلاحيات {target.mention} على `{ch.name}` ({keys})")


async def h_channel_perm_role(guild, ai, payload, invoker, channel):
    role = await _to_thread(ai.resolve_role, guild, _resolve_target(guild, payload, "Role", "Name"))
    return await _channel_perm(guild, ai, payload, invoker, role)


async def h_channel_perm_member(guild, ai, payload, invoker, channel):
    member = await ai.resolve_member(guild, _resolve_target(guild, payload, "Member", "member"))
    return await _channel_perm(guild, ai, payload, invoker, member)


# ==========================================================================
# B) الكاتجوريز — 6 مهارات
# ==========================================================================
async def h_create_category(guild, ai, payload, invoker, channel):
    name = _resolve_target(guild, payload, "Name", "name") or "new-category"
    cat = await guild.create_category(name=name)
    return _ok(f"تم إنشاء الكاتجوري `{cat.name}`")


async def h_delete_category(guild, ai, payload, invoker, channel):
    cat = await _to_thread(ai.resolve_category, guild, _resolve_target(guild, payload, "Name", "name"))
    if cat is None:
        return _fail("مش لاقي الكاتجوري المطلوبة")
    if len(cat.channels) > 0:
        return _fail(f"الكاتجوري `{cat.name}` فيها {len(cat.channels)} روم — احذف الرومات الأول (مبحذفش رومات بالعافية 🛡️)")
    name = cat.name
    await cat.delete()
    return _ok(f"تم حذف الكاتجوري `{name}`")


async def h_rename_category(guild, ai, payload, invoker, channel):
    cat = await _to_thread(ai.resolve_category, guild, _resolve_target(guild, payload, "Name", "name"))
    new_name = _resolve_target(guild, payload, "NewName", "new_name")
    if cat is None:
        return _fail("مش لاقي الكاتجوري المطلوبة")
    if not new_name:
        return _fail("مفيش الاسم الجديد")
    await cat.edit(name=new_name)
    return _ok(f"اتغير اسم الكاتجوري إلى `{new_name}`")


async def h_reorder_category(guild, ai, payload, invoker, channel):
    cat = await _to_thread(ai.resolve_category, guild, _resolve_target(guild, payload, "Name", "name"))
    if cat is None:
        return _fail("مش لاقي الكاتجوري المطلوبة")
    try:
        pos = int(pget(payload, "Position", "position", default=0))
    except (TypeError, ValueError):
        return _fail("الترتيب لازم يكون رقم")
    pos = max(0, min(pos, len(guild.categories) - 1))
    await cat.edit(position=pos)
    return _ok(f"تم نقل الكاتجوري `{cat.name}` للترتيب {pos}")


async def h_list_categories(guild, ai, payload, invoker, channel):
    lines = [f"📂 **الكاتجوريز ({len(guild.categories)}):**"]
    for i, c in enumerate(guild.categories):
        lines.append(f"{i + 1}. {c.name} ({len(c.channels)} روم)")
    return _ok("\n".join(lines))


async def h_category_info(guild, ai, payload, invoker, channel):
    cat = await _to_thread(ai.resolve_category, guild, _resolve_target(guild, payload, "Name", "name"))
    if cat is None:
        return _fail("مش لاقي الكاتجوري المطلوبة")
    lines = [f"📂 **{cat.name}** (`{cat.id}`)", f"الرومات ({len(cat.channels)}):"]
    lines += [f"- {ch.name}" for ch in cat.channels]
    return _ok("\n".join(lines[:40]))


# ==========================================================================
# C) الرتب — 14 مهارة
# ==========================================================================
async def h_create_role(guild, ai, payload, invoker, channel):
    name = _resolve_target(guild, payload, "Name", "name") or "new-role"
    color = _color(pget(payload, "Color", "color", default="#99AAB5"))
    perms = sanitize_perms(pget(payload, "Perms", "perms", default={}))
    try:
        pos = int(pget(payload, "Position", "position", default=0))
    except (TypeError, ValueError):
        pos = 0
    role = await guild.create_role(
        name=name, colour=color, permissions=discord.Permissions(**perms),
        hoist=bool(pget(payload, "Hoist", default=False)),
        mentionable=bool(pget(payload, "Mentionable", default=False)),
    )
    if pos > 0:
        pos = min(pos, len(guild.roles) - 2)
        try:
            await guild.edit_role_positions(positions={role: pos})
        except discord.Forbidden:
            pass
    msg = f"تم إنشاء الرتبة `{role.name}`"
    if perms:
        msg += f" مع {len(perms)} صلاحية"
    return _ok(msg)


async def h_delete_role(guild, ai, payload, invoker, channel):
    role = await _to_thread(ai.resolve_role, guild, _resolve_target(guild, payload, "Name", "name"))
    if role is None:
        return _fail("مش لاقي الرتبة المطلوبة")
    if role == guild.default_role:
        return _fail("مش ممكن تحذف رتبة @everyone")
    if role >= guild.me.top_role:
        return _fail(f"رتبة البوت لازم تكون فوق `{role.name}` عشان تحذفها")
    name = role.name
    await role.delete()
    return _ok(f"تم حذف الرتبة `{name}`")


async def h_rename_role(guild, ai, payload, invoker, channel):
    role = await _to_thread(ai.resolve_role, guild, _resolve_target(guild, payload, "Role", "Name"))
    new_name = _resolve_target(guild, payload, "Name", "NewName")
    if role is None:
        return _fail("مش لاقي الرتبة المطلوبة")
    if role == guild.default_role:
        return _fail("مش ممكن تعدل على @everyone")
    if not new_name:
        return _fail("مفيش الاسم الجديد")
    await role.edit(name=new_name)
    return _ok(f"اتغير اسم الرتبة إلى `{new_name}`")


async def h_set_role_color(guild, ai, payload, invoker, channel):
    role = await _to_thread(ai.resolve_role, guild, _resolve_target(guild, payload, "Role", "Name"))
    if role is None or role == guild.default_role:
        return _fail("مش لاقي الرتبة المطلوبة")
    await role.edit(colour=_color(pget(payload, "Color", "color", default="#99AAB5")))
    return _ok(f"اتغير لون الرتبة `{role.name}`")


async def h_set_role_position(guild, ai, payload, invoker, channel):
    role = await _to_thread(ai.resolve_role, guild, _resolve_target(guild, payload, "Role", "Name"))
    if role is None or role == guild.default_role:
        return _fail("مش لاقي الرتبة المطلوبة")
    try:
        pos = min(int(pget(payload, "Position", "position", default=0)), len(guild.roles) - 2)
    except (TypeError, ValueError):
        return _fail("الترتيب لازم يكون رقم")
    await guild.edit_role_positions(positions={role: max(pos, 0)})
    return _ok(f"تم نقل الرتبة `{role.name}` للترتيب {pos}")


async def h_set_role_permissions(guild, ai, payload, invoker, channel):
    role = await _to_thread(ai.resolve_role, guild, _resolve_target(guild, payload, "Role", "Name"))
    if role is None or role == guild.default_role:
        return _fail("مش لاقي الرتبة المطلوبة")
    await role.edit(permissions=discord.Permissions(**sanitize_perms(pget(payload, "Perms", "perms", default={}))))
    return _ok(f"تم تحديث صلاحيات الرتبة `{role.name}`")


async def h_grant_role(guild, ai, payload, invoker, channel):
    member = await ai.resolve_member(guild, _resolve_target(guild, payload, "Member", "member"))
    role = await _to_thread(ai.resolve_role, guild, _resolve_target(guild, payload, "Role", "Name"))
    if member is None:
        return _fail("مش لاقي العضو المطلوب")
    if role is None:
        return _fail("مش لاقي الرتبة المطلوبة")
    if role == guild.default_role or role >= guild.me.top_role:
        return _fail(f"مش ممكن تدي الرتبة `{role.name}`")
    g = guard(member, invoker, guild, "تعدل على")
    if g:
        return _fail(g)
    await member.add_roles(role)
    return _ok(f"اتدات رتبة `{role.name}` للعضو {member.mention}")


async def h_remove_role(guild, ai, payload, invoker, channel):
    member = await ai.resolve_member(guild, _resolve_target(guild, payload, "Member", "member"))
    role = await _to_thread(ai.resolve_role, guild, _resolve_target(guild, payload, "Role", "Name"))
    if member is None:
        return _fail("مش لاقي العضو المطلوب")
    if role is None:
        return _fail("مش لاقي الرتبة المطلوبة")
    if role >= guild.me.top_role:
        return _fail(f"رتبة البوت لازم تكون فوق `{role.name}` عشان تسحبها")
    await member.remove_roles(role)
    return _ok(f"اتشالت رتبة `{role.name}` من العضو {member.mention}")


async def h_role_members(guild, ai, payload, invoker, channel):
    role = await _to_thread(ai.resolve_role, guild, _resolve_target(guild, payload, "Role", "Name"))
    if role is None:
        return _fail("مش لاقي الرتبة المطلوبة")
    all_members = [m for m in guild.members if role in m.roles]
    if not all_members:
        return _ok(f"مفيش حد لابس رتبة `{role.name}`")
    lines = [f"👥 الأعضاء اللي لابسين `{role.name}` ({len(all_members)}):"]
    lines += [f"- {m.mention} ({m.name})" for m in all_members[:40]]
    if len(all_members) > 40:
        lines.append(f"... والباقي ({len(all_members) - 40})")
    return _ok("\n".join(lines))


async def h_copy_role(guild, ai, payload, invoker, channel):
    role = await _to_thread(ai.resolve_role, guild, _resolve_target(guild, payload, "Role", "Name"))
    if role is None:
        return _fail("مش لاقي الرتبة المطلوبة")
    if role >= guild.me.top_role:
        return _fail(f"رتبة البوت لازم تكون فوق `{role.name}`")
    new_name = _resolve_target(guild, payload, "Name", "name") or (role.name + "-copy")
    new_role = await guild.create_role(
        name=new_name, colour=role.colour, permissions=role.permissions,
        hoist=role.hoist, mentionable=role.mentionable,
    )
    return _ok(f"تم نسخ الرتبة `{role.name}` → `{new_role.name}`")


async def h_toggle_hoist(guild, ai, payload, invoker, channel):
    role = await _to_thread(ai.resolve_role, guild, _resolve_target(guild, payload, "Role", "Name"))
    if role is None or role == guild.default_role:
        return _fail("مش لاقي الرتبة المطلوبة")
    val = bool(pget(payload, "Hoist", "hoist", default=True))
    await role.edit(hoist=val)
    return _ok(f"تم {'تفعيل' if val else 'إيقاف'} العرض المنفصل للرتبة `{role.name}`")


async def h_toggle_mentionable(guild, ai, payload, invoker, channel):
    role = await _to_thread(ai.resolve_role, guild, _resolve_target(guild, payload, "Role", "Name"))
    if role is None or role == guild.default_role:
        return _fail("مش لاقي الرتبة المطلوبة")
    val = bool(pget(payload, "Mentionable", "mentionable", default=True))
    await role.edit(mentionable=val)
    return _ok(f"تم {'تفعيل' if val else 'إيقاف'} المنشن للرتبة `{role.name}`")


async def h_role_info(guild, ai, payload, invoker, channel):
    role = await _to_thread(ai.resolve_role, guild, _resolve_target(guild, payload, "Role", "Name"))
    if role is None:
        return _fail("مش لاقي الرتبة المطلوبة")
    perms = [p.replace("_", " ") for p, v in role.permissions if v]
    count = len([m for m in guild.members if role in m.roles])
    lines = [
        f"🎖️ **{role.name}** (`{role.id}`)",
        f"اللون: {role.color}",
        f"الترتيب: {role.position}",
        f"عدد الأعضاء: {count}",
        f"Hoist: {'✅' if role.hoist else '❌'} | Mentionable: {'✅' if role.mentionable else '❌'}",
    ]
    if perms:
        lines.append("الصلاحيات: " + ", ".join(perms[:15]) + ("..." if len(perms) > 15 else ""))
    return _ok("\n".join(lines))


async def h_list_roles(guild, ai, payload, invoker, channel):
    roles = sorted(guild.roles, key=lambda r: r.position, reverse=True)
    lines = [f"🎖️ **الرتب ({len(roles) - 1}):**"]
    for r in roles:
        if r.name != "@everyone":
            lines.append(f"- {r.mention} (Pos {r.position})")
    return _ok("\n".join(lines[:40]))


async def _bulk_role(guild, ai, payload, invoker, action: str, target_type: str):
    """إعطاء/سحب رتبة لمجموعة (كل الأعضاء/البوتات/البشر)."""
    role = await _to_thread(ai.resolve_role, guild, _resolve_target(guild, payload, "Role", "Name"))
    if role is None:
        return _fail("مش لاقي الرتبة المطلوبة")
    if role == guild.default_role or role >= guild.me.top_role:
        return _fail(f"مش ممكن تعدل على الرتبة `{role.name}` (رتبة البوت لازم تكون فوقها)")
    members = guild.members
    if target_type == "bots":
        members = [m for m in members if m.bot]
    elif target_type == "humans":
        members = [m for m in members if not m.bot]
    count = 0
    for m in members:
        try:
            if action == "give":
                if role not in m.roles:
                    await m.add_roles(role)
                    count += 1
            else:
                if role in m.roles:
                    await m.remove_roles(role)
                    count += 1
        except discord.Forbidden:
            continue
    verb = "أضفت" if action == "give" else "شلت"
    scope = {"all": "كل الأعضاء", "bots": "كل البوتات", "humans": "كل البشر"}[target_type]
    return _ok(f"تم {verb} رتبة `{role.name}` لـ {count} من {scope}")


async def h_give_role_all(guild, ai, payload, invoker, channel):
    return await _bulk_role(guild, ai, payload, invoker, "give", "all")


async def h_remove_role_all(guild, ai, payload, invoker, channel):
    return await _bulk_role(guild, ai, payload, invoker, "remove", "all")


async def h_give_role_bots(guild, ai, payload, invoker, channel):
    return await _bulk_role(guild, ai, payload, invoker, "give", "bots")


async def h_give_role_humans(guild, ai, payload, invoker, channel):
    return await _bulk_role(guild, ai, payload, invoker, "give", "humans")


# ==========================================================================
# D) الأعضاء — 21 مهارة
# ==========================================================================
async def h_kick(guild, ai, payload, invoker, channel):
    member = await ai.resolve_member(guild, _resolve_target(guild, payload, "Member", "member"))
    if member is None:
        return _fail("مش لاقي العضو المطلوب")
    g = guard(member, invoker, guild, "تطرد")
    if g:
        return _fail(g)
    reason = _resolve_target(guild, payload, "Reason") or None
    await member.kick(reason=reason)
    return _ok(f"تم طرد العضو {member.mention}" + (f" — السبب: {reason}" if reason else ""))


async def h_ban(guild, ai, payload, invoker, channel):
    member = await ai.resolve_member(guild, _resolve_target(guild, payload, "Member", "member"))
    if member is None:
        return _fail("مش لاقي العضو المطلوب")
    g = guard(member, invoker, guild, "تعمل بان لـ")
    if g:
        return _fail(g)
    reason = _resolve_target(guild, payload, "Reason") or None
    days = 1 if pget(payload, "DeleteMessages", default=False) else 0
    await member.ban(reason=reason, delete_message_days=days)
    return _ok(f"تم عمل بان للعضو {member.mention}" + (f" — السبب: {reason}" if reason else ""))


async def h_softban(guild, ai, payload, invoker, channel):
    member = await ai.resolve_member(guild, _resolve_target(guild, payload, "Member", "member"))
    if member is None:
        return _fail("مش لاقي العضو المطلوب")
    g = guard(member, invoker, guild, "تعمل سوفت بان لـ")
    if g:
        return _fail(g)
    reason = _resolve_target(guild, payload, "Reason") or None
    await member.ban(reason=reason, delete_message_days=1)
    await guild.unban(member, reason="Softban")
    return _ok(f"تم عمل سوفت بان لـ {member.mention} (بان + فك فورًا)")


async def h_unban(guild, ai, payload, invoker, channel):
    target = _resolve_target(guild, payload, "Member", "member")
    bans = await guild.bans().flatten()
    if not bans:
        return _fail("مفيش حد متبند أصلاً")
    user = None
    if target.isdigit():
        user = next((b.user for b in bans if b.user.id == int(target)), None)
    else:
        low = target.lower()
        for b in bans:
            if b.user.name.lower() == low or (b.user.global_name or "").lower() == low:
                user = b.user
                break
        if user is None:
            for b in bans:
                if low in b.user.name.lower() or low in (b.user.global_name or "").lower():
                    user = b.user
                    break
    if user is None:
        return _fail(f"مش لاقي حد متبند باسم `{target}`")
    await guild.unban(user)
    return _ok(f"تم فك البان عن {user.name}")


async def h_timeout(guild, ai, payload, invoker, channel):
    member = await ai.resolve_member(guild, _resolve_target(guild, payload, "Member", "member"))
    if member is None:
        return _fail("مش لاقي العضو المطلوب")
    g = guard(member, invoker, guild, "تسكت")
    if g:
        return _fail(g)
    try:
        minutes = int(pget(payload, "Minutes", "Time", default=30))
    except (TypeError, ValueError):
        minutes = 30
    minutes = max(1, min(minutes, MAX_TIMEOUT_MINUTES))
    await member.timeout(timedelta(minutes=minutes))
    return _ok(f"تم كتم العضو {member.mention} لمدة {minutes} دقيقة")


async def h_remove_timeout(guild, ai, payload, invoker, channel):
    member = await ai.resolve_member(guild, _resolve_target(guild, payload, "Member", "member"))
    if member is None:
        return _fail("مش لاقي العضو المطلوب")
    await member.timeout(None)
    return _ok(f"تم فك الكتم عن {member.mention}")


async def h_rename_member(guild, ai, payload, invoker, channel):
    member = await ai.resolve_member(guild, _resolve_target(guild, payload, "Member", "member"))
    if member is None:
        return _fail("مش لاقي العضو المطلوب")
    g = guard(member, invoker, guild, "تغير اسم")
    if g:
        return _fail(g)
    nickname = _resolve_target(guild, payload, "Nickname", "Nick", "Name")
    old = member.display_name
    await member.edit(nick=nickname or None)
    return _ok(f"اتغير اسم العضو من `{old}` إلى `{nickname}`" if nickname else f"تم تصفير اسم العضو `{member.name}`")


async def h_reset_nickname(guild, ai, payload, invoker, channel):
    member = await ai.resolve_member(guild, _resolve_target(guild, payload, "Member", "member"))
    if member is None:
        return _fail("مش لاقي العضو المطلوب")
    await member.edit(nick=None)
    return _ok(f"تم تصفير اسم العضو {member.mention}")


async def _voice_edit(guild, ai, payload, invoker, mute=None, deafen=None):
    member = await ai.resolve_member(guild, _resolve_target(guild, payload, "Member", "member"))
    if member is None:
        return _fail("مش لاقي العضو المطلوب")
    if member.voice is None and (mute is not None or deafen is not None):
        return _fail(f"{member.mention} مش في روم صوتي")
    kwargs = {}
    if mute is not None:
        kwargs["mute"] = mute
    if deafen is not None:
        kwargs["deafen"] = deafen
    await member.edit(**kwargs)
    parts = []
    if mute is True:
        parts.append("كتم")
    if mute is False:
        parts.append("فك كتم")
    if deafen is True:
        parts.append("طرشان")
    if deafen is False:
        parts.append("فك طرشان")
    return _ok(f"تم {', '.join(parts)} عن {member.mention}" if parts else f"تم التعديل على {member.mention}")


async def h_voice_mute(guild, ai, payload, invoker, channel):
    return await _voice_edit(guild, ai, payload, invoker, mute=True)


async def h_voice_unmute(guild, ai, payload, invoker, channel):
    return await _voice_edit(guild, ai, payload, invoker, mute=False)


async def h_voice_deafen(guild, ai, payload, invoker, channel):
    return await _voice_edit(guild, ai, payload, invoker, deafen=True)


async def h_voice_undeafen(guild, ai, payload, invoker, channel):
    return await _voice_edit(guild, ai, payload, invoker, deafen=False)


async def h_disconnect(guild, ai, payload, invoker, channel):
    member = await ai.resolve_member(guild, _resolve_target(guild, payload, "Member", "member"))
    if member is None:
        return _fail("مش لاقي العضو المطلوب")
    if member.voice is None:
        return _fail(f"{member.mention} مش في روم صوتي")
    await member.move_to(None)
    return _ok(f"تم فصل {member.mention} من الروم الصوتي")


async def h_move_member(guild, ai, payload, invoker, channel):
    member = await ai.resolve_member(guild, _resolve_target(guild, payload, "Member", "member"))
    if member is None:
        return _fail("مش لاقي العضو المطلوب")
    ch = await _to_thread(ai.resolve_channel, guild, _resolve_target(guild, payload, "Channel", "name"))
    if ch is None:
        return _fail("مش لاقي الروم الصوتي المطلوب")
    if not isinstance(ch, (discord.VoiceChannel, discord.StageChannel)):
        return _fail("الروم ده مش صوتي")
    if member.voice is None:
        return _fail(f"{member.mention} مش في روم صوتي أصلاً")
    await member.move_to(ch)
    return _ok(f"تم نقل {member.mention} إلى `{ch.name}`")


async def h_warn(guild, ai, payload, invoker, channel):
    member = await ai.resolve_member(guild, _resolve_target(guild, payload, "Member", "member"))
    if member is None:
        return _fail("مش لاقي العضو المطلوب")
    reason = _resolve_target(guild, payload, "Reason") or "بدون سبب"
    lst = add_warning(guild.id, member.id, reason, str(invoker))
    return _ok(f"⚠️ تم تحذير {member.mention} — السبب: {reason} (الإجمالي: {len(lst)})")


async def h_unwarn(guild, ai, payload, invoker, channel):
    member = await ai.resolve_member(guild, _resolve_target(guild, payload, "Member", "member"))
    if member is None:
        return _fail("مش لاقي العضو المطلوب")
    removed = remove_last_warning(guild.id, member.id)
    if removed is None:
        return _fail(f"{member.mention} مفيش عليه تحذيرات")
    return _ok(f"تم شيل آخر تحذير عن {member.mention} (السبب كان: {removed['reason']})")


async def h_show_warnings(guild, ai, payload, invoker, channel):
    member = await ai.resolve_member(guild, _resolve_target(guild, payload, "Member", "member"))
    if member is None:
        return _fail("مش لاقي العضو المطلوب")
    lst = list_warnings(guild.id, member.id)
    if not lst:
        return _ok(f"{member.mention} نظيف — مفيش عليه تحذيرات ✅")
    return _ok(_format_warns(lst, member.mention))


async def h_clear_warnings(guild, ai, payload, invoker, channel):
    member = await ai.resolve_member(guild, _resolve_target(guild, payload, "Member", "member"))
    if member is None:
        return _fail("مش لاقي العضو المطلوب")
    n = clear_all_warnings(guild.id, member.id)
    return _ok(f"تم مسح {n} تحذير عن {member.mention}" if n else f"{member.mention} مفيش عليه تحذيرات أصلًا")


async def h_member_info(guild, ai, payload, invoker, channel):
    member = await ai.resolve_member(guild, _resolve_target(guild, payload, "Member", "member")) or invoker
    roles = ", ".join(r.mention for r in member.roles[1:][:10]) or "—"
    lines = [
        f"👤 **{member}** (`{member.id}`)",
        f"الاسم العالمي: {member.global_name or '—'}",
        f"انضم في: {member.joined_at.strftime('%Y-%m-%d') if member.joined_at else '—'}",
        f"الحساب من: {member.created_at.strftime('%Y-%m-%d')}",
        f"أعلى رتبة: {member.top_role.mention}",
        f"الرتب ({len(member.roles) - 1}): {roles}",
    ]
    if member.voice:
        lines.append(f"🎙️ في: {member.voice.channel.name}")
    return _ok("\n".join(lines))


async def h_banned_list(guild, ai, payload, invoker, channel):
    bans = await guild.bans().flatten()
    if not bans:
        return _ok("مفيش حد متبند ✅")
    lines = [f"🔨 **المتبندين ({len(bans)}):**"]
    lines += [f"- {b.user.name} ({b.reason or 'بدون سبب'})" for b in bans[:40]]
    return _ok("\n".join(lines))


async def h_boosters(guild, ai, payload, invoker, channel):
    boosters = sorted(guild.premium_subscribers or [], key=lambda m: m.premium_since or 0)
    if not boosters:
        return _ok("مفيش بوسترز في السيرفر 😢")
    lines = [f"💎 **البوسترز ({len(boosters)}):**"]
    lines += [f"- {m.mention}" for m in boosters[:40]]
    return _ok("\n".join(lines))


async def h_ban_by_id(guild, ai, payload, invoker, channel):
    uid = _resolve_target(guild, payload, "UserID", "user_id", "ID", "id")
    if not uid.isdigit():
        return _fail("محتاج الـ User ID (رقم)")
    reason = _resolve_target(guild, payload, "Reason") or None
    try:
        await guild.ban(discord.Object(id=int(uid)), reason=reason)
        return _ok(f"تم عمل بان لليوزر `{uid}`" + (f" — السبب: {reason}" if reason else ""))
    except discord.Forbidden:
        return _fail("البوت مش عنده صلاحية البان")
    except discord.NotFound:
        return _fail("اليوزر ده مش موجود")
    except discord.HTTPException as e:
        return _fail(f"فشل البان: {e}")


# ==========================================================================
# E) الرسائل — 10 مهارات
# ==========================================================================
async def h_clear_messages(guild, ai, payload, invoker, channel):
    try:
        count = max(1, min(int(pget(payload, "Count", "count", default=10)), 100))
    except (TypeError, ValueError):
        count = 10
    deleted = await channel.purge(limit=count)
    return _ok(f"تم مسح {len(deleted)} رسالة")


async def h_clear_channel(guild, ai, payload, invoker, channel):
    deleted = await channel.purge(limit=500)
    return _ok(f"تم مسح {len(deleted)} رسالة من `{channel.name}` 🧹")


async def h_clear_user(guild, ai, payload, invoker, channel):
    member = await ai.resolve_member(guild, _resolve_target(guild, payload, "Member", "member", "User"))
    if member is None:
        return _fail("مش لاقي العضو المطلوب")
    try:
        count = max(1, min(int(pget(payload, "Count", "count", default=20)), 100))
    except (TypeError, ValueError):
        count = 20
    deleted = await channel.purge(limit=count, check=lambda m: m.author.id == member.id)
    return _ok(f"تم مسح {len(deleted)} رسالة من {member.mention}")


async def h_clear_bots(guild, ai, payload, invoker, channel):
    try:
        count = max(1, min(int(pget(payload, "Count", "count", default=20)), 100))
    except (TypeError, ValueError):
        count = 20
    deleted = await channel.purge(limit=count, check=lambda m: m.author.bot)
    return _ok(f"تم مسح {len(deleted)} رسالة بوتات")


async def h_announce(guild, ai, payload, invoker, channel):
    text = _resolve_target(guild, payload, "Message", "message")
    if not text:
        return _fail("مفيش نص للإعلان")
    target_ch = None
    chan_ref = pget(payload, "Channel", "channel")
    if chan_ref:
        target_ch = await _to_thread(ai.resolve_channel, guild, str(chan_ref))
    target_ch = target_ch or channel
    await target_ch.send(text[:2000])
    return _ok(f"تم نشر الإعلان في `{target_ch.name}` 📣")


async def h_poll(guild, ai, payload, invoker, channel):
    question = _resolve_target(guild, payload, "Question", "question") or "استطلاع"
    options = pget(payload, "Options", "options", default=None)
    if not isinstance(options, list) or len(options) < 2:
        options = ["نعم", "لا"]
    options = [str(o).strip()[:80] for o in options][:10]
    if len(options) < 2:
        options = ["نعم", "لا"]
    target_ch = None
    chan_ref = pget(payload, "Channel", "channel")
    if chan_ref:
        target_ch = await _to_thread(ai.resolve_channel, guild, str(chan_ref))
    target_ch = target_ch or channel
    embed = discord.Embed(title="📊 " + question[:256], color=discord.Colour.blurple())
    embed.description = "\n".join(f"{POLL_EMOJIS[i]} {o}" for i, o in enumerate(options))
    msg = await target_ch.send(embed=embed)
    for i in range(len(options)):
        await msg.add_reaction(POLL_EMOJIS[i])
    return _ok(f"تم نشر الاستطلاع في `{target_ch.name}` 📊 ({len(options)} خيارات)")


async def h_send_embed(guild, ai, payload, invoker, channel):
    title = _resolve_target(guild, payload, "Title", "title") or "Embed"
    desc = _resolve_target(guild, payload, "Description", "description") or "—"
    target_ch = channel
    chan_ref = pget(payload, "Channel", "channel")
    if chan_ref:
        target_ch = await _to_thread(ai.resolve_channel, guild, str(chan_ref)) or channel
    embed = discord.Embed(title=title[:256], description=desc[:4000], color=_color(pget(payload, "Color", "color", default="#5865F2")))
    await target_ch.send(embed=embed)
    return _ok(f"تم إرسال الـ Embed في `{target_ch.name}` 💠")


async def _last_message(ch):
    async for m in ch.history(limit=1):
        return m
    return None


async def h_pin_last(guild, ai, payload, invoker, channel):
    ch = channel
    chan_ref = pget(payload, "Channel", "channel")
    if chan_ref:
        ch = await _to_thread(ai.resolve_channel, guild, str(chan_ref)) or channel
    msg = await _last_message(ch)
    if msg is None:
        return _fail("مفيش رسائل في الروم")
    await msg.pin()
    return _ok(f"تم تثبيت آخر رسالة في `{ch.name}` 📌")


async def h_unpin_last(guild, ai, payload, invoker, channel):
    ch = channel
    chan_ref = pget(payload, "Channel", "channel")
    if chan_ref:
        ch = await _to_thread(ai.resolve_channel, guild, str(chan_ref)) or channel
    msg = await _last_message(ch)
    if msg is None:
        return _fail("مفيش رسائل في الروم")
    await msg.unpin()
    return _ok(f"تم فك تثبيت آخر رسالة في `{ch.name}`")


async def h_send_dm(guild, ai, payload, invoker, channel):
    member = await ai.resolve_member(guild, _resolve_target(guild, payload, "Member", "member"))
    text = _resolve_target(guild, payload, "Message", "message")
    if member is None:
        return _fail("مش لاقي العضو المطلوب")
    if not text:
        return _fail("مفيش نص الرسالة")
    try:
        await member.send(text[:2000])
        return _ok(f"تم إرسال رسالة خاصة لـ {member.mention} 📩")
    except discord.Forbidden:
        return _fail(f"مقدرتش أوصل لـ {member.mention} (قافل الرسائل الخاصة)")


async def h_send_message(guild, ai, payload, invoker, channel):
    text = _resolve_target(guild, payload, "Message", "message")
    if not text:
        return _fail("مفيش نص الرسالة")
    target_ch = channel
    chan_ref = pget(payload, "Channel", "channel")
    if chan_ref:
        target_ch = await _to_thread(ai.resolve_channel, guild, str(chan_ref)) or channel
    await target_ch.send(text[:2000])
    return _ok(f"تم إرسال الرسالة في `{target_ch.name}`")


async def h_react_last(guild, ai, payload, invoker, channel):
    emoji = _resolve_target(guild, payload, "Emoji", "emoji")
    if not emoji:
        return _fail("محتاج الإيموجي")
    target_ch = channel
    chan_ref = pget(payload, "Channel", "channel")
    if chan_ref:
        target_ch = await _to_thread(ai.resolve_channel, guild, str(chan_ref)) or channel
    msg = await _last_message(target_ch)
    if msg is None:
        return _fail("مفيش رسائل في الروم")
    try:
        await msg.add_reaction(emoji)
        return _ok(f"تمت إضافة ريأكشن {emoji} على آخر رسالة في `{target_ch.name}`")
    except discord.HTTPException:
        return _fail("الإيموجي ده مش موجود أو مش صالح")


# ==========================================================================
# F) الإنفيتات — 3 مهارات
# ==========================================================================
async def h_create_invite(guild, ai, payload, invoker, channel):
    ch = await _to_thread(ai.resolve_channel, guild, _resolve_target(guild, payload, "Channel", "Name")) or channel
    try:
        max_uses = int(pget(payload, "Uses", "uses", default=0))
    except (TypeError, ValueError):
        max_uses = 0
    try:
        max_age = int(pget(payload, "MaxAge", "max_age", default=0))
    except (TypeError, ValueError):
        max_age = 0
    invite = await ch.create_invite(max_age=max_age or None, max_uses=max_uses or None)
    return _ok(f"إنفيت للروم `{ch.name}`: {invite.url}")


async def h_list_invites(guild, ai, payload, invoker, channel):
    try:
        invites = await guild.invites()
    except discord.Forbidden:
        return _fail("البوت مش عنده صلاحية يعرض الإنفيتات")
    if not invites:
        return _ok("مفيش إنفيتات فعالة")
    lines = [f"🔗 **الإنفيتات ({len(invites)}):**"]
    for inv in invites[:40]:
        lines.append(f"- {inv.code} → {inv.channel.name} (استخدم {inv.uses} مرة)")
    return _ok("\n".join(lines))


async def h_revoke_invites(guild, ai, payload, invoker, channel):
    try:
        invites = await guild.invites()
    except discord.Forbidden:
        return _fail("البوت مش عنده صلاحية يحذف الإنفيتات")
    if not invites:
        return _ok("مفيش إنفيتات عشان تتشال")
    ch_name = _resolve_target(guild, payload, "Channel", "name").lower()
    for inv in invites:
        if not ch_name or inv.channel.name.lower() == ch_name:
            await inv.delete()
    return _ok(f"تم حذف كل الإنفيتات" + (f" بتاعة `{ch_name}`" if ch_name else "") + " 🧹")


# ==========================================================================
# G) الإيموجي — 3 مهارات
# ==========================================================================
async def h_add_emoji(guild, ai, payload, invoker, channel):
    name = _resolve_target(guild, payload, "Name", "name")
    url = _resolve_target(guild, payload, "URL", "url", "Image")
    if not name or not url:
        return _fail("محتاج اسم الإيموجي + رابط الصورة")
    img = await _fetch_image(url)
    if not img:
        return _fail("مقدرتش أجيب الصورة من الرابط")
    emoji = await guild.create_custom_emoji(name=name[:32], image=img)
    return _ok(f"تمت إضافة الإيموجي {emoji} ✅")


async def h_remove_emoji(guild, ai, payload, invoker, channel):
    name = _resolve_target(guild, payload, "Name", "name").lower()
    if not name:
        return _fail("محتاج اسم الإيموجي")
    for emoji in guild.emojis:
        if emoji.name.lower() == name:
            await emoji.delete()
            return _ok(f"تم حذف الإيموجي `{name}`")
    return _fail(f"مفيش إيموجي باسم `{name}`")


async def h_list_emojis(guild, ai, payload, invoker, channel):
    if not guild.emojis:
        return _ok("مفيش إيموجي في السيرفر")
    lines = [f"😀 **الإيموجي ({len(guild.emojis)}):**"]
    lines += [f"- {e} `:{e.name}:`" for e in guild.emojis[:50]]
    return _ok("\n".join(lines))


# ==========================================================================
# H) الويبهوكس — 3 مهارات
# ==========================================================================
async def h_create_webhook(guild, ai, payload, invoker, channel):
    ch = await _to_thread(ai.resolve_channel, guild, _resolve_target(guild, payload, "Channel", "Name")) or channel
    if not isinstance(ch, discord.TextChannel):
        return _fail("الويبهوكس بيتعمل في رومات نصية")
    name = _resolve_target(guild, payload, "Name", "name") or "Disor Webhook"
    wh = await ch.create_webhook(name=name)
    return _ok(f"تم إنشاء ويبهوك `{wh.name}` في `{ch.name}` 🪝 (URL: {wh.url[:60]}...)")


async def h_delete_webhook(guild, ai, payload, invoker, channel):
    ch = await _to_thread(ai.resolve_channel, guild, _resolve_target(guild, payload, "Channel", "Name")) or channel
    name = _resolve_target(guild, payload, "Name", "name").lower()
    if not name:
        return _fail("محتاج اسم الويبهوك")
    webhooks = await ch.webhooks()
    for wh in webhooks:
        if wh.name.lower() == name:
            await wh.delete()
            return _ok(f"تم حذف الويبهوك `{name}`")
    return _fail(f"مفيش ويبهوك باسم `{name}` في `{ch.name}`")


async def h_list_webhooks(guild, ai, payload, invoker, channel):
    try:
        webhooks = await guild.webhooks()
    except discord.Forbidden:
        return _fail("البوت مش عنده صلاحية يعرض الويبهوكس")
    if not webhooks:
        return _ok("مفيش ويبهوكس في السيرفر")
    lines = [f"🪝 **الويبهوكس ({len(webhooks)}):**"]
    lines += [f"- {w.name} → {w.channel.name if w.channel else '—'}" for w in webhooks[:40]]
    return _ok("\n".join(lines))


# ==========================================================================
# I) السيرفر — 18 مهارة
# ==========================================================================
async def h_server_info(guild, ai, payload, invoker, channel):
    humans = sum(1 for m in guild.members if not m.bot)
    bots = sum(1 for m in guild.members if m.bot)
    online = sum(1 for m in guild.members if m.status != discord.Status.offline)
    lines = [
        f"🛡️ **{guild.name}** (`{guild.id}`)",
        f"المالك: {guild.owner.mention if guild.owner else '—'}",
        f"الأعضاء: {guild.member_count} (بشر {humans} + بوتات {bots})",
        f"أونلاين: {online}",
        f"الرومات: {len(guild.channels)} | الكاتجوريز: {len(guild.categories)}",
        f"الرتب: {len(guild.roles) - 1}",
        f"الإيموجي: {len(guild.emojis)}",
        f"البوسترز: {guild.premium_subscription_count}",
        f"المستوى: {guild.verification_level.name}",
        f"انشأ في: {guild.created_at.strftime('%Y-%m-%d')}",
    ]
    return _ok("\n".join(lines))


async def h_member_count(guild, ai, payload, invoker, channel):
    return _ok(f"👥 عدد أعضاء `{guild.name}`: **{guild.member_count}**")


async def h_online_count(guild, ai, payload, invoker, channel):
    online = sum(1 for m in guild.members if m.status != discord.Status.offline)
    return _ok(f"🟢 أونلاين حالياً: **{online}** من أصل {guild.member_count}")


async def h_boost_count(guild, ai, payload, invoker, channel):
    return _ok(f"💎 بوستات السيرفر: **{guild.premium_subscription_count}**")


async def h_rename_server(guild, ai, payload, invoker, channel):
    name = _resolve_target(guild, payload, "Name", "name")
    if not name:
        return _fail("مفيش الاسم الجديد")
    await guild.edit(name=name[:100])
    return _ok(f"اتغير اسم السيرفر إلى `{name}`")


async def h_set_verification(guild, ai, payload, invoker, channel):
    level = str(pget(payload, "Level", "level", default="low")).lower()
    if level not in VERIF_LEVELS:
        return _fail("المستويات: none / low / medium / high / highest")
    await guild.edit(verification_level=discord.VerificationLevel(VERIF_LEVELS[level]))
    return _ok(f"تم ضبط مستوى التحقق على `{level}`")


async def h_set_afk(guild, ai, payload, invoker, channel):
    ch = await _to_thread(ai.resolve_channel, guild, _resolve_target(guild, payload, "Channel", "Name"))
    if ch is None:
        return _fail("مش لاقي الروم المطلوب")
    await guild.edit(afk_channel=ch)
    return _ok(f"تم ضبط روم الـ AFK على `{ch.name}` 💤")


async def h_set_system_channel(guild, ai, payload, invoker, channel):
    ch = await _to_thread(ai.resolve_channel, guild, _resolve_target(guild, payload, "Channel", "Name"))
    if ch is None:
        return _fail("مش لاقي الروم المطلوب")
    await guild.edit(system_channel=ch)
    return _ok(f"تم ضبط قناة النظام على `{ch.name}` ⚙️")


async def h_set_welcome(guild, ai, payload, invoker, channel):
    import guilddata
    text = _resolve_target(guild, payload, "Text", "Message", "message")
    ch = None
    chan_ref = pget(payload, "Channel", "channel")
    if chan_ref:
        ch = await _to_thread(ai.resolve_channel, guild, str(chan_ref))
    ch = ch or channel
    guilddata.set_welcome(guild.id, ch.id, text or None)
    return _ok(f"تم ضبط الترحيب في {ch.mention}" + (f" — النص: {text[:60]}" if text else ""))


async def h_welcome_off(guild, ai, payload, invoker, channel):
    import guilddata
    guilddata.set_welcome(guild.id, None, None)
    return _ok("تم إيقاف الترحيب")


async def h_set_autorole(guild, ai, payload, invoker, channel):
    import guilddata
    role = await _to_thread(ai.resolve_role, guild, _resolve_target(guild, payload, "Role", "Name"))
    if role is None:
        return _fail("مش لاقي الرتبة المطلوبة")
    if role >= guild.me.top_role:
        return _fail("رتبة البوت لازم تكون فوق الرتبة دي عشان يديها تلقائيًا")
    guilddata.set_autorole(guild.id, role.id)
    return _ok(f"الأعضاء الجدد هياخدوا رتبة `{role.name}` تلقائيًا")


async def h_autorole_off(guild, ai, payload, invoker, channel):
    import guilddata
    guilddata.set_autorole(guild.id, None)
    return _ok("تم إيقاف الرول التلقائي")


async def h_greet_test(guild, ai, payload, invoker, channel):
    import guilddata
    g = guilddata.get(guild.id)
    if not g.get("welcome_channel") or not g.get("welcome_text"):
        return _fail("الترحيب مش متظبط — استخدم `!welcome #قناة النص` الأول")
    text = str(g["welcome_text"]).replace("{user}", invoker.mention).replace("{server}", guild.name)
    await channel.send(f"🧪 **معاينة الترحيب:**\n{text}")
    return _ok("تم إرسال معاينة الترحيب")


async def h_perms_member(guild, ai, payload, invoker, channel):
    member = await ai.resolve_member(guild, _resolve_target(guild, payload, "Member", "member")) or invoker
    granted = [p.replace("_", " ") for p, v in member.guild_permissions if v]
    return _ok(f"🔑 صلاحيات {member.mention}:\n" + (", ".join(granted[:20]) if granted else "لا شيء"))


async def h_perms_role(guild, ai, payload, invoker, channel):
    role = await _to_thread(ai.resolve_role, guild, _resolve_target(guild, payload, "Role", "Name"))
    if role is None:
        return _fail("مش لاقي الرتبة المطلوبة")
    granted = [p.replace("_", " ") for p, v in role.permissions if v]
    return _ok(f"🔑 صلاحيات رتبة `{role.name}`:\n" + (", ".join(granted[:20]) if granted else "لا شيء"))


async def h_highest_role(guild, ai, payload, invoker, channel):
    member = await ai.resolve_member(guild, _resolve_target(guild, payload, "Member", "member")) or invoker
    return _ok(f"أعلى رتبة لـ {member.mention}: {member.top_role.mention}")


async def h_random_member(guild, ai, payload, invoker, channel):
    if not guild.members:
        return _fail("مفيش أعضاء")
    m = random.choice([x for x in guild.members if not x.bot] or guild.members)
    return _ok(f"🎲 اخترنا لك: {m.mention} 🎉")


async def h_member_avatar(guild, ai, payload, invoker, channel):
    member = await ai.resolve_member(guild, _resolve_target(guild, payload, "Member", "member")) or invoker
    return _ok(f"🖼️ صورة {member.mention}:\n{member.display_avatar.url}")


# ==========================================================================
# J) الصوتيات — 3 مهارات
# ==========================================================================
async def h_voice_channel_info(guild, ai, payload, invoker, channel):
    ch = await _to_thread(ai.resolve_channel, guild, _resolve_target(guild, payload, "Channel"))
    if ch is None:
        return _fail("مش لاقي الروم المطلوب")
    if not isinstance(ch, (discord.VoiceChannel, discord.StageChannel)):
        return _fail("الروم ده مش صوتي")
    lines = [f"🎙️ **{ch.name}** (`{ch.id}`)",
             f"النوع: {'ستيج' if isinstance(ch, discord.StageChannel) else 'صوتي'}"]
    if isinstance(ch, discord.VoiceChannel):
        lines.append(f"الحد الأقصى: {ch.user_limit or '∞'}")
        lines.append(f"البيتريت: {ch.bitrate // 1000} kbps")
    conn = len([m for m in ch.members if m.voice and m.voice.channel == ch])
    lines.append(f"الموجودين: {conn}")
    if conn:
        lines.append("الأعضاء: " + ", ".join(m.display_name for m in ch.members[:20]))
    return _ok("\n".join(lines))


async def h_move_all_voice(guild, ai, payload, invoker, channel):
    target = await _to_thread(ai.resolve_channel, guild, _resolve_target(guild, payload, "Channel", "name"))
    if target is None:
        return _fail("مش لاقي الروم الصوتي المطلوب")
    if not isinstance(target, (discord.VoiceChannel, discord.StageChannel)):
        return _fail("الروم ده مش صوتي")
    moved = 0
    for vc in list(guild.voice_channels) + list(guild.stage_channels):
        for m in list(vc.members):
            if m.voice and m.voice.channel == vc:
                try:
                    await m.move_to(target)
                    moved += 1
                except discord.Forbidden:
                    continue
    return _ok(f"تم نقل {moved} عضو إلى `{target.name}`")


async def h_disconnect_all_voice(guild, ai, payload, invoker, channel):
    moved = 0
    for vc in list(guild.voice_channels) + list(guild.stage_channels):
        for m in list(vc.members):
            if m.voice and m.voice.channel == vc:
                try:
                    await m.move_to(None)
                    moved += 1
                except discord.Forbidden:
                    continue
    return _ok(f"تم فصل {moved} عضو من كل الرومات الصوتية")


# ==========================================================================
# K) المتعة — 5 مهارات
# ==========================================================================
async def h_flip_coin(guild, ai, payload, invoker, channel):
    result = random.choice(["وجه 🦅", "كتابة 🪙"])
    return _ok(f"🪙 العملة: **{result}**")


async def h_roll_dice(guild, ai, payload, invoker, channel):
    try:
        sides = int(pget(payload, "Sides", "sides", default=6))
    except (TypeError, ValueError):
        sides = 6
    sides = max(2, min(sides, 100))
    return _ok(f"🎲 النرد ({sides} وجه): **{random.randint(1, sides)}**")


async def h_random_number(guild, ai, payload, invoker, channel):
    try:
        lo = int(pget(payload, "Min", "min", default=1))
        hi = int(pget(payload, "Max", "max", default=100))
    except (TypeError, ValueError):
        lo, hi = 1, 100
    if lo > hi:
        lo, hi = hi, lo
    return _ok(f"🔢 رقم عشوائي بين {lo} و {hi}: **{random.randint(lo, hi)}**")


async def h_choose_random(guild, ai, payload, invoker, channel):
    choices = pget(payload, "Choices", "choices", default=None)
    if not isinstance(choices, list) or len(choices) < 2:
        return _fail("محتاج على الأقل خيارين (Choices: [\"أ\", \"ب\"])")
    picked = random.choice([str(c) for c in choices])
    return _ok(f"🎯 اخترنا: **{picked}**")


async def h_bot_info(guild, ai, payload, invoker, channel):
    me = guild.me
    joined = me.joined_at.strftime("%Y-%m-%d") if me.joined_at else "—"
    return _ok(f"🤖 **{me.display_name}**\nID: `{me.id}`\nانضم للسيرفر: {joined}\nأعلى رتبة: {me.top_role.mention}")


# ==========================================================================
# I) السيرفر — إعدادات إضافية
# ==========================================================================
async def _server_image(guild, payload, attr: str, what: str):
    url = _resolve_target(guild, payload, "URL", "url", "Image", "image")
    if not url:
        return _fail(f"محتاج رابط الصورة")
    img = await _fetch_image(url)
    if not img:
        return _fail("مقدرتش أجيب الصورة من الرابط")
    try:
        await guild.edit(**{attr: img})
        return _ok(f"تم تغيير {what} السيرفر 🖼️")
    except discord.Forbidden:
        return _fail(f"السيرفر مش مؤهل لتغيير {what} (محتاج مستوى Boost أعلى)")


async def h_server_icon(guild, ai, payload, invoker, channel):
    return await _server_image(guild, payload, "icon", "أيقونة")


async def h_server_banner(guild, ai, payload, invoker, channel):
    return await _server_image(guild, payload, "banner", "بانر")


async def h_server_splash(guild, ai, payload, invoker, channel):
    return await _server_image(guild, payload, "splash", "سبلاش")


async def h_create_vanity(guild, ai, payload, invoker, channel):
    code = _resolve_target(guild, payload, "Code", "code")
    if not code:
        return _fail("محتاج الكود (مثال: my-server)")
    try:
        await guild.edit(vanity_code=code)
        return _ok(f"تم ضبط الـ Vanity URL: **discord.gg/{code}**")
    except discord.Forbidden:
        return _fail("السيرفر محتاج مستوى Boost 3 عشان الـ Vanity URL")


async def h_server_avatar(guild, ai, payload, invoker, channel):
    if not guild.icon:
        return _fail("السيرفر من غير أيقونة")
    return _ok(f"🖼️ أيقونة السيرفر:\n{guild.icon.url}")


# ==========================================================================
# جدول التوزيع (Dispatch)
# ==========================================================================
HANDLERS = {
    # A) القنوات
    "CreateTextChannel": h_create_text, "CreateVoiceChannel": h_create_voice,
    "CreateForumChannel": h_create_forum, "CreateStageChannel": h_create_stage,
    "DeleteChannel": h_delete_channel, "RenameChannel": h_rename_channel,
    "SetChannelTopic": h_set_topic, "MoveChannel": h_move_channel,
    "LockChannel": h_lock, "UnlockChannel": h_unlock,
    "EnableSlowmode": h_slowmode_on, "DisableSlowmode": h_slowmode_off,
    "EnableNsfw": h_nsfw_on, "DisableNsfw": h_nsfw_off,
    "CloneChannel": h_clone_channel, "SyncChannelPermissions": h_sync_channel,
    "CreateThread": h_create_thread, "DeleteThread": h_delete_thread,
    "ArchiveThread": h_archive_thread, "UnarchiveThread": h_unarchive_thread,
    "LockThread": h_lock_thread, "UnlockThread": h_unlock_thread,
    "ChannelInfo": h_channel_info, "ListChannels": h_list_channels,
    "SetChannelBitrate": h_set_voice_bitrate, "SetChannelUserLimit": h_set_voice_limit,
    "ChannelPermissionRole": h_channel_perm_role, "ChannelPermissionMember": h_channel_perm_member,
    # B) الكاتجوريز
    "CreateCategory": h_create_category, "DeleteCategory": h_delete_category,
    "RenameCategory": h_rename_category, "ReorderCategory": h_reorder_category,
    "ListCategories": h_list_categories, "CategoryInfo": h_category_info,
    # C) الرتب
    "CreateRole": h_create_role, "DeleteRole": h_delete_role,
    "RenameRole": h_rename_role, "SetRoleColor": h_set_role_color,
    "SetRolePosition": h_set_role_position, "SetRolePermissions": h_set_role_permissions,
    "GrantRole": h_grant_role, "RemoveRole": h_remove_role,
    "RoleMembers": h_role_members, "CopyRole": h_copy_role,
    "ToggleRoleHoist": h_toggle_hoist, "ToggleRoleMentionable": h_toggle_mentionable,
    "RoleInfo": h_role_info, "ListRoles": h_list_roles,
    "GiveRoleToAll": h_give_role_all, "TakeRoleFromAll": h_remove_role_all,
    "GiveRoleToBots": h_give_role_bots, "GiveRoleToHumans": h_give_role_humans,
    # D) الأعضاء
    "KickMember": h_kick, "BanMember": h_ban, "SoftBanMember": h_softban,
    "UnbanMember": h_unban, "TimeoutMember": h_timeout, "RemoveTimeout": h_remove_timeout,
    "RenameMember": h_rename_member, "ResetNickname": h_reset_nickname,
    "VoiceMute": h_voice_mute, "VoiceUnmute": h_voice_unmute,
    "VoiceDeafen": h_voice_deafen, "VoiceUndeafen": h_voice_undeafen,
    "DisconnectMember": h_disconnect, "MoveMember": h_move_member,
    "WarnMember": h_warn, "UnwarnMember": h_unwarn,
    "ShowWarnings": h_show_warnings, "ClearWarnings": h_clear_warnings,
    "MemberInfo": h_member_info, "BannedList": h_banned_list, "BoostersList": h_boosters,
    "BanByID": h_ban_by_id,
    # E) الرسائل
    "ClearMessages": h_clear_messages, "ClearChannel": h_clear_channel,
    "ClearUserMessages": h_clear_user, "ClearBotMessages": h_clear_bots,
    "Announce": h_announce, "CreatePoll": h_poll, "SendEmbed": h_send_embed,
    "PinLastMessage": h_pin_last, "UnpinLastMessage": h_unpin_last, "SendDM": h_send_dm,
    "SendMessage": h_send_message, "ReactLastMessage": h_react_last,
    # F) الإنفيتات
    "CreateInvite": h_create_invite, "ListInvites": h_list_invites, "RevokeInvites": h_revoke_invites,
    # G) الإيموجي
    "AddEmoji": h_add_emoji, "RemoveEmoji": h_remove_emoji, "ListEmojis": h_list_emojis,
    # H) الويبهوكس
    "CreateWebhook": h_create_webhook, "DeleteWebhook": h_delete_webhook, "ListWebhooks": h_list_webhooks,
    # J) الصوتيات
    "VoiceChannelInfo": h_voice_channel_info,
    "MoveAllToVoice": h_move_all_voice, "DisconnectAllVoice": h_disconnect_all_voice,
    # K) المتعة
    "FlipCoin": h_flip_coin, "RollDice": h_roll_dice,
    "RandomNumber": h_random_number, "ChooseRandom": h_choose_random,
    "BotInfo": h_bot_info,
    # I) السيرفر
    "ServerInfo": h_server_info, "MemberCount": h_member_count, "OnlineCount": h_online_count,
    "ServerBoostCount": h_boost_count, "RenameServer": h_rename_server,
    "SetVerificationLevel": h_set_verification, "SetAfkChannel": h_set_afk,
    "SetSystemChannel": h_set_system_channel, "SetWelcome": h_set_welcome,
    "WelcomeOff": h_welcome_off, "SetAutoRole": h_set_autorole, "AutoRoleOff": h_autorole_off,
    "GreetTest": h_greet_test, "PermsForMember": h_perms_member, "PermsForRole": h_perms_role,
    "HighestRole": h_highest_role, "RandomMember": h_random_member, "MemberAvatar": h_member_avatar,
    "ServerIcon": h_server_icon, "ServerBanner": h_server_banner,
    "ServerSplash": h_server_splash, "CreateVanityURL": h_create_vanity,
    "ServerAvatar": h_server_avatar,
}


# ==========================================================================
# المشغّل الرئيسي
# ==========================================================================
async def execute(commands: list, guild, invoker, ai, cfg, channel) -> list:
    results = []
    for cmd in commands:
        for key, payload in cmd.items():
            await asyncio.sleep(max(0.0, float(cfg.action_cooldown)))

            skill = next((s for s in HANDLERS if key.startswith(s)), None)
            if skill is None:
                results.append(_fail(f"أمر غير معروف: `{key}`"))
                continue

            required = SKILL_PERM_MAP[skill]
            if not has_permission(invoker, required):
                results.append(_fail(f"مش عندك صلاحية `{required}` عشان تنفذ `{skill}`"))
                continue

            try:
                res = await HANDLERS[skill](guild, ai, payload if isinstance(payload, dict) else {}, invoker, channel)
                results.append(res if isinstance(res, dict) else _ok(str(res)))
            except discord.Forbidden:
                results.append(_fail(
                    f"البوت نفسه مش عنده صلاحية يعمل `{skill}` — شيك على صلاحيات البوت وترتيب الرتب (رتبة البوت لازم تكون فوق)"
                ))
            except discord.HTTPException as e:
                results.append(_fail(f"ديسكورد رفض `{skill}`: {e}"))
            except Exception as e:  # آخر خط دفاع — البوت ميقفش أبدًا
                results.append(_fail(f"خطأ غير متوقع في `{skill}`: {e}"))

    return results
