"""
Disor v2 — بوت إدارة سيرفرات Discord بالذكاء الاصطناعي
نسخة مطورة من Disor: إصلاح كل مشاكل النسخة الأصلية + ميزات أقوى بكتير

المميزات:
- المشرفين بس (ADMIN_ONLY) — العضو العادي ممنوع
- 29 مهارة تنفيذ + ذاكرة محادثة + سياق للـ Parser
- رد أسرع: كاش سيرفر + استدعاءات LLM في فايبرات + موديل سريع للراوتر
- ترحيب + رول تلقائي للأعضاء الجدد
- سيرفر ويب keep-alive

التشغيل: python main.py
الإعدادات في data.json أو متغيرات البيئة (شوف README)
"""
import asyncio
import json
import logging
import time
from collections import defaultdict

import discord
from discord import app_commands
from discord.ext import commands

from ai import AI, extract_json
from memory import Memory
from settings import load_config
import skills as skills_mod
import web as web_mod
import guilddata

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("disor")

cfg = load_config()

if not cfg.token:
    raise SystemExit("❌ مفيش TOKEN في data.json أو DISCORD_TOKEN — حط توكن البوت")
if not cfg.api_key:
    raise SystemExit("❌ مفيش KEY في data.json أو GROQ_API_KEY — حط مفتاح Groq")

# --------------------------------------------------------------------------
# شخصية البوت (About) — بتتوصف للـ LLM في كل استدعاء
# --------------------------------------------------------------------------
_PERM_KEYS = ", ".join(sorted(discord.Permissions.VALID_FLAGS))

ABOUT = f"""You are a Discord server-management bot named Disor (Disor v2).
- Talk in Egyptian Arabic (المصريه العاميه) ONLY, never use any other language.
- You help users manage their Discord server. Be friendly, funny, and helpful.
- Keep answers reasonably short.

Available skills (126):
- Channels: create (text/voice/forum/stage), delete, rename, topic, move, lock/unlock, slowmode on/off, NSFW on/off, clone, sync perms, bitrate, user limit, channel perms (role/member), threads (create/delete/archive/unarchive/lock/unlock), info, list
- Categories: create, delete, rename, reorder, info, list
- Roles: create, delete, rename, color, position, permissions, grant, remove, members, copy, hoist, mentionable, info, list, give/remove to all, give to bots, give to humans
- Members: kick, ban, softban, unban, ban by ID, timeout, remove timeout, rename, reset nickname, voice mute/unmute, deafen/undeafen, disconnect, move, warn, unwarn, warnings, clear warnings, info, banned list, boosters
- Messages: clear, clear channel, clear user, clear bots, announce, poll, embed, pin/unpin, DM, send message, react last
- Invites, Emojis (add/remove/list), Webhooks (create/delete/list)
- Voice: voice channel info, move all to voice, disconnect all voice
- Fun: flip coin, roll dice, random number, choose random, bot info
- Server: info, member count, online count, boosts, rename, verification level, AFK channel, system channel, icon, banner, splash, vanity URL, welcome, autorole, perms check, random member, avatar

Aliases:
Channel: روم - شات - غرفه - قناة - شانل
Voice: فويس - صوتي
Role: رول - رتبه
Category: كاتجوري - قسم - تصنيف
Member: عضو - شخص - واحد
Kick: طرد | Ban: بان - حظر | Timeout: كتم - ميوت | Warn: حذر - تحذير
Poll: استطلاع - تصويت | Thread: ثريد | Webhook: ويبهوك | Clear: مسح - تنظيف | NSFW: روم 18+

Discord permission keys (use ONLY these in "Perms"):
{_PERM_KEYS}

⚠️ IMPORTANT (permissions):
- NEVER grant "administrator" unless the user EXPLICITLY asks for full admin (كل الصلاحيات / full admin / owner-level).
- If the user asks for an "admin role with what it needs" WITHOUT explicitly requesting administrator,
  infer the SPECIFIC safe permissions instead: manage_roles, manage_channels, kick_members, ban_members,
  manage_messages, manage_guild, moderate_members.
- When in doubt, prefer specific permissions over "administrator".
- A role's NAME does not determine its permissions (a role named "Admin" does not need administrator)."""


# --------------------------------------------------------------------------
# الإعدادات والكائنات
# --------------------------------------------------------------------------
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # privileged intent — فعّله في Developer Portal

