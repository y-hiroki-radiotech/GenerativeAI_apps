# logの基本は「いつ、どこで、誰が、どんな処理をしたのか」を出力する
# どこまで処理が終わっているのかを確認したい場合は、処理のまとまりごとや関数の開始・終了のタイミングでログに日時と処理経過を出力する
# ログ出力を呼び出す箇所
# 処理の開始・終了、重要な処理の周辺、例外が発生する箇所、外部との境界

from logging import getLogger, INFO, ERROR, StreamHandler, FileHandler

# ロガーを作成する
logger = getLogger(__name__)
# ログレベルを設定
logger.setLevel(INFO)
# !ハンドラーを作成する -> どこにログを出力するかを振り分ける役目
# ログを標準出力（コンソール）に出力したい場合は[StreamHandler]を使う
s_handler = StreamHandler()

# ログファイルを出力したい場合
f_handler = FileHandler("./app.log")

# ロガーにハンドラーを追加する
logger = getLogger(__name__)
logger.setLevel(INFO)
s_handler = StreamHandler()
s_handler.setLevel(ERROR)
logger.addHandler(s_handler)

# ログを出力
logger.critical("クリティカルレベルのログ")
logger.error("エラーレベルのログ")
logger.warning("ワーニングレベルのログ")
logger.info("インフォレベルのログ")
logger.debug("デバッグレベルのログ")
