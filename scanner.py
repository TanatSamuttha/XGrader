import cv2

def scan_detection(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, threshold = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    max_contour = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(max_contour)  # ใช้ boundingRect แทน

    return x, y, w, h

def main(image_path):
    frame = cv2.imread(image_path)
    frame_copy = frame.copy()
    x, y, w, h = scan_detection(frame_copy)

    # Crop เฉพาะบริเวณที่ตรวจพบ
    cropped = frame_copy[y:y+h, x:x+w]

    # บันทึกภาพที่ถูก crop
    cv2.imwrite(image_path, cropped)