bot = commands.Bot(command_prefix=cfg.prefix, intents=intents, help_command=None)
ai = AI(cfg.api_key, cfg.model, ABOUT, json_mode=cfg.json_mode, model_fast=cfg.model_fast)
memory = Memory(maxlen=cfg.max_history)

_START_TIME = time.time()
_chunked_guilds = set()
_info_cache: dict = {}
_rate: dict = defaultdict(list)       # user_id -> [timestamps]
_last_warn: dict = {}                 # user_id -> آخر وقت تحذير


def _rate_allowed(user_id: int) -> bool:
    now = time.time()
    lst = [t for t in _rate[user_id] if now - t < 60]
    _rate[user_id] = lst
    if len(lst) >= cfg.rate_limit_per_min:
        return False
    lst.append(now)
    return True


def is_admin(member: discord.Member) -> bool:
    """مين يعتبر 'مشرف' عشان يستخدم البوت أصلاً:
    مالك السيرفر أو عنده administrator أو لابس رول ALLOWED_ROLE."""
    if member == member.guild.owner:
        return True
    if member.guild_permissions.administrator:
        return True
    if cfg.allowed_role:
        rid = cfg.allowed_role
        for r in member.roles:
            if (rid.isdigit() and r.id == int(rid)) or r.name == rid:
                return True
    return False


def _build_server_info(guild: discord.Guild) -> str:
    """ملخص السيرفر اللي بيتبعت للـ LLM."""
    lines = [f"Server: {guild.name} ({guild.id})"]
    lines.append("Categories:")
    for c in guild.categories:
        lines.append(f"- {c.name} ({c.id})")
    lines.append("Channels:")
    for ch in guild.channels:
        kind = "voice" if isinstance(ch, discord.VoiceChannel) else (
            "forum" if isinstance(ch, discord.ForumChannel) else
            "stage" if isinstance(ch, discord.StageChannel) else "text")
        lines.append(f"- {ch.name} ({ch.id}) [{kind}]")
    lines.append("Roles:")
    for r in sorted(guild.roles, key=lambda r: r.position, reverse=True):
        if r.name != "@everyone":
            lines.append(f"- Pos {r.position}: {r.name} ({r.id})")
    lines.append("Members (first 150):")
    for mem in guild.members[:150]:
        gn = mem.global_name or mem.name
        lines.append(f"- {mem.name} | {gn} ({mem.id})")
    return "\n".join(lines)


def server_info(guild: discord.Guild) -> str:
    """مع كاش — بيتحسب مرة ويتجدد لما السيرفر يتغير (أسرع وأرخص)."""
    cached = _info_cache.get(guild.id)
    if cached:
        return cached
    info = _build_server_info(guild)
    _info_cache[guild.id] = info
    return info


def _invalidate(guild_id: int):
    _info_cache.pop(guild_id, None)


# --------------------------------------------------------------------------
# أوامر نصية (بريفكس)
# --------------------------------------------------------------------------
def _deny(ctx) -> bool:
    if is_admin(ctx.author):
        return False
    asyncio.create_task(ctx.reply("⛔ ممنوع — دي أوامر للمشرفين بس."))
    return True


