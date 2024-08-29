# Sudoku Solver

This project automatically solves Sudokus on websites like [sudoku.com](https://www.sudoku.com). The Sudoku Solver extracts the Sudoku board from a screenshot or image, recognizes the numbers in the cells, and then automatically solves the puzzle.

## Installation

1. **Install Python and Dependencies**:
    Ensure you have Python 3.x installed on your system. Install the required Python packages using:

    ```bash
    pip install -r requirements.txt
    ```

2. **Install Tesseract OCR**:
    This project uses Tesseract for optical character recognition (OCR). Install Tesseract:

    https://github.com/tesseract-ocr/tesseract/releases)


## Usage

1. **Extract Sudoku Board**:
    The Sudoku Solver extracts the Sudoku board from an screenshot. The extraction process is based on contour detection and subsequent extraction of individual cells.

2. **Optical Character Recognition**:
    Each cell is analyzed using Tesseract OCR to recognize the numbers it contains.

3. **Solve Sudoku**:
    Once the Sudoku board is extracted and the numbers are recognized, the Sudoku is automatically solved.
