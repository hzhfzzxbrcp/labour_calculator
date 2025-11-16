# app.py  表情包版  兼容 Pillow 10+  无字体依赖
import streamlit as st
import requests
import io
import random
from PIL import Image, ImageDraw, ImageFont
import qrcode

st.set_page_config(page_title="校园剩余价值计算器", page_icon="💸", layout="centered")
st.title("💸 校园「剩余价值」计算器")
st.caption("输入工时与利润率，一键生成带表情包的海报")

# ---- 打工人表情包 URL 池（透明 PNG） ----
EMOJI_POOL = [
    "https://github.com/hzhfzzxbrcp/emoji/raw/main/dog1.png",
    "https://github.com/hzhfzzxbrcp/emoji/raw/main/dog2.png",
    "https://github.com/hzhfzzxbrcp/emoji/raw/main/cat1.png",
]

@st.cache_data(show_spinner=False)
def get_emoji(url):
    """缓存下载表情包"""
    return Image.open(io.BytesIO(requests.get(url, timeout=10).content))

with st.form("input_form"):
    c1, c2, c3 = st.columns(3)
    with c1:
        hourly_wage = st.number_input("时薪 (元)", min_value=0.0, step=1.0, value=25.0)
    with c2:
        hours = st.number_input("工作时长 (小时)", min_value=0.0, step=0.5, value=8.0)
    with c3:
        profit_rate = st.number_input("老板利润率 (%)", min_value=0.0, max_value=100.0, step=1.0, value=70.0)
    submitted = st.form_submit_button("计算并生成海报", type="primary")

if submitted:
    labour_value = hourly_wage * hours
    surplus_value = labour_value * (profit_rate / 100)
    st.success(f"今日被剩余价值：**{surplus_value:.2f} 元**")

    # ---- 画布 ----
    W, H = 1080, 1350
    img = Image.new("RGB", (W, H), (255, 250, 240))
    draw = ImageDraw.Draw(img)

    # ---- 字体 ----
    try:
        font_big = ImageFont.truetype("simhei.ttf", 80)
        font_mid = ImageFont.truetype("simhei.ttf", 50)
        font_sml = ImageFont.truetype("simhei.ttf", 40)
    except:
        font_big = font_mid = font_sml = ImageFont.load_default()

    # ---- 居中函数 ----
    def center_text(text, font, y):
        tmp = Image.new("RGBA", (1, 1))
        draw_tmp = ImageDraw.Draw(tmp)
        left, top, right, bottom = draw_tmp.textbbox((0, 0), text, font=font)
        w = right - left
        return ((W - w) // 2, y)

    # ---- 文字内容 ----
    line1 = "今日被剩余价值"
    line2 = f"￥{surplus_value:.2f}"
    line3 = f"时薪 {hourly_wage} 元 × 工时 {hours} 小时"
    line4 = f"老板利润率 {profit_rate}%"
    slogan = "打工人，打工魂！"

    # ---- 逐行写字 ----
    y_start = 200
    draw.text(center_text(line1, font_mid, y_start), line1, font=font_mid, fill=(60, 60, 60))
    draw.text(center_text(line2, font_big, y_start + 100), line2, font=font_big, fill=(255, 87, 34))
    draw.text(center_text(line3, font_sml, y_start + 250), line3, font=font_sml, fill=(60, 60, 60))
    draw.text(center_text(line4, font_sml, y_start + 320), line4, font=font_sml, fill=(60, 60, 60))
    draw.text(center_text(slogan, font_mid, H - 200), slogan, font=font_mid, fill=(255, 87, 34))

    # ---- 贴表情包 ----
    emoji = get_emoji(random.choice(EMOJI_POOL))
    # 统一高度 300px，保持比例
    emoji = emoji.resize((int(emoji.width * 300 / emoji.height), 300), Image.LANCZOS)
    img.paste(emoji, ((W - emoji.width) // 2, 420), emoji)  # 最后一个参数用自身 alpha

    # ---- 输出海报 ----
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    byte_data = buf.getvalue()
    st.download_button("📥 下载海报（含表情包）", byte_data,
                       file_name=f"剩余价值_{surplus_value:.0f}元.jpg", mime="image/jpeg")
    st.image(byte_data, caption="长按保存海报", use_column_width=True)

    # ---- 分享卡片（含二维码+表情包） ----
    card_w, card_h = 1080, 1080
    card = Image.new("RGB", (card_w, card_h), (255, 250, 240))
    draw_c = ImageDraw.Draw(card)

    lines = ["校园剩余价值计算器", f"今日被剩余：￥{surplus_value:.2f}", "扫码一起算"]
    fonts = [font_mid, font_big, font_sml]
    y_pos = [80, 180, 320]
    for txt, f, y in zip(lines, fonts, y_pos):
        draw_c.text(center_text(txt, f, y), txt, font=f, fill=(60, 60, 60))

    # 二维码
    qr = qrcode.QRCode(box_size=12, border=2)
    qr.add_data(st.secrets.get("url", "https://hzhfzzxbrcp-labour-calculator-streamlit-app-xxxxx.streamlit.app"))
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color=(255, 87, 34), back_color=(255, 250, 240))
    card.paste(qr_img, ((card_w - qr_img.width) // 2, 420))

    # 再贴一次表情包（小一点）
    emoji_small = emoji.resize((int(emoji.width * 150 / emoji.height), 150), Image.LANCZOS)
    card.paste(emoji_small, ((card_w - emoji_small.width) // 2, 650), emoji_small)

    buf2 = io.BytesIO()
    card.save(buf2, format="JPEG", quality=90)
    byte_card = buf2.getvalue()
    st.download_button("📥 下载分享卡片（表情包+码）", byte_card,
                       file_name=f"分享卡片_{surplus_value:.0f}元.jpg", mime="image/jpeg")
    st.image(byte_card, caption="长按保存分享", use_column_width=True)

with st.expander("什么是「剩余价值」？"):
    st.markdown("剩余价值 = 你创造的价值 − 工资。老板利润率越高，被“剩余”的就越多。")