@bot.command(name="help", aliases=["مساعدة", "اوامر"])
async def help_cmd(ctx):
    embed = discord.Embed(
        title="🤖 Disor v3.5 — 126 مهارة",
        description="بوت إدارة سيرفرات بالذكاء الاصطناعي — اكتبله طلبك بالعامية وهو ينفذه!",
        color=discord.Colour.bright_green(),
    )
    embed.add_field(name="📢 مثال", value='اكتب `@Disor اعمل روم اسمه chat وحطه في كاتجوري Generals`', inline=False)
    embed.add_field(
        name="🛠️ المهارات (126)",
        value=(
            "• رومات: إنشاء/حذف/تعديل/نقل/قفل/فتح/سلو مود/وصف/NSFW/نسخ/بيتريت/صلاحيات\n"
            "• ثريدز: فتح/حذف/أرشفة/قفل\n"
            "• كاتجوريز: إنشاء/حذف/إعادة تسمية/ترتيب\n"
            "• رتب: إنشاء/حذف/تعديل/نسخ + إعطاء/سحب/للجميع/للبوتات\n"
            "• أعضاء: طرد/بان/سوفت بان/بان بالـ ID/كتم/تغيير اسم/صوتي كامل\n"
            "• تحذيرات: تحذير/شيل/عرض/مسح\n"
            "• صوتيات: معلومات روم/نقل الجميع/فصل الجميع\n"
            "• رسائل: مسح/إعلان/استطلاع/إيمبيد/تثبيت/رسالة/ريأكشن\n"
            "• سيرفر: أيقونة/بانر/فانيتي + إيموجي/ويبهوكس/إنفيتات + متعة"
        ),
        inline=False,
    )
    embed.add_field(
        name="🔧 أوامر نصية",
        value=(
            f"`{cfg.prefix}help` — المساعدة\n"
            f"`{cfg.prefix}status` — حالة البوت\n"
            f"`{cfg.prefix}welcome #قناة <نص>` — إعداد الترحيب\n"
            f"`{cfg.prefix}autorole @رتبة` — رول تلقائي للأعضاء الجدد\n"
            f"`{cfg.prefix}settings` — إعدادات السيرفر\n"
            f"`{cfg.prefix}warnings @عضو` — تحذيرات عضو"
        ),
        inline=False,
    )
    embed.add_field(
        name="⚡ أوامر سلايش",
        value="`/help` • `/status` • `/settings` • `/warnings` — بتظهر فورًا عند أول تشغيل.",
        inline=False,
    )
    embed.add_field(
        name="🔐 صلاحيات الاستخدام",
        value="البوت بيستجيب **للمشرفين بس** — العضو العادي ممنوع ⛔، وكل أمر لازم الصلاحية المطلوبة له.",
        inline=False,
    )
    await ctx.send(embed=embed)


@bot.command(name="skills", aliases=["المهارات"])
async def skills_cmd(ctx):
    if _deny(ctx):
        return
    embed = discord.Embed(title="🛠️ مهارات Disor", color=discord.Colour.bright_green())
    groups = {
        "🟦 القنوات": 28, "🟨 الكاتجوريز": 6, "🟩 الرتب": 18,
        "🟥 الأعضاء": 22, "🟪 الرسائل": 12, "🟫 الإنفيتات": 3,
        "🟧 الإيموجي": 3, "🟦 الويبهوكس": 3, "🎙️ الصوتيات": 3,
        "🟩 السيرفر": 23, "🎲 المتعة": 5,
    }
    total = sum(groups.values())
    embed.add_field(name=f"⚙️ إجمالي المهارات: {total}", value="مقسمة على المجموعات التالية 👇", inline=False)
    for name, count in groups.items():
        embed.add_field(name=name, value=f"{count} مهارة", inline=True)
    embed.set_footer(text="اكتب @Disor + طلبك بالعامية 😉")
    await ctx.send(embed=embed)


@bot.command(name="ping")
async def ping_cmd(ctx):
    await ctx.send(f"🏓 Pong! `{round(bot.latency * 1000)}ms`")


@bot.command(name="status", aliases=["الحالة"])
async def status_cmd(ctx):
    uptime = time.time() - _START_TIME
    h, rem = divmod(int(uptime), 3600)
    m, s = divmod(rem, 60)
    embed = discord.Embed(title="📊 حالة Disor", color=discord.Colour.bright_green())
    embed.add_field(name="البنق", value=f"{round(bot.latency * 1000)}ms", inline=True)
    embed.add_field(name="السيرفرات", value=len(bot.guilds), inline=True)
    embed.add_field(name="مدة التشغيل", value=f"{h}h {m}m {s}s", inline=True)
    embed.add_field(name="وضع المشرفين فقط", value="✅ مفعل" if cfg.admin_only else "❌ معطل", inline=True)
    embed.add_field(name="الموديل", value=cfg.model, inline=False)
    await ctx.send(embed=embed)


@bot.command(name="welcome", aliases=["ترحيب"])
async def welcome_cmd(ctx, channel: discord.TextChannel = None, *, text: str = None):
    if _deny(ctx):
        return
    g = guilddata.get(ctx.guild.id)
    if channel is None and text is None:
        cur = g.get("welcome_channel")
        cur_ch = bot.get_channel(cur) if cur else None
        await ctx.reply(
            "الترحيب الحالي:\n"
            f"• القناة: {cur_ch.mention if cur_ch else 'معطل ❌'}\n"
            f"• النص: {g.get('welcome_text') or 'معطل'}\n"
            f"لإعداده: `{cfg.prefix}welcome #قناة النص هنا`"
        )
        return
    if channel is None:
        await ctx.reply("محتاج تذكر القناة: `!welcome #قناة النص`")
        return
    guilddata.set_welcome(ctx.guild.id, channel.id, text or None)
    await ctx.reply(f"✅ تم ضبط الترحيب في {channel.mention}" + (f" — النص: {text}" if text else ""))


