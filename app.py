"""
简单记账本 — 主程序（界面层）
启动方式：streamlit run app.py
"""

import streamlit as st
from datetime import date, datetime
import plotly.express as px

import config
import database


# ==================== 页面配置（必须放在最前面）====================
st.set_page_config(
    page_title="简单记账本",
    page_icon="📒",
    layout="wide",
)


# ==================== Tab 1：添加账目 ====================
def render_add_tab():
    """渲染"添加账目"表单。"""
    st.subheader("📝 新增一笔账目")

    with st.form("add_form", clear_on_submit=True):
        col1, col2, col3 = st.columns([1, 1, 2])

        with col1:
            amount = st.number_input(
                "金额 (元)",
                min_value=0.01,
                max_value=999999.99,
                step=1.0,
                format="%.2f",
                help="请输入大于 0 的金额",
            )

        with col2:
            category = st.selectbox("分类", config.CATEGORIES)

        with col3:
            record_date = st.date_input(
                "日期",
                value=date.today(),
                min_value=date(2000, 1, 1),
                max_value=date.today(),
            )

        note = st.text_area(
            "备注 (选填)",
            max_chars=200,
            placeholder="例如：午餐黄焖鸡米饭、打车去公司…",
            height=68,
        )

        submitted = st.form_submit_button(
            "✅ 添加记录", type="primary", use_container_width=True
        )

        if submitted:
            date_str = record_date.strftime("%Y-%m-%d")
            success, msg = database.add_record(amount, category, date_str, note.strip())
            if success:
                st.success(msg)
                # st.rerun() 不需要，form clear_on_submit 会自动清空
            else:
                st.error(msg)


# ==================== Tab 2：查看列表 ====================
def render_view_tab():
    """渲染"查看列表"，支持按月份和分类筛选。"""
    st.subheader("📋 账目列表")

    # ---- 筛选控件 ----
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        filter_date = st.date_input(
            "筛选月份（留空看全部）",
            value=None,
            key="view_date",
        )
        filter_month = filter_date.strftime("%Y-%m") if filter_date else None

    with col2:
        filter_category = st.selectbox(
            "筛选分类",
            ["全部"] + config.CATEGORIES,
            key="view_category",
        )
        # 选"全部"时传 None，让 database 层不过滤分类
        category_param = None if filter_category == "全部" else filter_category

    with col3:
        st.markdown("<br>", unsafe_allow_html=True)  # 对齐按钮
        if st.button("🔄 清除筛选", use_container_width=True):
            # Streamlit 中清除筛选 = 重新运行即可（控件会回到默认值）
            st.rerun()

    # ---- 数据表格 ----
    df = database.get_records(month=filter_month, category=category_param)

    if df.empty:
        st.info("暂无数据，去「📝 添加账目」记一笔吧！")
    else:
        # 格式化金额列
        df_display = df.copy()
        df_display["amount"] = df_display["amount"].apply(lambda x: f"¥{x:.2f}")
        df_display.rename(columns={
            "id": "ID",
            "amount": "金额",
            "category": "分类",
            "date": "日期",
            "note": "备注",
        }, inplace=True)

        st.dataframe(df_display, use_container_width=True, hide_index=True)
        st.caption(f"共 {len(df)} 条记录")


# ==================== Tab 3：删除账目 ====================
def render_delete_tab():
    """渲染"删除账目"，输入 ID 并确认后删除。"""
    st.subheader("🗑️ 删除账目")

    # 折叠区：最近记录供参考
    df = database.get_records()
    if not df.empty:
        with st.expander("📋 点击展开最近记录（方便查找要删除的 ID）"):
            df_display = df.head(20).copy()
            df_display["amount"] = df_display["amount"].apply(lambda x: f"¥{x:.2f}")
            st.dataframe(df_display, use_container_width=True, hide_index=True)

    # 删除操作
    record_id = st.number_input("输入要删除的账目 ID", min_value=1, step=1)

    if st.button("🔍 查询并确认删除", type="primary"):
        record = database.get_record_by_id(record_id)

        if record is None:
            st.error(f"未找到 ID 为 {record_id} 的记录，请检查后重试。")
        else:
            # 显示记录详情
            st.warning(
                f"⚠️ 确认要删除以下记录？\n\n"
                f"**分类**：{record['category']}　|　"
                f"**日期**：{record['date']}　|　"
                f"**金额**：¥{record['amount']:.2f}\n\n"
                f"**备注**：{record['note'] or '（无）'}"
            )

            col_confirm, col_cancel = st.columns([1, 3])
            with col_confirm:
                if st.button("✅ 确认删除", type="primary"):
                    success, msg = database.delete_record(record_id)
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)


# ==================== Tab 4：统计图表 ====================
def render_stats_tab():
    """渲染"统计图表"，柱状图 + 汇总表。"""
    st.subheader("📊 分类统计")

    # 月份筛选
    filter_date = st.date_input(
        "统计月份（留空看全部）",
        value=None,
        key="stats_date",
    )
    filter_month = filter_date.strftime("%Y-%m") if filter_date else None

    df_stats = database.get_statistics(month=filter_month)

    if df_stats.empty:
        st.info("暂无数据可统计，先去记几笔账吧！")
        return

    # ---- 柱状图 ----
    tab_chart, tab_table = st.tabs(["📊 柱状图", "📋 数据表"])

    with tab_chart:
        # 使用 plotly 绘制分类柱状图
        fig = px.bar(
            df_stats,
            x="分类",
            y="总金额(元)",
            color="分类",
            color_discrete_sequence=px.colors.qualitative.Set2,
            title="各分类消费金额",
            text_auto=True,
        )
        fig.update_layout(
            showlegend=False,
            xaxis_title="",
            yaxis_title="金额 (元)",
        )
        fig.update_traces(texttemplate="¥%{y:.2f}", textposition="outside")
        st.plotly_chart(fig, use_container_width=True)

    with tab_table:
        st.dataframe(df_stats, use_container_width=True, hide_index=True)

        # 总计行
        total_amount = df_stats["总金额(元)"].sum()
        total_count = df_stats["笔数"].sum()
        st.markdown(f"**合计**：共 **{total_count}** 笔，总金额 **¥{total_amount:.2f}**")


# ==================== 主函数 ====================
def main():
    """程序入口：初始化数据库，渲染页面。"""

    # 标题
    st.title("📒 简单记账本")

    # 侧边栏：显示一点额外信息
    with st.sidebar:
        today = date.today()
        st.markdown(f"🗓️ **{today.strftime('%Y 年 %m 月 %d 日')}**")
        # 计算本月总消费
        this_month = today.strftime("%Y-%m")
        df_month = database.get_records(month=this_month)
        if not df_month.empty:
            total = df_month["amount"].sum()
            count = len(df_month)
            st.metric("本月消费 (元)", f"¥{total:.2f}")
            st.metric("本月笔数", f"{count} 笔")

    st.divider()

    # 四个标签页
    tab1, tab2, tab3, tab4 = st.tabs([
        "📝 添加账目",
        "📋 查看列表",
        "🗑️ 删除账目",
        "📊 统计图表",
    ])

    with tab1:
        render_add_tab()
    with tab2:
        render_view_tab()
    with tab3:
        render_delete_tab()
    with tab4:
        render_stats_tab()


if __name__ == "__main__":
    # 初始化数据库（首次运行自动创建 finance.db 和 records 表）
    database.init_database()
    main()
