import streamlit as st
import asyncio
from pydantic import BaseModel
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel
from config.models import PROVIDERS, DEFAULT_PROVIDER, DEFAULT_MODEL, DEFAULT_BASE_URL

# 初始化 session state
if 'api_key' not in st.session_state:
    st.session_state.api_key = "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"  # 设置默认 API Key
if 'provider' not in st.session_state:
    st.session_state.provider = DEFAULT_PROVIDER
if 'model_name' not in st.session_state:
    st.session_state.model_name = DEFAULT_MODEL
if 'base_url' not in st.session_state:
    st.session_state.base_url = DEFAULT_BASE_URL
if 'timeout' not in st.session_state:
    st.session_state.timeout = 30.0

# 创建共享的客户端
def create_client():
    headers = {
        "HTTP-Referer": "https://openrouter.ai/",
        "X-Title": "AI Article Generator",
        "Authorization": f"Bearer {st.session_state.api_key}"  # 添加 Authorization header
    }
    return AsyncOpenAI(
        api_key=st.session_state.api_key,
        base_url=st.session_state.base_url,
        timeout=st.session_state.timeout,
        default_headers=headers
    )

# 创建基础模型配置
def create_model():
    return OpenAIChatCompletionsModel(
        model=st.session_state.model_name,
        openai_client=create_client()
    )

# 定义文章结构
class Article(BaseModel):
    title: str
    outline: list[str]
    content: dict[str, str]
    summary: str
    keywords: list[str]

# Streamlit 界面
st.title("AI 文章生成器")

# 侧边栏配置
with st.sidebar:
    st.header("配置")
    
    # API 提供商选择
    st.subheader("API 提供商")
    selected_provider = st.selectbox(
        "选择 API 提供商",
        options=list(PROVIDERS.keys()),
        index=list(PROVIDERS.keys()).index(st.session_state.provider)
    )
    
    # 当提供商改变时更新 base_url 和模型
    if selected_provider != st.session_state.provider:
        st.session_state.provider = selected_provider
        st.session_state.base_url = PROVIDERS[selected_provider]["base_url"]
        # 重置模型选择为新提供商的第一个模型
        available_models = PROVIDERS[selected_provider]["models"]
        st.session_state.model_name = list(available_models.values())[0]
        # 强制刷新页面以更新所有状态
        st.rerun()
    
    # API 配置部分
    with st.expander("API 配置", expanded=not bool(st.session_state.api_key)):
        new_api_key = st.text_input(
            "API Key",
            value=st.session_state.api_key,
            type="password",
            help="""OpenRouter API Key 可以从 https://openrouter.ai/keys 获取。
            请确保包含完整的 Key（以 'sk-or-v1-' 开头）"""
        )
        new_base_url = st.text_input(
            "Base URL",
            value=PROVIDERS[st.session_state.provider]["base_url"],
            disabled=True,
            help="Base URL 会根据选择的提供商自动设置"
        )
        new_timeout = st.number_input(
            "Timeout (秒)",
            value=st.session_state.timeout,
            min_value=1.0,
            max_value=300.0,
            help="请求超时时间"
        )
        
        def validate_api_key(api_key: str) -> bool:
            """验证 API Key 格式"""
            if not api_key:
                return False
            if not api_key.startswith("sk-or-v1-"):
                return False
            if len(api_key) < 20:  # 简单的长度检查
                return False
            return True

        if st.button("保存 API 设置"):
            if not validate_api_key(new_api_key):
                st.error("请输入有效的 OpenRouter API Key（以 sk-or-v1- 开头）")
            else:
                st.session_state.api_key = new_api_key
                st.session_state.timeout = new_timeout
                st.success("API 设置已更新！")
    
    # 模型选择
    st.subheader("模型设置")
    available_models = PROVIDERS[st.session_state.provider]["models"]
    selected_model_name = st.selectbox(
        "选择模型",
        options=list(available_models.keys()),
        format_func=lambda x: x,
        index=list(available_models.values()).index(st.session_state.model_name)
            if st.session_state.model_name in available_models.values()
            else 0
    )
    st.session_state.model_name = available_models[selected_model_name]
    
    # 显示当前配置
    st.markdown("---")
    st.markdown("### 当前配置")
    st.markdown(f"提供商: {st.session_state.provider}")
    st.markdown(f"模型: {selected_model_name}")
    st.markdown(f"API URL: {st.session_state.base_url}")

# 主界面
if st.session_state.api_key == "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":
    st.info("当前使用的是默认 API Key，您可以在侧边栏设置自己的 API Key")
elif not st.session_state.api_key:
    st.warning("请先在侧边栏设置 API Key")
    st.info("OpenRouter API Key 可以从 https://openrouter.ai/keys 获取")

topic = st.text_input("请输入文章主题", "人工智能的发展历史")