@bot.command(name="welcomeoff", aliases=["ايقاف_الترحيب"])
async def welcomeoff_cmd(ctx):
    if _deny(ctx):
        return
    guilddata.set_welcome(ctx.guild.id, None, None)
    await ctx.reply("✅ تم إيقاف الترحيب")


@bot.command(name="autorole", aliases=["رول_تلقائي"])
async def autorole_cmd(ctx, role: discord.Role = None):
    if _deny(ctx):
        return
    if role is None:
        g = guilddata.get(ctx.guild.id)
        rid = g.get("autorole")
        r = ctx.guild.get_role(rid) if rid else None
        await ctx.reply(f"الرول التلقائي الحالي: {r.mention if r else 'معطل ❌'} — للإعداد: `{cfg.prefix}autorole @رتبة`")
        return
    if role >= ctx.guild.me.top_role:
        await ctx.reply("⚠️ رتبة البوت لازم تكون فوق الرتبة دي عشان يديها تلقائيًا.")
        return
    guilddata.set_autorole(ctx.guild.id, role.id)
    await ctx.reply(f"✅ الأعضاء الجدد هياخدوا رتبة {role.mention} تلقائيًا")


@bot.command(name="autoroleoff", aliases=["ايقاف_الرول"])
async def autoroleoff_cmd(ctx):
    if _deny(ctx):
        return
    guilddata.set_autorole(ctx.guild.id, None)
    await ctx.reply("✅ تم إيقاف الرول التلقائي")


@bot.command(name="settings", aliases=["الاعدادات"])
async def settings_cmd(ctx):
    if _deny(ctx):
        return
    g = guilddata.get(ctx.guild.id)
    wch = g.get("welcome_channel")
    wch_mention = bot.get_channel(wch).mention if wch and bot.get_channel(wch) else "معطل ❌"
    rid = g.get("autorole")
    role_mention = ctx.guild.get_role(rid).mention if rid and ctx.guild.get_role(rid) else "معطل ❌"
    embed = discord.Embed(title=f"⚙️ إعدادات {ctx.guild.name}", color=discord.Colour.blurple())
    embed.add_field(name="👋 قناة الترحيب", value=wch_mention, inline=True)
    embed.add_field(name="🎖️ الرول التلقائي", value=role_mention, inline=True)
    embed.add_field(name="🔐 وضع المشرفين فقط", value="✅" if cfg.admin_only else "❌", inline=True)
    embed.add_field(name="🚪 القنوات المسموحة", value="الكل 🌍" if not cfg.allowed_channels else f"{len(cfg.allowed_channels)} قناة", inline=True)
    embed.add_field(name="🤖 الموديل", value=cfg.model, inline=False)
    await ctx.send(embed=embed)


@bot.command(name="warnings", aliases=["التحذيرات"])
async def warnings_cmd(ctx, member: discord.Member = None):
    if _deny(ctx):
        return
    member = member or ctx.author
    lst = skills_mod.list_warnings(ctx.guild.id, member.id)
    if not lst:
        await ctx.reply(f"{member.mention} نظيف — مفيش عليه تحذيرات ✅")
        return
    lines = [f"⚠️ تحذيرات {member.mention} ({len(lst)}):"]
    for i, w in enumerate(lst, 1):
        ts = time.strftime("%Y-%m-%d %H:%M", time.localtime(w["ts"]))
        lines.append(f"{i}. {w['reason']} — بواسطة {w['by']} ({ts})")
    await ctx.reply("\n".join(lines))


# --------------------------------------------------------------------------
# أوامر سلايش (Slash Commands) — المظهر الحديث
# --------------------------------------------------------------------------
@bot.tree.command(name="help", description="📖 كل مهارات Disor")
async def slash_help(interaction: discord.Interaction):
    await interaction.response.send_message(
        "📖 **Disor v2** — بوت إدارة بالذكاء الاصطناعي\n\n"
        "اكتب `@Disor` + طلبك بالعامية وهو ينفذه! مثلًا:\n"
        "> @Disor اعمل روم اسمه chat وحطه في كاتجوري Generals\n\n"
        f"أو استخدم `{cfg.prefix}help` للتفاصيل الكاملة",
        ephemeral=True,
    )


