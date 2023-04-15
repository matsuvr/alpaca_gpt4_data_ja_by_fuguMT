# before running this script, please install the following packages:
# pip install pysbd transformers sentencepiece torch
# use python <= 3.10

import os
import re
import json
from transformers import pipeline, MarianMTModel, MarianTokenizer
import pysbd
import logging
logging.basicConfig(filename='example.log', level=logging.DEBUG, format='%(asctime)s:%(levelname)s:%(message)s')


seg_en = pysbd.Segmenter(language="en", clean=False)
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
os.environ["CUDA_LAUNCH_BLOCKING"] = "1"

model=MarianMTModel.from_pretrained('staka/fugumt-en-ja')
tokenizer=MarianTokenizer.from_pretrained('staka/fugumt-en-ja')
tokenizer.model_max_length = 1024

fugu_translator = pipeline('translation', model=model, tokenizer=tokenizer, max_length=1024) #GPUを使う場合は、device=0を指定する

#テキストを翻訳する
def translate_text(text):
    translated_result = []
    segmented_text = seg_en.segment(text)
    translated_result = fugu_translator(segmented_text)
    if translated_result:
        translated_text = ""
        for i in range(len(translated_result)):
            translated_text += translated_result[i]['translation_text']
    else:
        translated_text = ""
        print("Warning: No translation result found.")
    
    return translated_text


#コード部分と非コード部分を分ける
def split_code_and_noncode(text):
    #コード部分を抽出
    code_parts = re.findall(r"```[\s\S]*?```", text)
    #コード部分を除いたテキストを抽出
    noncode_parts = re.split(r"```[\s\S]*?```", text)
    #コード部分と非コード部分を結合
    parts = []
    for i in range(len(code_parts)):
        parts.append(noncode_parts[i])
        parts.append(code_parts[i])
    parts.append(noncode_parts[-1])
    return parts


#読み込むjsonファイルと、結果を保存するファイル名の冒頭を指定
jsonfile = "alpaca_gpt4_data.json"
output_jsonfile_head = "alpaca_gpt4_ja"


#jsonファイルを読み込む
with open(jsonfile, 'r') as f:
    data = json.load(f)

#100件ごとに分割する
chunk_repeat = int(len(data)/100)
chunk_amari = len(data)%100

#100件ごとに翻訳して、結果を保存する
resume_number = 0 # 途中から再開する場合は、ここに再開する番号を指定する
for i in range(chunk_repeat-resume_number):
    chunk = data[(i+resume_number)*100:(i+1+resume_number)*100]
    result = []
    for c in chunk:
        try:

            translated_item = {}
            translated_item["instruction"] = translate_text(c["instruction"])
    
            if "input" in c:
                input_text = c["input"]
                translated_item["input"] = translate_text(input_text)
            else:
                translated_item["input"] = ""
        
            output_parts = split_code_and_noncode(c["output"])
            for j in range(len(output_parts)):
                if j%2 == 0:
                    output_parts[j] = translate_text(output_parts[j])
                else:
                    output_parts[j] = output_parts[j]
            translated_item["output"] = "".join(output_parts)
            result.append(translated_item)
            print(((resume_number +i)*100)+len(result))
            logging.info(((resume_number + i)*100)+len(result))
        except RuntimeError as e:
            print("skip")
            skipped = {}
            skipped["instruction"] = "skip!!!!!!!!"
            skipped["input"] = "skip!!!!!!!!"
            skipped["output"] = "skip!!!!!!!!"
            result.append(skipped)
            logging.info("skip " + str(((resume_number + i)*100)+len(result)) + " because of " + str(e))
        except IndexError as e:
            print("skip")
            skipped = {}
            skipped["instruction"] = "skip!!!!!!!!"
            skipped["input"] = "skip!!!!!!!!"
            skipped["output"] = "skip!!!!!!!!"
            result.append(skipped)
            logging.info("skip " + str(((resume_number + i)*100)+len(result)) + " because of " + str(e))
        except Exception as e:
            print("skip")
            skipped = {}
            skipped["instruction"] = "skip!!!!!!!!"
            skipped["input"] = "skip!!!!!!!!"
            skipped["output"] = "skip!!!!!!!!"
            result.append(skipped)
            logging.info("skip " + str(((resume_number + i)*100)+len(result)) + " なんか知らんけどエラー！ " + str(e))
    
    with open(output_jsonfile_head  + "_" + str((i+resume_number)*100) + "_" + str((1+i+resume_number)*100) + ".json", 'w', encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

#残りの件数を翻訳して、結果を保存する
chunk = data[chunk_repeat*100:]
result = []
for c in chunk:
    translated_item = {}
    translated_item["instruction"] = translate_text(str(c["instruction"]))

    if "input" in c:
        input_text = str(c["input"])
        translated_item["input"] = translate_text(input_text)
    else:
        translated_item["input"] = ""
    
    output_parts = split_code_and_noncode(c["output"])
    for j in range(len(output_parts)):
        if j%2 == 0:
            output_parts[j] = translate_text(output_parts[j])
        else:
            output_parts[j] = output_parts[j]
    translated_item["output"] = "".join(output_parts)

    result.append(translated_item)
    print(len(result)+(chunk_repeat)*100)
    logging.info(len(result))

    with open(output_jsonfile_head + "_" + str(chunk_repeat*100) + "_" + str(len(data)) + ".json", 'w', encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)