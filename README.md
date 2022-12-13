# TwitterフォローRT企画の自動化WEBサービス
## バックエンド
### Django 4.0.6, python 3.10
## フロントエンド
### Javascript, HTML/CSS

## MacOSにDjangoをインストールする手順
### Pythonの仮想環境を作成します。
#### python3 -m venv <仮想環境名>
### パッケージ設置
#### pip3 install -r requirements.txt
### マイグレーション
#### python3 manage.py makemigrations
#### python3 manage.py migrate
### super-admin創造
#### python3 manage.py createsuperuser
### RUN
#### python3 manage.py runserver
