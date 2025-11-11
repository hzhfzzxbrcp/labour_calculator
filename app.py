# app.py
import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import base64
import os

# ---------- 页面元信息 ----------
st.set_page_config(
    page_title="校园剩余价值计算器",
    page_icon="💸",
    layout="centered"
)

# ---------- 标题 ----------
st.title("💸 校园「剩余价值」计算器")
st.caption("输入工时与利润率，一键生成朋友圈海报")

# ---------- 输入表单 ----------
with st.form("input_form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        hourly_wage = st.number_input("时薪 (元)", min_value=0.0, step=1.0, value=25.0)
    with col2:
        hours = st.number_input("工作时长 (小时)", min_value=0.0, step=0.5, value=8.0)
    with col3:
        profit_rate = st.number_input("老板利润率 (%)", min_value=0.0, max_value=100.0, step=1.0, value=70.0)
    submitted = st.form_submit_button("计算并生成海报", type="primary")

# ---------- 计算 ----------
if submitted:
    labour_value = hourly_wage * hours                     # 劳动力价值
    surplus_value = labour_value * (profit_rate / 100)     # 被剥削的剩余价值
    st.success(f"今日被剩余价值：**{surplus_value:.2f} 元**")

    # ---------- 生成海报 ----------
    # 画布尺寸
    W, H = 1080, 1350
    # 背景色
    bg_color = (255, 250, 240)
    img = Image.new("RGB", (W, H), bg_color)
    draw = ImageDraw.Draw(img)

    # 字体（优先用系统自带，没有则下载）
    try:
        font_big = ImageFont.truetype("simhei.ttf", 80)
        font_mid = ImageFont.truetype("simhei.ttf", 50)
        font_sml = ImageFont.truetype("simhei.ttf", 40)
    except:
        # 下载开源字体
        import requests
        url = "https://github.com/StellarCN/scp_zh/raw/master/fonts/SimHei.ttf"
        r = requests.get(url)
        with open("simhei.ttf", "wb") as f:
            f.write(r.content)
        font_big = ImageFont.truetype("simhei.ttf", 80)
        font_mid = ImageFont.truetype("simhei.ttf", 50)
        font_sml = ImageFont.truetype("simhei.ttf", 40)

    # 文字内容
    line1 = "今日被剩余价值"
    line2 = f"￥{surplus_value:.2f}"
    line3 = f"时薪 {hourly_wage} 元 × 工时 {hours} 小时"
    line4 = f"老板利润率 {profit_rate}%"

    # 文字颜色
    text_color = (60, 60, 60)
    accent_color = (255, 87, 34)

    # ---------- 居中辅助函数（兼容 Pillow 10+） ----------
def center_text(text, font, y):
    """
    返回文字左上角坐标 (x, y)，使其水平居中
    """
    # 用 textbbox 计算文字宽高（需要临时开一个 1×1 透明图）
    tmp = Image.new("RGBA", (1, 1), (0, 0, 0, 0))
    draw_tmp = ImageDraw.Draw(tmp)
    left, top, right, bottom = draw_tmp.textbbox((0, 0), text, font=font)
    w = right - left
    h = bottom - top          # 如果后续需要高度也能用
    x = (W - w) // 2
    return (x, y)
    # 逐行绘制
    y_start = 200
    draw.text(center_text(line1, font_mid, y_start), line1, font=font_mid, fill=text_color)
    draw.text(center_text(line2, font_big, y_start + 100), line2, font=font_big, fill=accent_color)
    draw.text(center_text(line3, font_sml, y_start + 250), line3, font=font_sml, fill=text_color)
    draw.text(center_text(line4, font_sml, y_start + 320), line4, font=font_sml, fill=text_color)

    # 底部 slogan
    slogan = "打工人，打工魂！"
    draw.text(center_text(slogan, font_mid, H - 200), slogan, font=font_mid, fill=accent_color)

    # 保存到内存
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=95)
    byte_data = buf.getvalue()

    # ---------- 提供下载 ----------
    st.download_button(
        label="📥 下载海报（长按可发朋友圈）",
        data=byte_data,
        file_name=f"剩余价值_{surplus_value:.0f}元.jpg",
        mime="image/jpeg"
    )

    # ---------- 页面预览 ----------
    st.image(byte_data, use_column_width=True)

# ---------- 底部说明 ----------
with st.expander("什么是「剩余价值」？"):
    st.markdown("""
    剩余价值 = 你创造的价值 − 工资。  
    老板利润率越高，被“剩余”的就越多。  
    本工具仅供娱乐，欢迎马克思主义探讨。
    """)