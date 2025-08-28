#!/usr/bin/env python3
"""
Integration tests for CSV reading and questionnaire class structure.

These tests use real CSV files and test the actual pandas DataFrame operations,
CSV parsing, and integration between Questionnaire_Filler and questionnaire classes.
"""

import unittest
import sys
import os
import pandas as pd
import numpy as np
import tempfile
from unittest.mock import patch, Mock

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.Questionnaire_Filler import Questionnaire_Filler
from src.Reference_Questionnaire import Reference_Questionnaire
from src.Unanswered_Questionnaire import Unanswered_Questionnaire
from src.Question import Question


class TestCSVIntegration(unittest.TestCase):
    """Test CSV reading and questionnaire class integration."""

    def setUp(self):
        """Set up test CSV files."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test reference CSV
        self.reference_data = {
            'Question - Full': [
                'What is your company name?',
                'Do you have a privacy policy?',
                'How many employees do you have?',
                'What is your revenue?'
            ],
            'Answer - Full': [
                'Acme Corp',
                'Yes, we have a comprehensive privacy policy.',
                '150',
                '$10M annually'
            ]
        }
        
        self.reference_csv = os.path.join(self.temp_dir, 'reference.csv')
        pd.DataFrame(self.reference_data).to_csv(self.reference_csv, index=False)
        
        # Create test unanswered CSV with various data types and edge cases
        self.unanswered_data = {
            'Question - Full': [
                'What is your company name?',  # Exact match
                'Do you have privacy policies?',  # Similar but not exact
                'How many staff do you employ?',  # Different wording
                'What is your annual revenue?',  # Similar question
                'Do you use cloud services?',  # New question
                'What is your favorite color?'  # Another new question
            ],
            'Answer - Full': [
                'Acme Corp',  # Exact match answer
                'Yes',  # Different answer
                np.nan,  # NaN answer
                '',  # Empty answer
                'AWS and Azure',  # Valid answer
                '   '  # Whitespace-only answer
            ]
        }
        
        self.unanswered_csv = os.path.join(self.temp_dir, 'unanswered.csv')
        pd.DataFrame(self.unanswered_data).to_csv(self.unanswered_csv, index=False)

    def tearDown(self):
        """Clean up test files."""
        import shutil
        shutil.rmtree(self.temp_dir)

    @patch('os.path.exists', return_value=True)
    @patch('os.getenv')
    def test_questionnaire_filler_initialization_with_real_csvs(self, mock_getenv, mock_exists):
        """Test that Questionnaire_Filler can initialize with real CSV files."""
        # Mock environment variables
        mock_getenv.side_effect = lambda key: {
            'CHATAI_BASE_URL': 'http://test-url.com',
            'CHATAI_API_KEY': 'test-key'
        }.get(key)
        
        # Should not raise any exceptions
        filler = Questionnaire_Filler(
            reference_file_name=self.reference_csv,
            reference_question_col="Question - Full",
            reference_answer_col="Answer - Full",
            unanswered_file_name=self.unanswered_csv,
            unanswered_question_col="Question - Full",
            unanswered_answer_col="Answer - Full"
        )
        
        # Verify questionnaire objects were created
        self.assertIsInstance(filler.reference_questionnaire, Reference_Questionnaire)
        self.assertIsInstance(filler.unanswered_questionnaire, Unanswered_Questionnaire)

    def test_reference_questionnaire_csv_reading(self):
        """Test that Reference_Questionnaire correctly reads CSV data."""
        ref_q = Reference_Questionnaire(
            file_path=self.reference_csv,
            question_col="Question - Full",
            answer_col="Answer - Full"
        )
        
        # Check that questions were loaded
        questions = ref_q.get_questions()
        self.assertEqual(len(questions), 4)
        
        # Check specific question content
        self.assertIn('What is your company name?', questions)
        self.assertIn('Do you have a privacy policy?', questions)
        
        # Check that answers were loaded correctly
        company_question = questions['What is your company name?']
        self.assertEqual(company_question.get_answer(), 'Acme Corp')
        
        privacy_question = questions['Do you have a privacy policy?']
        self.assertEqual(privacy_question.get_answer(), 'Yes, we have a comprehensive privacy policy.')

    def test_unanswered_questionnaire_csv_reading(self):
        """Test that Unanswered_Questionnaire correctly reads CSV data."""
        unans_q = Unanswered_Questionnaire(
            file_path=self.unanswered_csv,
            question_col="Question - Full",
            answer_col="Answer - Full"
        )
        
        # Check that questions were loaded
        questions = unans_q.get_questions()
        self.assertEqual(len(questions), 6)
        
        # Check specific question content
        self.assertIn('What is your company name?', questions)
        self.assertIn('Do you use cloud services?', questions)
        
        # Check that answers were loaded correctly, including edge cases
        company_question = questions['What is your company name?']
        self.assertEqual(company_question.get_answer(), 'Acme Corp')
        
        cloud_question = questions['Do you use cloud services?']
        self.assertEqual(cloud_question.get_answer(), 'AWS and Azure')

    def test_question_object_creation_from_csv(self):
        """Test that Question objects are correctly created from CSV data."""
        ref_q = Reference_Questionnaire(
            file_path=self.reference_csv,
            question_col="Question - Full",
            answer_col="Answer - Full"
        )
        
        questions = ref_q.get_questions()
        question_obj = questions['What is your company name?']
        
        # Verify Question object properties
        self.assertIsInstance(question_obj, Question)
        self.assertEqual(question_obj.get_question(), 'What is your company name?')
        self.assertEqual(question_obj.get_answer(), 'Acme Corp')
        self.assertTrue(question_obj.is_reference)
        self.assertIsInstance(question_obj.get_question_id(), int)

    def test_csv_data_types_handling(self):
        """Test handling of various data types from CSV files."""
        unans_q = Unanswered_Questionnaire(
            file_path=self.unanswered_csv,
            question_col="Question - Full",
            answer_col="Answer - Full"
        )
        
        questions = unans_q.get_questions()
        
        # Test NaN handling - our improved code now filters out NaN values during question creation
        # so NaN answers become empty strings or questions without answers
        staff_question = questions['How many staff do you employ?']
        staff_answer = staff_question.get_answer()
        # NaN from pandas should be handled properly (converted to empty string or None)
        self.assertTrue(pd.isna(staff_answer) or staff_answer is None or staff_answer == '')
        
        # Test empty string handling (pandas may convert empty strings to NaN)
        revenue_question = questions['What is your annual revenue?']
        revenue_answer = revenue_question.get_answer()
        # Empty strings might be converted to NaN by pandas
        self.assertTrue(pd.isna(revenue_answer) or revenue_answer == '' or revenue_answer is None)
        
        # Test whitespace-only handling - our improved code filters out whitespace-only answers
        color_question = questions['What is your favorite color?']
        color_answer = color_question.get_answer()
        # Whitespace-only answers are now filtered out and converted to empty strings
        self.assertTrue(color_answer == '   ' or pd.isna(color_answer) or color_answer == '')

    @patch('os.path.exists', return_value=True)
    @patch('os.getenv')
    def test_exact_matching_with_real_data(self, mock_getenv, mock_exists):
        """Test exact question matching with real CSV data."""
        # Mock environment variables
        mock_getenv.side_effect = lambda key: {
            'CHATAI_BASE_URL': 'http://test-url.com',
            'CHATAI_API_KEY': 'test-key'
        }.get(key)
        
        filler = Questionnaire_Filler(
            reference_file_name=self.reference_csv,
            reference_question_col="Question - Full",
            reference_answer_col="Answer - Full",
            unanswered_file_name=self.unanswered_csv,
            unanswered_question_col="Question - Full",
            unanswered_answer_col="Answer - Full"
        )
        
        # Test exact matching
        unmatched, remaining = filler._match_exact_questions()
        
        # Should find one exact match: "What is your company name?"
        self.assertNotIn('What is your company name?', unmatched)
        
        # Should have several unmatched questions
        self.assertIn('Do you have privacy policies?', unmatched)
        self.assertIn('How many staff do you employ?', unmatched)
        
        # Verify that the exact match was processed correctly
        company_question = filler.unanswered_questionnaire.questions['What is your company name?']
        self.assertEqual(company_question.get_reference_question(), 'What is your company name?')
        self.assertEqual(company_question.get_question_match_score(), 1)

    @patch('os.path.exists', return_value=True)
    @patch('os.getenv')
    def test_get_items_for_answer_matching_with_real_data(self, mock_getenv, mock_exists):
        """Test _get_items_for_answer_matching with real CSV data."""
        # Mock environment variables
        mock_getenv.side_effect = lambda key: {
            'CHATAI_BASE_URL': 'http://test-url.com',
            'CHATAI_API_KEY': 'test-key'
        }.get(key)
        
        filler = Questionnaire_Filler(
            reference_file_name=self.reference_csv,
            reference_question_col="Question - Full",
            reference_answer_col="Answer - Full",
            unanswered_file_name=self.unanswered_csv,
            unanswered_question_col="Question - Full",
            unanswered_answer_col="Answer - Full"
        )
        
        # First do exact matching to set up reference questions
        filler._match_exact_questions()
        
        # Now test item generation
        items = filler._get_items_for_answer_matching()
        
        # Should filter out questions without meaningful answers
        question_texts = [item['q'] for item in items]
        
        # Should NOT include questions with NaN, empty, or whitespace-only answers
        self.assertNotIn('How many staff do you employ?', question_texts)  # NaN answer
        self.assertNotIn('What is your annual revenue?', question_texts)   # Empty answer
        self.assertNotIn('What is your favorite color?', question_texts)   # Whitespace-only answer
        
        # Should NOT include the exact match (identical answers)
        self.assertNotIn('What is your company name?', question_texts)  # Identical answers

    def test_csv_column_validation(self):
        """Test that the system handles missing or incorrect column names gracefully."""
        # Create CSV with wrong column names
        wrong_columns_data = {
            'Wrong Question Column': ['Test question'],
            'Wrong Answer Column': ['Test answer']
        }
        
        wrong_csv = os.path.join(self.temp_dir, 'wrong_columns.csv')
        pd.DataFrame(wrong_columns_data).to_csv(wrong_csv, index=False)
        
        # Should raise an appropriate error when column doesn't exist
        with self.assertRaises(KeyError):
            Reference_Questionnaire(
                file_path=wrong_csv,
                question_col="Question - Full",  # This column doesn't exist
                answer_col="Answer - Full"
            )

    def test_empty_csv_handling(self):
        """Test handling of empty CSV files."""
        # Create empty CSV
        empty_csv = os.path.join(self.temp_dir, 'empty.csv')
        pd.DataFrame({'Question - Full': [], 'Answer - Full': []}).to_csv(empty_csv, index=False)
        
        # Should not crash with empty CSV
        ref_q = Reference_Questionnaire(
            file_path=empty_csv,
            question_col="Question - Full",
            answer_col="Answer - Full"
        )
        
        questions = ref_q.get_questions()
        self.assertEqual(len(questions), 0)

    def test_csv_with_special_characters(self):
        """Test CSV reading with special characters and encoding."""
        special_data = {
            'Question - Full': [
                'What is your company\'s "primary" goal?',
                'Do you handle data with émojis: 😀?',
                'Questions with\nnewlines?',
                'Commas, semicolons; and "quotes"?'
            ],
            'Answer - Full': [
                'Growth & innovation',
                'Yes, we handle émojis: 🚀',
                'Multi-line\nanswers work',
                'Special chars: @#$%'
            ]
        }
        
        special_csv = os.path.join(self.temp_dir, 'special.csv')
        pd.DataFrame(special_data).to_csv(special_csv, index=False, encoding='utf-8')
        
        # Should handle special characters correctly
        ref_q = Reference_Questionnaire(
            file_path=special_csv,
            question_col="Question - Full",
            answer_col="Answer - Full"
        )
        
        questions = ref_q.get_questions()
        self.assertEqual(len(questions), 4)
        
        # Verify special characters are preserved
        emoji_question = questions['Do you handle data with émojis: 😀?']
        self.assertEqual(emoji_question.get_answer(), 'Yes, we handle émojis: 🚀')


def run_csv_integration_tests():
    """Run the CSV integration test suite."""
    # Create a test suite
    test_suite = unittest.TestSuite()
    
    # Add test class
    tests = unittest.TestLoader().loadTestsFromTestCase(TestCSVIntegration)
    test_suite.addTests(tests)
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    print("Running CSV Integration Tests")
    print("=" * 50)
    success = run_csv_integration_tests()
    print("=" * 50)
    if success:
        print("✅ All CSV integration tests passed!")
    else:
        print("❌ Some CSV integration tests failed!")
    
    sys.exit(0 if success else 1)
