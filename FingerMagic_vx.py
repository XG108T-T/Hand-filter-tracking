import cv2
import mediapipe as mp
import numpy as np
import time

# ---------- 初始化 ----------
model_path = 'hand_landmarker.task'
base_options = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

options = HandLandmarkerOptions(
    base_options=base_options(model_asset_path=model_path),
    running_mode=VisionRunningMode.VIDEO,
    num_hands=2,
    min_hand_detection_confidence=0.5,
    min_hand_presence_confidence=0.5,
    min_tracking_confidence=0.5
)
landmarker = HandLandmarker.create_from_options(options)

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

print("喵~~ 酱酱~！这是自适应手指滤镜测试版本呀~  | 小宝可以按数字键切换滤镜呀~小宝如果想改这里的文字只要打开改改就好喵~")
print("   2: 二指模式 (用了交叉沙漏)")
print("   3-5: 多指模式 (更好的凸包填充)")
print("   1-4: 切换滤镜风格")
print("   空格: 黑白反转")
print("   ESC: 退出")

finger_count = 2
invert = False
filter_style = 1

finger_ids_all = [4, 8, 12, 16, 20]
finger_names = {4: '拇指', 8: '食指', 12: '中指', 16: '无名指', 20: '小指'}
color_map = {4: (0, 0, 255), 8: (0, 255, 0), 12: (255, 0, 0), 16: (255, 255, 0), 20: (255, 0, 255)}

