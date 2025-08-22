# Last Updated: 2025-08-22
# Description: A class for reading an unanswered questionnaire for Compliance team.

################################################################################
# Imports
################################################################################
import pandas as pd
from .Question import Question
import unicodedata
import re
import os

################################################################################
# Constants
################################################################################

# Compile once for performance
_SPACE_RE = re.compile(r"\s+")

################################################################################
# Questionnaire Class
################################################################################

"""
Purpose: Superclass for the "Reference_Questionnaire" and "Unanswered_Questionnaire" classes.

Attributes:
    file_path (str): Path to the CSV file to read.
    data (pd.DataFrame): The loaded data as a pandas DataFrame.
    questions (dict): A dictionary of Question objects contained within the file.
    question_col (str): The column name for the questions.
    answer_col (str): The column name for the answers.
    is_reference (bool): A boolean flag for whether the questionnaire is a reference questionnaire.

Methods:
    read_csv(file_path=None): Read a CSV file into a pandas DataFrame.
"""
class Questionnaire(object):

    """Initialize the Questionnaire class.
        
        Args:
            file_path (str, optional): Path to the CSV file to read.
            is_reference (bool, optional): A boolean flag for whether the questionnaire is a reference questionnaire.
            question_col (str, optional): The column name for the questions.
            answer_col (str, optional): The column name for the answers.
    """
    def __init__(self, file_path=None, 
                       is_reference=False, 
                       question_col="Question",
                       answer_col="Answer"):

        # Sets class attributes
        self.file_path = file_path
        self.data = None
        self.questions = dict()
        self.question_col = question_col
        self.answer_col = answer_col
        self.is_reference = is_reference

        # Reads in the data
        self._read_file()

        # Builds the questions from our dataset
        self._build_questions()



    """Reads in the file.
        
        Returns:
            N/A (Setter method for file data)
    """
    def _read_file(self):

        # Raises an error if the file path is not provided
        if (self.file_path == None):
            raise ValueError("ERROR: No File Type Specified")
        
        # Check if file exists
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"ERROR: File not found: {self.file_path}")
        
        # Sets self.data to the data from the file
        try:
            if self.file_path.endswith(".csv"):
                self.data = pd.read_csv(self.file_path)
            elif self.file_path.endswith(".xlsx"):
                self.data = pd.read_excel(self.file_path)
            else:
                raise ValueError("ERROR: File Type Not Supported. Only .csv and .xlsx files are supported.")
        except FileNotFoundError:
            raise  # Re-raise FileNotFoundError as-is
        except Exception as e:
            raise ValueError(f"ERROR: Failed to read file {self.file_path}: {str(e)}")
        


    """Get the loaded data.
        
        Returns:
            pd.DataFrame: The loaded data, or None if no data has been loaded.
    """
    def get_data(self):
        return self.data
    


    """
    Normalize text for exact-meaning comparison:
    - Unicode normalize to NFKC (merges visually identical forms)
    - Convert to lowercase (case-insensitive)
    - Strip leading/trailing spaces
    - Collapse multiple whitespace into a single space
    - Remove extra spaces before punctuation

    Args:
        text (str): The text to clean.

    Returns:
        str: The cleaned text.
    """
    def _clean_question(self, text: str) -> str:

        # Unicode normalization
        text = unicodedata.normalize("NFKC", text)

        # Collapse all whitespace
        text = _SPACE_RE.sub(" ", text)

        # Strip outer spaces
        text = text.strip()

        # Returns the cleaned text
        return text



    """Builds the questions from our dataset.
        
        Returns:
            N/A (Setter method for questions)
    """
    def _build_questions(self):
        
        # Validate that required columns exist
        if self.question_col not in self.data.columns:
            raise KeyError(f"ERROR: Question column '{self.question_col}' not found in file. Available columns: {list(self.data.columns)}")
        
        if self.answer_col not in self.data.columns:
            raise KeyError(f"ERROR: Answer column '{self.answer_col}' not found in file. Available columns: {list(self.data.columns)}")
        
        # Stores the questions and answers in a list of Question objects
        for index, row in self.data.iterrows():

            # Stores the current question
            curr_question = row[self.question_col]

            # Cleans the question
            curr_question = self._clean_question(curr_question)

            # Creates a new Question object
            question_obj = Question(curr_question, index, is_reference=self.is_reference)

            # If reference questionnaire, sets the answer for the question
            answer_value = row[self.answer_col]
            if (answer_value is not None and not pd.isna(answer_value) and str(answer_value).strip() != ""):
                question_obj.set_answer(answer_value)

            # Adds the question to the dictionary
            self.questions[curr_question] = question_obj



    """Get the questions.
        
        Returns:
            questions (dict): The questions.
    """
    def get_questions(self):
        return self.questions