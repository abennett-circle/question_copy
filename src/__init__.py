# Compliance Questionnaire Package
# Author: Austin Bennett, Circle Research
# Last Updated: 2025-08-19

"""
Compliance Questionnaire Package

This package provides automated questionnaire matching using AI-powered semantic analysis.
"""

__version__ = "1.0.0"
__author__ = "Austin Bennett, Circle Research"

# Import main classes for easy access
from .Questionnaire_Filler import Questionnaire_Filler
from .Question import Question
from .Questionnaire import Questionnaire
from .Reference_Questionnaire import Reference_Questionnaire
from .Unanswered_Questionnaire import Unanswered_Questionnaire

__all__ = [
    'Questionnaire_Filler',
    'Question', 
    'Questionnaire',
    'Reference_Questionnaire',
    'Unanswered_Questionnaire'
]

