---
marp: true
---
## 学習記録

- Roleの定義
  回答を担当するロールを選択する処理をするのだが、このロールを**生成させるのではなく**LLMに**選択させる**ことがポイント

- ## **LangGraphの作成の仕方**
  - プログラム内でどのようなステートが管理されるべきか
    この部分はpydanticでプログラムする
  - ステートを更新するノードとしてどのようなものがあるか、順を追って考えていく

---
## 要件定義書生成AIエージェント
- stateを生成クラスで更新するイメージかな？
