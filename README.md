# Question Copy

An automated solution for matching questions between questionnaires using AI-powered semantic analysis. Streamlines filling out new unanswered questionnaires by leveraging previously answered reference questionnaires to show previous answers and questions.

## Issues
Please report any issues with this software to Austin Bennett (austin.bennett@circle.com) and Mira Belenkiy (mira.belenkiy@circle.com) on the Circle Research team.

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation

1. **Install dependencies:**
   We recommend you create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

   Then install requirements:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up configuration:**
   ```bash
   cp config.env.template config.env
   # Edit config.env with your actual API credentials
   ```

3. **Run the questionnaire filler:**
   ```bash
   python question_copy.py data/Mock_Reference.csv data/Mock_Unanswered.csv
   ```

**Troubleshooting.**
If you get a connection error, this means you have to setup your Zscaler certificates:

```bash
# Check that you have Zscaler certificates installed
if [ -z "$(security find-certificate -p -c 'Zscaler Root CA')" ]; then  
  echo "Certificate does not exist. Please contact IT"  
  exit 1
else  
  mkdir $HOME/.certs &> /dev/null
  security find-certificate -p -c "Zscaler Root CA" > $HOME/.certs/zscaler_root_ca.pem
fi

# Install certifi
pip3 install certifi \
  && cat $HOME/.certs/zscaler_root_ca.pem >> $(python3 -m certifi) \
  && pip3 config set global.cert $(python3 -m certifi)

export CERT_PATH=$(python -m certifi)
export CURL_CA_BUNDLE=${CERT_PATH}
export REQUESTS_CA_BUNDLE=${CERT_PATH}
export SSL_CERT_FILE=${CERT_PATH}
```

## 📋 Usage

### Command Line Interface

**Basic usage structure:**
```bash
python question_copy.py <reference_file> <unanswered_file>
```

**With custom output:**
```bash
python question_copy.py <reference_file> <unanswered_file> --output results.xlsx
```

**With custom column names:**
```bash
python question_copy.py <reference_file> <unanswered_file> \
  --ref-question-col "Question - Full" \
  --ref-answer-col "Answer - Full" \
  --unans-question-col "Question - Full" \
  --unans-answer-col "Answer - Full"
```

**Python Notebook:**
There is also a Python Notebook for those who prefer running operations through them. The basic workflow of questionnaire filling is listed in "question_copy_notebook_version.ipynb"

### Arguments

**Required:**
- `reference_file` - Path to reference questionnaire (CSV/Excel), CSV preferred
- `unanswered_file` - Path to unanswered questionnaire (CSV/Excel), CSV preferred

**Optional:**
- `--ref-question-col` - Reference question column (default: "Question")
- `--ref-answer-col` - Reference answer column (default: "Answer")
- `--unans-question-col` - Unanswered question column (default: "Question")
- `--unans-answer-col` - Unanswered answer column (default: "Answer")
- `--output` - Output file name (default: "combined_questionnaire.xlsx")
- `--skip-config-check` - Skip config validation (for testing)

### Configuration

Create a `config.env` file with your API credentials:

```env
# ChatAI Circle API URL
CHATAI_BASE_URL=https://your-api-url.com

# ChatAI Circle API Key
CHATAI_API_KEY=your-api-key-here
```

## 📊 Input File Format

Your CSV/Excel files should have columns for questions and answers:

```csv
Question,Answer
"Do you have a privacy policy?","Yes, we have a comprehensive privacy policy."
"How many employees do you have?","150"
"What is your revenue?","$10M annually"
```

**Note:** If your files use different column names (like "Question - Full" instead of "Question"), specify them with the column arguments.

## 📈 Output

The tool generates an Excel file (.xlsx) with the following data:

### Output Columns
- **Current Question** - Question from unanswered file
- **Matched Question** - Best matching question from reference file
- **Matched Question Row** - Row number from the reference file
- **Question Match Score** - Question similarity score (0.0-1.0). Scores below threshold 0.85 marked as unreliable.
- **Current Answer** - Answer from unanswered file
- **Matched Answer** - Answer from reference questionnaire
- **Answer Match Score** - Answer similarity score (0.0-1.0). Scores below threshold 0.85 marked as unreliable.

### File Format Support
- **Excel format (.xlsx)** - Default output format
- **CSV format (.csv)** - Available for compatibility



## ⚡ Examples

### Example 1: Basic Usage
```bash
python question_copy.py data/Mock_Reference.csv data/Mock_Unanswered.csv
```

### Example 2: Custom Output File
```bash
# Excel format with visual formatting (recommended)
python question_copy.py data/Mock_Reference.csv data/Mock_Unanswered.csv --output my_results.xlsx

# CSV format for compatibility
python question_copy.py data/Mock_Reference.csv data/Mock_Unanswered.csv --output my_results.csv
```

### Example 3: Custom Column Names
```bash
python question_copy.py data/Mock_Reference.csv data/Mock_Unanswered.csv \
  --ref-question-col "Question - Full" \
  --ref-answer-col "Answer - Full" \
  --unans-question-col "Question - Full" \
  --unans-answer-col "Answer - Full" \
  --output custom_results.xlsx
```

### Example 4: Testing Mode
```bash
python question_copy.py data/Mock_Reference.csv data/Mock_Unanswered.csv --skip-config-check
```

## 🧪 Testing

Doc tests for developers: Run the test suite to verify everything works:

```bash
# Run all tests
python -m pytest test/ -v

# Run just unit tests
python -m pytest test/test_questionnaire_filler.py -v

# Run just CSV integration tests
python -m pytest test/test_csv_integration.py -v

# Run with built-in unittest
python test/test_questionnaire_filler.py
```

## 🔧 Troubleshooting

### Common Issues

**Config file not found:**
```
❌ Config file not found!
💡 Please create a config.env file with your API credentials.
```
**Solution:** Copy `config.env.template` to `config.env` and add your credentials.

**Column not found:**
```
❌ Column Error: Question column 'Question' not found in file.
```
**Solution:** Use `--ref-question-col` and related arguments to specify correct column names. For example, if your files use "Question - Full", add `--ref-question-col "Question - Full" --ref-answer-col "Answer - Full"`.

**File not found:**
```
❌ Error: Reference file 'missing.csv' not found!
```
**Solution:** Check file paths and ensure files exist. If you put a file into the same level as question_copy.py, you can run it directly. If you put it in the data folder, you need to specify that file path. For example "test.csv" put into the data folder would require "data/test.csv" that you feed to the terminal command as an argument.

## 📁 Project Structure

```
Compliance_Questionnaire/
├── src/                    # Source code
├── test/                   # Unit and integration tests
├── data/                   # Data files
│   ├── Mock_Reference.csv  # Sample reference questionnaire
│   └── Mock_Unanswered.csv # Sample unanswered questionnaire
├── question_copy.py        # Main command-line script
├── requirements.txt        # Python dependencies
├── config.env.template     # Configuration template
└── new_README.md          # This file
```

## 🎯 What It Does

1. **Loads** reference and unanswered questionnaires from CSV/Excel
2. **Matches** questions using exact matching and AI-powered semantic analysis
3. **Scores** question similarity (70% threshold for matching)
4. **Compares** answers between matched questions
5. **Generates** an Excel file with all results for review

Ready to streamline your questionnaire merging process! 🚀
