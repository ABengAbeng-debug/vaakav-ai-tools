import streamlit as st
import google.generativeai as genai
import requests
import re

# --- 配置区 ---
RAINFOREST_API_KEY = "7FB353319E0A44B8976692998F97B976" # 替换为你申请的Key
genai.configure(api_key="AIzaSyCAvh3QyI6gXo2EaSO6heis6DBKhK5KJ5g") # 替换为你的Gemini Key
model = genai.GenerativeModel('gemini-1.5-pro-latest')

def get_amazon_data(url):
    """通过 Rainforest API 抓取亚马逊实时数据"""
    # 从URL提取ASIN
    asin_match = re.search(r'/dp/([A-Z0-9]{10})', url)
    if not asin_match:
        return None
    
    params = {
        'api_key': RAINFOREST_API_KEY,
        'type': 'product',
        'amazon_domain': 'amazon.com',
        'asin': asin_match.group(1)
    }
    
    response = requests.get('https://api.rainforestapi.com/request', params=params)
    return response.json() if response.status_code == 200 else None

def ai_analyze_report(data):
    """将抓取到的海量数据交给 Gemini 精炼"""
    product = data.get('product', {})
    title = product.get('title')
    categories = product.get('categories')
    rating = product.get('rating')
    top_reviews = [r.get('body') for r in product.get('top_reviews', [])[:5]] # 取前5条评论
    
    prompt = f"""
    你是美妆品牌 VaaKav 的首席分析师。请分析以下竞争对手产品：
    
    产品名称: {title}
    类目: {categories}
    评分: {rating}星
    核心评论内容: {top_reviews}
    
    请输出一份决策报告：
    1. 趋势分析：基于评分和评论热度，该产品是否处于上升期？
    2. 避坑指南：现有产品的设计缺陷是什么？(根据评论分析)
    3. 差异化策略：VaaKav 如果推出同类产品，应如何在成分或包装上超越它？
    4. TikTok 爆点：这个产品最吸引眼球的视觉瞬间是什么？
    """
    
    response = model.generate_content(prompt)
    return response.text

# --- Streamlit 界面 ---
st.set_page_config(page_title="VaaKav AI 选品助手 (专业版)")
st.title("🚀 VaaKav 全自动选品分析系统")

url = st.text_input("粘贴亚马逊产品链接:", placeholder="https://www.amazon.com/dp/B0...")

if st.button("一键分析趋势"):
    if url:
        with st.spinner('正在调取亚马逊实时数据并由 Gemini 进行深度推演...'):
            raw_data = get_amazon_data(url)
            if raw_data and 'product' in raw_data:
                # 展示产品基本信息
                st.image(raw_data['product'].get('main_image', {}).get('link'), width=200)
                st.subheader(raw_data['product'].get('title'))
                
                # AI 分析
                report = ai_analyze_report(raw_data)
                st.markdown("---")
                st.markdown(report)
            else:
                st.error("数据抓取失败，请检查链接是否正确或 API 额度。")