# ---------- 滤镜函数 ----------
def apply_filter(roi, style=1, invert=False):
    if roi.size == 0:
        return roi
    if style == 1:  # 漫画
        smoothed = cv2.bilateralFilter(roi, d=9, sigmaColor=75, sigmaSpace=75)
        gray = cv2.cvtColor(smoothed, cv2.COLOR_BGR2GRAY)
        edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)
        kernel = np.ones((2,2), np.uint8)
        edges = cv2.dilate(edges, kernel, iterations=1)
        quantized = smoothed // 32 * 32
        if not invert:
            edges_mask = edges > 0
            quantized[edges_mask] = [0, 0, 0]
            bg_mask = edges == 0
            color_remnant = roi // 32 * 32
            quantized[bg_mask] = (np.ones_like(quantized[bg_mask]) * 255 * 0.7 + color_remnant[bg_mask] * 0.3).astype(np.uint8)
        else:
            edges_mask = edges > 0
            quantized[edges_mask] = [255, 255, 255]
            bg_mask = edges == 0
            color_remnant = roi // 32 * 32
            quantized[bg_mask] = (np.zeros_like(quantized[bg_mask]) * 0.7 + color_remnant[bg_mask] * 0.3).astype(np.uint8)
        return quantized
    elif style == 2:
        return cv2.bitwise_not(roi)
    elif style == 3:
        h, w = roi.shape[:2]
        small = cv2.resize(roi, (w//10, h//10), interpolation=cv2.INTER_LINEAR)
        return cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)
    elif style == 4:
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        return cv2.applyColorMap(gray, cv2.COLORMAP_JET)
    return roi

def fill_polygon(frame, pts, style, invert):
    mask = np.zeros((frame.shape[0], frame.shape[1]), dtype=np.uint8)
    cv2.fillPoly(mask, [pts], 255)
    roi = cv2.bitwise_and(frame, frame, mask=mask)
    filtered = apply_filter(roi, style, invert)
    frame = cv2.bitwise_and(frame, frame, mask=cv2.bitwise_not(mask))
    frame = cv2.add(frame, filtered)
    return frame

def line_intersection(p1, p2, p3, p4):
    x1, y1 = p1; x2, y2 = p2; x3, y3 = p3; x4, y4 = p4
    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if abs(denom) < 1e-6:
        return None
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
    u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom
    if 0 <= t <= 1 and 0 <= u <= 1:
        return (int(x1 + t * (x2 - x1)), int(y1 + t * (y2 - y1)))
    return None

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
    timestamp = int(time.time() * 1000)

    results = landmarker.detect_for_video(mp_image, timestamp)

    left_fingers = {}
    right_fingers = {}

    if results.hand_landmarks:
        for hand_idx, hand in enumerate(results.hand_landmarks):
            center_x = hand[0].x
            is_left = center_x < 0.5
            for i in range(finger_count):
                fid = finger_ids_all[i]
                lm = hand[fid]
                x = int(lm.x * w)
                y = int(lm.y * h)
                if is_left:
                    left_fingers[fid] = (x, y)
                else:
                    right_fingers[fid] = (x, y)

    selected_ids = finger_ids_all[:finger_count]
    if all(fid in left_fingers for fid in selected_ids) and all(fid in right_fingers for fid in selected_ids):
        # ---------- 算法分支 ----------
        if finger_count == 2:
            # --- 二指交叉沙漏 ---
            fid1, fid2 = selected_ids[0], selected_ids[1]
            L1 = left_fingers[fid1]
            R1 = right_fingers[fid1]
            L2 = left_fingers[fid2]
            R2 = right_fingers[fid2]
            cross_pt = line_intersection(L1, R1, L2, R2)
            if cross_pt:
                tri1 = np.array([L1, L2, cross_pt], dtype=np.int32)
                tri2 = np.array([R1, R2, cross_pt], dtype=np.int32)
                frame = fill_polygon(frame, tri1, filter_style, invert)
                frame = fill_polygon(frame, tri2, filter_style, invert)
                cv2.polylines(frame, [tri1], isClosed=True, color=(200,200,200), thickness=1)
                cv2.polylines(frame, [tri2], isClosed=True, color=(200,200,200), thickness=1)
                cv2.line(frame, L1, R1, color_map.get(fid1, (255,255,255)), 2)
                cv2.line(frame, L2, R2, color_map.get(fid2, (255,255,255)), 2)
                cv2.circle(frame, cross_pt, 10, (0, 255, 255), -1)
            else:
                quad = np.array([L1, L2, R2, R1], dtype=np.int32)
                frame = fill_polygon(frame, quad, filter_style, invert)
                cv2.polylines(frame, [quad], isClosed=True, color=(200,200,200), thickness=1)
                cv2.line(frame, L1, R1, color_map.get(fid1, (255,255,255)), 2)
                cv2.line(frame, L2, R2, color_map.get(fid2, (255,255,255)), 2)
        else:
            # --- 三指及以上：凸包填充 + 顺序边绘制 ---
            # 收集所有指尖点
            all_points = []
            for fid in selected_ids:
                all_points.append(left_fingers[fid])
                all_points.append(right_fingers[fid])
            # 计算凸包
            hull = cv2.convexHull(np.array(all_points, dtype=np.int32))
            hull_pts = hull.squeeze()  # shape (N,2)
            if len(hull_pts) >= 3:
                # 填充凸包区域
                frame = fill_polygon(frame, hull_pts, filter_style, invert)
                # 绘制凸包边框
                cv2.polylines(frame, [hull_pts], isClosed=True, color=(200,200,200), thickness=1)

            # 绘制内部边（顺序连接）
            # 左手内部边（按顺序）
            for i in range(len(selected_ids) - 1):
                cv2.line(frame, left_fingers[selected_ids[i]], left_fingers[selected_ids[i+1]], 
                         (200, 200, 200), 1, lineType=cv2.LINE_AA)
                cv2.line(frame, right_fingers[selected_ids[i]], right_fingers[selected_ids[i+1]], 
                         (200, 200, 200), 1, lineType=cv2.LINE_AA)
            # 配对边
            for fid in selected_ids:
                pt1 = left_fingers[fid]
                pt2 = right_fingers[fid]
                color = color_map.get(fid, (255, 255, 255))
                cv2.line(frame, pt1, pt2, color, 2, lineType=cv2.LINE_AA)

        # 绘制所有顶点
        for fid in selected_ids:
            pt1 = left_fingers[fid]
            pt2 = right_fingers[fid]
            color = color_map.get(fid, (200,200,200))
            cv2.circle(frame, pt1, 6, color, -1)
            cv2.circle(frame, pt2, 6, color, -1)
            cv2.putText(frame, f"L-{finger_names[fid]}", (pt1[0]-20, pt1[1]-15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200,200,200), 1)
            cv2.putText(frame, f"R-{finger_names[fid]}", (pt2[0]-20, pt2[1]-15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200,200,200), 1)

    # ---------- HUD ----------
    style_names = {1:'漫画', 2:'反转', 3:'像素', 4:'热感'}
    mode = "交叉沙漏" if finger_count == 2 else "凸包填充"
    status = f"手指:{finger_count} 模式:{mode} 风格:{style_names.get(filter_style, '')} 反转:{'ON' if invert else 'OFF'}"
    cv2.putText(frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200,200,200), 1)
    cv2.putText(frame, "2-5:手指喵 | 1-4:风格喵 | 空格:反转喵", (10, 60), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150,150,150), 1)
    
    cv2.imshow("Adaptive Convex Filter", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == 27:
        break
    elif key == ord(' '):
        invert = not invert
    elif key in [ord(str(i)) for i in range(2, 6)]:
        finger_count = int(chr(key))
        print(f"手指数量: {finger_count} | 模式: {'交叉沙漏' if finger_count == 2 else '凸包填充'}")
    elif key in [ord(str(i)) for i in range(1, 5)]:
        filter_style = int(chr(key))
        print(f"滤镜风格: {style_names[filter_style]}")

cap.release()
cv2.destroyAllWindows()