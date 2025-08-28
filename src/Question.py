# Last Updated: 2025-08-22
# Description: A class for storing questions to fill out an unanswered questionnaire for Compliance team.

################################################################################
# Question Class
################################################################################

"""
Purpose: Represents a single question with its answer.

Attributes:
    question (str): The question text.
    answer (str): The answer to the question.
    question_id (str): The ID of the question.
    is_reference (bool): A boolean flag for whether the question is a reference question.
    reference_question (str): The reference question.
    question_match_score (float): The question match score.
    answer_match_score (float): The answer match score.

Methods:
    set_answer(answer): Set the answer for the question.
"""
class Question(object):

    """Initialize the Question class.
        
        Args:
            question (str): The question text.
            question_id (str): The ID of the question.
            is_reference (bool): A boolean flag for whether the question is a reference question.
            question_match_score (float): The question match score.
            answer_match_score (float): The answer match score.
    """
    def __init__(self, question, question_id, is_reference=False, question_match_score=0, answer_match_score=0):
        
        # Sets class attributes
        self.question = question
        self.answer = ""
        self.question_id = question_id

        # Gets the most similar question from the Reference Questionnaire
        self.is_reference = is_reference
        if (is_reference):
            self.reference_question = self.question
        else:
            self.reference_question = ""

        # Sets the question match score
        self.question_match_score = question_match_score

        # Sets the answer match score
        self.answer_match_score = answer_match_score



    """Set the answer for the question.
        
        Args:
            answer (str): The answer to set.
    """
    def set_answer(self, answer):
        self.answer = answer



    """Set the reference question.
        
        Args:
            reference_question (str): The reference question to set.
    """
    def set_reference_question(self, reference_question):
        self.reference_question = reference_question



    """Set the question match score.
        
        Args:
            question_match_score (float): The question match score to set.
    """
    def set_question_match_score(self, question_match_score):
        self.question_match_score = question_match_score



    """Set the answer match score.
        
        Args:
            answer_match_score (float): The answer match score to set.
    """
    def set_answer_match_score(self, answer_match_score):
        self.answer_match_score = answer_match_score



    """Get the question text.
        
        Returns:
            str: The question text.
        """
    def get_question(self):
        return self.question
    
    

    """Get the cleaned question text.
        
        Returns:
            str: The cleaned question text.
        """
    def get_clean_question(self):
        return self.clean_question



    """Get the answer.
        
        Returns:
            str: The answer, or None if no answer has been set.
        """
    def get_answer(self):
        return self.answer
    


    """Get the boolean flag for whether the question is a reference question.
        
        Returns:
            bool: True if the question is a reference question, False otherwise.
        """
    def get_is_reference(self):
        return self.is_reference
    


    """Get the reference question.
        
        Returns:
            str: The reference question.
        """
    def get_reference_question(self):
        return self.reference_question
    


    """Get the question match score.

        Returns:
            float: The question match score.
        """
    def get_question_match_score(self):
        return self.question_match_score
    


    """Get the answer match score.
        
        Returns:
            float: The answer match score.
        """
    def get_answer_match_score(self):
        return self.answer_match_score
    


    """Get the question ID.
        
        Returns:
            str: The question ID.
        """
    def get_question_id(self):
        return self.question_id