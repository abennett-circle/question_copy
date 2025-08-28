# Last Updated: 2025-08-22
# Description: A class for reading an answered questionnaire for Compliance team.
#              (1) Inherits from the Questionnaire class.

################################################################################
# Imports
################################################################################
from .Questionnaire import Questionnaire

################################################################################
# Reference Questionnaire Class
################################################################################
"""
Purpose: Subclass of the Questionnaire class.

Attributes:
    N/A

"""
class Reference_Questionnaire(Questionnaire):

    """Initialize the Reference_Questionnaire class.
        
        Args:
            file_path (str, optional): Path to the CSV file to read.
    """
    def __init__(self, file_path=None, 
                       question_col="question",
                       answer_col="answer"):
        
        # Initializes the superclass    
        super().__init__(file_path,
                         is_reference=True,
                         question_col=question_col,
                         answer_col=answer_col)