# MCQ Master 🎯

A premium Streamlit-based Multiple Choice Question (MCQ) tester. Upload your Excel or CSV question sheets and test your knowledge with real-time scoring and time tracking.

## ✨ Features
- **Premium UI**: Modern dark-mode interface.
- **Flexible Loading**: Automatically detects columns like "Question", "Option A", "Option B", etc.
- **Interactive Navigation**: Sidebar navigation to jump between questions.
- **Time Tracking**: Monitors how long you take to finish the test.
- **Past Sets**: Automatically remembers and allows you to restart previously uploaded tests.
- **Export Results**: Download your performance report as an Excel file.
- **Detailed Review**: Review correct answers for any mistakes made.

## 🚀 How to Run
1. **Clone the repository** (or download the files).
2. **Install dependencies**:
   ```bash
   pip install streamlit pandas openpyxl
   ```
3. **Run the app**:
   ```bash
   streamlit run app.py
   ```

## 📋 Suggested File Format
Your Excel/CSV should have the following columns (names are flexible):
- `Question`
- `Option A`, `Option B`, `Option C`, `Option D`
- `Answer` (Exact text of the correct option)
