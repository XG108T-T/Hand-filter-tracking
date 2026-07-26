import cv2
import mediapipe as mp
import numpy as np
import time
import random

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

print("🎯 优化版手指特效 | 控制键")
print("   2-5: 选择手指数量")
print("   Q/W/E/R: 切换主滤镜风格")
print("   1: 切换简单/丰富模式 (丰富模式有重叠特效)")
print("   空格: 黑白反转")
print("   ESC: 退出")

# ---------- 配置 ----------
finger_count = 2
invert = False
global_style = 1  # 1:漫画, 2:反转, 3:像素, 4:热感
rich_mode = True  # True=丰富模式（有重叠特效），False=简单模式

finger_ids_all = [4, 8, 12, 16, 20]
finger_names = {4: '拇指', 8: '食指', 12: '中指', 16: '无名指', 20: '小指'}

# ---------- 主滤镜（快速） ----------
def apply_main_style(roi, style, invert=False):
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

# ---------- 重叠特效（中等复杂度） ----------
def overlap_effect_rgb_split(roi):
    h, w = roi.shape[:2]
    offset = random.randint(5, 15)
    b, g, r = cv2.split(roi)
    b_shift = np.roll(b, offset, axis=1)
    r_shift = np.roll(r, -offset, axis=1)
    return cv2.merge([b_shift, g, r_shift])

def overlap_effect_pixel_damage(roi):
    result = roi.copy()
    h, w = roi.shape[:2]
    ratio = 0.05
    coords = [(random.randint(0,w-1), random.randint(0,h-1)) for _ in range(int(h*w*ratio))]
    for x, y in coords:
        choice = random.choice(['black', 'white', 'random'])
        if choice == 'black':
            result[y, x] = [0, 0, 0]
        elif choice == 'white':
            result[y, x] = [255, 255, 255]
        else:
            result[y, x] = [random.randint(0,255) for _ in range(3)]
    return result

def overlap_effect_tear(roi):
    result = roi.copy()
    h, w = roi.shape[:2]
    y = random.randint(0, h-1)
    height = random.randint(2, 5)
    shift = random.randint(-20, 20)
    if y + height < h:
        slice_roi = result[y:y+height, :].copy()
        rolled = np.roll(slice_roi, shift, axis=1)
        result[y:y+height, :] = rolled
    return result

def overlap_effect_block_glitch(roi):
    result = roi.copy()
    h, w = roi.shape[:2]
    grid = random.choice([4, 6])
    block_h, block_w = h//grid, w//grid
    blocks = []
    for i in range(grid):
        for j in range(grid):
            y1, y2 = i*block_h, (i+1)*block_h
            x1, x2 = j*block_w, (j+1)*block_w
            blocks.append(result[y1:y2, x1:x2].copy())
    random.shuffle(blocks)
    idx = 0
    for i in range(grid):
        for j in range(grid):
            y1, y2 = i*block_h, (i+1)*block_h
            x1, x2 = j*block_w, (j+1)*block_w
            if idx < len(blocks):
                result[y1:y2, x1:x2] = blocks[idx]
                idx += 1
    return result

def overlap_effect_data_stream(roi):
    result = roi.copy()
    h, w = roi.shape[:2]
    chars = np.random.choice(['0', '1', '#', '%', '&'], (h//15, w//15))
    for i, row in enumerate(chars):
        for j, ch in enumerate(row):
            y = i*15 + 5
            x = j*15 + 5
            if y < h and x < w:
                color = (random.randint(100,255), random.randint(100,255), random.randint(100,255))
                cv2.putText(result, ch, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
    return result

OVERLAP_EFFECTS = [
    overlap_effect_rgb_split,
    overlap_effect_pixel_damage,
    overlap_effect_tear,
    overlap_effect_block_glitch,
    overlap_effect_data_stream,
]

def apply_overlap_effect(roi):
    """随机选择一种重叠特效"""
    if roi.size == 0 or not rich_mode:
        return roi
    func = random.choice(OVERLAP_EFFECTS)
    return func(roi)

def fill_quad(frame, quad, style, invert):
    """填充四边形主滤镜"""
    mask = np.zeros((frame.shape[0], frame.shape[1]), dtype=np.uint8)
    cv2.fillPoly(mask, [quad], 255)
    roi = cv2.bitwise_and(frame, frame, mask=mask)
    filtered = apply_main_style(roi, style, invert)
    frame[mask == 255] = filtered[mask == 255]
    return frame

def get_quad_mask(quad, shape):
    """生成四边形掩码"""
    mask = np.zeros(shape, dtype=np.uint8)
    cv2.fillPoly(mask, [quad], 255)
    return mask

# ---------- 主循环 ----------
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
        # 构建四边形列表
        quads = []
        for i in range(len(selected_ids) - 1):
            fid1 = selected_ids[i]
            fid2 = selected_ids[i+1]
            L1 = left_fingers[fid1]
            L2 = left_fingers[fid2]
            R1 = right_fingers[fid1]
            R2 = right_fingers[fid2]
            quad = np.array([L1, L2, R2, R1], dtype=np.int32)
            quads.append(quad)

        if quads:
            # 存储每个四边形的掩码
            masks = []
            for quad in quads:
                mask = get_quad_mask(quad, (h, w))
                masks.append(mask)

            # 1. 先填充所有四边形的主滤镜
            for i, quad in enumerate(quads):
                frame = fill_quad(frame, quad, global_style, invert)

            # 2. 处理重叠区域（丰富模式）
            if rich_mode and len(masks) > 1:
                # 对每对相邻四边形计算重叠区域
                for i in range(len(masks) - 1):
                    overlap_mask = cv2.bitwise_and(masks[i], masks[i+1])
                    if np.any(overlap_mask):
                        # 提取重叠区域
                        roi = cv2.bitwise_and(frame, frame, mask=overlap_mask)
                        # 应用重叠特效
                        overlapped = apply_overlap_effect(roi)
                        # 放回
                        frame[overlap_mask == 255] = overlapped[overlap_mask == 255]

    # ---------- HUD ----------
    style_names = {1:'漫画', 2:'反转', 3:'像素', 4:'热感'}
    mode_str = "丰富" if rich_mode else "简单"
    status = f"手指:{finger_count} 基调:{style_names.get(global_style, '')} 模式:{mode_str} 反转:{'ON' if invert else 'OFF'}"
    cv2.putText(frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200,200,200), 1)
    cv2.putText(frame, "2-5:手指数 | Q/W/E/R:基调 | 1:切换模式 | 空格:反转", (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150,150,150), 1)

    cv2.imshow("Optimized Finger FX", frame)

    # ---------- 键盘控制 ----------
    key = cv2.waitKey(1) & 0xFF
    if key == 27:
        break
    elif key == ord(' '):
        invert = not invert
    elif key == ord('1'):
        rich_mode = not rich_mode
        print(f"模式切换为: {'丰富' if rich_mode else '简单'}")
    elif key in [ord(str(i)) for i in range(2, 6)]:
        finger_count = int(chr(key))
        print(f"手指数量: {finger_count}")
    elif key == ord('q') or key == ord('Q'):
        global_style = 1
        print("基调: 漫画")
    elif key == ord('w') or key == ord('W'):
        global_style = 2
        print("基调: 反转")
    elif key == ord('e') or key == ord('E'):
        global_style = 3
        print("基调: 像素")
    elif key == ord('r') or key == ord('R'):
        global_style = 4
        print("基调: 热感")

cap.release()
cv2.destroyAllWindows()