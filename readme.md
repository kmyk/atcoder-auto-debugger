# AtCoder Auto Debugger

## なにこれ

AtCoder への提出の URL を送信すると自動でデバッグしてくれるすごいやつだよ

## 注意など

-   <https://kimiyuki.net/app/autodebugger/> にデプロイしてあるものは鯖が貧弱なのでリクエストの処理速度は遅いです。1提出あたり1分ぐらいはかかります

## 構成など

-   デバッガ: コンパイラの sanitizer (`-fsanitize=undefined`), 標準ライブラリの debug mode (`-D_GLIBCXX_DEBUG`), valgrind
-   ジャッジサーバ: Python, Docker
-   APIサーバ: Flask
-   フロントエンド: TypeScript, React
-   データベース: MySQL (queue 含む)
