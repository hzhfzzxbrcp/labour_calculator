# app.py  系统黑体+降级画布  无二维码  兼容 Pillow 10+
import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io

st.set_page_config(page_title="剩余价值计算器", page_icon="💸", layout="centered")
st.title("💸 校园「剩余价值」计算器")
st.caption("输入工时与利润率，一键生成朋友圈海报")

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

    # ---- 画布大小 & 字体 ----
    try:
        font_big = ImageFont.truetype("simhei.ttf", 80)
        font_mid = ImageFont.truetype("simhei.ttf", 50)
        font_sml = ImageFont.truetype("simhei.ttf", 40)
        W, H = 1080, 1350
    except:
        # 降级：画布减半 + 默认字体
        font_big = font_mid = font_sml = ImageFont.load_default()
        W, H = 540, 675

    img = Image.new("RGB", (W, H), (255, 250, 240))
    draw = ImageDraw.Draw(img)

    # ---- 居中函数（Pillow 10+） ----
    def center(text, y):
        tmp = Image.new("RGBA", (1, 1))
        left, _, right, _ = ImageDraw.Draw(tmp).textbbox((0, 0), text, font=font_big)
        w = right - left
        return ((W - w) // 2, y)

    # ---- 写字 ----
    y_start = 200
    draw.text(center("今日被剩余价值", y_start), "今日被剩余价值", font=font_mid, fill=(60, 60, 60))
    draw.text(center(f"￥{surplus:.2f}", y_start + 100), f"￥{surplus:.2f}", font=font_big, fill=(255, 87, 34))
    draw.text(center(f"时薪 {hourly} × 工时 {hours} × 利润率 {rate}%", y_start + 220),
              f"时薪 {hourly} × 工时 {hours} × 利润率 {rate}%", font=font_sml, fill=(60, 60, 60))
    draw.text(center("打工人，打工魂！", H - 120), "打工人，打工魂！", font=font_mid, fill=(255, 87, 34))

    # ---- 输出 ----
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    byte_data = buf.getvalue()
    st.download_button("📥 下载海报", byte_data, file_name=f"剩余价值_{surplus:.0f}元.jpg", mime="image/jpeg")
    st.image(byte_data, caption="长按保存海报", use_column_width=True)

with st.expander("什么是「剩余价值」？"):
    st.markdown("剩余价值 = 你创造的价值 − 工资。老板利润率越高，被“剩余”的就越多。")