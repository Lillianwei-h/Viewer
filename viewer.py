import os
import json
from flask import Flask, request, render_template, jsonify
import argparse

parser = argparse.ArgumentParser(description="")
parser.add_argument('dataset', type=str, choices=['vist', 'wikihow', 'remi', 'mathvista'], help='The dataset you want to view')

args = parser.parse_args()
print(args)

app = Flask(__name__,static_folder='./static')

current_index = 0
json_data = []
stored_data = {}
dataset = args.dataset
json_file_directory = f"./static/{dataset}"
filename = ""
total_num = 0
os.makedirs('output',exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_json():
    global json_data, json_file_directory, filename, total_num
    file = request.files['file']
    if file:
        filename = file.filename
        print("file name: ",file.filename)
        print("file dir: ",json_file_directory)
        json_data = json.load(file)
        total_num = len(json_data)
        return jsonify({"message": "JSON loaded", "status": "success"})
    return jsonify({"message": "No file provided", "status": "error"})

@app.route('/get_data', methods=['GET'])
def get_data():
    global current_index, json_data, json_file_directory,total_num
    if 0 <= current_index < total_num:
        data = json_data[current_index]
        id = data['id']

        question = data['question']
        question_text = ""
        question_images = []
        for q in question:
            if q['text'] is not None:
                question_text+=(q['text'] + '\n')
            if q['image'] is not None:
                img_path = os.path.join(json_file_directory, q['image'])
                question_images.append(img_path)

        answer = data['answer']
        answer_text = ""
        answer_images = []
        for q in answer:
            if q['text'] is not None:
                answer_text+=(q['text'] + '\n')
            if q['image'] is not None:
                answer_text+="\n---------------------- image ---------------------\n"
                img_path = os.path.join(json_file_directory, q['image'])
                answer_images.append(img_path)

        gt_answer = data['gt_answer']
        gt_answer_text = ""
        gt_answer_images = []
        for q in gt_answer[:min(3,len(gt_answer))]:
            if q['text'] is not None:
                gt_answer_text+=(q['text'] + '\n')
            if q['image'] is not None:
                gt_answer_text+="\n---------------------- image ---------------------\n"
                img_path = os.path.join(json_file_directory, q['image'])
                gt_answer_images.append(img_path)

        return jsonify({
            "index_info": str(current_index+1) + " / " + str(total_num),
            "id": id, 
            "question_text": question_text, 
            "question_images": question_images,
            "answer_text": answer_text,
            "answer_images": answer_images,
            "gt_answer_text":gt_answer_text,
            "gt_answer_images":gt_answer_images
            })
    
    return jsonify({"message": "Out of range", "status": "error"})

@app.route('/navigate', methods=['POST'])
def navigate():
    global current_index, json_data
    direction = request.json.get('direction')
    if direction == "next" and current_index < len(json_data) - 1:
        current_index += 1
        store_data()
    elif direction == "previous" and current_index > 0:
        current_index -= 1
        store_data()
    elif direction == "start":
        current_index = current_index*0
    return jsonify({"message": "Navigation success"})

def store_data():
    global stored_data, json_data, current_index, total_num
    if 0 <= current_index < total_num:
        current_id = json_data[current_index]["id"]
        user_data = request.json.get("user_data")
        stored_data[current_id] = user_data
        return jsonify({"message": "Data stored successfully", "status": "success"})
    return jsonify({"message": "Invalid index", "status": "error"})

@app.route('/store_all', methods=['POST'])
def store_all():
    store_data()
    global stored_data
    with open(f'output/{dataset}_{filename}','w') as f:
        json.dump(stored_data, f, indent=4)
    return jsonify({"message": "Data stored successfully", "status": "success"})
    
if __name__ == '__main__':
    app.run(debug=True)
