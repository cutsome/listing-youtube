# listing-youtube

## 環境構築

以下のコマンドを実行し、仮想環境にライブラリをインストールする

```
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

`.env`, `credentials.json` を作成する  
`xxx` となっている箇所を開発者から共有してもらい、作成したファイルにコピペする

```
cp .env.example .env
cp credentials.json.sample credentials.json
```

## 動作確認

以下のコマンドを実行する

```
python main.py 筋トレ
```

- 出力先
  - output.csv
  - [Google Sheets](https://docs.google.com/spreadsheets/d/14DCYX9MZxfJYw0GHAG9mm15kasEGwPCrYShgrOJxQog/edit?usp=sharing)
    - Google Sheets へアクセスするためのサービスアカウントは秘匿情報ですので、アウトプットのみを公開します。
