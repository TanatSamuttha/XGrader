import cv2
import os
from numpy import inf
from roboflow import Roboflow

rf = Roboflow(api_key="1e8BCOz9oLrhkIro48wN")
project = rf.workspace().project("xgrader")
model = project.version(3).model

def find_choice(lst, target):
    mn = inf
    closest_index = 0
    for i in range(0, len(lst)):
        tmp = abs(target - lst[i][0])
        if tmp < mn:
            mn = tmp
            closest_index = i
    return closest_index

def detect(paper):
    sum = cntbox = 0
    colors = [(0, 0, 255), (0, 255, 0), (255, 0, 0), (255, 255, 0), (255, 0, 255), (0, 255, 255)]
    image_path = paper
    image = cv2.imread(image_path)

    output_size = (800, 800)
    image = cv2.resize(image, output_size)
    output_image_path = paper
    cv2.imwrite(output_image_path, image)
    prediction_result = model.predict(image_path, confidence=40, overlap=30).json()

    height, width, _ = image.shape
    thickness = max(2, min(height, width) // 300)
    
    choice = []
    ans = []
    slot1, slot2, slot3, slot4 = [], [], [], []

    for i, prediction in enumerate(prediction_result["predictions"]):
        x1 = int(prediction['x'] - prediction['width'] / 2)
        y1 = int(prediction['y'] - prediction['height'] / 2)
        x2 = int(prediction['x'] + prediction['width'] / 2)
        y2 = int(prediction['y'] + prediction['height'] / 2)
        class_id = prediction["class_id"]
        class_name = model.class_labels[class_id] if hasattr(model, 'class_labels') else f"Class {class_id}"
        color = colors[class_id % len(colors)]
        cv2.rectangle(image, (x1, y1), (x2, y2), color, thickness)
        sum += abs(y1 - y2)
        cntbox += 1
        if class_id != 5:
            choice.append([x1, y1, class_id])
        else:
            ans.append([y1, x1])

    avg = sum / cntbox

    choice.sort()
    ans.sort()

    startY = choice[0][1]

    for yx in ans:
        y = yx[0]
        x = yx[1]
        xchoice = find_choice(choice, x)
        if xchoice <= 4:
            slot1.append([y, x, xchoice])
            color = colors[xchoice]
            cv2.circle(image, (x, y), thickness, color, thickness)
        elif xchoice <= 9:
            slot2.append([y, x, xchoice - 5])
            color = colors[xchoice - 5]
            cv2.circle(image, (x, y), thickness, color, thickness)
        elif xchoice <= 14:
            slot3.append([y, x, xchoice - 10])
            color = colors[xchoice - 10]
            cv2.circle(image, (x, y), thickness, color, thickness)
        else:
            slot4.append([y, x, xchoice - 15])
            color = colors[xchoice - 15]
            cv2.circle(image, (x, y), thickness, color, thickness)

    cv2.imwrite(image_path, image)
    print("Detected image saved as:", image_path)
    return slot1, slot2, slot3, slot4, avg, startY

def answerkeyscan(paper):
    slot1, slot2, slot3, slot4, avg, startY=detect(paper)
    answerkey = []
    for i in range(0,len(slot1)):answerkey.append(slot1[i][2]+1)
    for i in range(0,len(slot2)):answerkey.append(slot2[i][2]+1)
    for i in range(0,len(slot3)):answerkey.append(slot3[i][2]+1)
    for i in range(0,len(slot4)):answerkey.append(slot4[i][2]+1)
    print(answerkey)
    return answerkey

def grading(paper,answerkey):
    slot1, slot2, slot3, slot4, avg, startY = detect(paper)
    score=0

    image = cv2.imread(paper)
    font = cv2.FONT_HERSHEY_SIMPLEX
    color = (0, 0, 225)
    thickness = 2
    correct=[]
    print(len(answerkey))
    print(avg)
    
    idx = 0
    cut=False
    for i in range(0, len(slot1)):
        if i==0:
            if slot1[i][0] > startY+(2*avg)+(avg/3):
                idx += int(round((slot1[i][0]-startY)/avg,0)-1)
                cv2.putText(image, str(idx+1), (slot1[i][1]-30, slot1[i][0]+20), font, 0.7, color, thickness)
            if idx<len(answerkey) and slot1[i][2]+1 == answerkey[idx]:
                score += 1
                correct.append([slot1[i][0], slot1[i][1]])
        else:
            if slot1[i][0] > slot1[i-1][0]+avg+(avg/3):
                idx += int(round((slot1[i][0]-slot1[i-1][0])/avg,0))
                cut=False
                cv2.putText(image, str(idx+1), (slot1[i][1]-30, slot1[i][0]+20), font, 0.7, color, thickness)
            elif slot1[i][0] < slot1[i-1][0]+(avg/3):
                if idx<len(answerkey) and slot1[i-1][2]+1 == answerkey[idx]: 
                    if not cut: 
                        score -= 1
                        correct.pop()
                    cut=True
                cv2.putText(image, '-', (slot1[i-1][1]-5, slot1[i-1][0]+28), font, 1.5, color, thickness)
                cv2.putText(image, '-', (slot1[i][1]-5, slot1[i][0]+28), font, 1.5, color, thickness)
                continue
            else:
                idx += 1
                cut=False
            if idx<len(answerkey) and slot1[i][2]+1 == answerkey[idx]:
                score += 1
                print(slot1[i][1],' ', slot1[i][0])
                correct.append([slot1[i][0], slot1[i][1]])
                cut=False

    idx = 15
    cut=False
    for i in range(0, len(slot2)):
        if i==0:
            if slot2[i][0] > startY+(2*avg)+(avg/3):
                idx += int(round((slot2[i][0]-startY)/avg,0)-1)
                cv2.putText(image, str(idx+1), (slot2[i][1]-30, slot2[i][0]+20), font, 0.7, color, thickness)
            if idx<len(answerkey) and slot2[i][2]+1 == answerkey[idx]: 
                score += 1
                correct.append([slot2[i][0], slot2[i][1]])
        else:
            if slot2[i][0] > slot2[i-1][0]+avg+(avg/3):
                idx += int(round((slot2[i][0]-slot2[i-1][0])/avg,0))
                cv2.putText(image, str(idx+1), (slot2[i][1]-30, slot2[i][0]+20), font, 0.7, color, thickness)
            elif slot2[i][0] < slot2[i-1][0]+(avg/3):
                if idx<len(answerkey) and slot2[i-1][2]+1 == answerkey[idx]: 
                    if not cut: 
                        score -= 1
                        correct.pop()
                    cut=True
                cv2.putText(image, '-', (slot2[i-1][1]-5, slot2[i-1][0]+28), font, 1.5, color, thickness)
                cv2.putText(image, '-', (slot2[i][1]-5, slot2[i][0]+28), font, 1.5, color, thickness)
                continue
            else:
                idx += 1
                cut=False
            if idx<len(answerkey) and slot2[i][2]+1 == answerkey[idx]: 
                score += 1
                correct.append([slot2[i][0], slot2[i][1]])
                cut=False
    
    idx = 30
    cut=False
    for i in range(0, len(slot3)):
        if i==0:
            if slot3[i][0] > startY+(2*avg)+(avg/3):
                idx += int(round((slot3[i][0]-startY)/avg,0)-1)
                cv2.putText(image, str(idx+1), (slot3[i][1]-30, slot3[i][0]+20), font, 0.7, color, thickness)
            if idx<len(answerkey) and slot3[i][2]+1 == answerkey[idx]: 
                score += 1
                correct.append([slot3[i][0],slot3[i][1]])
        else:
            if slot3[i][0] > slot3[i-1][0]+avg+(avg/3):
                idx += int(round((slot3[i][0]-slot3[i-1][0])/avg,0))
                cv2.putText(image, str(idx+1), (slot3[i][1]-30, slot3[i][0]+20), font, 0.7, color, thickness)
            elif slot3[i][0] < slot3[i-1][0]+(avg/3):
                if idx<len(answerkey) and slot3[i-1][2]+1 == answerkey[idx]: 
                    if not cut: 
                        score -= 1
                        correct.pop()
                    cut-True
                cv2.putText(image, '-', (slot3[i-1][1]-5, slot3[i-1][0]+28), font, 1.5, color, thickness)
                cv2.putText(image, '-', (slot3[i][1]-5, slot3[i][0]+28), font, 1.5, color, thickness)
                continue
            else:
                idx += 1
                cut=False
            if idx<len(answerkey) and slot3[i][2]+1 == answerkey[idx]: 
                score += 1
                correct.append([slot3[i][0],slot3[i][1]])
                cut=False

    idx = 45
    cut=False
    for i in range(0, len(slot4)):
        if i==0:
            if slot4[i][0] > startY+(2*avg)+(avg/3):
                idx += int(round((slot4[i][0]-startY)/avg,0)-1)
                cv2.putText(image, str(idx+1), (slot4[i][1]-30, slot4[i][0]+20), font, 0.7, color, thickness)
            if idx<len(answerkey) and slot4[i][2]+1 == answerkey[idx]: 
                score += 1
                correct.append([slot4[i][0], slot4[i][1]])
        else:
            if slot4[i][0] > slot4[i-1][0]+avg+(avg/3):
                idx += int(round((slot4[i][0]-slot4[i-1][0])/avg,0))
                cv2.putText(image, str(idx+1), (slot4[i][1]-30, slot4[i][0]+20), font, 0.7, color, thickness)
            elif slot4[i][0] < slot4[i-1][0]+(avg/3):
                if idx<len(answerkey) and slot4[i-1][2]+1 == answerkey[idx]: 
                    if not cut: 
                        score -= 1
                        correct.pop()
                    cut=True
                cv2.putText(image, '-', (slot4[i-1][1]-5, slot4[i-1][0]+28), font, 1.5, color, thickness)
                cv2.putText(image, '-', (slot4[i][1]-5, slot4[i][0]+28), font, 1.5, color, thickness)
                continue
            else:
                idx += 1
                cut=False
            if idx<len(answerkey) and slot4[i][2]+1 == answerkey[idx]: 
                score += 1
                correct.append([slot4[i][0], slot4[i][1]])
                cut=False
    print(' ')
    for i in correct:
        cv2.putText(image, '+', (i[1]+8, i[0]+18), font, 0.5, (0,225,0), thickness)
        print(i[1],' ',i[0])
    
    height,width,chanels = image.shape
    position = (width-130, 50)
    text = str(score)+"/"+str(len(answerkey))
    image_with_text = cv2.putText(image, text, position, font, 1, color, thickness)
    cv2.imwrite(paper, image_with_text)

    return score