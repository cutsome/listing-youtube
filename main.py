import sys
import logging
import os
from pathlib import Path

import pandas as pd
import gspread
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials
from gspread_dataframe import set_with_dataframe
from googleapiclient.discovery import build


def main(word: str) -> None:

    logger.info(f"======= '{word}' から視聴回数順に 50件の動画を取得します。 =======")
    logger.info("======= START =======")

    ##############################
    # Configuration
    ##############################

    current_dir = Path(__file__).parent
    load_dotenv(f"{current_dir}/.env")

    API_KEY = os.getenv("API_KEY")

    ##############################
    # Youtube API から動画取得
    ##############################

    logger.info("======= 動画取得 START =======")

    # 視聴回数の多い順に 50 件取得
    youtube = build("youtube", "v3", developerKey=API_KEY)
    res = (
        youtube.search()
        .list(
            part="snippet",
            q=word,
            order="viewCount",
            type="video",
            maxResults=10,
        )
        .execute()
    )
    contents = list(res["items"])

    logger.info("======= 動画取得 END =======")

    ##############################
    # DataFrame で加工
    ##############################

    logger.info("======= データ加工 START =======")

    # df 化
    df = pd.DataFrame(contents)
    df_snippet = pd.DataFrame(list(df["snippet"]))[
        [
            "channelId",
            "channelTitle",
            "publishedAt",
            "title",
            "thumbnails",
            "description",
        ]
    ]
    df_id = pd.DataFrame(list(df["id"]))["videoId"]
    df = pd.concat([df_snippet, df_id], axis=1)

    # データ加工
    df["thumbnails"] = df["thumbnails"].map(lambda x: x["default"]["url"])
    df["publishedAt"] = df["publishedAt"].map(
        lambda x: x.split("T")[0].replace("-", "/")
    )

    # いいね数・コメント数・再生回数を取得
    def get_optional(id: str):
        return (
            youtube.videos()
            .list(part="statistics", id=id)
            .execute()["items"][0]["statistics"]
        )

    df_opt = pd.DataFrame(list(df["videoId"].map(lambda id: get_optional(id))))
    df = pd.concat([df, df_opt], axis=1)

    df = df.rename(
        columns={
            "channelId": "チャンネル ID",
            "channelTitle": "チャンネル名",
            "publishedAt": "公開日",
            "title": "動画タイトル",
            "thumbnails": "サムネイル URL",
            "description": "動画概要",
            "videoId": "動画 ID",
            "viewCount": "視聴回数",
            "likeCount": "高評価数",
            "commentCount": "コメント数",
        }
    )
    df = df.reindex(
        columns=[
            "チャンネル ID",
            "チャンネル名",
            "動画タイトル",
            "動画概要",
            "サムネイル URL",
            "公開日",
            "動画 ID",
            "視聴回数",
            "高評価数",
            "コメント数",
        ]
    )

    logger.info("======= データ加工 END =======")

    ##############################
    # CSV 出力
    ##############################

    logger.info("======= CSV 書込み処理 START =======")
    df.to_csv("output.csv", index=False)
    logger.info("======= CSV 書込み処理 END =======")

    ###################################
    # Google Sheets へ書込みする場合
    #
    # ※ クレデンシャルは非公開
    ###################################

    logger.info("======= スプレッドシート書込み処理 START =======")
    SCOPES = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    SERVICE_ACCOUNT_FILE = f"{current_dir}/credentials.json"
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        SERVICE_ACCOUNT_FILE, SCOPES
    )
    gs = gspread.authorize(credentials)
    SPREADSHEET_KEY = os.getenv("SP_KEY")
    workbook = gs.open_by_key(SPREADSHEET_KEY)
    worksheet = workbook.worksheet("動画リスト")

    worksheet.clear()
    set_with_dataframe(worksheet, df)
    logger.info("======= スプレッドシート書込み処理 END =======")

    logger.info("======= END =======")


if __name__ == "__main__":
    # ロギング設定
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)

    handler_format = logging.Formatter(
        "%(levelname)s: %(asctime)s: %(name)s: %(message)s"
    )
    stream_handler.setFormatter(handler_format)
    logger.addHandler(stream_handler)

    # 引数取得
    args = sys.argv
    if len(args) != 2:
        logger.error("Error: please pass the just one argument")
        sys.exit(1)
    main(args[1])
