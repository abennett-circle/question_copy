# Last Updated: 2025-08-22
# Description: A class for reading an unanswered questionnaire for Compliance team.
#              (1) Inherits from the Questionnaire class.

################################################################################
# Imports
################################################################################
from .Questionnaire import Questionnaire

################################################################################
# Unanswered Questionnaire Class
################################################################################
"""
Purpose: Subclass of the Questionnaire class.

Attributes:
    N/A

"""
class Unanswered_Questionnaire(Questionnaire):

    """Initialize the Unanswered_Questionnaire class.
        
        Args:
            file_path (str, optional): Path to the CSV file to read.
    """
    def __init__(self, file_path=None, 
                       question_col="question",
                       answer_col="answer"):
        
        # Initializes the superclass
        super().__init__(file_path,
                         is_reference=False,
                         question_col=question_col,
                         answer_col=answer_col)