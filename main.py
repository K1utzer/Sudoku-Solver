import cv2
import numpy as np
import pyautogui
import pytesseract
import re
from sudoku import Sudoku

pytesseract.pytesseract.tesseract_cmd = r'path_to_tesseract_exe'

MatLike = np.ndarray

def screenshot() -> MatLike:
    screenshot = pyautogui.screenshot()
    screenshot = np.array(screenshot)
    return cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)

def preprocess_image(image: MatLike) -> MatLike:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    kernel = np.ones((5, 5), np.uint8)
    eroded = cv2.erode(cv2.dilate(edges, kernel, iterations=1), kernel, iterations=1)
    return eroded

def find_chessboard_contour(image: MatLike) -> np.ndarray:
    contours, _ = cv2.findContours(image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    max_area = 0
    chessboard_contour = None

    for contour in contours:
        area = cv2.contourArea(contour)
        if area < 1000:
            continue
        for epsilon_factor in np.linspace(0.01, 0.1, 10):
            epsilon = epsilon_factor * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            if len(approx) == 4:
                x, y, w, h = cv2.boundingRect(approx)
                aspect_ratio = w / float(h)
                if 0.9 < aspect_ratio < 1.1 and area > max_area:
                    chessboard_contour = approx
                    max_area = area
    return chessboard_contour

def extract_board(gray_image: MatLike, contour: np.ndarray) -> np.ndarray:
    x, y, w, h = cv2.boundingRect(contour)
    single_field_w, single_field_h = int(w / 9), int(h / 9)
    binary_image = cv2.threshold(gray_image[y+5:y+h-2, x+5:x+w-2], 128, 255, cv2.THRESH_BINARY)[1]
    board = []
    for y1 in range(0, h - single_field_h, single_field_h):
        board_ver = []
        for x1 in range(0, w - single_field_w, single_field_w):
            cropped_img = binary_image[y1+2:y1+single_field_h-5, x1+2:x1+single_field_w-5]
            text = pytesseract.image_to_string(cropped_img, config=r'--oem 3 --psm 6 -c tessedit_char_whitelist=123456789')
            numbers = re.findall(r'\d+', text)
            board_ver.append(int(numbers[0]) if numbers else 0)
        board.append(board_ver)

    return np.array(board), x, y, single_field_w, single_field_h

def remove_duplicates(board: np.ndarray) -> np.ndarray:
    for i in range(9):
        unique_row, counts_row = np.unique(board[i, :], return_counts=True)
        for num, count in zip(unique_row, counts_row):
            if num != 0 and count > 1:
                board[i, board[i, :] == num] = 0

    for j in range(9):
        unique_col, counts_col = np.unique(board[:, j], return_counts=True)
        for num, count in zip(unique_col, counts_col):
            if num != 0 and count > 1:
                board[board[:, j] == num, j] = 0

    return board

def insert_number(x: int, y: int, number: int):
    pyautogui.click(x, y)
    pyautogui.write(str(number))

def solve_and_insert_sudoku(original_board: np.ndarray, x: int, y: int, single_field_w: int, single_field_h: int):
    original_board = remove_duplicates(original_board)
    puzzle = Sudoku(3, 3, board=original_board.tolist())
    print(puzzle)
    solved_board = puzzle.solve(raising=True).board
    print(puzzle.solve())

    for i in range(9):
        for j in range(9):
            if original_board[i][j] == 0 and solved_board[i][j] != 0:
                x3 = int(x + single_field_w * j + single_field_w / 2)
                y3 = int(y + single_field_h * i + single_field_h / 2)
                insert_number(x3, y3, solved_board[i][j])

def main():
    image = screenshot()
    eroded = preprocess_image(image)
    chessboard_contour = find_chessboard_contour(eroded)
    if chessboard_contour is not None:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        board, x, y, single_field_w, single_field_h = extract_board(gray, chessboard_contour)
        solve_and_insert_sudoku(board, x, y, single_field_w, single_field_h)

if __name__ == "__main__":
    main()