@bot.tree.command(name="status", description="📊 حالة البوت")
async def slash_status(interaction: discord.Interaction):
    uptime = time.time() - _START_TIME
    h, rem = divmod(int(uptime), 3600)
    m, s = divmod(rem, 60)
    embed = discord.Embed(title="📊 حالة Disor", color=discord.Colour.bright_green())
    embed.add_field(name="البنق", value=f"{round(bot.latency * 1000)}ms", inline=True)
    embed.add_field(name="السيرفرات", value=len(bot.guilds), inline=True)
    embed.add_field(name="مدة التشغيل", value=f"{h}h {m}m {s}s", inline=True)
    embed.add_field(name="وضع المشرفين فقط", value="✅ مفعل" if cfg.admin_only else "❌ معطل", inline=True)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="settings", description="⚙️ إعدادات السيرفر")
async def slash_settings(interaction: discord.Interaction):
    if not is_admin(interaction.user):
        await interaction.response.send_message("⛔ ممنوع — للمشرفين بس.", ephemeral=True)
        return
    g = guilddata.get(interaction.guild_id)
    wch = g.get("welcome_channel")
    wch_mention = bot.get_channel(wch).mention if wch and bot.get_channel(wch) else "معطل ❌"
    rid = g.get("autorole")
    role_mention = interaction.guild.get_role(rid).mention if rid and interaction.guild.get_role(rid) else "معطل ❌"
    embed = discord.Embed(title=f"⚙️ إعدادات {interaction.guild.name}", color=discord.Colour.blurple())
    embed.add_field(name="👋 قناة الترحيب", value=wch_mention, inline=True)
    embed.add_field(name="🎖️ الرول التلقائي", value=role_mention, inline=True)
    embed.add_field(name="🔐 وضع المشرفين فقط", value="✅" if cfg.admin_only else "❌", inline=True)
    embed.add_field(name="🤖 الموديل", value=cfg.model, inline=False)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="warnings", description="⚠️ تحذيرات عضو")
async def slash_warnings(interaction: discord.Interaction, member: discord.Member = None):
    if not is_admin(interaction.user):
        await interaction.response.send_message("⛔ ممنوع — للمشرفين بس.", ephemeral=True)
        return
    member = member or interaction.user
    lst = skills_mod.list_warnings(interaction.guild_id, member.id)
    if not lst:
        await interaction.response.send_message(f"{member.mention} نظيف — مفيش عليه تحذيرات ✅")
        return
    lines = [f"⚠️ تحذيرات {member.mention} ({len(lst)}):"]
    for i, w in enumerate(lst, 1):
        ts = time.strftime("%Y-%m-%d %H:%M", time.localtime(w["ts"]))
        lines.append(f"{i}. {w['reason']} — بواسطة {w['by']} ({ts})")
    await interaction.response.send_message("\n".join(lines))


# --------------------------------------------------------------------------
# أحداث الكاش (تجديد معلومات السيرفر عند أي تغيير)
# --------------------------------------------------------------------------
@bot.event
async def on_guild_channel_create(channel): _invalidate(channel.guild.id)
@bot.event
async def on_guild_channel_delete(channel): _invalidate(channel.guild.id)
@bot.event
async def on_guild_channel_update(before, after): _invalidate(after.guild.id)
@bot.event
async def on_guild_role_create(role): _invalidate(role.guild.id)
@bot.event
async def on_guild_role_delete(role): _invalidate(role.guild.id)
@bot.event
async def on_guild_role_update(before, after): _invalidate(after.guild.id)
@bot.event
async def on_member_join(member): _invalidate(member.guild.id)
@bot.event
async def on_member_remove(member): _invalidate(member.guild.id)
@bot.event
async def on_member_update(before, after): _invalidate(after.guild.id)
@bot.event
async def on_guild_update(before, after): _invalidate(after.id)


