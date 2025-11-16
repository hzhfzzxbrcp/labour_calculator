# app.py  极简·分享卡片带二维码  兼容 Pillow 10+
import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import qrcode
import io

st.set_page_config(page_title="剩余价值计算器", page_icon="💸", layout="centered")
st.title("💸 校园「剩余价值」计算器")

with st.form("form"):
    c1, c2, c3 = st.columns(3)
    with c1:
        hourly = st.number_input("时薪(元)", min_value=0.0, step=1.0, value=25.0)
    with c2:
        hours = st.number_input("工时(小时)", min_value=0.0, step=0.5, value=8.0)
    with c3:
        rate = st.number_input("利润率(%)", min_value=0.0, max_value=100.0, step=1.0, value=70.0)
    submitted = st.form_submit_button("计算并生成海报", type="primary")

if submitted:
    surplus = hourly * hours * (rate / 100)
    st.success(f"今日被剩余价值：**{surplus:.2f} 元**")

    # ---- 画布 ----
    W, H = 1080, 1350
    img = Image.new("RGB", (W, H), (255, 250, 240))
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()  # 零依赖

    # ---- 居中（Pillow 10+） ----
    def center(text, y):
        tmp = Image.new("RGBA", (1, 1))
        left, _, right, _ = ImageDraw.Draw(tmp).textbbox((0, 0), text, font=font)
        return ((W - (right - left)) // 2, y)

    # ---- 写字 ----
    y_start = 300
    draw.text(center("今日被剩余价值", y_start), "今日被剩余价值", font=font, fill=(60, 60, 60))
    draw.text(center(f"￥{surplus:.2f}", y_start + 80), f"￥{surplus:.2f}", font=font, fill=(255, 87, 34))
    draw.text(center(f"时薪 {hourly} × 工时 {hours} × 利润率 {rate}%", y_start + 160),
              f"时薪 {hourly} × 工时 {hours} × 利润率 {rate}%", font=font, fill=(60, 60, 60))

    # ---- 输出海报 ----
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    byte_img = buf.getvalue()
    st.download_button("📥 下载海报", byte_img, file_name=f"海报_{surplus:.0f}元.jpg", mime="image/jpeg")
    st.image(byte_img, use_column_width=True)

    # ---- 分享卡片（带二维码） ----
    card_w, card_h = 1080, 1080
    card = Image.new("RGB", (card_w, card_h), (255, 250, 240))
    draw_c = ImageDraw.Draw(card)

    draw_c.text(center("校园剩余价值计算器", 100), "校园剩余价值计算器", font=font, fill=(60, 60, 60))
    draw_c.text(center(f"今日被剩余：￥{surplus:.2f}", 200), f"今日被剩余：￥{surplus:.2f}", font=font, fill=(255, 87, 34))
    draw_c.text(center("扫码一起算", 320), "扫码一起算", font=font, fill=(60, 60, 60))

    # 二维码
    qr = qrcode.QRCode(box_size=15, border=2)
    qr.add_data("https://你的公网地址.streamlit.app")  # ← 换成你真实的地址
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color=(255, 87, 34), back_color=(255, 250, 240))
    qr_xy = ((card_w - qr_img.width) // 2, 420)
    card.paste(qr_img, qr_xy)

    buf2 = io.BytesIO()
    card.save(buf2, format="JPEG", quality=90)
    byte_card = buf2.getvalue()
    st.download_button("📥 下载分享卡片（含二维码）", byte_card,
                       file_name=f"分享卡片_{surplus:.0f}元.jpg", mime="image/jpeg")
    st.image(byte_card, caption="长按保存分享", use_column_width=True)