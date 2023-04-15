# alpaca_gpt4_datd_jp.json translated by fuguMT

https://github.com/Instruction-Tuning-with-GPT-4/GPT-4-LLM のリポジトリで公開されている、以下のデータを、英日翻訳エンジンfuguMTを用いて翻訳した物です。一部、翻訳出来なかった文字列にはAzure Translation APIを使って翻訳しています。

https://github.com/Instruction-Tuning-with-GPT-4/GPT-4-LLM/tree/main/data

データのライセンスは元データと同じく、CC BY NC 4.0です。元データはGPT-4から蒸留されたデータが含まれているので、OpenAIによる利用規約も適用されるはずです。取り扱いにはご注意ください。

fuguMTはstakaさんによる開発です。

https://huggingface.co/staka/fugumt-en-ja

https://staka.jp/wordpress/

# 付属のPythonスクリプトについて

翻訳に用いたスクリプトです。sentencepieceがPython 3.11ではpipでインストールできなかったので、Python 3.10を使っています。

WindowsのPowerShell環境では、以下の様にすれば動くと思います。
```
git clone https://github.com/matsuvr/alpaca_gpt4_data_ja_by_fuguMT.git
cd alpaca_gpt4_data_ja_by_fuguMT
# alpaca_gpt4_data_ja_by_fuguMTに https://github.com/Instruction-Tuning-with-GPT-4/GPT-4-LLM/raw/main/data/alpaca_gpt4_data.json をコピーしてください
py -3.10 -m venv venv
.\venv\Script\activate
pip install pysbd transformers sentencepiece torch requests
py -3.10 .\main.py
```

生成されるデータは、100項目ごとに分割した521ファイルになっているはずです。以下のスクリプトで連結します。
i7-97ooK、メモリ128GBの環境で40時間以上かかりました。

```
py -3.10 .\combine.py
```

すると、私が公開したものとほぼ同じデータができると思います。

スクリプト部分のライセンスはApache Licence 2.0ですので、お好きにご利用いただければ幸いです。プルリクも歓迎しております。