# --------------------------------------------------------------------------
# ترحيب + رول تلقائي للأعضاء الجدد
# --------------------------------------------------------------------------
@bot.event
async def on_member_join(member: discord.Member):
    g = guilddata.get(member.guild.id)
    try:
        if g.get("autorole"):
            role = member.guild.get_role(g["autorole"])
            if role and role < member.guild.me.top_role:
                await member.add_roles(role)
    except Exception as e:
        log.warning("autorole فشل لـ %s: %s", member, e)

    try:
        if g.get("welcome_channel") and g.get("welcome_text"):
            ch = member.guild.get_channel(g["welcome_channel"])
            if ch:
                text = str(g["welcome_text"])
                text = text.replace("{user}", member.mention).replace("{server}", member.guild.name)
                await ch.send(text[:2000])
    except Exception as e:
        log.warning("ترحيب فشل لـ %s: %s", member, e)


# --------------------------------------------------------------------------
# مسارات المعالجة
# --------------------------------------------------------------------------
async def _feedback(m: discord.Message, results: list):
    ok_count = sum(1 for r in results if r["ok"])
    total = len(results)
    if total == 0:
        return

    if ok_count == total:
        txt = "تم ✅"
    elif ok_count > 0:
        txt = f"تم خلصت {ok_count} من {total} ✅ والباقي فيه مشاكل ❌"
    else:
        txt = "مقدرتش أنفذ الطلب ❌"
    try:
        await m.reply(txt)
    except discord.HTTPException:
        pass

    try:
        if ok_count == total:
            await m.add_reaction("✅")
        elif ok_count > 0:
            await m.add_reaction("🟡")
        else:
            await m.add_reaction("❌")
    except discord.HTTPException:
        pass

    color = discord.Colour.green() if ok_count == total else discord.Colour.orange()
    embed = discord.Embed(
        title=f"تنفيذ الأوامر: {ok_count}/{total}",
        description="نتيجة كل أمر 👇",
        color=color,
    )
    for r in results:
        embed.add_field(name="✅ نجح" if r["ok"] else "❌ فشل", value=r["text"][:1024], inline=False)
    try:
        await m.channel.send(embed=embed)
    except discord.Forbidden:
        pass


async def _audit(m: discord.Message, results: list):
    if not cfg.audit_channel:
        return
    ch = m.guild.get_channel(cfg.audit_channel)
    if not ch:
        return
    try:
        embed = discord.Embed(title="📋 سجل عمليات", color=discord.Colour.dark_blue(), timestamp=discord.utils.utcnow())
        embed.set_author(name=str(m.author), icon_url=m.author.display_avatar.url)
        embed.add_field(name="الطلب", value=m.content[:1000], inline=False)
        for i, r in enumerate(results, 1):
            embed.add_field(name=f"{i}. " + ("✅" if r["ok"] else "❌"), value=r["text"][:1024], inline=False)
        await ch.send(embed=embed)
    except Exception as e:
        log.warning("audit failed: %s", e)


async def _handle_action(m: discord.Message, text: str):
    """مسار تنفيذ الأوامر."""
    if not is_admin(m.author):
        await m.reply("⚠️ مش عندك صلاحية إدارة السيرفر عشان تطلب أوامر تنفيذ.")
        return

    # رسالة "لحظات هعمله" قبل ما يشتغل (في فايبر عشان ميبلكش)
    try:
        ack = await asyncio.to_thread(ai.actioner, text)
        await m.reply(ack)
    except Exception as e:
        log.warning("actioner failed: %s", e)
        await m.reply("لحظات هعمله... ⏳")

    # الكلام → JSON (مع سياق الطلبات السابقة للفهم الأعمق)
    try:
        raw = await asyncio.to_thread(ai.parse, text, server_info(m.guild), memory.get_requests(m.author.id))
        commands = extract_json(raw) if isinstance(raw, str) else raw
    except Exception as e:
        log.exception("parser failed")
        await m.reply("🤔 ماقدرتش أفهم طلبك كويس.. جرّب تصيغه تاني (مثال: *اعمل روم اسمه chat*).")
        return

    cmds = []
    no_skill_msg = None
    for key, payload in commands.items():
        if str(key).startswith("NoSkill"):
            no_skill_msg = payload.get("Reply") if isinstance(payload, dict) else None
            continue
        cmds.append({key: payload})

    if no_skill_msg:
        await m.reply(no_skill_msg)
    if not cmds:
        return

    results = await skills_mod.execute(cmds, m.guild, m.author, ai, cfg, m.channel)
    await _feedback(m, results)
    await _audit(m, results)


