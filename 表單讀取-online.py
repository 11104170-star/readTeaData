import streamlit as st
import pandas as pd
from collections import Counter
import os

st.set_page_config(
    page_title="社課回饋分析工具",
    page_icon="🍵",
    layout="wide"
)

st.title("🍵 社課回饋分析工具")

st.write("支援 Excel（.xlsx）與 CSV（.csv）")

# =========================
# 上傳檔案
# =========================

uploaded_file = st.file_uploader(
    "請上傳 Excel 或 CSV 檔案",
    type=["xlsx", "csv"]
)

if uploaded_file is not None:

    try:

        ext = os.path.splitext(uploaded_file.name)[1].lower()

        # =========================
        # 讀取 Excel
        # =========================

        if ext == ".xlsx":

            df = pd.read_excel(uploaded_file)

        # =========================
        # 讀取 CSV
        # =========================

        elif ext == ".csv":

            encodings = [
                "utf-8-sig",
                "utf-8",
                "cp950",
                "big5"
            ]

            success = False

            for enc in encodings:

                try:

                    uploaded_file.seek(0)

                    df = pd.read_csv(
                        uploaded_file,
                        encoding=enc
                    )

                    st.success(f"成功使用編碼：{enc}")

                    success = True
                    break

                except:
                    pass

            if not success:
                st.error("CSV 編碼無法辨識")
                st.stop()

        else:

            st.error("不支援的檔案格式")
            st.stop()

        # =========================
        # 基本資訊
        # =========================

        rows = df.values.tolist()
        headers = list(df.columns)

        total = len(rows)

        st.header("📊 分析結果")

        st.write(f"### 填寫回饋表單人數：{total}人")

        # =========================
        # 判斷題目類型
        # =========================

        score_questions = []
        text_questions = []

        for col in headers:

            values = df[col].dropna().astype(str)

            is_score = True

            for v in values:

                v = v.strip()

                if v not in ["1", "2", "3", "4", "5"]:

                    is_score = False
                    break

            if is_score:
                score_questions.append(col)
            else:
                text_questions.append(col)

        # =========================
        # 產生輸出文字
        # =========================

        output_text = ""

        output_text += (
            f"填寫回饋表單人數：{total}人\n\n"
        )

        # =========================
        # 評分題
        # =========================

        if len(score_questions) > 0:

            output_text += (
                "題目（1-5分，1分最低、5分最高）\n\n"
            )

            for i, question in enumerate(
                score_questions,
                start=1
            ):

                counter = Counter()

                values = (
                    df[question]
                    .dropna()
                    .astype(str)
                )

                for v in values:

                    counter[v.strip()] += 1

                output_text += (
                    f"{i}.{question}\n"
                )

                result = []

                for score in sorted(
                    counter.keys(),
                    reverse=True
                ):

                    count = counter[score]

                    percent = (
                        count / total * 100
                    )

                    result.append(
                        f"{count}人{score}分（{percent:.2f}%）"
                    )

                output_text += (
                    "、".join(result)
                )

                output_text += "\n\n"

        # =========================
        # 文字題
        # =========================

        start_index = (
            len(score_questions) + 1
        )

        for idx, question in enumerate(
            text_questions,
            start=start_index
        ):

            output_text += (
                f"{idx}.{question}\n"
            )

            counter = Counter()

            blank = 0

            values = df[question]

            for v in values:

                if pd.isna(v):

                    blank += 1
                    continue

                text = str(v).strip()

                if text == "":

                    blank += 1

                else:

                    counter[text] += 1

            for text, count in counter.items():

                output_text += (
                    f"{text}（{count}）\n"
                )

            output_text += (
                f"空白（{blank}）\n\n"
            )

        # =========================
        # 顯示結果
        # =========================

        st.text_area(
            "分析結果",
            output_text,
            height=600
        )

        # =========================
        # 下載按鈕
        # =========================

        st.download_button(
            label="📥 下載 TXT",
            data=output_text,
            file_name="社課回饋分析.txt",
            mime="text/plain"
        )

    except Exception as e:

        st.error("發生錯誤")
        st.exception(e)