# 创建 agents（移到这里以便使用最新的配置）
def create_agents():
    model = create_model()
    return {
        'outline_agent': Agent(
            name="Outline Creator",
            instructions="""你是大纲创作专家。请为文章创建一个详细的大纲，包括标题和主要章节。
            请直接返回JSON格式，不要添加Markdown标记。
            输出格式：
            {
                "title": "文章标题",
                "outline": ["章节1", "章节2", "章节3"]
            }
            """,
            model=model
        ),
        'content_agent': Agent(
            name="Content Writer",
            instructions="""你是内容写作专家。根据提供的大纲，为每个章节创作详细内容。
            保持专业性和连贯性。重点关注内容的准确性和深度。
            请直接返回JSON格式，不要添加任何Markdown标记。
            """,
            model=model
        ),
        'summary_agent': Agent(
            name="Summary Expert",
            instructions="""你是总结和关键词专家。请阅读文章内容，提供一个简洁的总结，
            并提取3-5个关键词。请直接返回JSON格式，不要添加任何Markdown标记。
            输出格式：
            {
                "summary": "文章总结",
                "keywords": ["关键词1", "关键词2", "关键词3"]
            }
            """,
            model=model
        ),
        'editor_agent': Agent(
            name="Editor",
            instructions="""你是文章编辑，负责整合所有内容并生成最终的文章。
            请直接返回JSON格式，不要添加任何Markdown标记（如 ```json 或 ``` ）。
            按以下格式输出：
            {
                "title": "文章标题",
                "outline": ["章节1", "章节2", "章节3"],
                "content": {
                    "章节1": "内容1",
                    "章节2": "内容2",
                    "章节3": "内容3"
                },
                "summary": "文章总结",
                "keywords": ["关键词1", "关键词2", "关键词3"]
            }
            """,
            model=model,
            output_type=Article
        )
    }

# 添加异步写作函数
async def async_write_article(topic, status_text, progress_bar, agents):
    try:
        # 1. 创建大纲
        status_text.text("正在创建大纲...")
        progress_bar.progress(25)
        outline_result = await Runner.run(
            agents['outline_agent'], 
            f"请为主题 '{topic}' 创建一个详细的大纲。请直接返回JSON格式，不要添加Markdown标记。"
        )
        if not outline_result:
            raise Exception("大纲生成失败")
        
        # 2. 写作内容
        status_text.text("正在写作内容...")
        progress_bar.progress(50)
        content_result = await Runner.run(
            agents['content_agent'],
            f"""
            主题: {topic}
            大纲: {outline_result.final_output}
            请为每个章节写作详细内容。直接返回JSON格式，不要添加Markdown标记。
            """
        )
        if not content_result:
            raise Exception("内容生成失败")
        
        # 3. 生成总结和关键词
        status_text.text("正在生成总结和关键词...")
        progress_bar.progress(75)
        summary_result = await Runner.run(
            agents['summary_agent'],
            f"""
            文章内容:
            {content_result.final_output}
            请提供总结和关键词。直接返回JSON格式，不要添加Markdown标记。
            """
        )
        if not summary_result:
            raise Exception("总结生成失败")
        
        # 4. 整合所有内容
        status_text.text("正在整合文章...")
        progress_bar.progress(90)
        final_prompt = f"""
        请整合以下内容生成完整的文章。直接返回JSON格式，不要添加任何Markdown标记：

        大纲信息：{outline_result.final_output}
        章节内容：{content_result.final_output}
        总结和关键词：{summary_result.final_output}
        """
        
        result = await Runner.run(agents['editor_agent'], final_prompt)
        if not result:
            raise Exception("文章整合失败")
            
        progress_bar.progress(100)
        status_text.text("文章生成完成！")
        
        return result
        
    except Exception as e:
        error_msg = f"执行过程中出错: {str(e)}"
        status_text.error(error_msg)
        st.error(error_msg)
        return None

# 修改生成文章的按钮处理
if st.button("生成文章"):
    if not st.session_state.api_key:
        st.error("请先设置 API Key")
    else:
        with st.spinner("正在生成文章..."):
            try:
                # 创建进度条和状态文本
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # 创建 agents
                agents = create_agents()
                
                # 运行异步任务
                async def run_article():
                    return await async_write_article(
                        topic,
                        status_text,
                        progress_bar,
                        agents
                    )
                
                result = asyncio.run(run_article())
                
                if result and isinstance(result.final_output, Article):
                    article = result.final_output
                    
                    # 显示文章内容
                    st.header(article.title)
                    
                    st.subheader("大纲")
                    for section in article.outline:
                        st.markdown(f"- {section}")
                    
                    st.subheader("正文")
                    for title, content in article.content.items():
                        st.markdown(f"### {title}")
                        st.markdown(content)
                        st.markdown("---")
                    
                    st.subheader("总结")
                    st.markdown(article.summary)
                    
                    st.subheader("关键词")
                    st.markdown(", ".join(article.keywords))
                    
                    # 修改导出功能的实现
                    outline_text = "".join(f"- {section}\n" for section in article.outline)
                    content_text = "".join(f"### {title}\n{content}\n\n" for title, content in article.content.items())
                    keywords_text = ", ".join(article.keywords)
                    
                    markdown_text = (
                        f"# {article.title}\n\n"
                        f"## 大纲\n{outline_text}\n"
                        f"## 正文\n{content_text}\n"
                        f"## 总结\n{article.summary}\n\n"
                        f"## 关键词\n{keywords_text}"
                    )
                    
                    st.download_button(
                        "下载 Markdown 文件",
                        markdown_text,
                        f"{article.title}.md",
                        "text/markdown"
                    )
                else:
                    if result:
                        st.error(f"生成的内容格式不正确: {result.final_output}")
                    else:
                        st.error("生成文章失败，请重试")
                        
            except Exception as e:
                st.error(f"程序执行出错: {str(e)}")
                progress_bar.empty()
                status_text.empty()

# 添加页脚
st.markdown("---")
st.markdown(f"由 AI 驱动 | 基于 {selected_model_name} 模型") 