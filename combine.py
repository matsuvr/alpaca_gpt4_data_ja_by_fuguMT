#before run this code, you need to pip install requests

import requests, uuid, json

# 連番のJSONファイル名を生成する
start = 0
end = 52000
step = 100
json_files = [f"alpaca_gpt4_ja_{i}_{i+step}.json" for i in range(start, end, step)]
json_files.append(f"alpaca_gpt4_ja_52000_52002.json")

# 各JSONファイルを読み込み、各行を辞書オブジェクトに変換してリストに追加する
merged_data = []
for json_file in json_files:
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        for d in data:
            merged_data.append(d)


# ログファイル名
log_file = "example.log"

# "skip"を含む行を抽出する
with open(log_file, "r") as f:
    lines = f.readlines()
    skip_lines = [line for line in lines if "skip" in line]

# "skip"を含む行から数値を抽出し、整数型に変換してリストに追加する
skip_numbers = []
for line in skip_lines:
    if "skip" in str(line):
        number = int(line.split("skip")[1].split("because")[0])
        skip_numbers.append(number)

# 英語版のjsonファイルを読み込む
with open("alpaca_gpt4_data.json", 'r') as f:
    data = json.load(f)

# fuguMTで翻訳出来なかった行をMicrosoft Azureの翻訳を利用するための設定
key = "<azure translation api key>"
endpoint = "https://api.cognitive.microsofttranslator.com"

# location, also known as region.
# required if you're using a multi-service or regional (not global) resource. It can be found in the Azure portal on the Keys and Endpoint page.
location = "<your location>"

path = '/translate'
constructed_url = endpoint + path

params = {
    'api-version': '3.0',
    'from': 'en',
    'to': ['ja']
}

headers = {
    'Ocp-Apim-Subscription-Key': key,
    # location required if you're using a multi-service or regional (not global) resource.
    'Ocp-Apim-Subscription-Region': location,
    'Content-type': 'application/json',
    'X-ClientTraceId': str(uuid.uuid4())
}

for s in skip_numbers:
# You can pass more than one object in body.
    body = [{
        'text': data[s-1]['instruction']
        }]

    request = requests.post(constructed_url, params=params, headers=headers, json=body)
    response = request.json()
    instruction = response[0]["translations"][0]["text"]
    merged_data[s-1]["instruction"] = instruction


    body = [{
        'text': data[s-1]['input']
        }]

    request = requests.post(constructed_url, params=params, headers=headers, json=body)
    response = request.json()
    input = response[0]["translations"][0]["text"]
    merged_data[s-1]["input"] = input

    body = [{
        'text': data[s-1]['output']
        }]

    request = requests.post(constructed_url, params=params, headers=headers, json=body)
    response = request.json()
    output = response[0]["translations"][0]["text"]
    merged_data[s-1]["output"] = output

    line = '{"instruction": "' + repr(instruction) + '", "input": "' + repr(input) + '", "output": "' + repr(output) + '"}'

    print(line)

#あとはprintしたものを手動コピペで目視確認しながらjsonlファイルに書き込む！ 最後は目視！

# リストに追加された辞書オブジェクトを新しいJSONファイルに書き込む
with open("alpaca_gpt4_data_ja.json", "w", encoding="utf-8") as f:
    json.dump(merged_data, f, indent=4, ensure_ascii=False)