async def _handle_chat(m: discord.Message, text: str):
    """مسار المحادثة العادية مع ذاكرة."""
    history = memory.get(m.author.id)
    try:
        reply = await asyncio.to_thread(ai.chat, text, history, server_info(m.guild))
    except Exception as e:
        log.exception("chat failed")
        await m.reply("⚠️ حصلت مشكلة في الرد.. جرّب تاني بعد شوية.")
        return
    memory.add(m.author.id, "user", text)
    memory.add(m.author.id, "assistant", reply)
    try:
        await m.reply(reply)
    except discord.HTTPException as e:
        log.warning("reply failed: %s", e)


# --------------------------------------------------------------------------
# الحدث الرئيسي
# --------------------------------------------------------------------------
@bot.event
async def on_ready():
    log.info("✅ جاهز! دخول كـ %s (ID: %s)", bot.user, bot.user.id)
    log.info("السيرفرات: %s", ", ".join(g.name for g in bot.guilds) or "مفيش")
    try:
        await bot.change_presence(activity=discord.Activity(
            type=discord.ActivityType.listening, name="طلبات المشرفين 👀"))
    except Exception:
        pass
    web_mod.set_status(online=True, guilds=len(bot.guilds), latency_ms=bot.latency * 1000)

    # مزامنة أوامر السلايش لكل سيرفر (بتظهر فورًا)
    for guild in bot.guilds:
        try:
            await bot.tree.sync(guild=guild)
        except Exception as e:
            log.warning("sync سلايش فشل لـ %s: %s", guild.name, e)


async def _ensure_members(guild: discord.Guild):
    """تحميل الأعضاء مرة واحدة لكل سيرفر (عشان الاسم → ID يشتغل صح)."""
    if guild.id not in _chunked_guilds:
        _chunked_guilds.add(guild.id)
        try:
            if not guild.chunked:
                await guild.chunk(cache=True)
        except Exception as e:
            log.warning("chunking failed for %s: %s", guild.name, e)


@bot.event
async def on_message(m: discord.Message):
    if m.author.bot or not m.guild:
        return

    # الأوامر النصية (بريفكس)
    if m.content.startswith(cfg.prefix):
        await bot.process_commands(m)
        return

    # فلترة القنوات
    if cfg.allowed_channels and m.channel.id not in cfg.allowed_channels:
        return

    mentioned = bot.user in m.mentions
    if cfg.require_mention and not mentioned:
        return

    text = m.content
    if mentioned:
        text = text.replace(f"<@{bot.user.id}>", "").replace(f"<@!{bot.user.id}>", "").strip()
    if not text:
        return

    # 🔒 المشرفين بس — العضو العادي ممنوع ⛔
    if cfg.admin_only and not is_admin(m.author):
        now = time.time()
        if now - _last_warn.get(m.author.id, 0) > 30:
            _last_warn[m.author.id] = now
            try:
                await m.reply("⛔ ممنوع — البوت للمشرفين بس.")
            except discord.HTTPException:
                pass
        return

    # حد المعدل
    if not _rate_allowed(m.author.id):
        now = time.time()
        if now - _last_warn.get(m.author.id, 0) > 10:
            _last_warn[m.author.id] = now
            await m.reply("🛑 انت بتكلم بسرعة جدًا.. استنى شوية.")
        return

    # تسجيل الطلب للسياق + تحميل الأعضاء
    memory.add_request(m.author.id, text)
    await _ensure_members(m.guild)

    try:
        async with m.channel.typing():
            decision = await asyncio.to_thread(ai.router, text)
            log.info("[%s] %s -> %s", m.author, text[:80], decision)
            if decision == "USER_WANTS_ACTION":
                await _handle_action(m, text)
            else:
                await _handle_chat(m, text)
    except Exception as e:
        log.exception("unhandled error")
        try:
            await m.reply("⚠️ حصل خطأ غير متوقع.. جرب تاني.")
        except Exception:
            pass


if __name__ == "__main__":
    # سيرفر الويب (keep-alive)
    web_mod.start_web(cfg.web_port)
    try:
        bot.run(cfg.token)
    except discord.LoginFailure:
        raise SystemExit("❌ التوكن غلط — راجع توكن البوت")
