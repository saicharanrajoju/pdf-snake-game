# 🐍 PDF Snake Game 

Ever thought of playing a game *inside* a PDF? Tired of reading and hustling through documents? Take a break and play Snake right here! 📄➡️🎮

This project is an experiment exploring the possibilities (and limitations!) of creating interactive fun in unexpected places using Python and embedded JavaScript.

## ▶️ How to Play (Important!)

❗ **IMPORTANT:** This is a interactive PDF currently **only works correctly in Google Chrome on a Desktop/Laptop**. It **will likely NOT work** on mobile devices, or in other browsers/viewers like Firefox, Safari, Edge (non-Chrome mode), or Adobe Reader due to crucial differences in PDF JavaScript support.

1.  **Download:** Get the `snake_pdf_final.pdf` file from this repository.
2.  **Open with CHROME:** Use **Google Chrome** on a **Desktop computer** to open the `snake_pdf_final.pdf` file. (Other browsers/viewers/mobile will not work).
3.  **Start:** Click the "Start Game" button.
4.  **FOCUS! (Maybe):** You *might* need to **click once anywhere on the page** after starting to ensure keyboard input works.
5.  **Controls:** Use **W (Up), A (Left), S (Down), D (Right)** keys ⌨️ to control the snake.
6.  **Goal:** Steer the snake (gray squares) to eat the blinking food pellet (also a gray square). Avoid hitting the edges or the snake's own body!
7.  **Restart:** After Game Over, click the "Start Game" button again.

## 🤔 Why Does It (Only) Work in Chrome?

Modern web browsers like Google Chrome have built-in PDF viewers. Chrome uses an engine called **PDFium** to render PDFs.

This game works in Chrome because PDFium provides *sufficient* support for the specific **AcroForm JavaScript APIs** used here:

* **PDF Generation:** The basic structure created by Python is standard PDF.
* **Embedded JavaScript:** PDFium executes the JavaScript embedded within the PDF.
* **Event Handling:** It correctly handles the JavaScript triggered by button clicks (`/A`) and keystrokes (`/AA /K`) in the text field.
* **Dynamic `.hidden` Property:** Crucially, PDFium allows the JavaScript to dynamically change the `field.hidden` property of the button fields via `field.hidden = ...`. This showing and hiding of the pre-defined gray buttons creates the visual effect of movement.

Other PDF viewers (like Firefox's PDF.js, native OS viewers, mobile viewers) implement the JavaScript APIs differently or incompletely. They often fail to handle the rapid `.hidden` property changes or the event handling correctly, which is why the game appears broken or static in those environments.

## ⚙️ How It Works (Technical Summary)

* **Python Generator (`generate_snake_pdf.py`):** Creates the PDF structure, grid buttons, UI elements. Reads JS from file.
* **Embedded JavaScript (`snake_game.js`):** Contains game logic, runs inside the PDF viewer.
* **`.hidden` for Visuals:** Toggles button visibility (`field.hidden = true/false`) to draw the game state.
* **Static Grid:** Background lines are drawn directly onto the PDF page content.
* **Blinking Food:** Food pellet toggles visibility via `.hidden`.

## 🛠️ How to Generate Your Own

1.  **Prerequisites:** Python 3.
2.  **Files:** `generate_snake_pdf.py` and `snake_game.js` in the same directory.
3.  **Run:** `python generate_snake_pdf.py` in terminal.
4.  Output: `snake_pdf_final.pdf`.

## ❗ Challenges & Workarounds Recap

* Dynamic colors (`fillColor`), text (`value`), and borders (`/BS`) proved unreliable across viewers.
* Solution: Used the `.hidden` property for visuals, added a static background grid, and made the food blink.

😊This was a fun exploration into PDF limits! Potential future ideas:
* Score display (using a Text Field).
* Variable speed.
* Other `.hidden`-based games?

## 💡 Got any Ideas?
Feel free to fork this project, experiment, or open an issue if you have ideas or find bugs! 🙏


